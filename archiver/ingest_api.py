import json
import requests
import logging

import requests.packages.urllib3.util.retry as retry

import config
import polling

# TODO this file may be removed if the event will contain all the hca submission details
# if not, this must be integrated with the current ingest api module that other ingest services uses

AUTH0_PARAMS = {
    "client_id": "Zdsog4nDAnhQ99yiKwMQWAPc2qUDlR99",
    "client_secret": "t-OAE-GQk_nZZtWn-QQezJxDsLXmU7VSzlAh9cKW5vb87i90qlXGTvVNAjfT9weF",
    "audience": "http://localhost:8080",
    "grant_type": "client_credentials"
}

AUTH0_URL = 'https://danielvaughan.eu.auth0.com/oauth/token'


class IngestAPI:
    def __init__(self, url=None):
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'Content-type': 'application/json',
        }
        self.url = url if url else config.INGEST_API_URL
        self.logger.info(f'Using {self.url}')
        self.entity_cache = {}
        self.cache_enabled = True

        retry_policy = retry.Retry(
            total=100,  # seems that this has a default value of 10,
            # setting this to a very high number so that it'll respect the status retry count
            status=17,  # status is the no. of retries if response is in status_forcelist,
            # this count will retry for ~20mins with back off timeout within
            read=10,
            status_forcelist=[500, 502, 503, 504],
            backoff_factor=0.6)

        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_policy)
        self.session.mount('https://', adapter)

    def get_related_entity(self, entity, relation, related_entity_type):
        related_entity_url = entity['_links'][relation]['href']
        related_entities = list(self._get_all(related_entity_url, related_entity_type))
        return related_entities

    def get_submission_by_id(self, submission_id):
        get_submission_url = self.url + '/submissionEnvelopes/' + submission_id

        response = self.session.get(get_submission_url, headers=self.headers)

        submission = None

        if response.ok:
            submission = response.json()

        return submission

    def get_concrete_entity_type(self, entity):
        content = entity.get('content')
        schema_url = content.get('describedBy')
        response = self.session.get(schema_url, headers=self.headers)
        schema = self._handle_response(response)

        return schema.get('name')

    def get_entity_by_uuid(self, entity_type, uuid):
        entity_url = f'{self.url}{entity_type}/search/findByUuid?uuid={uuid}'

        entity_json = self._get_cached_entity(uuid)

        if not entity_json:
            response = self.session.get(entity_url, headers=self.headers)
            entity_json = self._handle_response(response)
            self._cache_entity(uuid, entity_json)

        return entity_json

    def _get_cached_entity(self, uuid):
        if self.cache_enabled and self.entity_cache.get(uuid):
            return self.entity_cache.get(uuid)

    def _cache_entity(self, uuid, entity_json):
        if self.cache_enabled and not self.entity_cache.get(uuid):
            self.entity_cache[uuid] = entity_json

    def get_submission_by_uuid(self, submission_uuid):
        return self.get_entity_by_uuid('submissionEnvelopes', submission_uuid)

    def get_biomaterial_by_uuid(self, biomaterial_uuid):
        return self.get_entity_by_uuid('biomaterials', biomaterial_uuid)

    def get_project_by_uuid(self, project_uuid):
        return self.get_entity_by_uuid('projects', project_uuid)

    def get_file_by_uuid(self, file_uuid):
        return self.get_entity_by_uuid('files', file_uuid)

    def get_bundle_uuids(self, project_uuid):
        project = self.get_project_by_uuid(project_uuid)
        submissions = self.get_related_entity(project, "submissionEnvelopes", "submissionEnvelopes")

        bundle_uuids = []
        for submission in submissions:
            bundle_manifests = self.get_related_entity(submission, "bundleManifests", "bundleManifests")
            for bundle_manifest in bundle_manifests:
                bundle_uuids.append(bundle_manifest.get("bundleUuid"))

        return bundle_uuids

    def get_samples(self, get_samples_url):
        response = self.session.get(get_samples_url, headers=self.headers)

        samples = []

        if response.ok:
            samples = response.json()["_embedded"]["samples"]

        return samples

    def get_bundle_manifest(self, bundle_uuid):
        get_bundle_manifest_url = self.url + '/bundleManifests/search/findByBundleUuid?uuid=' + bundle_uuid
        response = self.session.get(get_bundle_manifest_url, headers=self.headers)
        return self._handle_response(response)

    def update_content(self, entity_url, content_json):
        response = self.session.get(entity_url)
        content = self._handle_response(response)['content']
        content.update(content_json)
        response = requests.patch(entity_url, json.dumps({'content': content}))

        return self._handle_response(response)

    def _handle_response(self, response):
        response.raise_for_status()
        return response.json()

    def create_submission(self, auth_token):
        if not auth_token:
            auth_token = self.get_auth_token()

        token_type = auth_token['token_type']
        access_token = auth_token['access_token']

        auth_header = f"{token_type} {access_token}"

        headers = {
            'Content-type': 'application/json',
            'Authorization': auth_header
        }

        links = self.get_ingest_links()
        create_submission_url = links['submissionEnvelopes']['href'].rsplit("{")[0]

        response = requests.post(create_submission_url, headers=headers, data='{}')

        return self._handle_response(response)

    def delete_submission(self, submission_url):
        response = requests.delete(submission_url, headers=self.headers)
        response.raise_for_status()

    def get_ingest_links(self):
        response = self.session.get(self.url, headers=self.headers)
        ingest = self._handle_response(response)

        if ingest:
            return ingest["_links"]

        return None

    def link_samples_to_submission(self, link_url, sample_url):
        sample_id = sample_url.split('/')[-1]
        link_url = link_url + '/' + sample_id
        response = requests.put(link_url, headers=self.headers)

        return self._handle_response(response)

    def get_submit_url(self, submission):
        submission_url = submission['_links']['self']['href']
        response = self.session.get(submission_url, headers=self.headers)
        submission = self._handle_response(response)

        if submission and 'submit' in submission['_links']:
            return submission['_links']["submit"]["href"].rsplit("{")[0]

        return None

    def submit(self, submit_url):
        response = requests.put(submit_url, headers=self.headers)

        return self._handle_response(response)

    def get_auth_token(self):
        response = requests.post(AUTH0_URL,
                                 data=json.dumps(AUTH0_PARAMS),
                                 headers={'Content-type': 'application/json'})
        response.raise_for_status()
        data = response.json()

        return data

    def get_link_href(self, hal_response, link_name):
        link = hal_response['_links'][link_name]
        return link['href'].rsplit("{")[0] if link else ''

    def create_sample(self, submission, content):
        samples_url = self.get_link_href(submission, 'biomaterials')

        response = requests.post(samples_url,
                                 data=json.dumps(content),
                                 headers=self.headers)

        response.raise_for_status()
        return response.json()

    def submit_if_valid(self, submission):
        try:
            submit_url = polling.poll(
                lambda: self.get_submit_url(submission),
                step=5,
                timeout=60
            )
            self.submit(submit_url)
        except polling.TimeoutException:
            self.logger.error("Failed to do an update submission. The submission takes too long to get " +
                              "validated and couldn't be submitted.")

    def _get_all(self, url, entity_type):
        r = self.session.get(url, headers=self.headers)
        r.raise_for_status()
        if "_embedded" in r.json():
            for entity in r.json()["_embedded"][entity_type]:
                yield entity
            while "next" in r.json()["_links"]:
                r = self.session.get(r.json()["_links"]["next"]["href"], headers=self.headers)
                for entity in r.json()["_embedded"][entity_type]:
                    yield entity