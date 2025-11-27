SHELL := /bin/bash
.PHONY: *

define assert_command_exists
	if ! command -v $(1) &> /dev/null; then \
		echo -e "\033[0;31mERROR\033[0m: $(2)" && exit 1; \
	fi
endef

DOCKER_COMPOSE := docker compose -f ../docker-compose.yml
UVRUN := uv run --env-file .env
WORK_POOL_NAME := omop_es-worker

help: ## Show this help
	@echo
	@grep -E '^[a-zA-Z_0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%s\033[0m|%s\n", $$1, $$2}' \
        | column -t -s '|'
	@echo

clean:   ## Stop all Prefect services, take the server down, and reset the database, DESTRUCTIVE action!
	$(DOCKER_COMPOSE) down prefect_server

config: ## Display prefect config information
	$(UVRUN) prefect config view --show-secrets

deploy-all: uv-exists ## Deploy all Prefect flows
	$(UVRUN) prefect --no-prompt deploy --all

deploy: uv-exists ## Deploy a single Prefect flow (interactive selection) and start a worker
	$(UVRUN) prefect deploy

start-worker: start-pool ## Start a Prefect worker of type 'process'
	$(UVRUN) prefect worker start --pool '${WORK_POOL_NAME}'

start-pool: uv-exists ## Start a Prefect worker pool
	-$(UVRUN) prefect work-pool create '${WORK_POOL_NAME}' --type process --overwrite

start-server: ## Start the Prefect server
	$(DOCKER_COMPOSE) up -d prefect_server

stop-server: ## Stop the Prefect server
	$(DOCKER_COMPOSE) stop prefect_server

delete-pool: uv-exists ## Delete the Prefect worker pool
	$(UVRUN) prefect work-pool delete '${WORK_POOL_NAME}' # allow failure in case pool does not exist

reset-prefect-database: ## Reset the Prefect database, DESTRUCTIVE action!
	$(DOCKER_COMPOSE) exec prefect_server prefect server database reset -y

test: uv-exists ## Run tests of our Prefect functionality
	$(UVRUN) pytest . -s --log-cli-level=INFO

uv-exists: ## Check if uv is available
	$(call assert_command_exists, uv, "Please install uv: https://docs.astral.sh/uv/getting-started/installation/")

.SILENT:  # all targets
