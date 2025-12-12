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
import re
import subprocess
from pathlib import Path

import dotenv
from prefect import flow, logging, runtime, task

from run_subprocess import run_subprocess

ROOT_PATH = Path(__file__).parents[1]
DEPLOYMENT_NAME = str(runtime.deployment.name).lower()
IS_PROD = os.environ.get("ENVIRONMENT", "dev") == "prod"

logger = logging.get_logger()

def name_with_timestamp() -> str:
    """Generate a name for the flow run with a timestamp."""
    now = datetime.datetime.now(datetime.timezone.utc)
    # return f"{DEPLOYMENT_NAME}_{now.isoformat()}"
    return f"{now:%Y%m%d_%H%M%S}"


def dry_run_if(condition: bool):
    """Optionally yield the dry-run flag for docker compose commands."""
    if condition:
        yield "--dry-run"


def use_prod_if(condition: bool):
    """Optionally yield the prod flag for docker compose commands."""
    if condition:
        yield "-f"
        yield "docker-compose.prod.yml"


@flow(flow_run_name="{"+"settings_id"+"}_"+name_with_timestamp(), log_prints=True)
def run_omop_es(
    settings_id: str,
    omop_es_version: str = "master",
    batched: bool = False,
    zip_output: bool = False,
    # extract_dt: datetime.datetime = datetime.datetime.now(datetime.timezone.utc),
) -> None:
    """Run omop_es data extraction workflow.

    Args:
        settings_id: Project settings identifier
        omop_es_version: Git ref to use - can be a branch name, commit SHA, or tag name
        batched: Whether to run in batched mode
        zip_output: Whether to compress output
    """
    pinned_version = pin_omop_es_version(omop_es_version)
    build_docker(ROOT_PATH, project_name=settings_id, omop_es_version=omop_es_version)
    run_omop_es_docker(
        working_dir=ROOT_PATH,
        settings_id=settings_id,
        omop_es_version=pinned_version,
        batched=batched,
        output_directory=runtime.flow_run.name,
        zip_output=zip_output,
    )


@task()
def pin_omop_es_version(ref: str) -> str:
    """
    Finds the latest commit hash for the given OMOP_ES ref.

    Args:
        ref: The OMOP_ES ref to find the latest commit hash for. Can be a branch, tag, or commit SHA.

    Returns:
        The latest commit hash for the given OMOP_ES ref.
    """
    dotenv.load_dotenv(ROOT_PATH / ".env")
    github_pat = os.environ.get("GITHUB_PAT")
    if not github_pat:
        raise ValueError("GITHUB_PAT environment variable not set")
    omop_es_url = (
        f"https://x-access-token:{github_pat}@github.com/uclh-criu/omop_es.git"
    )

    try:
        sha = get_latest_commit_sha(omop_es_url, ref)
    except RuntimeError:
        logger.error(f"Invalid OMOP_ES ref: {ref}")
        raise

    logger.info("Pinning OMOP_ES version to %s", sha)
    return sha


@task(retries=10, retry_delay_seconds=10)
def build_docker(
    working_dir: Path,
    project_name: str,
    omop_es_version: str,
    dry_run: bool = False,
) -> None:
    args = [
        "docker",
        "compose",
        *use_prod_if(IS_PROD),
        *dry_run_if(dry_run),
        "--project-name",
        project_name,
        "build",
        "omop_es",
        "--build-arg",
        f"OMOP_ES_VERSION={omop_es_version}",
    ]
    run_subprocess(working_dir, args)


@task(retries=5, retry_delay_seconds=1800)
def run_omop_es_docker(
    working_dir: Path,
    settings_id: str,
    omop_es_version: str,
    batched: bool,
    output_directory: str,
    zip_output: bool,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["SETTINGS_ID"] = settings_id
    env["OMOP_ES_VERSION"] = omop_es_version
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
        f"SETTINGS_ID={env['SETTINGS_ID']}",
        "--env",
        f"OMOP_ES_VERSION={env['OMOP_ES_VERSION']}",
        "--env",
        f"BATCHED={env['BATCHED']}",
        "--env",
        f"OUTPUT_DIRECTORY={env['OUTPUT_DIRECTORY']}",
        "--env",
        f"ZIP_OUTPUT={env['ZIP_OUTPUT']}",
        "--env",
        "DEBUG",  # passed through from global env
        "--rm",
        "omop_es",
    ]
    return run_subprocess(working_dir, args, env)


def get_latest_commit_sha(repo_url: str, ref: str) -> str:
    """
    Get the latest commit SHA for a given reference.
    If ref is already a valid SHA, return it directly.

    Args:
        repo_url: URL of the repository
        ref: Reference to the commit (e.g., branch name or tag)

    Returns:
        Latest commit SHA

    Raises:
        RuntimeError: If the git command fails to execute or if the SHA format is invalid
    """
    validate_ref(repo_url, ref)

    if is_valid_sha(ref):
        return ref

    try:
        result = subprocess.run(
            ["git", "ls-remote", repo_url, ref],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(e.stderr)
        raise RuntimeError(f"Failed to get latest commit SHA for {repo_url}/{ref}: {e}")

    sha = result.stdout.strip().split("\t")[0]
    if is_valid_sha(sha):
        return sha

    raise RuntimeError(f"Invalid SHA format for {repo_url}/{ref}: {sha}")


def validate_ref(repo_url: str, ref: str) -> None:
    """
    Validate a reference (branch, tag, or commit SHA) in a Git repository.

    Args:
        repo_url: URL of the repository
        ref: Reference to the commit (e.g., branch name, tag or commit sha)

    Raises:
        RuntimeError: If the ref is invalid or does not exist in the repository
    """

    # git fetch only works with full-length SHA
    if is_valid_sha(ref) and len(ref) < 40:
        logger.warning("Short SHA provided, impossible to validate.")
        return

    try:
        subprocess.check_call(
            ["git", "fetch", repo_url, ref],
            # we don't care about the output here
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to fetch reference {ref} from {repo_url}") from e


def is_valid_sha(sha: str) -> bool:
    """
    Check if string matches SHA format (40 hex characters for long or 7 for short SHA).

    Args:
        sha: String to check

    Returns:
        True if format is valid, False otherwise
    """
    pattern = r"^[a-fA-F0-9]{7,40}$"
    return bool(re.match(pattern, sha))
