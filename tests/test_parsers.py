import pytest
import sys
import os
import json

# Add the after directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'after'))

from after.parsers import DataParser
from after.exceptions import ParseError


class TestDataParser:
    """Test cases for DataParser class."""

    def test_parse_json_valid(self):
        """Test parsing valid JSON data."""
        json_data = '{"id": 1, "name": "John", "email": "john@example.com"}'
        result = DataParser.parse_data(json_data)
        
        expected = {"id": 1, "name": "John", "email": "john@example.com"}
        assert result == expected

    def test_parse_json_invalid(self):
        """Test parsing invalid JSON data."""
        invalid_json = '{"id": 1, "name": "John", "email": "john@example.com"'  # Missing closing brace
        
        with pytest.raises(ParseError):
            DataParser.parse_data(invalid_json)

    def test_parse_xml_valid(self):
        """Test parsing valid XML data."""
        xml_data = '''<user>
            <id>1</id>
            <name>John</name>
            <email>john@example.com</email>
        </user>'''
        
        result = DataParser.parse_data(xml_data)
        
        expected = {"id": "1", "name": "John", "email": "john@example.com"}
        assert result == expected

    def test_parse_xml_invalid(self):
        """Test parsing invalid XML data."""
        invalid_xml = '<user><id>1</id><name>John</name>'  # Missing closing tag
        
        with pytest.raises(ParseError):
            DataParser.parse_data(invalid_xml)

    def test_parse_dict_data(self):
        """Test parsing dictionary data (already parsed)."""
        dict_data = {"id": 1, "name": "John", "email": "john@example.com"}
        result = DataParser.parse_data(dict_data)
        
        assert result == dict_data

    def test_parse_unsupported_format(self):
        """Test parsing unsupported data format."""
        unsupported_data = "plain text data"
        
        with pytest.raises(ParseError, match="Unrecognized string format"):
            DataParser.parse_data(unsupported_data)

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        with pytest.raises(ParseError, match="Unrecognized string format"):
            DataParser.parse_data("")

    def test_parse_none_data(self):
        """Test parsing None data."""
        with pytest.raises(ParseError, match="Unsupported data type"):
            DataParser.parse_data(None)

    def test_parse_complex_json(self):
        """Test parsing complex JSON with nested objects."""
        complex_json = '''{
            "id": 1,
            "name": "John Doe",
            "contact": {
                "email": "john@example.com",
                "phone": "123-456-7890"
            },
            "preferences": ["email", "sms"]
        }'''
        
        result = DataParser.parse_data(complex_json)
        
        assert result["id"] == 1
        assert result["name"] == "John Doe"
        assert result["contact"]["email"] == "john@example.com"
        assert result["preferences"] == ["email", "sms"]

    def test_parse_xml_with_attributes(self):
        """Test parsing XML with attributes."""
        xml_data = '''<user id="1" active="true">
            <name>John</name>
            <email>john@example.com</email>
        </user>'''
        
        result = DataParser.parse_data(xml_data)
        
        # Should handle attributes and text content
        assert "name" in result
        assert "email" in result
        assert result["name"] == "John"
        assert result["email"] == "john@example.com"

    def test_parse_json_array(self):
        """Test parsing JSON array."""
        json_array = '[{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]'
        
        result = DataParser.parse_data(json_array)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "John"
        assert result[1]["name"] == "Jane"

    def test_parse_malformed_xml_injection(self):
        """Test parsing XML with potential injection attempts."""
        malicious_xml = '''<user>
            <id>1</id>
            <name>John</name>
            <script>alert('xss')</script>
            <email>john@example.com</email>
        </user>'''
        
        # Should parse without executing any scripts
        result = DataParser.parse_data(malicious_xml)
        
        assert "script" in result  # Should be treated as regular data
        assert result["script"] == "alert('xss')"  # Should be escaped/safe
        assert result["name"] == "John"