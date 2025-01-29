FROM rocker/tidyverse:4.4.2

RUN apt update && \
    apt-get update && \
    apt-get upgrade -y

RUN apt-get install -y \
    curl \
    gnupg \
    libudunits2-dev \
    libgdal-dev

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

RUN install2.r --error --deps TRUE --skipinstalled \
    --repos http://cran.rstudio.com/ \
    devtools \
    tidyverse \
    here \
    config \
    R.utils \
    odbc \
    DBI \
    arrow \
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

ENTRYPOINT ["bash", "/app/entrypoint.sh"]