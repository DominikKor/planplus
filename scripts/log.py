import logging
import os
from pathlib import Path
from dotenv import load_dotenv


def configure_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, ".env"))
    is_prod = os.getenv("ENV_NAME") == "Production"

    if is_prod:
        fh = logging.FileHandler("debug.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        logger.addHandler(fh)

    logger.addHandler(ch)

    return logger
