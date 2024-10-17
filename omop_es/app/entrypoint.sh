#!/bin/bash
#
# Used to debug R libraries
# Rscript /app/test_libraries.R
#
# Define all variables
# Git variables are coming from the '.env' file
FULL_GIT_URL="https://${GIT_USERNAME}:${GIT_PASSWORD}@${GIT_URL}"
OMOP_ES_DIR="/omop_es"
# The following variables are relative to the OMOP_ES directory
METADATA_VERSION="./omop_metadata/metadata_version.txt"
METADATA_DOWNLOAD="./omop_metadata/download_omop_metadata.R"
MAIN_BATCHED="./main_batched.R"
MAIN_COMMAND="./main_command.R"
#
# Clone the GitHub repo if it doesn't exist,
# otherwise pull the latest version of the specified branch
if [ ! -d $OMOP_ES_DIR ]; then
    git clone -b $GIT_BRANCH $FULL_GIT_URL $OMOP_ES_DIR
else
    git -C $OMOP_ES_DIR pull $FULL_GIT_URL $GIT_BRANCH
fi
#
# Move to the OMOP_ES directory
cd $OMOP_ES_DIR
#
# Download the metadata files if they don't exist
if [ ! -f $METADATA_VERSION ]; then
    Rscript $METADATA_DOWNLOAD
fi
#
# Run the batched process if specified otherwise run the simple process
# All the variables prefixed with CRDM are coming from the 'docker compose up' command line,
# and sent to the container in the 'docker-compose.yml' file
if $CRDM_BATCH; then
    Rscript $MAIN_BATCHED --id $CRDM_ID --zip $CRDM_ZIP --batch $CRDM_START --dir $CRDM_DIR
else
    Rscript $MAIN_COMMAND --id $CRDM_ID
fi