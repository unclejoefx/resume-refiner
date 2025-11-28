"""Resume scoring service."""

import logging
from typing import List, Dict, Tuple
from app.models.resume import ResumeContent
from app.models.analysis import GrammarIssue, ATSSuggestion

logger = logging.getLogger(__name__)


class ResumeScorer:
    """Calculate resume scores based on various factors."""

    # Scoring weights
    GRAMMAR_WEIGHT = 0.30  # 30%
    ATS_WEIGHT = 0.35  # 35%
    CONTENT_WEIGHT = 0.35  # 35%

    # Grammar scoring parameters
    GRAMMAR_PENALTY_PER_ISSUE = 2.0  # Deduct 2 points per grammar issue
    MIN_GRAMMAR_SCORE = 40.0  # Minimum grammar score

    # Content scoring parameters
    MIN_SUMMARY_LENGTH = 50
    IDEAL_SUMMARY_LENGTH = 200
    MIN_EXPERIENCE_ENTRIES = 1
    IDEAL_EXPERIENCE_ENTRIES = 3
    MIN_EDUCATION_ENTRIES = 1
    MIN_SKILLS = 5
    IDEAL_SKILLS = 15

    @staticmethod
    def calculate_grammar_score(
        text_length: int,
        grammar_issues: List[GrammarIssue]
    ) -> float:
        """
        Calculate grammar score based on issues found.

        Args:
            text_length: Total length of text checked
            grammar_issues: List of grammar issues

        Returns:
            Grammar score (0-100)
        """
        if text_length == 0:
            logger.warning("Zero text length for grammar scoring")
            return 0.0

        # Start with perfect score
        score = 100.0

        # Deduct points for each issue
        num_issues = len(grammar_issues)
        penalty = num_issues * ResumeScorer.GRAMMAR_PENALTY_PER_ISSUE

        score -= penalty

        # Apply minimum floor
        score = max(score, ResumeScorer.MIN_GRAMMAR_SCORE)

        logger.info(f"Grammar score: {score:.1f} ({num_issues} issues, {text_length} chars)")
        return round(score, 1)

    @staticmethod
    def calculate_content_score(resume_content: ResumeContent) -> float:
        """
        Calculate content quality score based on resume structure.

        Args:
            resume_content: Parsed resume content

        Returns:
            Content score (0-100)
        """
        score = 0.0
        max_score = 100.0

        # Contact information (20 points)
        contact_points = 0
        if resume_content.contact_info:
            if resume_content.contact_info.name:
                contact_points += 5
            if resume_content.contact_info.email:
                contact_points += 5
            if resume_content.contact_info.phone:
                contact_points += 5
            if resume_content.contact_info.linkedin:
                contact_points += 5
        score += contact_points

        # Professional summary (15 points)
        summary_points = 0
        if resume_content.summary:
            summary_len = len(resume_content.summary)
            if summary_len >= ResumeScorer.MIN_SUMMARY_LENGTH:
                # Partial credit based on length
                if summary_len >= ResumeScorer.IDEAL_SUMMARY_LENGTH:
                    summary_points = 15
                else:
                    ratio = summary_len / ResumeScorer.IDEAL_SUMMARY_LENGTH
                    summary_points = 15 * ratio
        score += summary_points

        # Experience section (30 points)
        experience_points = 0
        num_experience = len(resume_content.experience)
        if num_experience >= ResumeScorer.MIN_EXPERIENCE_ENTRIES:
            if num_experience >= ResumeScorer.IDEAL_EXPERIENCE_ENTRIES:
                experience_points = 30
            else:
                ratio = num_experience / ResumeScorer.IDEAL_EXPERIENCE_ENTRIES
                experience_points = 30 * ratio
        score += experience_points

        # Education section (20 points)
        education_points = 0
        num_education = len(resume_content.education)
        if num_education >= ResumeScorer.MIN_EDUCATION_ENTRIES:
            education_points = 20
        score += education_points

        # Skills section (15 points)
        skills_points = 0
        total_skills = sum(len(skill.skills) for skill in resume_content.skills)
        if total_skills >= ResumeScorer.MIN_SKILLS:
            if total_skills >= ResumeScorer.IDEAL_SKILLS:
                skills_points = 15
            else:
                ratio = total_skills / ResumeScorer.IDEAL_SKILLS
                skills_points = 15 * ratio
        score += skills_points

        logger.info(f"Content score breakdown: contact={contact_points:.1f}, "
                   f"summary={summary_points:.1f}, experience={experience_points:.1f}, "
                   f"education={education_points:.1f}, skills={skills_points:.1f}")

        final_score = min(score, max_score)
        logger.info(f"Content score: {final_score:.1f}")
        return round(final_score, 1)

    @staticmethod
    def calculate_ats_score(
        resume_content: ResumeContent,
        ats_suggestions: List[ATSSuggestion]
    ) -> float:
        """
        Calculate ATS compatibility score.

        Args:
            resume_content: Parsed resume content
            ats_suggestions: List of ATS suggestions

        Returns:
            ATS score (0-100)
        """
        score = 100.0

        # Deduct points based on suggestion importance
        for suggestion in ats_suggestions:
            if suggestion.importance == "high":
                score -= 10
            elif suggestion.importance == "medium":
                score -= 5
            elif suggestion.importance == "low":
                score -= 2

        # Bonus points for good structure
        if resume_content.contact_info and resume_content.contact_info.email:
            score += 0  # Already at 100, just checking structure exists

        # Check for required sections
        sections = resume_content.sections
        required_sections = ['experience', 'education', 'skills']
        missing_sections = [s for s in required_sections if s not in sections]

        # Deduct for missing critical sections
        score -= len(missing_sections) * 15

        # Apply bounds
        score = max(0, min(100, score))

        logger.info(f"ATS score: {score:.1f} ({len(ats_suggestions)} suggestions, "
                   f"{len(missing_sections)} missing sections)")
        return round(score, 1)

    @staticmethod
    def calculate_overall_score(
        grammar_score: float,
        ats_score: float,
        content_score: float
    ) -> float:
        """
        Calculate weighted overall score.

        Args:
            grammar_score: Grammar score (0-100)
            ats_score: ATS score (0-100)
            content_score: Content score (0-100)

        Returns:
            Overall weighted score (0-100)
        """
        overall = (
            grammar_score * ResumeScorer.GRAMMAR_WEIGHT +
            ats_score * ResumeScorer.ATS_WEIGHT +
            content_score * ResumeScorer.CONTENT_WEIGHT
        )

        logger.info(f"Overall score: {overall:.1f} "
                   f"(grammar={grammar_score:.1f}, ats={ats_score:.1f}, content={content_score:.1f})")

        return round(overall, 1)

    @staticmethod
    def get_score_rating(score: float) -> str:
        """
        Get qualitative rating for score.

        Args:
            score: Score value (0-100)

        Returns:
            Rating string
        """
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 50:
            return "Needs Improvement"
        else:
            return "Poor"
