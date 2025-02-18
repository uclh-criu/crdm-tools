# Scheduling pipeline runs with Prefect

>[!WARNING]
> EXPERIMENTAL



## Quickstart

From this directory, first set the required environment variables:

```shell
cp template.env .env
```

and fill out the `.env` file as needed.

Then start the local Prefect server:

```shell
uv run prefect server start
```

You should now see the dashboard live at http://localhost:4200/dashboard.

From a new terminal window/session, start a new worker pool with the desired **concurrency limit**:

```shell
uv run prefect worker start --pool 'omop_es-worker' --type process --limit <CONCURRENCY_LIMIT>
```

You're now ready to deploy the `omop_es` flow with:

```shell
uv run prefect deploy
```

Note that this will automatically schedule a run of the flow. You can also manually deploy the flow
with:

```shell
# Example using the mock project
uv run prefect deployment run 'run-omop-es/omop_es-mock'
```

Note that this might result in duplicate runs, however.

## Configuring projects

_Under construction_

## Deploy Prefect on the GAE

To run Prefect on the GAE, make sure to set the following environment variables in `prefect/.env`:

```shell
# For GAE14, will differ for other GAE instances
PREFECT_SERVER_API_HOST=uclvlddpragae14
PREFECT_SERVER_API_PORT=8081
PREFECT_API_URL=http://uclvlddpragae14:8081/api
```

For unknown reasons, the GAE is unable to serve the Prefect server on the default `4200` port.
With these settings, the dashboard will be hosted at `http://uclvlddpragae14:8081/dashboard`
(accessible through the UCLH network only).

When running `prefect` commands (see above) on the GAE, make sure to set the `NO_PROXY` environment
variable for your session (setting it in `.env` is not enough):

```shell
# Run this for every new terminal session
export NO_PROXY="localhost,127.0.0.1,uclvlddpragae14"
```

