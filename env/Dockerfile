FROM r-base:4.1.3

RUN apt-get update && \
    apt-get install -y \
        iputils-ping \
        git \
        curl \
        gnupg \
        unixodbc \
        unixodbc-dev \
        odbcinst \
        libc6 \
        libodbcinst2 \
        libpq5 \
        libssl-dev \
        libxml2-dev \
        libcurl4-openssl-dev \
        libfontconfig1-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libfreetype6-dev \
        libpng-dev \
        libtiff5-dev \
        libjpeg-dev

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    # PostgreSQL Driver
    apt-get install -y odbc-postgresql && \
    # SQL Server Driver
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

ARG LIBARROW_BINARY=TRUE

RUN R -e "install.packages('devtools', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('tidyverse', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('here', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('config', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('R.utils', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('odbc', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('DBI', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('arrow', type = 'source')"
RUN R -e "install.packages('lubridate', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('glue', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('dbplyr', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('assertive', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('assertr', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('chron', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('RSQLite', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('bit64', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('rjson', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('log4r', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('R6', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('cli', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"
RUN R -e "install.packages('janitor', repos = 'https://cran.ma.imperial.ac.uk/', dependencies = TRUE)"

ENTRYPOINT ["sh", "/app/entrypoint.sh"]