"""Upload endpoints."""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from uuid import UUID
from datetime import datetime
from app.models.resume import ResumeUpload
from app.utils.file_handler import save_upload_file
from app.utils.file_cleanup import cleanup_old_files
from app.services.parser import DocumentParser

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for demonstration (replace with database in production)
# TODO: Replace with proper database implementation
uploads_db = {}


@router.post("/", response_model=ResumeUpload)
async def upload_resume(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a resume file (PDF or DOCX).

    Args:
        file: Uploaded resume file
        background_tasks: FastAPI background tasks

    Returns:
        ResumeUpload object with upload details
    """
    logger.info(f"Received upload request for file: {file.filename}")

    try:
        # Save file
        file_path, file_type = await save_upload_file(file)
        logger.info(f"File saved: {file_path}")

        # Parse document
        try:
            content = DocumentParser.parse(file_path, file_type)
            logger.info(f"Document parsed successfully: {file_path}")
        except Exception as e:
            logger.error(f"Parsing failed for {file_path}: {e}", exc_info=True)
            # Continue even if parsing fails
            content = None

        # Create upload record
        upload = ResumeUpload(
            filename=file.filename,
            file_type=file_type,
            file_path=file_path,
            content=content,
        )

        # Store in database
        uploads_db[str(upload.id)] = upload
        logger.info(f"Upload record created with ID: {upload.id}")

        # Schedule file cleanup as background task
        if background_tasks:
            background_tasks.add_task(cleanup_old_files)
            logger.debug("File cleanup task scheduled")

        return upload

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Upload failed for {file.filename}")
        raise HTTPException(status_code=500, detail="Upload failed. Please try again.")


@router.get("/{upload_id}", response_model=ResumeUpload)
async def get_upload(upload_id: str):
    """
    Get upload details by ID.

    Args:
        upload_id: Upload ID

    Returns:
        ResumeUpload object
    """
    if upload_id not in uploads_db:
        raise HTTPException(status_code=404, detail="Upload not found")

    return uploads_db[upload_id]
