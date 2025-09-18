import datetime
import logging
from typing import List, Dict, Any, Optional

from .config import load_config
from .validators import DataValidator
from .parsers import DataParser
from .auth_service import AuthenticationService
from .database_service import DatabaseService
from .encryption_service import EncryptionService
from .file_service import FileService
from .backup_service import BackupService
from .reporting_service import ReportingService
from .exceptions import APIException, ValidationError, ParseError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Main data processing facade with proper separation of concerns."""

    def __init__(self):
        self.config = load_config()
        self.auth_service = AuthenticationService(self.config.ldap, self.config.admin_password)
        self.database_service = DatabaseService(self.config.database)
        self.encryption_service = EncryptionService(self.config.api)
        self.file_service = FileService()
        self.backup_service = BackupService(self.config.backup, self.config.api)
        self.reporting_service = ReportingService()

        self.processed_data = []
        self.errors = []

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials."""
        try:
            return self.auth_service.authenticate_user(username, password)
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            self.errors.append(f"Authentication error: {str(e)}")
            return False

    def parse_input_data(self, input_data: List[Any]) -> List[Dict[str, Any]]:
        """Parse input data from various formats."""
        parsed_data = []

        for item in input_data:
            try:
                parsed = DataParser.parse_data(item)
                if parsed:
                    parsed_data.append(parsed)
            except ParseError as e:
                logger.warning(f"Parse error: {str(e)}")
                self.errors.append(str(e))
            except Exception as e:
                logger.error(f"Unexpected parse error: {str(e)}")
                self.errors.append(f"Unexpected parse error: {str(e)}")

        return parsed_data

    def validate_and_process_data(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and process parsed data."""
        processed_data = []

        for data_item in parsed_data:
            try:
                result = DataValidator.validate_user_data(data_item)
                processed_item = result['data']
                processed_item['created_date'] = datetime.datetime.now().isoformat()

                processed_data.append(processed_item)
                self.errors.extend(result['errors'])

            except ValidationError as e:
                logger.warning(f"Validation error: {str(e)}")
                self.errors.append(str(e))
            except Exception as e:
                logger.error(f"Unexpected validation error: {str(e)}")
                self.errors.append(f"Unexpected validation error: {str(e)}")

        return processed_data

    def save_processed_data(self, processed_data: List[Dict[str, Any]]) -> bool:
        """Save processed data to database."""
        try:
            return self.database_service.save_user_data(processed_data)
        except Exception as e:
            logger.error(f"Database save error: {str(e)}")
            self.errors.append(f"Database save error: {str(e)}")
            return False

    def save_to_file(self, filename: str, data: List[Dict[str, Any]], format_type: str = 'json') -> bool:
        """Save data to file."""
        try:
            return self.file_service.save_to_file(filename, data, format_type)
        except Exception as e:
            logger.error(f"File save error: {str(e)}")
            self.errors.append(f"File save error: {str(e)}")
            return False

    def backup_data(self, data: List[Dict[str, Any]]) -> bool:
        """Backup data to configured locations."""
        try:
            return self.backup_service.backup_data(data)
        except Exception as e:
            logger.error(f"Backup error: {str(e)}")
            self.errors.append(f"Backup error: {str(e)}")
            return False

    def generate_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate processing report."""
        return self.reporting_service.generate_report(data, self.errors)

    def process_everything(self, input_data: List[Any], output_file: Optional[str] = None, backup: bool = True) -> Dict[str, Any]:
        """
        Main processing method that maintains the same interface as the original god class.

        This method orchestrates the entire data processing pipeline while maintaining
        the same input/output behavior as the original implementation.
        """
        logger.info("Starting data processing pipeline")

        parsed_data = self.parse_input_data(input_data)
        if not parsed_data:
            logger.warning("No valid data to process")
            return {
                'success': False,
                'processed_count': 0,
                'errors': self.errors
            }

        processed_data = self.validate_and_process_data(parsed_data)
        if not processed_data:
            logger.warning("No data passed validation")
            return {
                'success': False,
                'processed_count': 0,
                'errors': self.errors
            }

        self.processed_data = processed_data

        database_saved = self.save_processed_data(processed_data)

        if output_file:
            self.save_to_file(output_file, processed_data)

        if backup:
            self.backup_data(processed_data)

        report = self.generate_report(processed_data)

        logger.info(f"Data processing completed: {len(processed_data)} records processed")

        return {
            'success': True,
            'processed_count': len(processed_data),
            'report': report,
            'errors': self.errors
        }

    def cleanup(self):
        """Clean up resources and temporary files."""
        try:
            self.file_service.cleanup_temp_files()
            self.database_service.close_connection()
            self.auth_service.close_connection()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.cleanup()