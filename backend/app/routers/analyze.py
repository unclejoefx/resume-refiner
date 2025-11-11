"""Analysis endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from app.models.analysis import Analysis, GrammarIssue, ATSSuggestion, ContentSuggestion
from app.services.grammar_checker import GrammarChecker
from app.services.ats_optimizer import ATSOptimizer
from app.services.claude_service import ClaudeService

router = APIRouter()

# In-memory storage for demonstration
analyses_db = {}


class AnalyzeRequest(BaseModel):
    """Request model for analysis."""

    resume_id: str
    job_description: Optional[str] = ""


class GrammarCheckRequest(BaseModel):
    """Request model for grammar check."""

    text: str


class ATSCheckRequest(BaseModel):
    """Request model for ATS check."""

    resume_id: str
    job_description: Optional[str] = ""


@router.post("/", response_model=Analysis)
async def analyze_resume(request: AnalyzeRequest):
    """
    Perform full resume analysis.

    Args:
        request: Analysis request with resume ID and optional job description

    Returns:
        Complete analysis results
    """
    # Import here to avoid circular import
    from app.routers.upload import uploads_db

    # Get resume
    if request.resume_id not in uploads_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = uploads_db[request.resume_id]

    if not resume.content:
        raise HTTPException(status_code=400, detail="Resume content not parsed")

    try:
        # Initialize services
        grammar_checker = GrammarChecker()
        ats_optimizer = ATSOptimizer()
        claude_service = ClaudeService()

        # Run all analyses
        grammar_issues = await grammar_checker.check_grammar(resume.content.raw_text)
        ats_score, ats_suggestions = await ats_optimizer.analyze_ats_compatibility(
            resume.content, request.job_description
        )
        content_suggestions = await claude_service.analyze_content(resume.content)

        # Calculate scores
        grammar_score = max(0, 100 - len(grammar_issues) * 5)
        content_score = 85.0  # Placeholder

        overall_score = (grammar_score + ats_score + content_score) / 3

        # Create analysis record
        analysis = Analysis(
            resume_id=resume.id,
            overall_score=overall_score,
            grammar_score=grammar_score,
            ats_score=ats_score,
            content_score=content_score,
            grammar_issues=grammar_issues,
            ats_suggestions=ats_suggestions,
            content_suggestions=content_suggestions,
        )

        # Store analysis
        analyses_db[str(analysis.id)] = analysis

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/{analysis_id}", response_model=Analysis)
async def get_analysis(analysis_id: str):
    """
    Get analysis results by ID.

    Args:
        analysis_id: Analysis ID

    Returns:
        Analysis results
    """
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analyses_db[analysis_id]


@router.post("/grammar", response_model=List[GrammarIssue])
async def check_grammar(request: GrammarCheckRequest):
    """
    Run grammar check on text.

    Args:
        request: Grammar check request

    Returns:
        List of grammar issues
    """
    grammar_checker = GrammarChecker()
    issues = await grammar_checker.check_grammar(request.text)
    return issues


@router.post("/ats", response_model=dict)
async def check_ats(request: ATSCheckRequest):
    """
    Run ATS optimization check.

    Args:
        request: ATS check request

    Returns:
        ATS score and suggestions
    """
    from app.routers.upload import uploads_db

    if request.resume_id not in uploads_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = uploads_db[request.resume_id]

    if not resume.content:
        raise HTTPException(status_code=400, detail="Resume content not parsed")

    ats_optimizer = ATSOptimizer()
    score, suggestions = await ats_optimizer.analyze_ats_compatibility(
        resume.content, request.job_description
    )

    return {"score": score, "suggestions": suggestions}
