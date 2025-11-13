# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Resume Refiner is a tool for improving and refining resumes.

## Project Status

**Phase 1 (Foundation) - COMPLETED ✅**

The project structure has been established with:
- Backend API using FastAPI
- Frontend application using React + TypeScript + Vite
- File upload functionality
- Basic UI components for resume analysis
- API endpoints for upload, analysis, and export

**Phase 2 (Document Processing) - COMPLETED ✅**

Document parsing functionality has been implemented:
- PDF parser using pdfplumber with text extraction
- DOCX parser using python-docx with support for tables
- Intelligent section detection (contact info, summary, experience, education, skills)
- Contact information extraction (email, phone, LinkedIn, name)
- DocumentPreview component for displaying parsed content
- Comprehensive test suite for parser functionality

**Next Steps**: Phase 3 - Grammar and Basic Analysis (implement grammar checking and scoring)

## Development Commands

### Backend

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Code formatting
black app/
flake8 app/
```

### Frontend

```bash
# Setup
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

## Architecture

### Backend Structure
- **FastAPI** application with modular architecture
- **Models**: Pydantic models for data validation
- **Services**: Business logic layer (parser, Claude API, grammar checker, ATS optimizer, formatter)
- **Routers**: API endpoints (upload, analyze, export)
- **Utils**: Helper functions for file handling

### Frontend Structure
- **React** with TypeScript for type safety
- **Components**: Reusable UI components (UploadSection, AnalysisResults, ScoreDisplay, SuggestionCard, DocumentPreview)
- **Pages**: Main application pages (Home)
- **Services**: API client using Axios
- **Types**: TypeScript interfaces matching backend models

### Document Parser Features
- **PDF Support**: Extracts text from all pages using pdfplumber
- **DOCX Support**: Parses paragraphs and tables using python-docx
- **Section Detection**: Identifies common resume sections automatically
- **Contact Extraction**: Regex-based extraction of emails, phone numbers, LinkedIn URLs
- **Smart Parsing**: Attempts to structure unstructured text into meaningful sections

### API Flow
1. User uploads resume → POST /api/upload/
2. Backend parses document → Returns upload object with parsed content
3. Frontend requests analysis → POST /api/analyze/
4. Backend runs grammar check, ATS analysis, AI suggestions → Returns analysis results
5. User views results and can export → GET /api/export/{id}/pdf or /docx
