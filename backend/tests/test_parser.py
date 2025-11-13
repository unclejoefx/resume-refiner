"""Tests for document parser with security improvements."""

import pytest
from app.services.parser import DocumentParser
from app.services.parser_config import ParserConfig
from app.models.resume import ResumeContent, ContactInfo


def test_parse_unsupported_file_type():
    """Test that unsupported file types raise ValueError."""
    with pytest.raises(ValueError):
        DocumentParser.parse("test.txt", "txt")


def test_parse_pdf_returns_resume_content():
    """Test that PDF parsing returns ResumeContent object."""
    # This will fail gracefully with non-existent file
    result = DocumentParser.parse_pdf("dummy.pdf")
    assert isinstance(result, ResumeContent)
    # Should contain error message
    assert "File not found" in result.raw_text or "Unable to process" in result.raw_text


def test_parse_docx_returns_resume_content():
    """Test that DOCX parsing returns ResumeContent object."""
    # This will fail gracefully with non-existent file
    result = DocumentParser.parse_docx("dummy.docx")
    assert isinstance(result, ResumeContent)
    # Should contain error message
    assert "File not found" in result.raw_text or "Unable to process" in result.raw_text


def test_extract_contact_info_with_email():
    """Test contact info extraction with email."""
    text = "John Doe\nEmail: john.doe@example.com\nPhone: 555-123-4567"
    contact = DocumentParser._extract_contact_info(text)

    assert contact is not None
    assert contact.email == "john.doe@example.com"
    assert contact.name == "John Doe"
    assert "5551234567" in contact.phone  # Normalized


def test_extract_contact_info_with_linkedin():
    """Test contact info extraction with LinkedIn."""
    text = "Jane Smith\nlinkedin.com/in/janesmith\ntest@example.com"
    contact = DocumentParser._extract_contact_info(text)

    assert contact is not None
    assert "linkedin.com/in/janesmith" in contact.linkedin
    assert contact.email == "test@example.com"


def test_extract_summary():
    """Test summary extraction."""
    text = """
    John Doe

    Summary:
    Experienced software engineer with 5+ years of expertise in Python and web development.
    Passionate about building scalable applications.

    Experience:
    Some work history here
    """
    summary = DocumentParser._extract_summary(text)

    assert summary is not None
    assert "software engineer" in summary.lower()
    assert len(summary) >= ParserConfig.MIN_SUMMARY_LENGTH
    assert len(summary) <= ParserConfig.MAX_SUMMARY_LENGTH


def test_sanitize_text_removes_control_characters():
    """Test that text sanitization removes control characters."""
    text = "Hello\x00World\x01Test\nNewline\tTab"
    sanitized = DocumentParser._sanitize_text(text)

    assert '\x00' not in sanitized
    assert '\x01' not in sanitized
    assert '\n' in sanitized  # Newlines preserved
    assert '\t' in sanitized  # Tabs preserved


def test_normalize_phone():
    """Test phone number normalization."""
    assert DocumentParser._normalize_phone("(555) 123-4567") == "5551234567"
    assert DocumentParser._normalize_phone("+1-555-123-4567") == "+15551234567"
    assert DocumentParser._normalize_phone("555.123.4567") == "5551234567"
