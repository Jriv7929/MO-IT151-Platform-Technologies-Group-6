"""
Logging configuration for the FinMark data pipeline.

Logs are written to:
    logs/pipeline.log

Messages are also displayed in the terminal.
"""

import logging

from config import LOG_DIR, PIPELINE_LOG_FILE, create_project_directories


def get_logger(name: str = "finmark_pipeline") -> logging.Logger:
    """
    Create and return the FinMark pipeline logger.

    Parameters
    ----------
    name:
        Name assigned to the logger.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    create_project_directories()

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate log messages when the module is reloaded.
    if logger.handlers:
        return logger

    log_format = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(
        PIPELINE_LOG_FILE,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger initialized.")
    logger.info("Log directory: %s", LOG_DIR)

    return logger