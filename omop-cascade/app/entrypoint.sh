#!/bin/bash
#
# Used to debug R libraries
# Rscript /app/test_libraries.R
#
# Define all variables
# Git variables are coming from the '.env' file
FULL_GIT_URL="https://${GITHUB_PAT}@${GIT_URL}"
OMOP_CASCADE_DIR="/omop-cascade"
# The following variable is relative to the omop-cascade directory
IMPORT_OMOP="./import_omop.R"
#
# Clone the GitHub repo if it doesn't exist,
# otherwise pull the latest version of the specified branch
if [ ! -d $OMOP_CASCADE_DIR ]; then
	git clone -b $GIT_BRANCH $FULL_GIT_URL $OMOP_CASCADE_DIR
else
	git -C $OMOP_CASCADE_DIR pull $FULL_GIT_URL $GIT_BRANCH
fi
#
# Move to the omop-cascade directory
cd $OMOP_CASCADE_DIR
#
# Run the R script to import an OMOP parquet dataset
# into a database
# The CRDM_ID is coming from the 'docker compose up' command line
# and sent to the container in the 'docker-compose.yml' file
Rscript $IMPORT_OMOP --id $CRDM_ID
