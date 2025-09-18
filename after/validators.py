import re
from typing import Dict, Any, List
from .exceptions import ValidationError

class DataValidator:
    """Handles data validation operations."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return False
        cleaned = re.sub(r'[^\d]', '', phone)
        return len(cleaned) >= 10

    @staticmethod
    def validate_ssn(ssn: str) -> bool:
        """Validate SSN format."""
        if not ssn:
            return False
        pattern = r'^\d{3}-\d{2}-\d{4}$'
        return re.match(pattern, ssn) is not None

    @staticmethod
    def validate_credit_card(cc: str) -> bool:
        """Validate credit card format."""
        if not cc:
            return False
        cleaned = re.sub(r'[^\d]', '', cc)
        return len(cleaned) == 16

    @staticmethod
    def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and process user data."""
        if not isinstance(user_data, dict):
            raise ValidationError("User data must be a dictionary")

        errors = []

        processed = {
            'id': str(user_data.get('id', '')),
            'name': str(user_data.get('name', '')).upper(),
            'email': str(user_data.get('email', '')).lower(),
            'phone': re.sub(r'[^\d]', '', str(user_data.get('phone', ''))),
        }

        processed['email_valid'] = DataValidator.validate_email(processed['email'])
        processed['phone_valid'] = DataValidator.validate_phone(processed['phone'])

        if not processed['email_valid']:
            errors.append(f"Invalid email: {processed['email']}")

        if not processed['phone_valid']:
            errors.append(f"Invalid phone: {processed['phone']}")

        return {
            'data': processed,
            'errors': errors
        }