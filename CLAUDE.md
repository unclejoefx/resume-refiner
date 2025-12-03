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

**Phase 2 Security Hardening - COMPLETED ✅**

Critical security fixes applied:
- ReDoS protection with regex timeout
- Specific exception handling with logging
- Input validation and sanitization
- Configuration management (ParserConfig)
- File cleanup background task
- Comprehensive logging infrastructure

**Phase 3 (Grammar and Basic Analysis) - COMPLETED ✅**

Grammar checking and scoring functionality implemented:
- LanguageTool integration for grammar checking
- Singleton pattern for performance optimization
- Resume scoring algorithm with weighted factors
- Grammar score based on issue count
- Content score based on resume completeness
- ATS score based on compatibility
- Overall weighted score calculation
- Comprehensive test suite for grammar and scoring

**Phase 4 (Claude API Integration) - COMPLETED ✅**

AI-powered content suggestions implemented:
- Anthropic Claude API integration using AsyncAnthropic client
- Intelligent prompt engineering for structured JSON responses
- Content analysis for summary, experience, and skills sections
- Direct improvement methods for summaries and bullet points
- Graceful degradation when API key is not configured
- Comprehensive error handling (rate limits, timeouts, API errors)
- Input validation and truncation for cost control
- 21 comprehensive tests with full mock coverage
- Fixed .env configuration parsing for CSV values
- Frontend already displays AI suggestions

**Next Steps**: Phase 5 - ATS Optimization (detailed implementation)

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

### Claude AI Service Features
- **Smart Analysis**: Analyzes summary, experience bullets, and skills sections
- **Structured Prompts**: Enforces JSON responses for reliable parsing
- **Best Practices**: Promotes action verbs, metrics, and impact-focused content
- **Graceful Fallback**: Works without API key (returns empty suggestions)
- **Cost Control**: Input truncation and limits prevent excessive API usage
- **Error Resilience**: Handles rate limits, timeouts, and malformed responses

### API Flow
1. User uploads resume → POST /api/upload/
2. Backend parses document → Returns upload object with parsed content
3. Frontend requests analysis → POST /api/analyze/
4. Backend runs:
   - Grammar check (LanguageTool)
   - ATS compatibility analysis
   - **Claude AI content suggestions** (if API key configured)
   - Scoring calculation (weighted: Grammar 30%, ATS 35%, Content 35%)
5. Returns comprehensive analysis with AI-powered suggestions
6. User views results and can export → GET /api/export/{id}/pdf or /docx

### Configuration
To enable Claude AI suggestions, add your API key to `.env`:
```bash
CLAUDE_API_KEY=your_api_key_here
```

Get your API key from: https://console.anthropic.com/

Without the API key, the application works normally but content suggestions will be empty.
