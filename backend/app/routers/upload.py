"""Upload endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import UUID
from datetime import datetime
from app.models.resume import ResumeUpload
from app.utils.file_handler import save_upload_file
from app.services.parser import DocumentParser

router = APIRouter()

# In-memory storage for demonstration (replace with database in production)
uploads_db = {}


@router.post("/", response_model=ResumeUpload)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX).

    Args:
        file: Uploaded resume file

    Returns:
        ResumeUpload object with upload details
    """
    try:
        # Save file
        file_path, file_type = await save_upload_file(file)

        # Parse document
        try:
            content = DocumentParser.parse(file_path, file_type)
        except Exception as e:
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

        return upload

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


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
