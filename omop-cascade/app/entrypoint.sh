#!/bin/bash
# Rscript /app/test_libraries.R
URL="https://${GIT_USERNAME}:${GIT_PASSWORD}@${GIT_URL}"
DIR="/omop-cascade"
[ -d "$DIR" ] && git -C "$DIR" pull "$URL"
[ ! -d "$DIR" ] && git clone "$URL" "$DIR"
cd /omop-cascade
Rscript import_omop.R --id $CRDM_ID