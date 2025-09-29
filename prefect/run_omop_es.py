#  Copyright (c) University College London Hospitals NHS Foundation Trust
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
################################################################################

import datetime
import os
import subprocess
from pathlib import Path

from prefect import flow, runtime, task

from run_subprocess import run_subprocess

ROOT_PATH = Path(__file__).parents[1]
DEPLOYMENT_NAME = str(runtime.deployment.name).lower()
IS_PROD = os.environ.get("ENVIRONMENT", "dev") == "prod"


def name_with_timestamp() -> str:
    """Generate a name for the flow run with a timestamp."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"{DEPLOYMENT_NAME}_{now.isoformat()}"


def dry_run_if(condition: bool):
    """Optionally yield the dry-run flag for docker compose commands."""
    if condition:
        yield "--dry-run"


def use_prod_if(condition: bool):
    """Optionally yield the prod flag for docker compose commands."""
    if condition:
        yield "-f"
        yield "docker-compose.prod.yml"


@flow(flow_run_name=name_with_timestamp, log_prints=True)
def run_omop_es(
    settings_id: str,
    omop_es_branch: str = "master",
    batched: bool = False,
    output_directory: str = "",
    zip_output: bool = False,
) -> None:
    build_args = ["--build-arg", f"OMOP_ES_BRANCH={omop_es_branch}"]
    build_docker(ROOT_PATH, project_name=settings_id, build_args=build_args)
    run_omop_es_docker(
        working_dir=ROOT_PATH,
        settings_id=settings_id,
        batched=batched,
        output_directory=output_directory,
        zip_output=zip_output,
    )


@task(retries=10, retry_delay_seconds=10)
def build_docker(
    working_dir: Path,
    project_name: str,
    build_args: list[str] = [],
    dry_run: bool = False,
) -> None:
    build_args = build_args or []
    args = [
        "docker",
        "compose",
        *use_prod_if(IS_PROD),
        *dry_run_if(dry_run),
        "--project-name",
        project_name,
        "build",
        "omop_es",
    ]
    args += build_args
    run_subprocess(working_dir, args)


@task(retries=5, retry_delay_seconds=1800)
def run_omop_es_docker(
    working_dir: Path,
    settings_id: str,
    batched: bool,
    output_directory: str,
    zip_output: bool,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["SETTINGS_ID"] = settings_id
    env["BATCHED"] = str(batched)
    env["OUTPUT_DIRECTORY"] = str(output_directory)
    env["ZIP_OUTPUT"] = str(zip_output)
    args = [
        "docker",
        "compose",
        *use_prod_if(IS_PROD),
        "--project-name",
        f"{settings_id}",
        "run",
        "--env",
        "SETTINGS_ID",
        "--env",
        "BATCHED",
        "--env",
        "OUTPUT_DIRECTORY",
        "--env",
        "ZIP_OUTPUT",
        "--env",
        "DEBUG",  # passed through from global env
        "--rm",
        "omop_es",
    ]
    return run_subprocess(working_dir, args, env)
