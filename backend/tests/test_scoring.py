"""Tests for resume scoring service."""

import pytest
from app.services.scoring import ResumeScorer
from app.models.resume import ResumeContent, ContactInfo, Experience, Education, Skill
from app.models.analysis import GrammarIssue, ATSSuggestion


def test_calculate_grammar_score_no_issues():
    """Test grammar score with no issues."""
    score = ResumeScorer.calculate_grammar_score(1000, [])
    assert score == 100.0


def test_calculate_grammar_score_with_issues():
    """Test grammar score with issues."""
    issues = [
        GrammarIssue(text="test", message="error", suggestions=[]),
        GrammarIssue(text="test", message="error", suggestions=[]),
    ]

    score = ResumeScorer.calculate_grammar_score(1000, issues)

    # Should be 100 - (2 * 2.0) = 96.0
    assert score == 96.0


def test_calculate_grammar_score_minimum_floor():
    """Test grammar score minimum floor."""
    # Create many issues
    issues = [GrammarIssue(text="test", message="error", suggestions=[])] * 50

    score = ResumeScorer.calculate_grammar_score(1000, issues)

    # Should not go below minimum
    assert score >= ResumeScorer.MIN_GRAMMAR_SCORE


def test_calculate_content_score_minimal_resume():
    """Test content score with minimal resume."""
    content = ResumeContent(raw_text="test")

    score = ResumeScorer.calculate_content_score(content)

    # Should be low but not zero
    assert 0 <= score < 50


def test_calculate_content_score_complete_resume():
    """Test content score with complete resume."""
    content = ResumeContent(
        contact_info=ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone="555-1234",
            linkedin="linkedin.com/in/johndoe"
        ),
        summary="A" * 200,  # Good length summary
        experience=[
            Experience(company="Company1", position="Developer", bullets=[]),
            Experience(company="Company2", position="Senior Developer", bullets=[]),
            Experience(company="Company3", position="Lead Developer", bullets=[]),
        ],
        education=[
            Education(institution="University", degree="BS Computer Science", achievements=[])
        ],
        skills=[
            Skill(category="Technical", skills=["Python", "JavaScript", "React", "Docker",
                                                 "AWS", "SQL", "Git", "Linux", "TypeScript",
                                                 "Node.js", "PostgreSQL", "MongoDB", "Redis",
                                                 "Kubernetes", "CI/CD"])
        ],
        raw_text="test",
        sections={}
    )

    score = ResumeScorer.calculate_content_score(content)

    # Should be high
    assert score >= 85


def test_calculate_ats_score_no_suggestions():
    """Test ATS score with no suggestions."""
    content = ResumeContent(
        contact_info=ContactInfo(email="test@example.com"),
        raw_text="test",
        sections={'experience': {}, 'education': {}, 'skills': {}}
    )

    score = ResumeScorer.calculate_ats_score(content, [])

    assert score == 100.0


def test_calculate_ats_score_with_suggestions():
    """Test ATS score with suggestions."""
    content = ResumeContent(
        contact_info=ContactInfo(email="test@example.com"),
        raw_text="test",
        sections={'experience': {}, 'education': {}}  # Missing skills
    )

    suggestions = [
        ATSSuggestion(category="format", message="test", importance="high"),
        ATSSuggestion(category="keywords", message="test", importance="medium"),
    ]

    score = ResumeScorer.calculate_ats_score(content, suggestions)

    # Should be 100 - 10 (high) - 5 (medium) - 15 (missing section) = 70
    assert score == 70.0


def test_calculate_ats_score_missing_sections():
    """Test ATS score with missing required sections."""
    content = ResumeContent(
        contact_info=ContactInfo(email="test@example.com"),
        raw_text="test",
        sections={}  # All sections missing
    )

    score = ResumeScorer.calculate_ats_score(content, [])

    # Should deduct for missing sections
    assert score < 60  # 100 - 3*15 = 55


def test_calculate_overall_score():
    """Test overall score calculation."""
    grammar = 90.0
    ats = 85.0
    content = 80.0

    overall = ResumeScorer.calculate_overall_score(grammar, ats, content)

    # Weighted average
    expected = (90 * 0.30) + (85 * 0.35) + (80 * 0.35)
    assert overall == pytest.approx(expected, 0.1)


def test_get_score_rating():
    """Test score rating conversion."""
    assert ResumeScorer.get_score_rating(95) == "Excellent"
    assert ResumeScorer.get_score_rating(85) == "Very Good"
    assert ResumeScorer.get_score_rating(75) == "Good"
    assert ResumeScorer.get_score_rating(65) == "Fair"
    assert ResumeScorer.get_score_rating(55) == "Needs Improvement"
    assert ResumeScorer.get_score_rating(45) == "Poor"


def test_scoring_weights_sum_to_one():
    """Test that scoring weights sum to 1.0."""
    total = (ResumeScorer.GRAMMAR_WEIGHT +
             ResumeScorer.ATS_WEIGHT +
             ResumeScorer.CONTENT_WEIGHT)

    assert total == pytest.approx(1.0, 0.001)
