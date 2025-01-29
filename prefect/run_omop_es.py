import subprocess
import datetime
from pathlib import Path

from prefect import flow, task, runtime, logging

ROOT_PATH = Path(__file__).parents[1]
OMOP_ES_PATH = ROOT_PATH / "omop_es"


def name_with_timestamp() -> str:
    name = runtime.deployment.name
    now = datetime.datetime.now(datetime.timezone.utc)
    return f"{name}_{now.isoformat()}"


@flow(flow_run_name=name_with_timestamp, retries=2, retry_delay_seconds=300)
def run_docker(input_data: str = "default") -> None:
    build_docker(OMOP_ES_PATH)
    write(ROOT_PATH, input_data)


@task()
def build_docker(project_path: Path) -> None:
    args = ["docker", "compose", "build"]
    run_subprocess(project_path, args)


def run_subprocess(project_path: Path, args: list[str]) -> None:
    """Helper to run subprocesses, logging stderr."""
    logger = logging.get_run_logger()
    result = subprocess.run(args, cwd=project_path, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise subprocess.CalledProcessError(
            result.returncode, args, output=result.stdout, stderr=result.stderr
        )
    logger.debug(result.stderr)


@task(retries=3, retry_delay_seconds=120)
def write(project_path: Path, input_data: str) -> None:
    # FIXME: need correct input arguments
    args = [
        "docker",
        "compose",
        "--project-name",
        "project",
        "run",
        "--remove-orphans",
        "dummy_app",
        "uv",
        "run",
        "omop_es",
    ]
    run_subprocess(project_path, args)


if __name__ == "__main__":
    run_docker()

