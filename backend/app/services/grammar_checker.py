"""Grammar checking service using LanguageTool."""

import logging
from typing import List
import language_tool_python
from app.models.analysis import GrammarIssue

logger = logging.getLogger(__name__)

# Global LanguageTool instance (initialized once for performance)
_language_tool = None


def get_language_tool():
    """Get or create LanguageTool instance (singleton pattern)."""
    global _language_tool
    if _language_tool is None:
        try:
            logger.info("Initializing LanguageTool...")
            _language_tool = language_tool_python.LanguageTool('en-US')
            logger.info("LanguageTool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LanguageTool: {e}")
            raise
    return _language_tool


class GrammarChecker:
    """Grammar checking service using LanguageTool."""

    # Maximum text length to check (prevent performance issues)
    MAX_TEXT_LENGTH = 50000  # 50KB

    # Categories to ignore (too noisy for resumes)
    IGNORED_CATEGORIES = {
        'TYPOGRAPHY',  # Resume formatting is intentional
        'CASING',  # Resume section headers often use specific casing
    }

    @staticmethod
    async def check_grammar(text: str, max_issues: int = 50) -> List[GrammarIssue]:
        """
        Check text for grammar issues using LanguageTool.

        Args:
            text: Text to check
            max_issues: Maximum number of issues to return (default 50)

        Returns:
            List of grammar issues found
        """
        if not text or not text.strip():
            logger.debug("Empty text provided for grammar check")
            return []

        # Limit text length for performance
        if len(text) > GrammarChecker.MAX_TEXT_LENGTH:
            logger.warning(f"Text truncated from {len(text)} to {GrammarChecker.MAX_TEXT_LENGTH} for grammar check")
            text = text[:GrammarChecker.MAX_TEXT_LENGTH]

        try:
            tool = get_language_tool()

            logger.info(f"Checking grammar for {len(text)} characters")
            matches = tool.check(text)
            logger.info(f"Found {len(matches)} grammar issues")

            issues = []
            for match in matches:
                # Skip ignored categories
                if match.category in GrammarChecker.IGNORED_CATEGORIES:
                    continue

                # Extract suggestions (limit to top 3)
                suggestions = match.replacements[:3] if match.replacements else []

                issue = GrammarIssue(
                    text=match.context,
                    message=match.message,
                    suggestions=suggestions,
                    category=match.category,
                    line=match.sentence,
                    offset=match.offset
                )
                issues.append(issue)

                # Limit total issues returned
                if len(issues) >= max_issues:
                    logger.info(f"Reached max issues limit ({max_issues}), stopping")
                    break

            logger.info(f"Returning {len(issues)} grammar issues after filtering")
            return issues

        except Exception as e:
            logger.exception(f"Error during grammar check: {e}")
            # Return empty list on error (graceful degradation)
            return []

    @staticmethod
    async def check_grammar_by_section(text: str, section_name: str = "full") -> List[GrammarIssue]:
        """
        Check grammar for a specific section with section context.

        Args:
            text: Text to check
            section_name: Name of the section being checked

        Returns:
            List of grammar issues found
        """
        logger.info(f"Checking grammar for section: {section_name}")
        issues = await GrammarChecker.check_grammar(text)

        # Add section context to each issue
        for issue in issues:
            issue.category = f"{section_name}: {issue.category}" if issue.category else section_name

        return issues

    @staticmethod
    def close():
        """Close LanguageTool instance (cleanup)."""
        global _language_tool
        if _language_tool is not None:
            try:
                _language_tool.close()
                logger.info("LanguageTool closed")
            except Exception as e:
                logger.warning(f"Error closing LanguageTool: {e}")
            finally:
                _language_tool = None
