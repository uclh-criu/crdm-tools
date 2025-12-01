# crdm-tools

This repository provides infrastructure tools to run
[`omop_es`](https://github.com/uclh-criu/omop_es) and
[`omop-cascade`](https://github.com/uclh-criu/omop-cascade) in containerised environments on the
GAE.

In addition, the [`prefect/` directory](prefect/) provides data workflow orchestration with
[Prefect](https://docs.prefect.io/v3/get-started/index) to allow automatic scheduling of `omop_es`
runs.

## Deploying the Prefect infrastructure

<!--prettier-ignore-->
> [!WARNING]
> EXPERIMENTAL

First set the required environment variables:

```shell
cp template.env .env
```

and fill out the `.env` file as needed.

We provide a `Makefile` to run the relevant deployment commands. Run `make help` to see the
available commands.

### Starting the server

To spin up the server run:

```shell
make start-server
```

You should now see the dashboard live at http://localhost:4200/dashboard. The port can be configured
through the `PREFECT_SERVER_API_PORT` environment variable.

To see the Prefect config, including connection details, run:

```shell
make config
```

The Prefect server is running inside a Docker container. You can access the logs for the server by
running (the `-f` option will continuously stream the logs):

```shell
docker compose logs -f prefect_server
```

### Starting a worker

Before deploying Prefect flows, we need an active
[worker pool](https://docs.prefect.io/v3/concepts/work-pools). To run any of the deployed flows, we
also need a running worker in that pool.

At the moment, we are using simple ["process" workers](https://docs.prefect.io/v3/concepts/workers),
meaning the worker will run in a subprocess from wherever the worker is started.

To start a worker, run the following command in a different terminal window/session than where you
started the server:

```shell
make start-worker
```

This will run in the foreground and block your shell, so run this in a `tmux` (or similar) session.
You can use this to monitor the logs for any flow that uses this worker (the logs will also show up
in the Prefect dashboard).

### Deploying Prefect flows

[Deployments](https://docs.prefect.io/v3/concepts/deployments) are used to configure how
[Prefect flows](https://docs.prefect.io/v3/concepts/flows) should be run. Their configuration is
defined in [`prefect.yaml`](./prefect.yaml).

In a third terminal window/session, different than where you started the worker or server, create a
deployment by running:

```shell
make deploy
```

This will open an interactive shell where you can select a specific flow to deploy.

**Note**: when prompted by prefect
`? Would you like to save configuration for this deployment for faster deployments in the future?`,
you typically want to reject by typing `n` to avoid Prefect overwriting the existing configuration
in `prefect.yaml` and potentially hardcoding absolute file paths.

Alternatively you can create all deployments defined in `prefect.yaml` by running:

```shell
make deploy-all
```

This will push the configuration for the Prefect flows to the server and make them ready to run. You
should now be able to see any deployments you created at in the Deployments section of the Prefect
dashboard.

If any of the deployments have a [schedule](https://docs.prefect.io/v3/concepts/schedules), they
will start running automatically based on their schedule.

To manually trigger a flow run, you can use the dashboard or the Prefect CLI:

```shell
uv run prefect deployment run '<deployment_name>'
```

### Stopping the server

To stop the server:

```shell
make stop-server
```

This will preserve existing deployments and settings. Workers will also continue to run but will be
suspended until the server is restarted.

### Teardown

To stop all Prefect services, take the server down, and reset the database:

<!--prettier-ignore-->
> [!WARNING]
> This is a destructive operation. It will delete all deployments, flows, tasks, and data stored in the Prefect database.
> This operation cannot be undone.

```shell
make down
```

## Configuring projects

_Under construction_

## Deploy Prefect on the GAE

To run Prefect on the GAE, make sure to set the following environment variables in the root
directory `.env`:

```shell
# For GAE10, will differ for other GAE instances
PREFECT_SERVER_API_HOST=uclvlddpragae10
PREFECT_SERVER_API_PORT=8082
PREFECT_API_URL=http://uclvlddpragae10:8082/api
```

The `4200` port is unavaiable on the GAE. With these settings, the dashboard will be hosted at
`http://uclvlddpragae10:8082/dashboard` (accessible through the UCLH network only).

When running `prefect` commands (see above) on a GAE, make sure the GAE's address is included in the
`NO_PROXY` environment variable in the `.env` file and run `uv` with the `--env-file .env` flag, as
`prefect` doesn't pick up this variable automatically:

```shell
NO_PROXY="localhost,127.0.0.1,uclvlddpragae10"
```

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

## Development

The main Prefect infrastructure is implemented in the [`prefect/`](./prefect/) directory. The
Dockerfile and entrypoint script for the the `omop_es` pipeline is located in the
[`docker/`](./docker) directory.

We use [`pre-commit`](https://pre-commit.com/) to enforce code style and formatting. Install it by
running `pip install pre-commit` and then run `pre-commit install` to install the hooks.

### Testing

Tests for the Prefect workflow can be run using the following command:

```shell
make test
```
