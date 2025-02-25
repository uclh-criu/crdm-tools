FROM rocker/tidyverse:4.4.2 as base

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    curl \
    gnupg \
    libudunits2-dev \
    libgdal-dev && \
    apt-get autoremove --yes && apt-get clean --yes && rm -rf /var/lib/apt/lists/*

# Enable Microsoft's MySQL
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

RUN install2.r --error --skipinstalled \
    --repos http://cran.rstudio.com/ \
    devtools \
    here \
    arrow \
    tidyverse \
    dbplyr \
    glue \
    assertr \
    assertthat \
    chron \
    RSQLite \
    bit64 \
    rjson \
    log4r \
    odbc \
    R6 \
    cli \
    janitor \
    zip \
    jsonvalidate \
    processx \
    R.utils \
    rlang \
    DBI \
    readr \
    readxl \
    remotes \
    && rm -rf /tmp/downloaded_packages

# omop_es
FROM base as omop_es
RUN R -e "remotes::install_github('andysouth/omopcept')"
WORKDIR /app
COPY --chmod=0755 ./omop_es.sh .
CMD ["/app/omop_es.sh"]

# omop-cascade
FROM base as omop-cascade
WORKDIR /app
COPY --chmod=0755 ./omop-cascade.sh .
CMD ["/app/omop-cascade.sh"]

