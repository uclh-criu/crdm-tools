SHELL := /bin/bash
.PHONY: *

define assert_command_exists
	if ! command -v $(1) &> /dev/null; then \
		echo -e "\033[0;31mERROR\033[0m: $(2)" && exit 1; \
	fi
endef

UVRUN := uv run --env-file .env
POOL_NAME := omop_es-mock-worker

help: ## Show this help
	@echo
	@grep -E '^[a-zA-Z_0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%s\033[0m|%s\n", $$1, $$2}' \
        | column -t -s '|'
	@echo

stop:    ## Stop all Prefect services and take the server down
	$(MAKE) stop-pool
	$(MAKE) stop-server

clean:   ## Stop Prefect services, take the server down, and reset the database
	$(MAKE) stop
	$(MAKE) reset-prefect-database
	rm -rf /tmp/runner_storage

deploy-all: start-pool ## Deploy all Prefect flows and start a worker
	$(UVRUN) prefect deploy --all
	$(MAKE) start-worker

deploy: start-pool ## Deploy a single Prefect flow (interactive selection) and start a worker
	$(UVRUN) prefect deploy
	$(MAKE) start-worker

start-worker: start-pool ## Start a Prefect worker of type 'process'
	$(UVRUN) prefect worker start --pool '${POOL_NAME}'

start-pool: uv-exists ## Start a Prefect worker pool
	-$(UVRUN) prefect work-pool create '${POOL_NAME}' --type process --overwrite

start-server: uv-exists ## Start the Prefect server in the background
	-$(UVRUN) prefect server start --background # allow failure in case server already running

stop-server: uv-exists ## Stop the Prefect server
	$(UVRUN) prefect server stop

stop-pool: uv-exists ## Stop the Prefect worker pool
	-$(UVRUN) prefect work-pool delete '${POOL_NAME}' # allow failure in case pool does not exist

reset-prefect-database: uv-exists ## Reset the Prefect database
	$(UVRUN) prefect server database reset -y

test: uv-exists ## Run tests of our Prefect functionality
	$(UVRUN) pytest . --log-cli-level=INFO -s

uv-exists: ## Check if uv is available
	$(call assert_command_exists, uv, "Please install uv: https://docs.astral.sh/uv/getting-started/installation/")

.SILENT:  # all targets
