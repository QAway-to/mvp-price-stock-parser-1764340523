import json
from pathlib import Path
from typing import Union, List, Dict, Any

class OutputHandler:
    """
    Handles the comprehensive extracted data, saving it to structured JSON files.

    This module is responsible for persisting the richer, more complex data
    extracted by the parser, especially "everything in the description".
    Initially, it supports saving individual products or a list of products to
    JSON files. It's designed with extensibility in mind for future integrations
    with databases or other structured formats.
    """

    def __init__(self, output_dir: Union[str, Path] = "output"):
        """
        Initializes the OutputHandler with a specified output directory.

        The directory will be created if it does not already exist, including
        any necessary parent directories.

        Args:
            output_dir: The directory where output JSON files will be stored.
                        Defaults to "output".
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _serialize_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """
        Helper method to serialize data (dictionary or list of dictionaries) to a JSON string.

        Uses an indent of 4 for human readability and ensures non-ASCII characters
        are correctly preserved (e.g., Cyrillic characters in descriptions).

        Args:
            data: The data structure to serialize. Can be a dictionary for a single product
                  or a list of dictionaries for multiple products.

        Returns:
            A JSON formatted string.

        Raises:
            ValueError: If the provided data is not JSON serializable (e.g., contains
                        unsupported Python objects like sets or custom class instances
                        without a custom JSON encoder).
        """
        try:
            return json.dumps(data, indent=4, ensure_ascii=False)
        except TypeError as e:
            raise ValueError(f"Data not JSON serializable: {e}") from e

    def save_product_data(self, product_data: Dict[str, Any], filename: str) -> Path:
        """
        Saves a single comprehensive extracted product data dictionary to a JSON file.

        The filename will automatically be given a '.json' extension if not present.
        The file will be stored in the `output_dir` configured for this handler.

        Args:
            product_data: A dictionary containing comprehensive extracted product data.
                          This typically includes fields like 'name', 'price', 'stock',
                          and a detailed 'description' object (which itself can be
                          a complex, nested dictionary or list).
            filename: The desired base name of the JSON file (e.g., "product_id_123"
                      or "product_id_123.json").

        Returns:
            The absolute path to the newly created or updated JSON file.

        Raises:
            IOError: If there's an issue writing the file to disk (e.g., permissions,
                     disk full, invalid path component).
            ValueError: If the `product_data` is not JSON serializable.
        """
        file_path = self.output_dir / filename
        if not file_path.suffix == ".json":
            file_path = file_path.with_suffix(".json")

        serialized_data = self._serialize_data(product_data)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(serialized_data)
            return file_path.resolve()  # Return absolute path
        except IOError as e:
            raise IOError(f"Failed to write data to {file_path}: {e}") from e

    def save_all_products_to_single_file(self, products_list: List[Dict[str, Any]], filename: str) -> Path:
        """
        Saves a list of comprehensive extracted product data dictionaries to a single JSON file.

        This method is ideal for batch saving multiple products into one consolidated file.
        The filename will automatically be given a '.json' extension if not present.
        The file will be stored in the `output_dir` configured for this handler.

        Args:
            products_list: A list of dictionaries, where each dictionary represents
                           comprehensive extracted product data (similar to `product_data`
                           in `save_product_data`).
            filename: The desired base name of the JSON file (e.g., "all_products"
                      or "all_products.json").

        Returns:
            The absolute path to the newly created or updated JSON file.

        Raises:
            IOError: If there's an issue writing the file to disk.
            ValueError: If any item in `products_list` is not JSON serializable.
        """
        file_path = self.output_dir / filename
        if not file_path.suffix == ".json":
            file_path = file_path.with_suffix(".json")

        serialized_data = self._serialize_data(products_list)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(serialized_data)
            return file_path.resolve()  # Return absolute path
        except IOError as e:
            raise IOError(f"Failed to write data to {file_path}: {e}") from e