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

import os

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


def test_star_use_prod_if():
    # Test that *dry_run_if expands as we expect
    command_with = ["docker", "compose", *run_omop_es.use_prod_if(True), "do-thing"]
    command_without = ["docker", "compose", *run_omop_es.use_prod_if(False), "do-thing"]
    assert command_with == [
        "docker",
        "compose",
        "-f",
        "docker-compose.prod.yml",
        "do-thing",
    ]
    assert command_without == ["docker", "compose", "do-thing"]


# See https://docs.prefect.io/v3/develop/test-workflows#unit-testing-tasks for
# how to test tasks (or sub functions) outside of a flow context.
#
# > If your task uses a logger, you can disable the logger to avoid the
# > RuntimeError raised from a missing flow context.


def test_build_docker():
    with disable_run_logger():
        run_omop_es.build_docker.fn(
            working_dir=run_omop_es.ROOT_PATH,
            project_name="my-project",
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
            settings_id="test",
            omop_es_branch="master",
            batched=False,
            output_directory="",
            zip_output=False,
        )

    # String values of the arguments we passed into the function 👆
    expected_env_values = {
        "SETTINGS_ID": "test",
        "BATCHED": "False",
        "OUTPUT_DIRECTORY": "",
        "ZIP_OUTPUT": "False",
    }

    for var, expected_value in expected_env_values.items():
        assert f"{var}={expected_value}" in result.stdout, (
            f"Environment variable {var} not set correctly: {result.stdout}"
        )


def test_run_omop_es_docker_can_run_batched():
    os.environ["DEBUG"] = "true"
    with disable_run_logger():
        result = run_omop_es.run_omop_es_docker.fn(
            working_dir=run_omop_es.ROOT_PATH,
            settings_id="test",
            omop_es_branch="master",
            batched=True,
            output_directory="foo",
            zip_output=True,
        )

    expected_command = "Rscript ./main/batched.R --settings_id test --output_directory foo --zip_output"

    ## Check that expected_command is the last line of result.stdout
    assert expected_command == result.stdout.strip().split("\n")[-1], (
        f"Expected command '{expected_command}',\ngot '{result.stdout}'"
    )


def test_version_pinning_with_branch_pulls_latest():
    """Test that using a branch name results in git pull being called."""
    os.environ["DEBUG"] = "true"

    with disable_run_logger():
        result = run_omop_es.run_omop_es_docker.fn(
            working_dir=run_omop_es.ROOT_PATH,
            settings_id="test",
            omop_es_branch="master",
            batched=False,
            output_directory="",
            zip_output=False,
        )

    # Shell output goes to stderr due to set -x in bash script
    output = result.stdout.strip().split("\n")
    assert "Checking out latest from branch: master" in output, (
        f"Expected branch checkout message in stdout output: {output}"
    )


def test_version_pinning_with_commit_sha():
    """Test that using a commit SHA results in pinned checkout (no git pull)."""
    os.environ["DEBUG"] = "true"

    test_sha = "f439272"

    with disable_run_logger():
        result = run_omop_es.run_omop_es_docker.fn(
            working_dir=run_omop_es.ROOT_PATH,
            settings_id="test",
            omop_es_branch=test_sha,
            batched=False,
            output_directory="",
            zip_output=False,
        )

    output = result.stdout.strip().split("\n")
    assert f"Checking out pinned version: {test_sha}" in output, (
        f"Expected version checkout message in stdout output: {output}"
    )


def test_version_pinning_fails_with_invalid_sha():
    """Test that using an invalid commit SHA results in an error."""
    os.environ["DEBUG"] = "true"

    test_sha = "invalid_sha"

    # with pytest.raises():
    with disable_run_logger():
        result = run_omop_es.run_omop_es_docker.fn(
            working_dir=run_omop_es.ROOT_PATH,
            settings_id="test",
            omop_es_branch=test_sha,
            batched=False,
            output_directory="",
            zip_output=False,
        )

    assert "Invalid commit SHA" in result.stderr, (
        f"Expected error message in stderr output: {result.stderr}"
    )
