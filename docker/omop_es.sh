#!/bin/bash
#  Copyright (c) University College London Hospitals NHS Foundation Trust
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
################################################################################

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
    [ -n "$OMOP_ES_OUTPUT_DIRECTORY" ] && CMD="$CMD --output_directory $OMOP_ES_OUTPUT_DIRECTORY"
else
    CMD="Rscript $MAIN_COMMAND --settings_id $OMOP_ES_SETTINGS_ID"
    ## Add on extra CLI arguments if they're filled
    [ "$OMOP_ES_ZIP_OUTPUT" = true ] && CMD="$CMD --zip_output"
fi

$CMD
