# Scheduling pipeline runs with Prefect

> [!WARNING]
> EXPERIMENTAL

## Quickstart

From this directory, first set the required environment variables:

```shell
cp template.env .env
```

and fill out the `.env` file as needed.

Then start the local Prefect server:

```shell
uv run --env-file .env prefect server start
```

You should now see the dashboard live at http://localhost:4200/dashboard.

From a new terminal window/session, start a new worker pool with the desired **concurrency limit**:

```shell
uv run --env-file .env prefect worker start --pool 'omop_es-worker' --type process --limit <CONCURRENCY_LIMIT>
```

You're now ready to deploy the `omop_es` flow with:

```shell
uv run --env-file .env prefect deploy
```

Note that this will automatically schedule a run of the flow. You can also manually deploy the flow
with:

```shell
# Example using the mock project
uv run --env-file .env prefect deployment run 'run-omop-es/omop_es-mock'
```

Note that this might result in duplicate runs, however.

## Using the `Makefile`

Alternatively, all the above commands can be run through `make`. Run `make help` to see the available commands.

To spin up the server run:

```shell
make start-server
```

Then in a different terminal window/session you can start a worker pool and deploy all flows, by running:

```shell
make deploy-all
```

To stop everything (including the server):

```shell
make stop
```

To just stop the worker pool and keep the server up:

```shell
make stop-pool
```

## Configuring projects

_Under construction_

## Deploy Prefect on the GAE

To run Prefect on the GAE, make sure to set the following environment variables in `prefect/.env`:

```shell
# For GAE10, will differ for other GAE instances
PREFECT_SERVER_API_HOST=uclvlddpragae10
PREFECT_SERVER_API_PORT=8082
PREFECT_API_URL=http://uclvlddpragae10:8082/api
```

For unknown reasons, the GAE is unable to serve the Prefect server on the default `4200` port.
With these settings, the dashboard will be hosted at `http://uclvlddpragae10:8082/dashboard`
(accessible through the UCLH network only).

When running `prefect` commands (see above) on a GAE, make sure the GAE's address is included in
the `NO_PROXY` environment variable in the `prefect/.env` file and run `uv` with the
`--env-file .env` flag (see examples above), as `prefect` doesn't pick up this variable automatically:

```shell
NO_PROXY="localhost,127.0.0.1,uclvlddpragae10"
```

## Management the running instance on the GAE

🚧 _Under development - Work in progress_

We currently don't run Prefect in Docker but in simple processes in `tmux` on GAE10.

This might change in the future, but for now it means that the person running the server needs to take it down, ensure all processes are killed, and remove the `/tmp/runner_storage` directory if it exists before someone else can start the server.
(Other users won't have permission to write to a `/tmp` subdirectory that they didn't create.)
