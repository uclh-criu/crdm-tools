# Scheduling pipeline runs with Prefect

<!--prettier-ignore-->
> [!WARNING]
> EXPERIMENTAL

## Quickstart

From this directory, first set the required environment variables:

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

You should now see the dashboard live at http://localhost:4200/dashboard.

Note that this will run in the foreground and so block your shell. We recommend running this in a
`tmux` (or similar) session.

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

This will again run in the foreground and so block your shell, so run this in a `tmux` (or similar)
session. You can use this to monitor the logs for any flow that uses this worker (the logs will also
show up in the Prefect dashboard).

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

Alternatively you can create all deployments defined in `prefect.yaml` by running:

```shell
make deploy-all
```

This will push the configuration for the Prefect flows to the server and make them ready to run. You
should now be able to see any deployments you created at http://127.0.0.1:4200/deployments.

If any of the deployments have a [schedule](https://docs.prefect.io/v3/concepts/schedules), they
will start running automatically based on their schedule.

To manually trigger a flow run, you can use the dashboard or the Prefect CLI:

```shell
uv run prefect deployment run <deployment_name>
```

### Cleaning up

To stop everything (including the server):

```shell
make stop
```

To just stop the worker pool and keep the server up:

```shell
make stop-pool
```

To stop all Prefect services, take the server down, and reset the database:

```shell
make clean
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

For unknown reasons, the GAE is unable to serve the Prefect server on the default `4200` port. With
these settings, the dashboard will be hosted at `http://uclvlddpragae10:8082/dashboard` (accessible
through the UCLH network only).

When running `prefect` commands (see above) on a GAE, make sure the GAE's address is included in the
`NO_PROXY` environment variable in the `prefect/.env` file and run `uv` with the `--env-file .env`
flag (see examples above), as `prefect` doesn't pick up this variable automatically:

```shell
NO_PROXY="localhost,127.0.0.1,uclvlddpragae10"
```

## Management of the running instance on the GAE

🚧 _Under development - Work in progress_

We currently don't run Prefect in Docker but in simple processes in `tmux` on GAE10.

This might change in the future, but for now it means that the person running the server needs to
take it down, ensure all processes are killed, and remove the `/tmp/runner_storage` directory if it
exists before someone else can start the server. (Other users won't have permission to write to a
`/tmp` subdirectory that they didn't create.)

Running `make clean` takes care of this.
