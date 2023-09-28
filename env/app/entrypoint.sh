#!/bin/sh
if [ "$CRDM_TOOL" = "omop-cascade" ]; then
    cd /app/omop-cascade
    Rscript import_omop.R --id $CRDM_CONF
fi
if [ "$CRDM_TOOL" = "omop_es" ]; then
    URL="https://${OE_GIT_USERNAME}:${OE_GIT_TOKEN}@${OE_GIT_URL}"
    DIR="/app/omop_es"
    [ -d "$DIR" ] && git -C "$DIR" pull "$URL"
    [ ! -d "$DIR" ] && git clone "$URL" "$DIR"
    cd /app/omop_es
    Rscript main_command.R --id $CRDM_CONF
fi
