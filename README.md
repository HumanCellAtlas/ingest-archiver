[![Ingest Archiver Build Status](https://travis-ci.org/HumanCellAtlas/ingest-archiver.svg?branch=master)](https://travis-ci.org/HumanCellAtlas/ingest-archiver)
[![Maintainability](https://api.codeclimate.com/v1/badges/8ce423001595db4e6de7/maintainability)](https://codeclimate.com/github/HumanCellAtlas/ingest-archiver/maintainability)
[![codecov](https://codecov.io/gh/HumanCellAtlas/ingest-archiver/branch/master/graph/badge.svg)](https://codecov.io/gh/HumanCellAtlas/ingest-archiver)

_This repository was part of HCA DCP/1 and is not maintained anymore. DCP/2 development of this component continues in the forked repository at https://github.com/ebi-ait/ingest-archiver._

# Ingest Archiver
The archiver service is an ingest component that:
- Submits metadata to the appropriate external accessioning authorities. These are currently only EBI authorities (e.g. Biosamples).
- Converts metadata into the format accepted by each external authority

In the future it will:
- Update HCA metadata with accessions provided by external authorities

At the moment it consists of 3 stages.
1. Running the metadata archiver (MA) script (the one in this repository) which archives the metadata of a submission through the USI. This script also checks the submission of the files by the file uploader (see below).
1. Running the file uploader (FIU) of the archive data to the USI which runs on the EBI cluster. This will need access to the file submission JSON instructions generated by the metadata archiver.
1. Running the metadata archiver (MA) again to validate and submit the entire submission.

This component is currently invoked manually after an HCA submission.

# How to run
## Step 1 - Install the script requirements ##
`sudo pip3 install -r requirements.txt`

## Step 2 - Get project UUID ##
Get the project UUID of the project you want to archive. For example rsatija dataset `5f256182-5dfc-4070-8404-f6fa71d37c73`

## Step 3 - Set environment variables ##
```
# Required variables
# The location from which to pull metadata for submission. This is currently always the ingest 
# production environment.
$ export INGEST_API_URL=http://api.ingest.data.humancellatlas.org/

# The USI service to use for the submission. Choose between test and production
# TEST - https://submission-dev-ebi.ac.uk
# PROD - https://submission.ebi.ac.uk
$ export USI_API_URL=https://submission-dev.ebi.ac.uk

# The USI uses an EBI Authentication and Authorization Profile (AAP) account.
# There are separate ones for test and production.
# First we need to specify the AAP URL.
# TEST - https://explore.api.aai.ebi.ac.uk/auth
# PROD - https://api.aai.ebi.ac.uk/auth
$ export AAP_API_URL=https://explore.api.aai.ebi.ac.uk/auth

# Second we need to specify different AAP domains for test and production
# TEST - subs.test-team-21
# PROD - subs.team-2
$ export AAP_API_DOMAIN=subs.test-team-21

# Lastly we need to specify the AAP account password. It will be different for test and 
# production services.
# If you don't know them then please ask an ingest dev or another EBI wrangler.
$ export AAP_API_PASSWORD=password
```

## Step 4 - Run the metadata archiver ##
`./cli.py --alias_prefix=HCA_2019-01-07 --project_uuid=2a0faf83-e342-4b1c-bb9b-cf1d1147f3bb`

The --alias-prefix above is something the USI uses to identify entities for linking purposes. It is not related to HCA data and will not appear in the submission itself. However it needs to be unique for each submission. In principle it could be anything but we suggest that you stick with something along the lines of `--alias_prefix=HCA_YYYY-MM-DD`, e.g. `--alias_prefix=HCA_2019-01-07`

You should get output like:
```
Processing 6 bundles:
0d172fd7-f5af-4307-805b-3a421cdabd76
9526f387-bb5a-4a1b-9fd1-8ff977c62ffd
4d07290e-8bcc-4060-9b67-505133798ab0
b6d096f4-239a-476d-9685-2a03c86dc06b
985a9cb6-3665-4c04-9b93-8f41e56a2c71
19f1a1f8-d563-43a8-9eb3-e93de1563555

* PROCESSING BUNDLE 1/6: 0d172fd7-f5af-4307-805b-3a421cdabd76
Finding project entities in bundle...
1
Finding study entities in bundle...
1
Finding sample entities in bundle...
17
Finding sequencingExperiment entities in bundle...
1
Finding sequencingRun entities in bundle...
1
...
Entities to be converted: {
    "project": 1,
    "study": 1,
    "sample": 19,
    "sequencingExperiment": 6,
    "sequencingRun": 6
}
Saving Report file...
Saved to /home/me/ingest-archiver/ARCHIVER_2019-01-04T115615/REPORT.json!
##################### FILE ARCHIVER NOTIFICATION
Saved to /home/me/ingest-archiver/ARCHIVER_2019-01-04T115615/FILE_UPLOAD_INFO.json!
```

## Step 5 - Check REPORT.json ##
In your current directory, the MA will have generated a directory with the name `ARCHIVER_<timestamp>` containing two files, `REPORT.json` and `FILE_UPLOAD_INFO.json`. Inspect `REPORT.json` for errors. If there are any data files to upload you will always see FileReference usi_validation_errors in the submission_errors field. These you can ignore - we will upload the files in the following steps. For example: 

```
    "completed": false,
    "submission_errors": [
        {
            "error_message": "Failed in USI validation.",
            "details": {
                "usi_validation_errors": [
                    {
                        "FileReference": [
                            "The file [306982e4-5a13-4938-b759-3feaa7d44a73.bam] referenced in the metadata is not exists on the file storage area."
                        ]
                    },
                    {
                        "FileReference": [
                            "The file [988de423-1543-4a84-be9a-dd81f5feecff.bam] referenced in the metadata is not exists on the file storage area."
                        ]
                    },
                    {
                        "FileReference": [
                            "The file [fd226091-9a8f-44a8-b49e-257fffa2b931.bam] referenced in the metadata is not exists on the file storage area."
                        ]
                    }
                ]
            }
        }
    ],
```

If you see problems in the entities added to the submission with non-empty errors and warnings fields then please report. This is a small snippet showing a successful entity addition:

```
    "entities": {
        "HCA_2019-01-07-13-53__project_2a0faf83-e342-4b1c-bb9b-cf1d1147f3bb": {
            "errors": [], 
            "accession": null,
            "warnings": [], 
            "entity_url": "https://submission-dev.ebi.ac.uk/api/projects/c26466cd-9551-46c9-b760-72e05cfc51ac"
        },
```

## Step 6 - Copy FILE_UPLOAD_INFO.json to cluster ###
`FILE_UPLOAD_INFO.json` contains the instructions necessary for the file uploader to convert and upload submission data to the USI. You need to copy this file to HCA NFS directory accessible by the cluster. However, you also need to give it a unique name so that it doesn't clash with any existing JSON files.

Therefore, prepend something to the filename to make it unique. This can be anything but we suggest your username and the dataset. For example `mfreeberg_rsatija_FILE_UPLOAD_INFO.json`

You will copy the file using the secure copy (`scp`) command. This will need your EBI password and is equivalent to copying a file through ssh. For example

```scp FILE_UPLOAD_INFO.json ebi-cli.ebi.ac.uk:/nfs/production/hca/mfreeberg_rsatija_FILE_UPLOAD_INFO.json```

## Step 7 - Login to cluster ##
Login to EBI CLI to access the cluster with your EBI password
`ssh ebi-cli.ebi.ac.uk`

## Step 8 - Run the file uploader ##
Run the file uploader with the bsub command below. We will explain more about the components below.

`bsub 'singularity run -B /nfs/production/hca:/data docker://quay.io/humancellatlas/ingest-file-archiver -d=/data -f=/data/mfreeberg_rsatija_FILE_UPLOAD_INFO.json -l=https://explore.api.aai.ebi.ac.uk/auth -p=<ebi-aap-password> -u=hca-ingest'`

* `bsub` - the command for submitting a job to the cluster
* `singularity` - the cluster runs jobs using Singularity containers.
* `B /nfs/production/hca:/data` - this binds the `/nfs/production/hca` directory to `/data` inside the container.
* `docker://quay.io/humancellatlas/ingest-file-archiver` - Singularity can run Docker images directly. This is the image for the file uploader.
* `-d=/data` - workspace used to store downloaded files, metadata and conversions.
* `-f=/data/mfreeberg_rsatija_FILE_UPLOAD_INFO.json` - the location of the `FILE_UPLOAD_INFO.json` you copied in a previous step.
* `-l=https://explore.api.aai.ebi.ac.uk/auth` - The AAP API url, same as the AAP_API_URL environmental variable. As above, this will need to be `-l=https://api.aai.ebi.ac.uk/auth` instead if you are submitting to production USI.
* `-p=<ebi-aap-password>` - Test or production USI AAP password as used previously
* `-u=hca-ingest` - The USI user to use. This will always be hca-ingest right now.

On submitting you will see a response along the lines

`Job <894044> is submitted to default queue <research-rh7>.`

This shows that the job has been submitted to the cluster. To see the status of the job run

`bjobs -W`

The job should be reported as running but may also be pending if the cluster is busy.

If you want to see the job's current stdout/stderr then run the [bpeek command](https://www.ibm.com/support/knowledgecenter/en/SSETD4_9.1.3/lsf_command_ref/bpeek.1.html)

`bpeek <job-id>`

Once the job is running processing may take a long time, many days in the case where a dataset has many data file conversions to perform. It will continue running after you logout and on completion or failure will e-mail you with the results. Wait until you receive this e-mail before proceeding with the next step.

Here are some further useful links about using the cluster and associated commands.

* https://sysinf.ebi.ac.uk/doku.php?id=ebi_cluster_good_computing_guide
* https://sysinf.ebi.ac.uk/doku.php?id=introducing_singularity

## Step 9 - Check the cluster job results e-mail
The e-mail you receive will have a title similar to `Job %JOB-ID%: <singularity run -B /nfs/production/hca/mfreeberg:/data docker://quay.io/humancellatlas/ingest-file-archiver -d=/data -f=/data/FILE_UPLOAD_INFO.json -l=https://explore.api.aai.ebi.ac.uk/auth -p=%PW% -u=hca-ingest> in cluster <EBI> Done`

This will contain a whole load of detail about the job run. Scroll down to the bottom and you should see a bunch of INFO messages such as 

`INFO:hca:File process_15.json: GET SUCCEEDED. Stored at fd226091-9a8f-44a8-b49e-257fffa2b931/process_15.json.`

and 

`INFO:hca:File PBMC_RNA_R1.fastq.gz: GET SUCCEEDED. Stored at fd226091-9a8f-44a8-b49e-257fffa2b931/PBMC_RNA_R1.fastq.gz.`

If you see any `WARNING` or `ERROR` messages please re-run the singularity command from the previous step (it will retry the failed steps) and tell ingest development.

## Step 10 - Validate submission and submit ##
To do this you need to run the metadata archiver again on your local machine as you did earlier.

`./cli.py --submission_url=https://submission-dev.ebi.ac.uk/api/submissions/<submission-uuid>`

You can get the submission UUID from either the output of the initial metadata archiver run, e.g.

`USI SUBMISSION: https://submission-dev.ebi.ac.uk/api/submissions/b729f228-d587-440c-ae5b-d0c1f34b8766`

or in the `REPORT.json` in the `submission-url` field (there will be several). For example,

`"submission_url": "https://submission-dev.ebi.ac.uk/api/submissions/b729f228-d587-440c-ae5b-d0c1f34b8766"`

On success you will get the message `SUCCESSFULLY SUBMITTED`. You're done!

## Running the data uploader outside of singularity.
For test purposes you can run the data uploader outside of singularity with the command

`docker run --rm -v $PWD:/data quay.io/humancellatlas/ingest-file-archiver -d=/data -f=/data/FILE_UPLOAD_INFO.json -l=https://api.aai.ebi.ac.uk/auth -p=<password> -u=hca-ingest`

# How to run the tests

```
python -m unittest discover -s tests -t tests

```

# Versioning

For the versions available, see the [tags on this repository](https://github.com/HumanCellAtlas/ingest-archiver/tags).

# License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details
