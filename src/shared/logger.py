"""Logging configuration for the Organic Funnel Agent."""
import sys
from loguru import logger
from pathlib import Path


def setup_logger(log_dir: str = "logs"):
    """Configure the logger with file and console output."""
    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Add console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO"
    )

    # Add file handler for all logs
    logger.add(
        f"{log_dir}/agent.log",
        rotation="100 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="DEBUG"
    )

    # Add separate file for errors
    logger.add(
        f"{log_dir}/errors.log",
        rotation="100 MB",
        retention="90 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="ERROR"
    )

    return logger


# Initialize logger
log = setup_logger()
