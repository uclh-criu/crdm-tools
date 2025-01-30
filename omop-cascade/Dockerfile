# TODO: merge with omop_es/Dockerfile, use single image for both
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

COPY app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
