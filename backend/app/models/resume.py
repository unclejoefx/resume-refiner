"""Resume data models."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ContactInfo(BaseModel):
    """Contact information model."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None


class Experience(BaseModel):
    """Work experience model."""

    company: str
    position: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education model."""

    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class Skill(BaseModel):
    """Skill model."""

    category: Optional[str] = None
    skills: List[str] = Field(default_factory=list)


class ResumeContent(BaseModel):
    """Parsed resume content model."""

    contact_info: Optional[ContactInfo] = None
    summary: Optional[str] = None
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    raw_text: str = ""
    sections: Dict[str, Any] = Field(default_factory=dict)


class ResumeUpload(BaseModel):
    """Resume upload model."""

    id: UUID = Field(default_factory=uuid4)
    user_id: Optional[str] = None
    filename: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    file_type: str  # "pdf" or "docx"
    file_path: str
    content: Optional[ResumeContent] = None

    class Config:
        """Pydantic config."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
