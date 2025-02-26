#!/bin/bash

set -euxo pipefail

# Define all variables
# Git variables are coming from the '.env' file
OMOP_ES_DIR="omop_es"

# The following variables are relative to the OMOP_ES directory
MAIN_BATCHED="./main_batched.R"
MAIN_COMMAND="./main_command.R"

# Move to the OMOP_ES directory
cd $OMOP_ES_DIR

# Run the batched process if specified otherwise run the simple process
# All the variables prefixed with OMOP_ES are coming from the 'docker compose up' command line,
# and sent to the container in the 'docker-compose.yml' file
if [ "$OMOP_ES_BATCHED" = true ]; then
	echo "Running batched omop_es for ${OMOP_ES_SETTINGS_ID}..."
	Rscript $MAIN_BATCHED --settings_id $OMOP_ES_SETTINGS_ID --start_batch $OMOP_ES_START_BATCH --extract_dt $OMOP_ES_EXTRACT_DT
else
	echo "Running omop_es for ${OMOP_ES_SETTINGS_ID}..."
	if [ "$OMOP_ES_ZIP_OUTPUT" = true ]; then
		echo "Zipping output..."
		Rscript $MAIN_COMMAND --settings_id $OMOP_ES_SETTINGS_ID --zip_output
	else
		Rscript $MAIN_COMMAND --settings_id $OMOP_ES_SETTINGS_ID
	fi
fi
