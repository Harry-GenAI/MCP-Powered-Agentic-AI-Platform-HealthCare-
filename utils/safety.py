from utils.logger import logger

# -----------------------
# BLOCKED WORDS
# -----------------------
UNSAFE_INPUT = ["hack", "illegal", "exploit"]

SENSITIVE_DATA = ["salary", "ssn", "confidential", "internal use only"]


# -----------------------
# INPUT GUARDRAILS
# -----------------------
def is_safe_input(question: str) -> bool:
    logger.info("Running input safety check")

    q = question.lower()
    safe = not any(word in q for word in UNSAFE_INPUT)

    if not safe:
        logger.warning("Blocked unsafe query")

    return safe


# -----------------------
# CONTEXT SANITIZATION (protecting sensitive data leakage to the API's)
# -----------------------
def has_sensitive_data(text:str) -> bool:
    text = text.lower()
    return any(word in text for word in SENSITIVE_DATA)

def sanitize_context(text:str)-> str:
    if has_sensitive_data(text):
        logger.info("Blocked context because it contains sensitive data.")
        return "Context contains sensitive data or confidential data so it was not shared."
    
    return text
