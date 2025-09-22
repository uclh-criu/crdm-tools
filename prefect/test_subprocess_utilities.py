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
import logging
from pathlib import Path
import subprocess
from prefect.logging import disable_run_logger

import run_subprocess

_LOG_MESSAGES_AND_EXPECTED_LEVELS = [
    ("[DEBUG]", "DEBUG"),
    ("[DEBUG] This is a debug message", "DEBUG"),
    ("[INFO] This is an info message", "INFO"),
    ("[WARNING] This is a warning message", "WARNING"),
    ("[ERROR] This is an error message", "ERROR"),
]


@pytest.mark.parametrize(
    "message, expected_level",
    _LOG_MESSAGES_AND_EXPECTED_LEVELS
    + [
        # Some extra test cases
        ("[CRITICAL] This is a critical message", "CRITICAL"),
        ("[UNKNOWN] This is an unknown level message", "UNKNOWN"),
        ("[FLIBBLE] This is a nonsense level message", "FLIBBLE"),
        ("This is a message without a level", None),
    ],
)
def test_log_level_extraction(message, expected_level):
    assert run_subprocess.extract_log_level(message) == expected_level, (
        f"Expected '{expected_level}' for message '{message}'"
    )


@pytest.mark.parametrize(
    "message, expected_level",
    _LOG_MESSAGES_AND_EXPECTED_LEVELS
    + [
        # Unknown levels should default to INFO
        ("[UNKNOWN] This is an unknown level message", "INFO"),
        ("[FLIBBLE] This is a nonsense level message", "INFO"),
        ("This is a message without a level", "INFO"),
    ],
)
def test_log(caplog, message, expected_level):
    caplog.clear()
    caplog.set_level(logging.NOTSET)  # Log everything

    message_in_bytes = bytes(message, "utf-8")
    run_subprocess.log(message_in_bytes, logging.getLogger())

    assert len(caplog.records) == 1, "Expected one log record"
    assert message in caplog.text, f"Expected message '{message}' in log"
    assert caplog.records[0].levelname == expected_level, (
        f"Expected log level '{expected_level}'"
    )


# See https://docs.prefect.io/v3/develop/test-workflows#unit-testing-tasks for
# how to test tasks (or sub functions) outside of a flow context.
#
# > If your task uses a logger, you can disable the logger to avoid the
# > RuntimeError raised from a missing flow context.


def test_run_subprocess():
    with disable_run_logger():
        run_subprocess.run_subprocess(
            working_dir=Path(__file__).parent,
            args=["echo", "Hello, World!"],
        )


def test_run_subprocess_error():
    with disable_run_logger():
        with pytest.raises(subprocess.CalledProcessError):
            run_subprocess.run_subprocess(
                working_dir=Path(__file__).parent,
                args=["false"],
            )
