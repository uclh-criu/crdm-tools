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

FROM rocker/tidyverse:4.4.3 AS base

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    curl \
    # dependency for arrow R pkg
    cmake \
    # dependency for V8 R pkg
    libnode-dev \
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

# Add docker user
ARG DOCKER_USER_GID
RUN groupadd --gid $DOCKER_USER_GID docker && useradd --create-home --gid $DOCKER_USER_GID docker

# Set ownership of /home/docker as this is where renv will store its cache
RUN chown -R docker:docker /home/docker && \
    chmod -R g+rwXs /home/docker

WORKDIR /app
RUN chown -R docker:docker /app && \
    chmod -R g+rwXs /app
USER docker

# omop_es-builder
# using multi-stage build so the GitHub PAT is not present in the final image
FROM base AS omop_es-builder

# Initial pull, always clone from default branch for initial renv restore
# This step is cached
ARG GITHUB_PAT
RUN git clone https://${GITHUB_PAT}@github.com/uclh-criu/omop_es.git ./omop_es

WORKDIR /app/omop_es
# Its a bit dumb but let's use the cache if we get a network error
RUN for i in 1 2 3 4; do \
    Rscript -e "options(Ncpus=4); renv::restore()" && break || \
    (echo "renv::restore() failed, attempt $i/4" && sleep 5); \
    done

RUN Rscript omop_metadata/download_omop_metadata.R && \
    Rscript source_access/UCLH/mock_database/recreate_mockdb.R

# Pull the requested branch and update any changed packages
ARG OMOP_ES_BRANCH=master
# Disable caching so we always pull the latest ref
ARG CACHE_BUST
RUN git checkout ${OMOP_ES_BRANCH}
RUN Rscript -e "options(Ncpus=4); renv::restore()"

# Final omop_es image
FROM base AS omop_es

ARG RENV_CACHE=/home/docker/.cache/R/renv

COPY --from=omop_es-builder --chown=docker:docker --chmod=0755 /app/omop_es /app/omop_es
COPY --from=omop_es-builder --chown=docker:docker --chmod=0755 ${RENV_CACHE} ${RENV_CACHE}
COPY --chmod=0755 ./omop_es.sh .

CMD ["/app/omop_es.sh"]


# =====================================================================================================================

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

RUN install2.r --error --skipinstalled \
    --repos http://cran.rstudio.com/ \
    devtools \
    tidyverse \
    here \
    config \
    R.utils \
    odbc \
    DBI \
    arrow \
    nanoarrow \
    lubridate \
    glue \
    dbplyr \
    assertr \
    chron \
    RSQLite \
    bit64 \
    rjson \
    log4r \
    R6 \
    cli \
    janitor \
    purrr \
    RPostgres \
    && rm -rf /tmp/downloaded_packages

USER docker

COPY --from=omop-cascade-builder --chmod=0775 /app/omop-cascade /app
WORKDIR /app
CMD Rscript /app/import_omop.R --id=${CRDM_ID}
