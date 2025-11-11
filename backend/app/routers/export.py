"""Export endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from uuid import uuid4
from app.services.formatter import DocumentFormatter

router = APIRouter()


@router.get("/{analysis_id}/pdf")
async def export_pdf(analysis_id: str):
    """
    Export resume as PDF.

    Args:
        analysis_id: Analysis ID

    Returns:
        PDF file
    """
    from app.routers.analyze import analyses_db
    from app.routers.upload import uploads_db

    # Get analysis
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = analyses_db[analysis_id]

    # Get resume
    resume_id = str(analysis.resume_id)
    if resume_id not in uploads_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = uploads_db[resume_id]

    if not resume.content:
        raise HTTPException(status_code=400, detail="Resume content not available")

    try:
        # Generate PDF
        formatter = DocumentFormatter()
        output_dir = Path("./exports")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / f"{uuid4()}.pdf"
        pdf_path = await formatter.generate_pdf(resume.content, str(output_path))

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"resume_refined_{analysis_id[:8]}.pdf",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/{analysis_id}/docx")
async def export_docx(analysis_id: str):
    """
    Export resume as DOCX.

    Args:
        analysis_id: Analysis ID

    Returns:
        DOCX file
    """
    from app.routers.analyze import analyses_db
    from app.routers.upload import uploads_db

    # Get analysis
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = analyses_db[analysis_id]

    # Get resume
    resume_id = str(analysis.resume_id)
    if resume_id not in uploads_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = uploads_db[resume_id]

    if not resume.content:
        raise HTTPException(status_code=400, detail="Resume content not available")

    try:
        # Generate DOCX
        formatter = DocumentFormatter()
        output_dir = Path("./exports")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / f"{uuid4()}.docx"
        docx_path = await formatter.generate_docx(resume.content, str(output_path))

        return FileResponse(
            docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"resume_refined_{analysis_id[:8]}.docx",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX generation failed: {str(e)}")
