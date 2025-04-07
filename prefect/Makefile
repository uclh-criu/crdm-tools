SHELL := /bin/bash
.PHONY: *

define assert_command_exists
	if ! command -v $(1) &> /dev/null; then \
		echo -e "\033[0;31mERROR\033[0m: $(2)" && exit 1; \
	fi
endef

POOL_NAME := omop_es-mock-worker

help: ## Show this help
	@echo
	@grep -E '^[a-zA-Z_0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%s\033[0m|%s\n", $$1, $$2}' \
        | column -t -s '|'
	@echo

stop:    ## Stop Prefect services
	$(MAKE) stop-pool
	$(MAKE) stop-server

clean:   ## Stop Prefect services and reset the database
	$(MAKE) stop
	$(MAKE) reset-prefect-database

deploy-all: start-pool ## Deploy all Prefect flows and start a worker
	uv run --env-file .env prefect deploy --all
	$(MAKE) start-worker

deploy: start-pool ## Deploy a single Prefect flow (interactive selection) and start a worker
	uv run --env-file .env prefect deploy
	$(MAKE) start-worker

start-worker: start-pool ## Start a Prefect worker of type 'process'
	uv run --env-file .env prefect worker start --pool '${POOL_NAME}'

start-pool: start-server ## Start a Prefect worker pool
	-uv run --env-file .env prefect work-pool create '${POOL_NAME}' --type process # allow failure in case pool already exists

start-server: uv-exists ## Start the Prefect server
	-uv run --env-file .env prefect server start --background # allow failure in case server already running

stop-server: uv-exists ## Stop the Prefect server
	uv run --env-file .env prefect server stop

stop-pool: uv-exists ## Stop the Prefect worker pool
	-uv run --env-file .env prefect work-pool delete '${POOL_NAME}' # allow failure in case pool does not exist

reset-prefect-database: uv-exists ## Reset the Prefect database
	uv run --env-file .env prefect server database reset -y

uv-exists: ## Check if uv is available
	$(call assert_command_exists, uv, "Please install uv: https://docs.astral.sh/uv/getting-started/installation/")


.SILENT:  # all targets
