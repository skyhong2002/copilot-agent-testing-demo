import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the after directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'after'))

from after.auth_service import AuthenticationService
from after.config import LDAPConfig


class TestAuthenticationService:
    """Test cases for AuthenticationService class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.ldap_config = LDAPConfig(
            server="ldap://test-server:389",
            username="testadmin",
            password="testpass",
            base_dn="dc=test,dc=com"
        )
        self.admin_password = "test_admin_pass"
        self.auth_service = AuthenticationService(self.ldap_config, self.admin_password)

    def test_authenticate_admin_user_success(self):
        """Test successful admin authentication."""
        result = self.auth_service.authenticate_user("admin", self.admin_password)
        assert result is True

    def test_authenticate_admin_user_failure(self):
        """Test failed admin authentication with wrong password."""
        result = self.auth_service.authenticate_user("admin", "wrong_password")
        assert result is False

    @patch('ldap.initialize')
    def test_authenticate_ldap_user_success(self, mock_ldap_init):
        """Test successful LDAP user authentication."""
        # Mock LDAP connection and operations
        mock_conn = Mock()
        mock_ldap_init.return_value = mock_conn
        
        # Mock successful search result
        mock_conn.search_s.return_value = [
            ("cn=testuser,ou=users,dc=test,dc=com", {"cn": ["testuser"]})
        ]
        
        # Mock successful bind
        mock_conn.simple_bind_s.return_value = None
        
        result = self.auth_service.authenticate_user("testuser", "userpass")
        assert result is True

    @patch('ldap.initialize')
    def test_authenticate_ldap_user_not_found(self, mock_ldap_init):
        """Test LDAP authentication when user is not found."""
        # Mock LDAP connection
        mock_conn = Mock()
        mock_ldap_init.return_value = mock_conn
        
        # Mock empty search result (user not found)
        mock_conn.search_s.return_value = []
        
        result = self.auth_service.authenticate_user("nonexistentuser", "password")
        assert result is False

    @patch('ldap.initialize')
    def test_authenticate_ldap_connection_failure(self, mock_ldap_init):
        """Test LDAP authentication when connection fails."""
        # Mock LDAP connection failure
        mock_ldap_init.side_effect = Exception("LDAP connection failed")
        
        result = self.auth_service.authenticate_user("testuser", "password")
        assert result is False

    @patch('ldap.initialize')
    def test_authenticate_ldap_bind_failure(self, mock_ldap_init):
        """Test LDAP authentication when bind fails (wrong password)."""
        # Mock LDAP connection
        mock_conn = Mock()
        mock_ldap_init.return_value = mock_conn
        
        # Mock successful search result
        mock_conn.search_s.return_value = [
            ("cn=testuser,ou=users,dc=test,dc=com", {"cn": ["testuser"]})
        ]
        
        # Mock failed bind (wrong password)
        mock_conn.simple_bind_s.side_effect = Exception("Invalid credentials")
        
        result = self.auth_service.authenticate_user("testuser", "wrongpass")
        assert result is False

    def test_authenticate_empty_credentials(self):
        """Test authentication with empty credentials."""
        result = self.auth_service.authenticate_user("", "")
        assert result is False
        
        result = self.auth_service.authenticate_user("user", "")
        assert result is False
        
        result = self.auth_service.authenticate_user("", "pass")
        assert result is False

    def test_authenticate_none_credentials(self):
        """Test authentication with None credentials."""
        result = self.auth_service.authenticate_user(None, None)
        assert result is False
        
        result = self.auth_service.authenticate_user("user", None)
        assert result is False
        
        result = self.auth_service.authenticate_user(None, "pass")
        assert result is False

    @patch('ldap.initialize')
    def test_ldap_injection_attempt(self, mock_ldap_init):
        """Test that LDAP injection attempts are handled safely."""
        # Mock LDAP connection
        mock_conn = Mock()
        mock_ldap_init.return_value = mock_conn
        
        # Mock empty search result for injection attempt
        mock_conn.search_s.return_value = []
        
        # Attempt LDAP injection
        malicious_username = "admin)(|(password=*))"
        result = self.auth_service.authenticate_user(malicious_username, "password")
        
        # Should fail safely without exposing data
        assert result is False
        
        # Verify that search was called (implementation should escape the input)
        mock_conn.search_s.assert_called()