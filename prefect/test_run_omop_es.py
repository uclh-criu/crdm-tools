import pytest
from freezegun import freeze_time
from prefect.testing.utilities import prefect_test_harness

import run_omop_es


@freeze_time("2025-01-01")
def test_name_with_timestamp():
    # The prefect deployment name is set to 'None' (because we're not in a prefect deployment)
    assert run_omop_es.name_with_timestamp() == "None_2025-01-01T00:00:00+00:00"


def test_star_dry_run_if():
    # Test that *dry_run_if expands as we expect
    command_with = ["docker", "compose", *run_omop_es.dry_run_if(True), "do-thing"]
    command_without = ["docker", "compose", *run_omop_es.dry_run_if(False), "do-thing"]
    assert command_with == ["docker", "compose", "--dry-run", "do-thing"]
    assert command_without == ["docker", "compose", "do-thing"]


@pytest.mark.skip(reason="Currently broken: can't get test harness to work with tasks?")
@pytest.mark.slow
def test_build_docker(tmp_path):
    with prefect_test_harness(server_startup_timeout=60):
        run_omop_es.build_docker(
            working_dir=tmp_path,
            dry_run=True,
        )


@pytest.mark.skip(reason="Currently broken: can't get test harness to work with tasks?")
@pytest.mark.slow
def test_run_omop_es_docker():
    with prefect_test_harness():
        run_omop_es.run_omop_es_docker(
            working_dir=run_omop_es.ROOT_PATH,
            batched=False,
            settings_id="mock_project_settings",
            zip_output=False,
            start_batch=None,
            extract_dt=None,
            dry_run=True,
        )
