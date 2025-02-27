FROM rocker/tidyverse:4.4.2 AS base

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    curl \
    gnupg \
    libudunits2-dev \
    libgdal-dev && \
    apt-get autoremove --yes && apt-get clean --yes && rm -rf /var/lib/apt/lists/*

# Enable Microsoft SQLServer
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 && \
    apt-get autoremove --yes && apt-get clean --yes && rm -rf /var/lib/apt/lists/*


RUN install2.r --error --skipinstalled \
    --repos http://cran.rstudio.com/ \
    DBI \
    R.utils \
    R6 \
    RPostgres \
    RSQLite \
    arrow \
    assertr \
    assertthat \
    bit64 \
    chron \
    cli \
    config \
    dbplyr \
    devtools \
    glue \
    here \
    janitor \
    jsonvalidate \
    log4r \
    lubridate \
    odbc \
    processx \
    purrr \
    readr \
    readxl \
    remotes \
    rjson \
    rlang \
    zip \
    && rm -rf /tmp/downloaded_packages

RUN R -e "remotes::install_github('andysouth/omopcept')"

# Add docker user
ARG DOCKER_USER_GID
RUN groupadd --gid $DOCKER_USER_GID docker && useradd --gid $DOCKER_USER_GID docker

WORKDIR /app

# omop_es-builder
# using multi-stage build so the GitHub PAT is not present in the final image
FROM base AS omop_es-builder

ARG OMOP_ES_BRANCH
ARG GITHUB_PAT

RUN git clone -b ${OMOP_ES_BRANCH} https://${GITHUB_PAT}@github.com/uclh-criu/omop_es.git ./omop_es

WORKDIR /app/omop_es
RUN Rscript omop_metadata/download_omop_metadata.R && \
    Rscript source_access/UCLH/mock_database/recreate_mockdb.R

# Final omop_es iamge
FROM base AS omop_es

COPY --from=omop_es-builder /app/omop_es /app/omop_es
COPY --chmod=0755 ./omop_es.sh .

USER docker

CMD ["/app/omop_es.sh"]

# omop-cascade
# omop-cascade-builder
# using multi-stage build so the GitHub PAT is not present in the final image
FROM base AS omop-cascade-builder

ARG OMOP_CASCADE_BRANCH
ARG GITHUB_PAT

RUN git clone -b ${OMOP_CASCADE_BRANCH} \
    https://${GITHUB_PAT}@github.com/uclh-criu/omop-cascade.git \
    ./omop-cascade

# omop-cascade
FROM base AS omop-cascade

COPY --from=omop-cascade-builder /app/omop-cascade /app/omop-cascade

USER docker
WORKDIR /app/omop-cascade
CMD ["sh", "-c", "Rscript import_omop.R --id=${CRDM_ID}"]
