#!/bin/bash
# Rscript /app/test_libraries.R
URL="https://${GIT_USERNAME}:${GIT_PASSWORD}@${GIT_URL}"
DIR="/omop_es"
OUT="/share/criudata/crdm-tools/omop_es/$CRDM_ID/$(date +"%Y%m%d%H%M%S")"
[ -d "$DIR" ] && git -C "$DIR" pull "$URL"
[ ! -d "$DIR" ] && git clone "$URL" "$DIR" && cd /omop_es && Rscript env_setup/download_omop_metadata.R
cd /omop_es
if $CRDM_BATCH; then
    Rscript main_batched.R --id $CRDM_ID
else
    Rscript main_command.R --id $CRDM_ID
fi
mkdir -p $OUT
mv /share/local/* $OUT