import json
import logging
import sys
from typing import Any, Dict, List, Optional

# Assuming 'src' is a Python package and 'parser.py' and 'output_handler.py'
# are modules within that package.
# Example project structure:
# project_root/
# ├── src/
# │   ├── __init__.py
# │   ├── main.py
# │   ├── parser.py
# │   └── output_handler.py
# └── config.json
#
# These imports expect that 'src' is treated as a package.
# The `parser.py` module is expected to expose a function
# `parse_product_data(url: str, parser_type: str) -> Optional[Dict[str, Any]]`.
# The `output_handler.py` module is expected to expose a function
# `save_data(data: Dict[str, Any]) -> None`.
from src.parser import parse_product_data
from src.output_handler import save_data


CONFIG_FILE = "config.json"


def setup_logging() -> None:
    """
    Configures the basic logging for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Loads configuration from a specified JSON file.

    Args:
        config_path: The path to the configuration JSON file.

    Returns:
        A dictionary containing the loaded configuration.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the configuration file is malformed JSON.
        ValueError: If the configuration structure is invalid.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if "websites" not in config or not isinstance(config["websites"], list):
            raise ValueError("Config file must contain a 'websites' key with a list of entries.")
        return config
    except FileNotFoundError:
        logging.critical(f"Configuration file not found at: {config_path}")
        raise
    except json.JSONDecodeError:
        logging.critical(f"Error decoding JSON from configuration file: {config_path}")
        raise
    except ValueError as e:
        logging.critical(f"Invalid configuration structure in {config_path}: {e}")
        raise
    except Exception as e:
        logging.critical(f"An unexpected error occurred while loading config: {e}", exc_info=True)
        raise


def main() -> None:
    """
    Main orchestration function. Loads configuration, iterates through websites,
    invokes the parser, and passes extracted data to the output handler.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting product data parsing process...")

    config: Dict[str, Any]
    try:
        config = load_config(CONFIG_FILE)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        logger.critical("Failed to load configuration. Exiting.")
        sys.exit(1)

    websites_to_parse: List[Dict[str, str]] = config.get("websites", [])

    if not websites_to_parse:
        logger.warning("No websites defined in the configuration. Nothing to parse.")
        return

    for website_info in websites_to_parse:
        name = website_info.get("name", "Unknown Product")
        url = website_info.get("url")
        parser_type = website_info.get("parser_type", "default")

        if not url:
            logger.error(f"Skipping '{name}': URL not provided in config.")
            continue

        logger.info(f"Processing '{name}' from URL: {url} (Parser Type: {parser_type})")

        try:
            # Invoke the refactored parser
            extracted_data = parse_product_data(url, parser_type)

            if extracted_data:
                logger.info(f"Successfully extracted data for '{name}'.")
                # Augment extracted data with source configuration for context/traceability
                extracted_data["source_config"] = website_info
                # Pass data to the output handler
                save_data(extracted_data)
                logger.info(f"Data for '{name}' sent to output handler.")
            else:
                logger.warning(f"No data extracted for '{name}' from URL: {url}.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing '{name}' (URL: {url}): {e}", exc_info=True)

    logger.info("Product data parsing process completed.")


if __name__ == "__main__":
    main()