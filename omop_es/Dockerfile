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

RUN R -e "remotes::install_github('andysouth/omopcept')"

COPY app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
