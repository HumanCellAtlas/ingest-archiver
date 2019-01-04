[![Ingest Archiver Build Status](https://travis-ci.org/HumanCellAtlas/ingest-archiver.svg?branch=master)](https://travis-ci.org/HumanCellAtlas/ingest-archiver)
[![Maintainability](https://api.codeclimate.com/v1/badges/8ce423001595db4e6de7/maintainability)](https://codeclimate.com/github/HumanCellAtlas/ingest-archiver/maintainability)
[![codecov](https://codecov.io/gh/HumanCellAtlas/ingest-archiver/branch/master/graph/badge.svg)](https://codecov.io/gh/HumanCellAtlas/ingest-archiver)

# Ingest Archiver
The archiver service is an ingest component that:
- Submits metadata to the appropriate external accessioning authorities. These are currently only EBI authorities (e.g. Biosamples).
- Converts metadata into the format accepted by each external authority

In the future it will:
- Update HCA metadata with accessions provided by external authorities

At the moment it consists of a minimum of 2 steps.
1. A metadata archiver (MA) script (the one in this repository) which archives the metadata of a submission through the USI. This script also checks the submission of the files by the file uploader (see below).
1. A file uploader (FIU) of the archive data to the USI which runs on the EBI cluster. This will need access to the file submission JSON instructions generated by the metadata archiver.

The archiver uses the [USI Submissions API](https://submission-dev.ebi.ac.uk/api/docs/how_to_submit_data_programatically.html#_overview) to communicate with EBI external authorities.

This component is currently invoked manually after an HCA submission.

# How to run
# Run the archiver script
1. Install the script requirements
`sudo pip3 install -r requirements.txt`

2. Get the project UUID of the project you want to archive. For example rsatija dataset `5f256182-5dfc-4070-8404-f6fa71d37c73`

3. Set environment variables
```
# Required variables
# If you don’t know the EBI Authentication and Authorization Profile (AAP) password we’re using for 
# archiving please ask an ingest dev or another EBI wrangler. This password will be different
# depending on whether you're upload to test archives through USI or production ones.
$ export AAP_API_PASSWORD=password
$ export INGEST_API_URL=http://api.ingest.data.humancellatlas.org/

# https://submission-dev-ebi.ac.uk - USI test archiving. This only gets wiped every 24 hours so if you
# want to eep testing you may have to do so with a different dataset.
# https://submission.ebi.ac.uk - USI production archiving.
$ export USI_API_URL=https://submission-dev.ebi.ac.uk

# Optional variables
# VALIDATION_POLL_FOREVER and SUBMISSION_POLL_FOREVER control whether this script keeps checking for 
# successful validation then submission through the USI once it has completed the metadata archiving
# part. If these aren't set to TRUE or you stop the script before validation/submission has 
# completed, then you can always run the script again later, at which point it will jump back to 
# validation/submission polling rather than trying to archive metadata again. 
# Default for these parameters is FALSE.
$ export VALIDATION_POLL_FOREVER=TRUE
$ export SUBMISSION_POLL_FOREVER=TRUE
```

4. Run the metadata archiver
`python3 cli.py --project_uuid=2a0faf83-e342-4b1c-bb9b-cf1d1147f3bb`

You should get output like
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
Entities to be converted: {}
Saving Report file...
Saved to /home/me/ingest-archiver/ARCHIVER_2019-01-04T115615/REPORT.json!
##################### FILE ARCHIVER NOTIFICATION
Saved to /home/me/ingest-archiver/ARCHIVER_2019-01-04T115615/FILE_UPLOAD_INFO.json!
```

5. In your current directory, the MA will have generated a directory with the name `ARCHIVER_<timestamp>`. Change to this directory, e.g. 
`cd ARCHIVER_2018-12-10T141748`

6. In this directory there will be a file called `FILE_UPLOAD_INFO.json`. Copy this file to the HCA NFS namespace via the cluster. For this step you must be connected to the EBI internal network
`scp FILE_UPLOAD_INFO.json ebi-cli.ebi.ac.uk:/nfs/production/hca`

EITHER
7a . Login to EBI CLI with your usual user and password
`ssh ebi-cli.ebi.ac.uk`
  
OR
7b. On your local machine run
`docker run --rm -v $PWD:/data quay.io/humancellatlas/ingest-file-archiver -d=/data -f=/data/FILE_UPLOAD_INFO.json -l=https://api.aai.ebi.ac.uk/auth -p=<password> -u=hca-ingest`

8. Run the metadata archiver with this switch
`python3 cli.py --submission_url="https://submission-dev.ebi.ac.uk/api/submissions/<submission-uuid>"`

e.g. 

`python3 cli.py --submission_url="https://submission-dev.ebi.ac.uk/api/submissions/68fb4263-0868-4391-a9dc-eb59ab30a833`

Keep running or rerun until it says SUCCESSFULLY SUBMITTED

# How to run the tests

```
python -m unittest discover -s tests -t tests

```

# Deployment
See https://github.com/HumanCellAtlas/ingest-kube-deployment.

An AAP username and password is also needed to use the USI API and must be set in the config.py or as environment variable.

# Versioning

For the versions available, see the [tags on this repository](https://github.com/HumanCellAtlas/ingest-archiver/tags).

# License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details
