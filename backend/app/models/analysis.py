"""Analysis data models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class GrammarIssue(BaseModel):
    """Grammar issue model."""

    text: str
    message: str
    suggestions: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    line: Optional[int] = None
    offset: Optional[int] = None


class ATSSuggestion(BaseModel):
    """ATS optimization suggestion model."""

    category: str  # e.g., "keywords", "formatting", "sections"
    message: str
    importance: str  # "high", "medium", "low"
    current_value: Optional[str] = None
    suggested_value: Optional[str] = None


class ContentSuggestion(BaseModel):
    """Content improvement suggestion model."""

    section: str  # e.g., "summary", "experience", "skills"
    original_text: str
    suggested_text: str
    explanation: str
    impact: str  # "high", "medium", "low"


class Analysis(BaseModel):
    """Resume analysis model."""

    id: UUID = Field(default_factory=uuid4)
    resume_id: UUID
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    overall_score: float = Field(ge=0, le=100)
    grammar_score: Optional[float] = Field(default=None, ge=0, le=100)
    ats_score: Optional[float] = Field(default=None, ge=0, le=100)
    content_score: Optional[float] = Field(default=None, ge=0, le=100)
    grammar_issues: List[GrammarIssue] = Field(default_factory=list)
    ats_suggestions: List[ATSSuggestion] = Field(default_factory=list)
    content_suggestions: List[ContentSuggestion] = Field(default_factory=list)
    formatting_issues: List[str] = Field(default_factory=list)

    class Config:
        """Pydantic config."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
