"""Tests for grammar checker service."""

import pytest
from app.services.grammar_checker import GrammarChecker
from app.models.analysis import GrammarIssue


@pytest.mark.asyncio
async def test_check_grammar_empty_text():
    """Test grammar check with empty text."""
    issues = await GrammarChecker.check_grammar("")
    assert issues == []


@pytest.mark.asyncio
async def test_check_grammar_correct_text():
    """Test grammar check with correct text."""
    text = "This is a well-written sentence with no errors."
    issues = await GrammarChecker.check_grammar(text)

    # Should have 0 or very few issues
    assert isinstance(issues, list)
    assert len(issues) < 3  # Allow for minor suggestions


@pytest.mark.asyncio
async def test_check_grammar_with_errors():
    """Test grammar check detects errors."""
    text = "This are a sentence with grammer errors."
    issues = await GrammarChecker.check_grammar(text)

    assert isinstance(issues, list)
    assert len(issues) > 0  # Should detect errors

    # Check issue structure
    if issues:
        issue = issues[0]
        assert isinstance(issue, GrammarIssue)
        assert hasattr(issue, 'text')
        assert hasattr(issue, 'message')
        assert hasattr(issue, 'suggestions')


@pytest.mark.asyncio
async def test_check_grammar_length_limit():
    """Test that long text is truncated."""
    # Create text longer than MAX_TEXT_LENGTH
    long_text = "A" * (GrammarChecker.MAX_TEXT_LENGTH + 1000)

    issues = await GrammarChecker.check_grammar(long_text)

    # Should not crash, returns list
    assert isinstance(issues, list)


@pytest.mark.asyncio
async def test_check_grammar_max_issues_limit():
    """Test that max issues limit is respected."""
    # Text with many potential issues
    text = "this are wrong. that are incorrect. these is bad. " * 20

    issues = await GrammarChecker.check_grammar(text, max_issues=5)

    # Should not exceed max_issues
    assert len(issues) <= 5


@pytest.mark.asyncio
async def test_check_grammar_by_section():
    """Test section-specific grammar checking."""
    text = "Software engineer with experience."
    section = "summary"

    issues = await GrammarChecker.check_grammar_by_section(text, section)

    assert isinstance(issues, list)
    # Category should include section name if issues found
    if issues:
        assert section in issues[0].category


def test_grammar_checker_config():
    """Test grammar checker configuration."""
    assert GrammarChecker.MAX_TEXT_LENGTH > 0
    assert isinstance(GrammarChecker.IGNORED_CATEGORIES, set)
    assert len(GrammarChecker.IGNORED_CATEGORIES) > 0
