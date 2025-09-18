import pytest
import sys
import os
import sqlite3
from unittest.mock import Mock, patch

# Add the after directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'after'))

from after.database_service import DatabaseService
from after.config import DatabaseConfig


class TestDatabaseService:
    """Test cases for DatabaseService class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Use proper DatabaseConfig structure
        self.config = DatabaseConfig(
            driver="SQLite",
            server=":memory:",
            database="test",
            username="test",
            password="test"
        )
        self.db_service = DatabaseService(self.config)

    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are prevented."""
        # Create a test table
        with sqlite3.connect(':memory:') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE users (
                    id TEXT,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    created_date TEXT,
                    email_valid INTEGER,
                    phone_valid INTEGER
                )
            ''')
            
            # Mock the database service connection
            with patch.object(self.db_service, '_get_connection', return_value=conn):
                # Test data with potential SQL injection
                malicious_data = [{
                    'id': "1'; DROP TABLE users; --",
                    'name': "Test User",
                    'email': "test@example.com",
                    'phone': "1234567890",
                    'created_date': "2023-01-01",
                    'email_valid': True,
                    'phone_valid': True
                }]
                
                # This should not cause SQL injection due to parameterized queries
                result = self.db_service.save_user_data(malicious_data)
                
                # Verify the table still exists and contains the data
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                
                # The injection attempt should be treated as literal data
                assert count == 1, "SQL injection prevented - table should still exist with data"
                
                # Verify the malicious string was stored as literal data
                cursor.execute("SELECT id FROM users WHERE id = ?", ("1'; DROP TABLE users; --",))
                stored_id = cursor.fetchone()
                assert stored_id is not None, "Malicious string should be stored as literal data"

    def test_save_user_data_success(self):
        """Test successful user data saving."""
        with sqlite3.connect(':memory:') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE users (
                    id TEXT,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    created_date TEXT,
                    email_valid INTEGER,
                    phone_valid INTEGER
                )
            ''')
            
            with patch.object(self.db_service, '_get_connection', return_value=conn):
                test_data = [{
                    'id': "1",
                    'name': "John Doe",
                    'email': "john@example.com",
                    'phone': "1234567890",
                    'created_date': "2023-01-01",
                    'email_valid': True,
                    'phone_valid': True
                }]
                
                result = self.db_service.save_user_data(test_data)
                assert result is True
                
                # Verify data was saved
                cursor.execute("SELECT * FROM users")
                rows = cursor.fetchall()
                assert len(rows) == 1

    def test_save_user_data_empty_list(self):
        """Test handling of empty data list."""
        result = self.db_service.save_user_data([])
        assert result is True  # Empty list should be handled gracefully

    def test_get_user_by_id_with_injection_attempt(self):
        """Test user retrieval with SQL injection attempt."""
        with sqlite3.connect(':memory:') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE users (
                    id TEXT,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    created_date TEXT,
                    email_valid INTEGER,
                    phone_valid INTEGER
                )
            ''')
            
            # Insert test data
            cursor.execute('''
                INSERT INTO users (id, name, email, phone, created_date, email_valid, phone_valid)
                VALUES ('1', 'John Doe', 'john@example.com', '1234567890', '2023-01-01', 1, 1)
            ''')
            
            with patch.object(self.db_service, '_get_connection', return_value=conn):
                # Attempt SQL injection
                malicious_id = "1' OR '1'='1"
                user = self.db_service.get_user_by_id(malicious_id)
                
                # Should return None or handle injection safely
                # The exact behavior depends on implementation, but should not expose all data
                assert user is None or (isinstance(user, dict) and user.get('id') == malicious_id)

    def test_database_connection_error_handling(self):
        """Test handling of database connection errors."""
        # Create a service with invalid connection string
        invalid_config = DatabaseConfig(
            driver="Invalid Driver",
            server="invalid_server",
            database="invalid_db",
            username="invalid_user",
            password="invalid_pass"
        )
        invalid_db_service = DatabaseService(invalid_config)
        
        test_data = [{'id': '1', 'name': 'Test'}]
        
        # Should handle connection error gracefully
        result = invalid_db_service.save_user_data(test_data)
        assert result is False

    def teardown_method(self):
        """Clean up after each test method."""
        if hasattr(self.db_service, 'connection') and self.db_service.connection:
            self.db_service.connection.close()