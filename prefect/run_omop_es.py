import datetime
from pathlib import Path
from typing import List, Optional

from prefect import flow, runtime, task

from run_subprocess import run_subprocess

ROOT_PATH = Path(__file__).parents[1]
DEPLOYMENT_NAME = runtime.deployment.name


def name_with_timestamp() -> str:
    """Generate a name for the flow run with a timestamp."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"{DEPLOYMENT_NAME}_{now.isoformat()}"


def dry_run_if(condition: bool):
    """Optionally yield the dry-run flag for docker compose commands."""
    if condition:
        yield "--dry-run"


@flow(flow_run_name=name_with_timestamp, log_prints=True)
def run_omop_es(
    build_args: List[str] = [],
    batched: bool = False,
    settings_id: str = "mock_project_settings",
    zip_output: Optional[bool] = False,
    start_batch: Optional[str] = None,
    extract_dt: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    build_docker(ROOT_PATH, build_args=build_args, dry_run=dry_run)
    run_omop_es_docker(
        working_dir=ROOT_PATH,
        batched=batched,
        settings_id=settings_id,
        zip_output=zip_output,
        start_batch=start_batch,
        extract_dt=extract_dt,
        dry_run=dry_run,
    )


@task(retries=10, retry_delay_seconds=10)
def build_docker(
    working_dir: Path, build_args: List[str] = [], dry_run: bool = False
) -> None:
    args = [
        "docker",
        "compose",
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
    batched: bool,
    settings_id: str,
    zip_output: Optional[bool],
    start_batch: Optional[str],
    extract_dt: Optional[str],
    dry_run: bool = False,
) -> None:
    args = [
        "docker",
        "compose",
        *dry_run_if(dry_run),
        "--project-name",
        DEPLOYMENT_NAME,
        "run",
        "--rm",
        "--env",
        f"OMOP_ES_BATCHED={batched}",
        "--env",
        f"OMOP_ES_SETTINGS_ID={settings_id}",
        "--env",
        f"OMOP_ES_START_BATCH={start_batch}",
        "--env",
        f"OMOP_ES_EXTRACT_DT={extract_dt}",
        "--env",
        f"OMOP_ES_ZIP_OUTPUT={zip_output}",
        "omop_es",
    ]
    run_subprocess(working_dir, args)


if __name__ == "__main__":
    run_omop_es()
