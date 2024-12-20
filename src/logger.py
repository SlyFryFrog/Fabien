import logging
import logging.config
from src.constants import LOGGER_CONFIG_FILE

def log_config(config: str = LOGGER_CONFIG_FILE) -> logging.Logger:
    """Creates a logger with the specified config file

    Args:
        config (str, optional): Config file for logging. 
        Defaults to LOGGER_CONFIG_FILE.

    Returns:
        Logger: Returns a logger based on the config file used.
    """
    logging.config.fileConfig(config)
    logger = logging.getLogger("Fabien")
    return logger

LOGGER: logging.Logger = log_config()