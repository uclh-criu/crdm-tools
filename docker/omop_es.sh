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

# Helper function to convert to lowercase
tolower() {
	echo "$1" | tr '[:upper:]' '[:lower:]'
}

# Define all variables
# Git variables are coming from the '.env' file
OMOP_ES_DIR="omop_es"

DEBUG=$(tolower ${DEBUG:-false})
BATCHED=$(tolower ${BATCHED:-false})
ZIP_OUTPUT=$(tolower ${ZIP_OUTPUT:-false})

# The following variables are relative to the OMOP_ES directory
MAIN_BATCHED="./main/batched.R"
MAIN_COMMAND="./main/command.R"

# Move to the OMOP_ES directory
cd $OMOP_ES_DIR

# Fetch latest refs from remote to ensure we can checkout any branch/tag/commit
git fetch --all --tags --quiet

# Determine if OMOP_ES_BRANCH is a commit SHA, tag, or branch
if git rev-parse --verify "${OMOP_ES_BRANCH}^{commit}" >/dev/null 2>&1; then
	echo "Checking out pinned version: ${OMOP_ES_BRANCH}"
	git checkout "${OMOP_ES_BRANCH}"
	echo "Running omop_es from pinned commit: $(git rev-parse --short HEAD)"
else
	echo "Checking out latest from branch: ${OMOP_ES_BRANCH}"
	git checkout "${OMOP_ES_BRANCH}"
	git pull origin "${OMOP_ES_BRANCH}"
	echo "Running omop_es from commit: $(git rev-parse --short HEAD)"
fi

# Run the batched process if specified, otherwise run the simple process
# Variables are passed through from the environment
if [ $BATCHED = "true" ]; then
	echo "Running batched omop_es..."
	CMD="Rscript $MAIN_BATCHED --settings_id $SETTINGS_ID"
	# Add on extra CLI arguments if they're filled
	[ -n "$OUTPUT_DIRECTORY" ] && CMD="$CMD --output_directory $OUTPUT_DIRECTORY"
else
	CMD="Rscript $MAIN_COMMAND --settings_id $SETTINGS_ID"
fi

## Add on extra CLI arguments if they're filled
[ $ZIP_OUTPUT = "true" ] && CMD="$CMD --zip_output"

# If in debug mode, only print the command
if [ "$DEBUG" = "true" ]; then
	echo "$CMD"
	exit 0
fi

echo "Installing dependencies..."
# Disable pak as this invalidates where we expect the cache to be
Rscript -e "options(Ncpus=4, renv.config.pak.enabled=FALSE); renv::restore()"

if [ "$ENVIRONMENT" = "dev" ]; then
	echo "Recreating mock database..."
	Rscript source_access/UCLH/mock_database/recreate_mockdb.R
fi

echo "Running omop_es for ${SETTINGS_ID}..."

$CMD
