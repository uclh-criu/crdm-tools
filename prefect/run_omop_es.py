import subprocess
import datetime
from pathlib import Path
from typing import Optional

from prefect import flow, task, runtime, logging

ROOT_PATH = Path(__file__).parents[1]
OMOP_ES_PATH = ROOT_PATH / "omop_es"


def name_with_timestamp() -> str:
    name = runtime.deployment.name
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"{name}_{now.isoformat()}"


@flow(flow_run_name=name_with_timestamp)
def run_omop_es(
    batched: bool = False,
    settings_id: str = "mock_project_settings",
    zip_output: Optional[bool] = False,
    start_batch: Optional[str] = None,
    extract_dt: Optional[str] = None,
) -> None:
    build_docker(OMOP_ES_PATH)
    run_omop_es_docker(
        working_dir=ROOT_PATH,
        batched=batched,
        settings_id=settings_id,
        zip_output=zip_output,
        start_batch=start_batch,
        extract_dt=extract_dt,
    )


@task(retries=10, retry_delay_seconds=10)
def build_docker(working_dir: Path) -> None:
    args = ["docker", "compose", "build", "omop_es"]
    run_subprocess(working_dir, args)


def run_subprocess(working_dir: Path, args: list[str]) -> None:
    """Helper to run subprocesses, logging stderr."""
    logger = logging.get_run_logger()
    result = subprocess.run(args, cwd=working_dir, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise subprocess.CalledProcessError(
            result.returncode, args, output=result.stdout, stderr=result.stderr
        )
    logger.debug(result.stderr)


@task(retries=5, retry_delay_seconds=1800)
def run_omop_es_docker(
    working_dir: Path,
    batched: bool,
    settings_id: str,
    zip_output: Optional[bool],
    start_batch: Optional[str],
    extract_dt: Optional[str],
) -> None:
    args = [
        "docker",
        "compose",
        "--project-name",
        "omop_es-prefect",
        "run",
        "--remove-orphans",
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
