"""File handling utilities."""

import os
import shutil
from pathlib import Path
from uuid import uuid4
from typing import Tuple
from fastapi import UploadFile, HTTPException
from app.config import settings


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return Path(filename).suffix.lower()


def validate_file(file: UploadFile) -> Tuple[bool, str]:
    """
    Validate uploaded file.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file.filename:
        return False, "No filename provided"

    extension = get_file_extension(file.filename)

    if extension not in settings.ALLOWED_EXTENSIONS:
        return False, f"File type {extension} not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"

    return True, ""


async def save_upload_file(file: UploadFile) -> Tuple[str, str]:
    """
    Save uploaded file to disk.

    Returns:
        Tuple of (file_path, file_type)

    Raises:
        HTTPException: If file validation fails or save fails
    """
    # Validate file
    is_valid, error_message = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    extension = get_file_extension(file.filename)
    file_type = extension.lstrip(".")
    unique_filename = f"{uuid4()}{extension}"
    file_path = upload_dir / unique_filename

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    return str(file_path), file_type
