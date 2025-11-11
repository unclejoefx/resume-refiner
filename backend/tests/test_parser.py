"""Tests for document parser."""

import pytest
from app.services.parser import DocumentParser
from app.models.resume import ResumeContent


def test_parse_unsupported_file_type():
    """Test that unsupported file types raise ValueError."""
    with pytest.raises(ValueError):
        DocumentParser.parse("test.txt", "txt")


def test_parse_pdf_returns_resume_content():
    """Test that PDF parsing returns ResumeContent object."""
    # This is a placeholder test
    # TODO: Add actual test with sample PDF file
    result = DocumentParser.parse_pdf("dummy.pdf")
    assert isinstance(result, ResumeContent)


def test_parse_docx_returns_resume_content():
    """Test that DOCX parsing returns ResumeContent object."""
    # This is a placeholder test
    # TODO: Add actual test with sample DOCX file
    result = DocumentParser.parse_docx("dummy.docx")
    assert isinstance(result, ResumeContent)
