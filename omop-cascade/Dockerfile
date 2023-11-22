FROM r-base:4.1.3

RUN apt update && \
    apt-get update && \
    apt-get upgrade -y

RUN apt-get install -y \
        bash \
        curl \
        git \
        gnupg \
        cmake \
        libc6 \
        libpq5 \
        libssl-dev \
        libxml2-dev \
        libcurl4-openssl-dev \
        libodbcinst2 \
        unixodbc \
        unixodbc-dev \
        odbcinst \
        odbc-postgresql \
        libfontconfig1-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libpng-dev \
        libtiff5-dev \
        libjpeg-dev \
        libpq-dev \
        libmariadb-dev \
        clang-tidy \
        clang-format \
        libsnappy-dev \
        libthrift-dev \
        rapidjson-dev \
        lz4 \
        re2c \
        gzip \
        brotli \
        zstd \
        bzip2 \
        libudunits2-dev \
        proj-bin \
        libproj-dev \
        libcrypto++-dev \
        libgeos-dev

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

RUN wget -qO- https://boostorg.jfrog.io/artifactory/main/release/1.83.0/source/boost_1_83_0.tar.bz2 | tar -C /tmp --bzip2 -x && \
    cd /tmp/boost_1_83_0 && \
    ./bootstrap.sh && \
    ./b2 install

RUN wget -qO- https://github.com/OSGeo/gdal/releases/download/v3.7.1/gdal-3.7.1.tar.gz | tar -C /tmp --gzip -x && \
    cd /tmp/gdal-3.7.1 && \
    mkdir build &&\
    cd build && \
    cmake -DGDAL_BUILD_OPTIONAL_DRIVERS=OFF -DOGR_BUILD_OPTIONAL_DRIVERS=OFF .. &&\
    cmake --build . &&\
    cmake --build . --target install

ENV LD_LIBRARY_PATH=/usr/local/lib
ENV GDAL_LIBRARY_PATH=/usr/local/lib/libgdal.so

RUN R -e "update.packages(ask = FALSE, checkBuilt = TRUE)"
RUN R -e "install.packages('devtools', dependencies = TRUE)"
RUN R -e "install.packages('here', dependencies = TRUE)"
RUN R -e "install.packages('arrow', dependencies = TRUE)"
RUN R -e "install.packages('tidyverse', dependencies = TRUE)"
RUN R -e "install.packages('dbplyr', dependencies = TRUE)"
RUN R -e "install.packages('glue', dependencies = TRUE)"
RUN R -e "install.packages('assertive', dependencies = TRUE)"
RUN R -e "install.packages('assertr', dependencies = TRUE)"
RUN R -e "install.packages('chron', dependencies = TRUE)"
RUN R -e "install.packages('RSQLite', dependencies = TRUE)"
RUN R -e "install.packages('bit64', dependencies = TRUE)"
RUN R -e "install.packages('rjson', dependencies = TRUE)"
RUN R -e "install.packages('log4r', dependencies = TRUE)"
RUN R -e "install.packages('odbc', dependencies = TRUE)"
RUN R -e "install.packages('R6', dependencies = TRUE)"
RUN R -e "install.packages('cli', dependencies = TRUE)"
RUN R -e "install.packages('janitor', dependencies = TRUE)"

RUN R -e "install.packages('config', dependencies = TRUE)"

ENTRYPOINT ["bash", "/app/entrypoint.sh"]