"""Structured logging configuration with PII redaction for VidyaSetu."""
import logging
import re
import sys
from typing import Any

# Regular expressions to mask sensitive identifiers
MASK_PATTERNS = [
    # 12-digit Aadhaar / APAAR numbers (e.g. 1234 5678 9012 or 123456789012)
    (re.compile(r"\b\d{4}\s?\d{4}\s?(\d{4})\b"), r"XXXX-XXXX-\1"),
    # Standard email masking
    (re.compile(r"([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]*@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"), r"\1***@\2"),
    # 10-digit mobile phone numbers
    (re.compile(r"\b(\+91[\-\s]?)?[6-9]\d{5}(\d{4})\b"), r"+91-XXXXX-\2"),
]


class PIIRedactingFormatter(logging.Formatter):
    """Custom formatter that automatically redacts sensitive personal identifiers."""

    def format(self, record: logging.LogRecord) -> str:
        orig_msg = super().format(record)
        redacted = orig_msg
        for pattern, replacement in MASK_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted


def setup_logging(log_level: str = "INFO") -> None:
    """Configure institutional structured logging."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = PIIRedactingFormatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for existing_handler in list(root_logger.handlers):
        root_logger.removeHandler(existing_handler)

    root_logger.addHandler(handler)

    # Set external libraries to warning to avoid log spam
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


logger = logging.getLogger("vidyasetu")
