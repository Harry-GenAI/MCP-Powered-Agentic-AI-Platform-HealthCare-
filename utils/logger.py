import logging
import sys

def setup_logger():

    logger = logging.getLogger("enterprise-rag")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s| %(levelname)s | %(name)s | %(message)s"
    )

    #console_handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger

logger = setup_logger()
