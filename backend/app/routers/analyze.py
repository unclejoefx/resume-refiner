"""Analysis endpoints with grammar checking and scoring."""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from app.models.analysis import Analysis, GrammarIssue, ATSSuggestion, ContentSuggestion
from app.services.grammar_checker import GrammarChecker
from app.services.ats_optimizer import ATSOptimizer
from app.services.claude_service import ClaudeService
from app.services.scoring import ResumeScorer

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for demonstration
# TODO: Replace with database
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
    Perform full resume analysis with grammar check and scoring.

    Args:
        request: Analysis request with resume ID and optional job description

    Returns:
        Complete analysis results
    """
    logger.info(f"Starting analysis for resume ID: {request.resume_id}")

    # Import here to avoid circular import
    from app.routers.upload import uploads_db

    # Get resume
    if request.resume_id not in uploads_db:
        logger.error(f"Resume not found: {request.resume_id}")
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = uploads_db[request.resume_id]

    if not resume.content:
        logger.error(f"Resume content not parsed: {request.resume_id}")
        raise HTTPException(status_code=400, detail="Resume content not parsed")

    try:
        # Initialize services
        grammar_checker = GrammarChecker()
        ats_optimizer = ATSOptimizer()
        claude_service = ClaudeService()

        logger.info("Running grammar check...")
        # Run grammar check
        grammar_issues = await grammar_checker.check_grammar(resume.content.raw_text)

        logger.info("Running ATS analysis...")
        # Run ATS analysis
        ats_score_raw, ats_suggestions = await ats_optimizer.analyze_ats_compatibility(
            resume.content, request.job_description
        )

        logger.info("Running content analysis...")
        # Run AI content analysis (placeholder for now)
        content_suggestions = await claude_service.analyze_content(resume.content)

        # Calculate scores using scoring service
        logger.info("Calculating scores...")
        grammar_score = ResumeScorer.calculate_grammar_score(
            len(resume.content.raw_text),
            grammar_issues
        )

        content_score = ResumeScorer.calculate_content_score(resume.content)

        ats_score = ResumeScorer.calculate_ats_score(
            resume.content,
            ats_suggestions
        )

        overall_score = ResumeScorer.calculate_overall_score(
            grammar_score,
            ats_score,
            content_score
        )

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

        logger.info(f"Analysis completed for {request.resume_id}: "
                   f"overall={overall_score:.1f}, grammar={grammar_score:.1f}, "
                   f"ats={ats_score:.1f}, content={content_score:.1f}")

        return analysis

    except Exception as e:
        logger.exception(f"Analysis failed for {request.resume_id}")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


@router.get("/{analysis_id}", response_model=Analysis)
async def get_analysis(analysis_id: str):
    """
    Get analysis results by ID.

    Args:
        analysis_id: Analysis ID

    Returns:
        Analysis results
    """
    logger.info(f"Retrieving analysis: {analysis_id}")

    if analysis_id not in analyses_db:
        logger.error(f"Analysis not found: {analysis_id}")
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
    logger.info(f"Grammar check requested for {len(request.text)} characters")

    try:
        grammar_checker = GrammarChecker()
        issues = await grammar_checker.check_grammar(request.text)

        logger.info(f"Grammar check found {len(issues)} issues")
        return issues

    except Exception as e:
        logger.exception("Grammar check failed")
        raise HTTPException(status_code=500, detail="Grammar check failed")


@router.post("/ats", response_model=dict)
async def check_ats(request: ATSCheckRequest):
    """
    Run ATS optimization check.

    Args:
        request: ATS check request

    Returns:
        ATS score and suggestions
    """
    logger.info(f"ATS check requested for resume: {request.resume_id}")

    from app.routers.upload import uploads_db

    if request.resume_id not in uploads_db:
        logger.error(f"Resume not found: {request.resume_id}")
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = uploads_db[request.resume_id]

    if not resume.content:
        logger.error(f"Resume content not parsed: {request.resume_id}")
        raise HTTPException(status_code=400, detail="Resume content not parsed")

    try:
        ats_optimizer = ATSOptimizer()
        score, suggestions = await ats_optimizer.analyze_ats_compatibility(
            resume.content, request.job_description
        )

        logger.info(f"ATS check completed: score={score}, suggestions={len(suggestions)}")
        return {"score": score, "suggestions": suggestions}

    except Exception as e:
        logger.exception("ATS check failed")
        raise HTTPException(status_code=500, detail="ATS check failed")
