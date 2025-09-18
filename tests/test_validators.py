import pytest
import sys
import os

# Add the after directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'after'))

from after.validators import DataValidator
from after.exceptions import ValidationError


class TestDataValidator:
    """Test cases for DataValidator class."""

    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org",
            "123@domain.com"
        ]
        
        for email in valid_emails:
            assert DataValidator.validate_email(email), f"Expected {email} to be valid"

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        invalid_emails = [
            "",
            "invalid",
            "@domain.com",
            "user@",
            "user.domain.com",
            "user@domain",
            "user@domain.",
            None
        ]
        
        for email in invalid_emails:
            assert not DataValidator.validate_email(email), f"Expected {email} to be invalid"

    def test_validate_phone_valid(self):
        """Test phone validation with valid phone numbers."""
        valid_phones = [
            "1234567890",
            "(123) 456-7890",
            "123-456-7890",
            "+1-123-456-7890",
            "123.456.7890"
        ]
        
        for phone in valid_phones:
            assert DataValidator.validate_phone(phone), f"Expected {phone} to be valid"

    def test_validate_phone_invalid(self):
        """Test phone validation with invalid phone numbers."""
        invalid_phones = [
            "",
            "123",
            "abc",
            "123-456",
            None
        ]
        
        for phone in invalid_phones:
            assert not DataValidator.validate_phone(phone), f"Expected {phone} to be invalid"

    def test_validate_ssn_valid(self):
        """Test SSN validation with valid SSNs."""
        valid_ssns = [
            "123-45-6789",
            "987-65-4321"
        ]
        
        for ssn in valid_ssns:
            assert DataValidator.validate_ssn(ssn), f"Expected {ssn} to be valid"

    def test_validate_ssn_invalid(self):
        """Test SSN validation with invalid SSNs."""
        invalid_ssns = [
            "",
            "123456789",
            "123-45-678",
            "12-345-6789",
            "abc-de-fghi",
            None
        ]
        
        for ssn in invalid_ssns:
            assert not DataValidator.validate_ssn(ssn), f"Expected {ssn} to be invalid"

    def test_validate_credit_card_valid(self):
        """Test credit card validation with valid numbers."""
        valid_cards = [
            "1234567890123456",
            "4111-1111-1111-1111",
            "4111 1111 1111 1111"
        ]
        
        for card in valid_cards:
            assert DataValidator.validate_credit_card(card), f"Expected {card} to be valid"

    def test_validate_credit_card_invalid(self):
        """Test credit card validation with invalid numbers."""
        invalid_cards = [
            "",
            "123456789012345",  # 15 digits
            "12345678901234567",  # 17 digits
            "abcd1234567890123",
            None
        ]
        
        for card in invalid_cards:
            assert not DataValidator.validate_credit_card(card), f"Expected {card} to be invalid"

    def test_validate_user_data_valid(self):
        """Test user data validation with valid data."""
        user_data = {
            'id': 12345,
            'name': 'john doe',
            'email': 'John.Doe@Example.COM',
            'phone': '(123) 456-7890'
        }
        
        result = DataValidator.validate_user_data(user_data)
        
        assert result['data']['id'] == '12345'
        assert result['data']['name'] == 'JOHN DOE'
        assert result['data']['email'] == 'john.doe@example.com'
        assert result['data']['phone'] == '1234567890'
        assert result['data']['email_valid'] is True
        assert result['data']['phone_valid'] is True
        assert len(result['errors']) == 0

    def test_validate_user_data_invalid_email_phone(self):
        """Test user data validation with invalid email and phone."""
        user_data = {
            'id': 12345,
            'name': 'john doe',
            'email': 'invalid-email',
            'phone': '123'
        }
        
        result = DataValidator.validate_user_data(user_data)
        
        assert result['data']['email_valid'] is False
        assert result['data']['phone_valid'] is False
        assert len(result['errors']) == 2
        assert any('Invalid email' in error for error in result['errors'])
        assert any('Invalid phone' in error for error in result['errors'])

    def test_validate_user_data_non_dict(self):
        """Test user data validation with non-dictionary input."""
        with pytest.raises(ValidationError, match="User data must be a dictionary"):
            DataValidator.validate_user_data("not a dict")

    def test_validate_user_data_missing_fields(self):
        """Test user data validation with missing fields."""
        user_data = {}
        
        result = DataValidator.validate_user_data(user_data)
        
        assert result['data']['id'] == ''
        assert result['data']['name'] == ''
        assert result['data']['email'] == ''
        assert result['data']['phone'] == ''
        assert result['data']['email_valid'] is False
        assert result['data']['phone_valid'] is False