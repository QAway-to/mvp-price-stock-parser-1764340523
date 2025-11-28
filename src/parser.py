from typing import Dict, Any, List, Optional
from lxml import html


def parse_product_page(html_content: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses product page HTML content using a dynamic configuration of CSS or XPath selectors.

    The parser iterates through defined data points in the configuration, attempting to extract
    data based on the provided selector, type (css/xpath), and whether multiple values are expected.

    Args:
        html_content: The HTML content of the product page as a string.
        config: A dictionary containing parsing configurations. Expected structure:
                {
                    "data_points": {
                        "item_key_1": {"selector": "css_selector_or_xpath", "type": "css|xpath", "multi": true|false},
                        "item_key_2": {"selector": "css_selector_or_xpath", "type": "css|xpath", "multi": true|false}
                    }
                }
                - 'selector': The CSS selector or XPath expression. For attributes, use '::attr(attribute_name)'
                              for CSS or '@attribute_name' for XPath (e.g., 'img::attr(src)', '//img/@src').
                - 'type': 'css' or 'xpath'. Defaults to 'css' if omitted.
                - 'multi': True if multiple values are expected (returns a list), False otherwise (returns
                           a single value or None). Defaults to False if omitted.

    Returns:
        A dictionary where keys are data point names and values are the extracted data.
        Failed extractions will result in None (for single values) or an empty list (for multi-values).
    """
    tree = html.fromstring(html_content)
    results: Dict[str, Any] = {}

    for data_key, selector_config in config.get('data_points', {}).items():
        selector = selector_config.get('selector')
        selector_type = selector_config.get('type', 'css').lower()
        multi = selector_config.get('multi', False)
        
        if not selector:
            results[data_key] = [] if multi else None
            continue

        extracted_elements: List[Any] = []
        try:
            if selector_type == 'css':
                extracted_elements = tree.cssselect(selector)
            elif selector_type == 'xpath':
                extracted_elements = tree.xpath(selector)
            else:
                results[data_key] = [] if multi else None
                continue
        except Exception:
            # Catching broad exceptions for robustness, a more specific error handling
            # strategy could be implemented for production (e.g., logging).
            results[data_key] = [] if multi else None
            continue

        processed_data: List[str] = []
        for el in extracted_elements:
            if isinstance(el, str):  # Selector directly returned an attribute string
                processed_data.append(el.strip())
            elif hasattr(el, 'text_content'):  # It's an lxml Element, extract text content
                text = el.text_content().strip()
                if text:
                    processed_data.append(text)
        
        if multi:
            results[data_key] = processed_data
        else:
            results[data_key] = processed_data[0] if processed_data else None

    return results