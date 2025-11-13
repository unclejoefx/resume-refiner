"""File cleanup utilities for managing uploaded files."""

import logging
from pathlib import Path
from datetime import datetime, timedelta
from app.config import settings
from app.services.parser_config import ParserConfig

logger = logging.getLogger(__name__)


async def cleanup_old_files():
    """
    Remove uploaded files older than retention period.

    This function should be called periodically as a background task
    to prevent disk space exhaustion and ensure PII data is not retained.
    """
    try:
        upload_dir = Path(settings.UPLOAD_DIR)

        if not upload_dir.exists():
            logger.debug(f"Upload directory does not exist: {upload_dir}")
            return

        cutoff_time = datetime.now() - timedelta(hours=ParserConfig.FILE_RETENTION_HOURS)
        cutoff_timestamp = cutoff_time.timestamp()

        deleted_count = 0
        error_count = 0

        for file_path in upload_dir.glob("*"):
            if not file_path.is_file():
                continue

            try:
                # Check file age
                file_mtime = file_path.stat().st_mtime

                if file_mtime < cutoff_timestamp:
                    file_path.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old file: {file_path.name}")

            except PermissionError:
                logger.warning(f"Permission denied deleting file: {file_path}")
                error_count += 1
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")
                error_count += 1

        if deleted_count > 0 or error_count > 0:
            logger.info(f"File cleanup completed: {deleted_count} deleted, {error_count} errors")

    except Exception as e:
        logger.exception(f"Error during file cleanup: {e}")
