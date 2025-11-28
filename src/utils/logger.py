import logging
import os
from typing import Optional

# --- Configuration Constants ---
# Environment variable to control the application's log level
LOG_LEVEL_ENV_VAR = "APP_LOG_LEVEL"
# Default log level if no environment variable is set
DEFAULT_LOG_LEVEL = logging.INFO
# Standard format for log messages
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# Standard format for timestamps in log messages
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Global flag to track if the logger has been configured by this module.
# This prevents duplicate handlers if configure_logging is called multiple times.
_logger_configured = False


def configure_logging(
    level: Optional[int] = None,
    log_file: Optional[str] = None,
    force_reconfigure: bool = False,
) -> None:
    """
    Configures the root logger for the application.

    This function sets up a console handler and an optional file handler
    with a consistent format. It's designed to be called once during
    application startup to establish the primary logging configuration.

    Args:
        level: The logging level (e.g., logging.INFO, logging.DEBUG).
               If None, it tries to read the log level from the
               APP_LOG_LEVEL environment variable, defaulting to logging.INFO.
        log_file: Optional path to a log file. If provided, a FileHandler
                  will be added to write logs to this file.
        force_reconfigure: If True, forces re-configuration even if logging
                           has already been configured by this module. Use
                           with caution, as it will remove existing handlers
                           from the root logger before re-applying settings.
    """
    global _logger_configured

    if _logger_configured and not force_reconfigure:
        # If already configured by this module and not forcing a re-configuration,
        # simply return to prevent duplicate handlers.
        return

    # Determine the desired log level.
    if level is None:
        level_str = os.getenv(LOG_LEVEL_ENV_VAR, "INFO").upper()
        level_map = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }
        level = level_map.get(level_str, DEFAULT_LOG_LEVEL)

    # Get the root logger instance.
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers from the root logger ONLY if force_reconfigure is True.
    # This is crucial for preventing duplicate log messages if configuration
    # is explicitly reapplied, or to replace an existing setup.
    if force_reconfigure:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
            try:
                handler.close()  # Attempt to close handler resources
            except Exception:
                pass  # Ignore errors during closing

    # Create and add a console handler (StreamHandler).
    # This ensures logs are always visible in the console.
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # If a log file path is provided, create and add a file handler.
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            # Log the error about the file handler, but allow the application
            # to continue with console logging. A temporary logger is used
            # to avoid potential recursion if the root logger itself is misconfigured.
            temp_logger = logging.getLogger(__name__ + ".setup_error")
            temp_logger.error(f"Failed to set up file logger at '{log_file}': {e}")

    _logger_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a logger instance for a given name.

    Ensures that logging is configured by this module before returning the logger.
    If `configure_logging` hasn't been called yet, this function will
    automatically call it with default settings to ensure a basic logging
    setup is always available.

    Args:
        name: The name of the logger (typically `__name__` of the module
              requesting the logger). This allows for hierarchical logging.

    Returns:
        A configured `logging.Logger` instance.
    """
    if not _logger_configured:
        # If this module hasn't set up logging yet, do it with default settings.
        # This guarantees that any logger retrieved via get_logger is always
        # properly initialized according to this utility's configuration.
        configure_logging()

    return logging.getLogger(name)


# --- Module Initialization ---
# This block ensures that a basic logging setup is always available as soon as
# 'src.utils.logger' is imported, even if `configure_logging()` is not
# explicitly called later by the main application logic.
if not _logger_configured:
    configure_logging()