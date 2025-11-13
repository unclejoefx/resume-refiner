"""Configuration for document parser."""

from typing import Dict, List


class ParserConfig:
    """Configuration constants for document parsing."""

    # Text extraction limits
    MAX_RAW_TEXT_LENGTH = 500000  # 500KB - Prevent memory exhaustion
    MAX_TEXT_FOR_CONTACT_EXTRACTION = 10000  # First 10KB usually contains contact info

    # Summary constraints
    MIN_SUMMARY_LENGTH = 50  # Minimum characters to consider valid summary
    MAX_SUMMARY_LENGTH = 1000  # Prevent excessive summary text

    # Experience constraints
    MAX_EXPERIENCE_DESCRIPTION_LENGTH = 500  # API response size limit
    MAX_EXPERIENCE_ENTRIES = 20  # Reasonable maximum number of jobs

    # Education constraints
    MAX_EDUCATION_INSTITUTION_LENGTH = 200  # Reasonable institution name length
    MAX_EDUCATION_ENTRIES = 10  # Reasonable maximum degrees

    # Skills constraints
    MAX_SKILLS_COUNT = 20  # UI display constraint
    MIN_SKILL_LENGTH = 2  # Minimum characters for valid skill

    # Regex timeout (seconds)
    REGEX_TIMEOUT = 2.0  # Prevent ReDoS attacks

    # Section headers for detection
    SECTION_HEADERS: Dict[str, List[str]] = {
        'experience': [
            'experience',
            'work experience',
            'employment',
            'work history',
            'professional experience',
            'employment history'
        ],
        'education': [
            'education',
            'academic background',
            'academic history',
            'educational background'
        ],
        'skills': [
            'skills',
            'technical skills',
            'core competencies',
            'competencies',
            'technical competencies'
        ],
        'summary': [
            'summary',
            'professional summary',
            'profile',
            'objective',
            'about me',
            'career objective'
        ],
    }

    # Regex patterns (compiled for performance)
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    LINKEDIN_PATTERN = r'linkedin\.com/in/[\w-]+'

    # Degree patterns for education extraction
    DEGREE_PATTERNS = [
        r"(Bachelor|Master|PhD|Ph\.D\.|B\.S\.|M\.S\.|B\.A\.|M\.A\.|MBA|BS|MS|BA|MA)[^\n]{0,100}",
        r"(University|College|Institute|School)[^\n]{0,100}"
    ]

    # File cleanup
    FILE_RETENTION_HOURS = 24  # Delete files after 24 hours
