import logging
import sys

class DebugOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG

def setup_logger():

    logger = logging.getLogger("Private LLM Rag System")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    #console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Show ONLY DEBUG logs
    console_handler.addFilter(DebugOnlyFilter())

    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()