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
    renv \
    rjson \
    rlang \
    zip \
    && rm -rf /tmp/downloaded_packages

# Add docker user
ARG DOCKER_USER_GID
RUN groupadd --gid $DOCKER_USER_GID docker && useradd --gid $DOCKER_USER_GID docker

# Set ownership of /home/docker as this is where renv will store its cache
RUN mkdir /home/docker && \
    chown -R docker:docker /home/docker && \
    chmod -R g+rwXs /home/docker

WORKDIR /app
RUN chown -R docker:docker /app && \
    chmod -R g+rwXs /app
USER docker

# omop_es-builder
# using multi-stage build so the GitHub PAT is not present in the final image
FROM base AS omop_es-builder

ARG OMOP_ES_BRANCH=master
ARG GITHUB_PAT

RUN git clone -b ${OMOP_ES_BRANCH} https://${GITHUB_PAT}@github.com/uclh-criu/omop_es.git ./omop_es

WORKDIR /app/omop_es
# Its a bit dumb but let's use the cache if we get a network error
RUN Rscript -e "renv::restore()" || \
    Rscript -e "renv::restore()" || \
    Rscript -e "renv::restore()" || \
    Rscript -e "renv::restore()"

RUN Rscript omop_metadata/download_omop_metadata.R && \
    Rscript source_access/UCLH/mock_database/recreate_mockdb.R

# Final omop_es iamge
FROM base AS omop_es

ARG RENV_CACHE=/home/docker/.cache/R/renv

COPY --from=omop_es-builder --chown=docker:docker --chmod=0755 /app/omop_es /app/omop_es
COPY --from=omop_es-builder --chown=docker:docker --chmod=0755 ${RENV_CACHE} ${RENV_CACHE}
COPY --chmod=0755 ./omop_es.sh .

CMD ["/app/omop_es.sh"]

# omop-cascade
# omop-cascade-builder
# using multi-stage build so the GitHub PAT is not present in the final image
FROM base AS omop-cascade-builder

ARG OMOP_CASCADE_BRANCH
ARG GITHUB_PAT

RUN git clone -b ${OMOP_CASCADE_BRANCH} \
    https://${GITHUB_PAT}@github.com/uclh-criu/omop-cascade.git \
    /app/omop-cascade

# omop-cascade
FROM base AS omop-cascade

COPY --from=omop-cascade-builder --chmod=0775 /app/omop-cascade /app
WORKDIR /app
CMD Rscript /app/import_omop.R --id=${CRDM_ID}
