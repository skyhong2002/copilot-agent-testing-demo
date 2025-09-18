import logging
from typing import List, Dict, Any, Optional
from .config import DatabaseConfig
from .exceptions import DatabaseError

logger = logging.getLogger(__name__)

class DatabaseService:
    """Handles database operations with proper parameterized queries."""

    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self._connection = None

    def _connect(self) -> bool:
        """Establish database connection."""
        try:
            import pyodbc
            self._connection = pyodbc.connect(self.db_config.connection_string)
            return True
        except ImportError:
            logger.warning("pyodbc module not available")
            return False
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise DatabaseError(f"Database connection failed: {str(e)}")

    def save_user_data(self, data: List[Dict[str, Any]]) -> bool:
        """Save user data using parameterized queries to prevent SQL injection."""
        if not data:
            return True

        if not self._connect():
            logger.warning("Database not available, skipping save operation")
            return False

        try:
            cursor = self._connection.cursor()

            query = """
            INSERT INTO users (id, name, email, phone, created_date, email_valid, phone_valid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            for record in data:
                cursor.execute(query, (
                    record.get('id', ''),
                    record.get('name', ''),
                    record.get('email', ''),
                    record.get('phone', ''),
                    record.get('created_date', ''),
                    record.get('email_valid', False),
                    record.get('phone_valid', False)
                ))

            self._connection.commit()
            logger.info(f"Successfully saved {len(data)} records to database")
            return True

        except Exception as e:
            logger.error(f"Database save error: {str(e)}")
            if self._connection:
                self._connection.rollback()
            raise DatabaseError(f"Database save error: {str(e)}")

    def close_connection(self):
        """Close database connection."""
        if self._connection:
            try:
                self._connection.close()
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")
            finally:
                self._connection = None