# crdm-tools

This repository provides infrastructure tools to run
[`omop_es`](https://github.com/uclh-criu/omop_es) and
[`omop-cascade`](https://github.com/uclh-criu/omop-cascade) in containerised environments on the
GAE.

In addition, the [`prefect/` directory](prefect/README.md) provides data workflow orchestration with
[Prefect](https://docs.prefect.io/v3/get-started/index) to allow automatic scheduling of `omop_es`
runs.

## Building the images

Use `docker compose build` to build all images, or specify the image to build.

### `omop_es`

```shell
docker compose build omop_es
```

### `omop-cascade`

```shell
docker compose build omop-cascade
```

## Version Pinning

The `OMOP_ES_VERSION` environment variable controls which version of `omop_es` to use. It accepts:

- **Branch name** (e.g., `master`, `feature/xyz`) - Always pulls the latest commit from that branch
- **Commit SHA** (e.g., `a1b2c3d4` or full SHA) - Pins to a specific commit (no automatic updates)
- **Tag name** (e.g., `v1.0.0`) - Pins to a specific release (no automatic updates)

When using a branch name, the container will `git pull` to get the latest code on each run. When
using a commit SHA or tag, the container will checkout that specific version without pulling
updates.

## Running the containers for local development

Set environment variables:

```shell
# Copy the templates and fill out as needed
cp template.env .env
cp omop_es/template.env omop_es/.env
cp omop-cascade/template.env omop-cascade/.env
```

```shell
docker compose --project-name <PROJECT-NAME> run --build \
    --env SETTINGS_ID=<SETTINGS_ID>
    --env ... \
    omop_es
```

## Running the containers in production

Adjust the `.env` files accordingly.

### `omop_es`

```shell
docker compose -f docker-compose.prod.yml --project-name <PROJECT-NAME> run --build \
    --env SETTINGS_ID=<SETTINGS_ID> \
    --env ... \
    omop_es
```

## Access to private GitHub repos from GAE

To be able to clone GitHub repos on a GAE, create a new
[fine-grained personal access token](https://github.com/settings/personal-access-tokens), make sure
the "Resource owner" is set to `uclh-criu` and then select the repositories you want to access.
Submit the request to generate the token and then make sure to copy the token to a safe place as it
will not be shown again!

First store your PAT in a file on the GAE in the path `~/.pat.txt`, then configure `git` to use the
token by running the following command:

```shell
git config --global credential.helper 'store --file ~/.pat.txt'
```

This process needs to be repeated for every GAE.

Additionally record the token in the `GITHUB_PAT` environment variable in the `.env` file in this
repository's root.
