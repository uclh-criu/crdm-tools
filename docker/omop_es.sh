#!/bin/bash

set -euxo pipefail

# Define all variables
# Git variables are coming from the '.env' file
OMOP_ES_DIR="omop_es"

# The following variables are relative to the OMOP_ES directory
MAIN_BATCHED="./main/batched.R"
MAIN_COMMAND="./main/command.R"

# Move to the OMOP_ES directory
cd $OMOP_ES_DIR

# Run the batched process if specified otherwise run the simple process
# All the variables prefixed with OMOP_ES are coming from the 'docker compose up' command line,
# and sent to the container in the 'docker-compose.yml' file

echo "Running omop_es for ${OMOP_ES_SETTINGS_ID}..."
if [ "$OMOP_ES_BATCHED" = true ]; then
    echo "Running batched omop_es..."
    CMD="Rscript $MAIN_BATCHED --settings_id $OMOP_ES_SETTINGS_ID"
    # Add on extra CLI arguments if they're filled
    [ -n "$OMOP_ES_OUTPUT_DIRECTORY" ] && CMD="$CMD --output-directory $OMOP_ES_OUTPUT_DIRECTORY"
else
    CMD="Rscript $MAIN_COMMAND --settings_id $OMOP_ES_SETTINGS_ID"
    ## Add on extra CLI arguments if they're filled
    [ "$OMOP_ES_ZIP_OUTPUT" = true ] && CMD="$CMD --zip_output"
fi

$CMD
