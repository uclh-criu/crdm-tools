# Docker images

The [Dockerfile](./Dockerfile) in this directory defines a [multi-stage build](https://docs.docker.com/build/building/multi-stage/)
to provide images for `omop_es` and `omop-cascade`, sharing a common base image.

The entrypoints for each image is defined by the `omop_es.sh` and `omop_cascade.sh` scripts, respectively.

[Building the images](/README.md#building-the-images) should be done through `docker compose` from the root of this directory.
