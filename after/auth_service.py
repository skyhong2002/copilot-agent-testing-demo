import logging
from typing import Optional
from .config import LDAPConfig
from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)

class AuthenticationService:
    """Handles user authentication operations."""

    def __init__(self, ldap_config: LDAPConfig, admin_password: str):
        self.ldap_config = ldap_config
        self.admin_password = admin_password
        self._ldap_conn = None

    def _connect_ldap(self) -> bool:
        """Establish LDAP connection."""
        try:
            import ldap
            self._ldap_conn = ldap.initialize(self.ldap_config.server)
            self._ldap_conn.simple_bind_s(self.ldap_config.username, self.ldap_config.password)
            return True
        except ImportError:
            logger.warning("LDAP module not available")
            return False
        except Exception as e:
            logger.error(f"LDAP connection failed: {str(e)}")
            raise AuthenticationError(f"LDAP connection failed: {str(e)}")

    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user against LDAP or admin credentials."""
        if not username or not password:
            return False

        if username == "admin" and password == self.admin_password:
            logger.info("Admin user authenticated")
            return True

        if not self._connect_ldap():
            logger.warning("LDAP authentication unavailable, falling back to admin only")
            return False

        try:
            import ldap
            search_filter = f"(uid={username})"
            results = self._ldap_conn.search_s(
                self.ldap_config.base_dn,
                ldap.SCOPE_SUBTREE,
                search_filter
            )

            if results:
                user_dn = results[0][0]
                self._ldap_conn.simple_bind_s(user_dn, password)
                logger.info(f"User {username} authenticated via LDAP")
                return True
        except Exception as e:
            logger.error(f"LDAP authentication failed for {username}: {str(e)}")

        return False

    def close_connection(self):
        """Close LDAP connection."""
        if self._ldap_conn:
            try:
                self._ldap_conn.unbind()
            except Exception as e:
                logger.error(f"Error closing LDAP connection: {str(e)}")
            finally:
                self._ldap_conn = None