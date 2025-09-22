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

import pytest
from freezegun import freeze_time
from prefect.logging import disable_run_logger

import run_omop_es
import run_subprocess


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


# See https://docs.prefect.io/v3/develop/test-workflows#unit-testing-tasks for
# how to test tasks (or sub functions) outside of a flow context.
#
# > If your task uses a logger, you can disable the logger to avoid the
# > RuntimeError raised from a missing flow context.


@pytest.mark.slow
def test_build_docker():
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


def test_run_omop_es_docker_sets_env_correctly(mocker):
    mocker.patch("run_omop_es.run_subprocess", wrapped_run_subrocess)

    with disable_run_logger():
        result = run_omop_es.run_omop_es_docker.fn(
            working_dir=run_omop_es.ROOT_PATH,
            settings_id="mock_project_settings",
            batched=False,
            output_dir="",
            zip_output=False,
        )

    # String values of the arguments we passed into the function 👆
    expected_env_values = {
        "SETTINGS_ID": "mock_project_settings",
        "BATCHED": "False",
        "OUTPUT_DIR": "",
        "ZIP_OUTPUT": "False",
    }

    for var, expected_value in expected_env_values.items():
        assert f"{var}={expected_value}" in result.stdout, (
            f"Environment variable {var} not set correctly: {result.stdout}"
        )
