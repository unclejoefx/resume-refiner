"""Document parsing service."""

from pathlib import Path
from typing import Optional
from app.models.resume import ResumeContent


class DocumentParser:
    """Document parser for PDF and DOCX files."""

    @staticmethod
    def parse_pdf(file_path: str) -> ResumeContent:
        """
        Parse PDF file and extract content.

        Args:
            file_path: Path to PDF file

        Returns:
            ResumeContent object with extracted data
        """
        # Placeholder implementation
        # TODO: Implement with PyPDF2 or pdfplumber
        return ResumeContent(
            raw_text="PDF parsing not yet implemented",
        )

    @staticmethod
    def parse_docx(file_path: str) -> ResumeContent:
        """
        Parse DOCX file and extract content.

        Args:
            file_path: Path to DOCX file

        Returns:
            ResumeContent object with extracted data
        """
        # Placeholder implementation
        # TODO: Implement with python-docx
        return ResumeContent(
            raw_text="DOCX parsing not yet implemented",
        )

    @classmethod
    def parse(cls, file_path: str, file_type: str) -> ResumeContent:
        """
        Parse document based on file type.

        Args:
            file_path: Path to document file
            file_type: File type (pdf or docx)

        Returns:
            ResumeContent object with extracted data

        Raises:
            ValueError: If file type is not supported
        """
        if file_type == "pdf":
            return cls.parse_pdf(file_path)
        elif file_type == "docx":
            return cls.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
