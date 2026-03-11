from pathlib import Path
from time import sleep

import typer
import random
from datetime import datetime
from loguru import logger

app = typer.Typer()

@app.command()
def write_message(message: str, filename: Path = Path("output.txt")):
    """Writes the message and current timestamp to a file 25% of the time, raises error otherwise"""
    for i in range(2000):
        sleep(0.1)
        logger.debug(f"Some logging output {i}")
    
    sleep(1)
    if random.random() < 0.25:
        with open(filename, "a") as file:
            timestamp = datetime.now().isoformat()
            file.write(f"{timestamp}: {message}\n")
        logger.info(f"Message written to {filename}")
    else:
        logger.error("Message not written this time.")
        raise NotImplementedError("Planned failure.")
