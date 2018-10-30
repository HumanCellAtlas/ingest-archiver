import json
import unittest
import re
from unittest import TestCase

import requests
from mock import patch, Mock, MagicMock

import config
from archiver.converter import SampleConverter
from archiver.usiapi import USIAPI, ValidationStatus


# TODO use mocks for requests
# TODO add test cases

class USIAPITest(TestCase):

    def test_get_token_given_valid_credentials_return_token(self):
        # given:
        usi_api = USIAPI()

        # and:
        user_name = 'hca-ingest'
        password = 'password'

        # and:
        expected_token = 'ab009c1'

        # when:
        with patch.object(requests, 'get') as http_get:
            response = Mock()
            response.ok = True
            response.text = expected_token
            http_get.return_value = response
            token = usi_api.get_token(user_name, password)

        # then:
        self.assertEqual(expected_token, token)

    def test_get_token_given_invalid_credentials_return_none(self):
        # given:
        usi_api = USIAPI()

        # and:
        user_name = 'invalid'
        password = 'invalid'

        # when:
        with patch.object(requests, 'get') as http_get:
            response = Mock()
            response.ok = False
            http_get.return_value = response
            token = usi_api.get_token(user_name, password)

        # then:
        self.assertFalse(token)

    def test_fetch_validation_results(self):
        # given:
        base_url = 'https://ebi.ac.uk'
        usi_api = USIAPI(base_url=base_url)

        # when:
        submittable_id = '3fde005'
        authentication_token = '8dd9bb1'
        with patch.object(requests, 'get') as http_get:
            response = MagicMock()
            response.json.return_value = {'version': 7, 'validationStatus': 'Error'}
            http_get.return_value = response
            result = usi_api.fetch_validation_results(submittable_id, authentication_token)

        # then:
        http_get.assert_called()
        args, kwargs = http_get.call_args

        # and:
        url_pattern = re.compile(f'^{base_url}/.*/{submittable_id}$')
        self.assertTrue(url_pattern.match(args[0]), 'Call URL does not match expected pattern.')

        # and:
        self.assertIsNotNone(kwargs['headers'], 'No headers supplied with request.')
        self.assertEqual(f'Bearer {authentication_token}', kwargs['headers']['Authorization'])

        # and:
        self.assertIsNotNone(result)
        self.assertEqual(7, result.version)
        self.assertEqual(ValidationStatus.ERROR, result.status)


class TestUSIAPI(unittest.TestCase):

    def setUp(self):
        self.usi_api = USIAPI()

        with open(config.JSON_DIR + 'hca/biomaterials.json', encoding=config.ENCODING) as data_file:
            hca_samples = json.loads(data_file.read())

        self.hca_submission = {'samples': hca_samples}
        self.converter = SampleConverter()

        pass

    def test_create_submission(self):
        usi_submission = self.usi_api.create_submission()
        print(usi_submission)

        delete_url = usi_submission['_links']['self:delete']['href']
        self.usi_api.delete_submission(delete_url)

        self.assertTrue(usi_submission['_links']['self']['href'])

    def test_get_submission_contents(self):
        usi_submission = self.usi_api.create_submission()

        get_contents_url = usi_submission['_links']['contents']['href']

        contents = self.usi_api.get_contents(get_contents_url)

        delete_url = usi_submission['_links']['self:delete']['href']
        self.usi_api.delete_submission(delete_url)

        self.assertTrue(contents)

    def test_create_sample(self):
        usi_submission = self.usi_api.create_submission()

        get_contents_url = usi_submission['_links']['contents']['href']
        contents = self.usi_api.get_contents(get_contents_url)
        create_sample_url = contents['_links']['samples:create']['href']

        samples = self.hca_submission['samples']
        sample = samples[0]

        converted_sample = self.converter.convert(sample)

        created_usi_sample = self.usi_api.create_sample(create_sample_url, converted_sample)

        # clean up submission in USI
        delete_url = usi_submission['_links']['self:delete']['href']
        self.usi_api.delete_submission(delete_url)

        self.assertTrue(created_usi_sample)
