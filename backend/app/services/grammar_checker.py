"""Grammar checking service."""

from typing import List
from app.models.analysis import GrammarIssue


class GrammarChecker:
    """Grammar checking service."""

    @staticmethod
    async def check_grammar(text: str) -> List[GrammarIssue]:
        """
        Check text for grammar issues.

        Args:
            text: Text to check

        Returns:
            List of grammar issues found
        """
        # Placeholder implementation
        # TODO: Implement with LanguageTool or grammar-check library
        return []
