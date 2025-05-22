import pytest
from freezegun import freeze_time
from copy import copy
from prefect.testing.utilities import prefect_test_harness
from prefect.tasks import Task
from prefect.logging import disable_run_logger

import run_subprocess
import run_omop_es


@freeze_time("2025-01-01")
def test_name_with_timestamp():
    # The prefect deployment name is set to 'None' (because we're not in a prefect deployment)
    # we intercept this and set it to lowercase because docker is picky about project names.
    assert run_omop_es.name_with_timestamp() == "none_2025-01-01T00:00:00+00:00"


def test_star_dry_run_if():
    # Test that *dry_run_if expands as we expect
    command_with = ["docker", "compose", *run_omop_es.dry_run_if(True), "do-thing"]
    command_without = ["docker", "compose", *run_omop_es.dry_run_if(False), "do-thing"]
    assert command_with == ["docker", "compose", "--dry-run", "do-thing"]
    assert command_without == ["docker", "compose", "do-thing"]


def no_prefect_retries(func: Task) -> Task:
    # A Prefect-decorated flow/task function has 10 retries: we don't want that in a test.
    _func = copy(func)
    _func.retries = 0
    return _func


@pytest.mark.slow
def test_build_docker_in_prefect():
    # Can actually consider deleting this since it's the same as the test below
    with prefect_test_harness():
        no_prefect_retries(run_omop_es.build_docker)(
            working_dir=run_omop_es.ROOT_PATH,
            dry_run=True,
        )


# See https://docs.prefect.io/v3/develop/test-workflows#unit-testing-tasks for
# how to test tasks (or sub functions) outside of a flow context.
#
# > If your task uses a logger, you can disable the logger to avoid the
# > RuntimeError raised from a missing flow context.


@pytest.mark.slow
def test_build_docker_outside_prefect():
    with disable_run_logger():
        run_omop_es.build_docker.fn(
            working_dir=run_omop_es.ROOT_PATH,
            dry_run=True,
        )


def wrapped_run_subrocess(*args, **kwargs):
    """
    This is very coupled to the implementation of run_omop_es_docker!
    run_omop_es_docker calls run_subprocess with arguments: working_dir, args,
    env where args is a confusingly named argument passed to subprocess.Popen.

    We want to intercept this, overwrite the default docker entry point and add
    the bash env command:

    > docker <> run --rm omop_es

    becomes:

    > docker <> run --rm omop_es env
    """
    args[1].append("env")
    return run_subprocess.run_subprocess(*args, **kwargs)


@pytest.mark.skip("Reproduces crdm-tools/#26.")
def test_run_omop_es_docker_sets_env_correctly(mocker):
    mocker.patch("run_omop_es.run_subprocess", wrapped_run_subrocess)

    with disable_run_logger():
        result = run_omop_es.run_omop_es_docker.fn(
            working_dir=run_omop_es.ROOT_PATH,
            batched=False,
            settings_id="mock_project_settings",
            zip_output=False,
            start_batch=None,
            extract_dt=None,
        )

    assert "OMOP_ES_SETTINGS_ID=mock_project_settings" in result.stdout, (
        f"Setting ID not propagated: {result.stdout}"
    )
    assert "OMOP_ES_BATCHED=False" in result.stdout, "Batched flag not propagated"
    # TODO: the rest of these!
