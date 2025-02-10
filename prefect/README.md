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
