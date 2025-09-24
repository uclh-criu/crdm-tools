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
    omop_es_branch: str = "master",
    settings_id: str = "mock_project_settings",
    batched: bool = False,
    output_directory: str | None = "",
    zip_output: bool | None = False,
) -> None:
    build_args = ["--build-arg", f"OMOP_ES_BRANCH={omop_es_branch}"]
    build_docker(ROOT_PATH, build_args=build_args)
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
    build_args: list[str] | None = None,
    dry_run: bool = False,
) -> None:
    build_args = build_args or []
    is_prod = os.environ.get("ENV", "dev") == "prod"
    args = [
        "docker",
        "compose",
        *use_prod_if(is_prod),
        *dry_run_if(dry_run),
        "--project-name",
        DEPLOYMENT_NAME,
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
    output_directory: str | None,
    zip_output: bool | None,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["SETTINGS_ID"] = settings_id
    env["BATCHED"] = str(batched)
    env["OUTPUT_DIRECTORY"] = (
        str(output_directory) if output_directory is not None else ""
    )
    env["ZIP_OUTPUT"] = str(zip_output) if zip_output is not None else ""
    args = [
        "docker",
        "compose",
        "--project-name",
        DEPLOYMENT_NAME,
        "run",
        "--env",
        "SETTINGS_ID",
        "--env",
        "BATCHED",
        "--env",
        "OUTPUT_DIRECTORY",
        "--env",
        "ZIP_OUTPUT",
        "--rm",
        "omop_es",
    ]
    return run_subprocess(working_dir, args, env)


if __name__ == "__main__":
    run_omop_es()
