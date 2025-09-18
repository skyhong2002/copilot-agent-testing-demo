import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from .exceptions import ParseError

class DataParser:
    """Handles data parsing operations."""

    @staticmethod
    def parse_json(json_string: str) -> Dict[str, Any]:
        """Parse JSON string to dictionary."""
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ParseError(f"JSON parse error: {str(e)}")

    @staticmethod
    def parse_xml(xml_string: str) -> Dict[str, Any]:
        """Parse XML string to dictionary."""
        try:
            root = ET.fromstring(xml_string)
            data = {}
            for child in root:
                data[child.tag] = child.text
            return data
        except ET.ParseError as e:
            raise ParseError(f"XML parse error: {str(e)}")

    @staticmethod
    def parse_data(data_input: Any) -> Optional[Dict[str, Any]]:
        """Parse input data based on its type and format."""
        if isinstance(data_input, dict):
            return data_input

        if isinstance(data_input, str):
            data_input = data_input.strip()
            if data_input.startswith('{') or data_input.startswith('['):
                return DataParser.parse_json(data_input)
            elif data_input.startswith('<'):
                return DataParser.parse_xml(data_input)
            else:
                raise ParseError(f"Unrecognized string format: {data_input[:50]}...")

        raise ParseError(f"Unsupported data type: {type(data_input)}")