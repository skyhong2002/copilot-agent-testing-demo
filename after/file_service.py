import json
import xml.etree.ElementTree as ET
import os
import logging
from typing import List, Dict, Any
from .exceptions import APIException

logger = logging.getLogger(__name__)

class FileService:
    """Handles file operations."""

    def __init__(self):
        self.temp_files = []

    def save_to_json(self, filename: str, data: List[Dict[str, Any]]) -> bool:
        """Save data to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.temp_files.append(filename)
            logger.info(f"Data saved to JSON file: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON file {filename}: {str(e)}")
            raise APIException(f"File save error: {str(e)}")

    def save_to_xml(self, filename: str, data: List[Dict[str, Any]]) -> bool:
        """Save data to XML file."""
        try:
            root = ET.Element("data")
            for item in data:
                record = ET.SubElement(root, "record")
                for key, value in item.items():
                    elem = ET.SubElement(record, str(key))
                    elem.text = str(value) if value is not None else ""

            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            self.temp_files.append(filename)
            logger.info(f"Data saved to XML file: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save XML file {filename}: {str(e)}")
            raise APIException(f"File save error: {str(e)}")

    def save_to_file(self, filename: str, data: List[Dict[str, Any]], format_type: str = 'json') -> bool:
        """Save data to file in specified format."""
        if format_type.lower() == 'json':
            return self.save_to_json(filename, data)
        elif format_type.lower() == 'xml':
            return self.save_to_xml(filename, data)
        else:
            raise APIException(f"Unsupported file format: {format_type}")

    def cleanup_temp_files(self):
        """Clean up temporary files."""
        for filename in self.temp_files:
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                    logger.debug(f"Removed temporary file: {filename}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {filename}: {str(e)}")
        self.temp_files.clear()