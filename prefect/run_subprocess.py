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

import re
import subprocess
from logging import Logger
from pathlib import Path
from typing import Optional

from prefect import logging
from prefect.logging.loggers import LoggingAdapter


def run_subprocess(
    working_dir: Path, args: list[str], env: Optional[dict] = None
) -> subprocess.CompletedProcess:
    """Helper to run subprocesses, logging stderr."""
    logger = logging.get_run_logger()
    logger.info(f"Running subprocess without logs: {' '.join(args)}")

    proc = subprocess.run(args, cwd=working_dir, env=env)
    stdout = []
    stderr = []

    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, args, stdout, stderr)
    return subprocess.CompletedProcess(args, proc.returncode, stdout, stderr)


def log(line: bytes, logger: Logger | LoggingAdapter) -> None:
    # Detect log level from the line and call appropriate logger function
    stripped_line = line.decode().strip()
    log_level = extract_log_level(stripped_line)

    match log_level:
        case "DEBUG":
            logger.debug(stripped_line)
        case "INFO":
            logger.info(stripped_line)
        case "WARNING" | "WARN":
            logger.warning(stripped_line)
        case "ERROR":
            logger.error(stripped_line)
        case "CRITICAL":
            logger.critical(stripped_line)
        case _:
            logger.info(stripped_line)


def extract_log_level(log_message: str) -> Optional[str]:
    pattern = r"\[(.*?)\]"
    match = re.search(pattern, log_message)
    return match.group(1) if match else None
