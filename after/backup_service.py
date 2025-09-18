import datetime
import logging
from typing import List, Dict, Any
from .config import BackupConfig, APIConfig
from .exceptions import BackupError

logger = logging.getLogger(__name__)

class BackupService:
    """Handles data backup operations."""

    def __init__(self, backup_config: BackupConfig, api_config: APIConfig):
        self.backup_urls = backup_config.urls
        self.api_key = api_config.api_key

    def backup_data(self, data: List[Dict[str, Any]]) -> bool:
        """Backup data to configured URLs."""
        if not data:
            logger.info("No data to backup")
            return True

        backup_payload = {
            'timestamp': datetime.datetime.now().isoformat(),
            'data': data,
            'api_key': self.api_key
        }

        success_count = 0
        errors = []

        for url in self.backup_urls:
            try:
                logger.info(f"Simulating backup to {url}")
                logger.info(f"Backup payload size: {len(data)} records")
                success_count += 1
            except Exception as e:
                error_msg = f"Backup failed for {url}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        if success_count == 0:
            raise BackupError(f"All backup operations failed: {'; '.join(errors)}")

        if errors:
            logger.warning(f"Some backups failed: {'; '.join(errors)}")

        logger.info(f"Backup completed: {success_count}/{len(self.backup_urls)} successful")
        return success_count > 0