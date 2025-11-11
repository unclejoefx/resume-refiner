# Resume Refiner

AI-powered resume analysis and optimization tool that helps improve resumes through grammar checking, ATS optimization, and content enhancement using Claude AI.

## Features

- **Document Upload**: Support for PDF and DOCX resume formats
- **AI-Powered Analysis**: Content improvement suggestions using Anthropic's Claude API
- **Grammar Checking**: Automated grammar and spell checking
- **ATS Optimization**: Applicant Tracking System compatibility analysis
- **Format Standardization**: Export refined resumes in multiple formats
- **Comprehensive Scoring**: Overall resume scoring with detailed breakdowns

## Project Structure

```
resume-refiner/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models/      # Data models
│   │   ├── services/    # Business logic
│   │   ├── routers/     # API endpoints
│   │   └── utils/       # Helper functions
│   ├── tests/           # Backend tests
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API client
│   │   └── types/       # TypeScript types
│   └── package.json
└── README.md
```

## Technology Stack

### Backend
- **Framework**: FastAPI
- **AI**: Anthropic Claude API
- **Document Processing**: PyPDF2, python-docx
- **Grammar Check**: LanguageTool

### Frontend
- **Framework**: React + TypeScript
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **File Upload**: react-dropzone

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Claude API key from Anthropic

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd resume-refiner
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your Claude API key
# CLAUDE_API_KEY=your_api_key_here
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Create .env file from example
cp .env.example .env

# The default API URL is http://localhost:8000
# Modify if needed in .env
```

### 4. Running the Application

#### Start Backend Server

```bash
# From backend directory with virtual environment activated
cd backend
uvicorn app.main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

#### Start Frontend Development Server

```bash
# From frontend directory
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Upload
- `POST /api/upload/` - Upload resume file
- `GET /api/upload/{upload_id}` - Get upload details

### Analysis
- `POST /api/analyze/` - Analyze uploaded resume
- `GET /api/analyze/{analysis_id}` - Get analysis results
- `POST /api/analyze/grammar` - Run grammar check
- `POST /api/analyze/ats` - Run ATS optimization check

### Export
- `GET /api/export/{analysis_id}/pdf` - Export as PDF
- `GET /api/export/{analysis_id}/docx` - Export as DOCX

## Development

### Backend Testing

```bash
cd backend
pytest
```

### Code Formatting

```bash
# Backend
cd backend
black app/
flake8 app/

# Frontend
cd frontend
npm run lint
```

## Environment Variables

### Backend (.env)
```
CLAUDE_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./resume_refiner.db
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Current Implementation Status

This is Phase 1 (Foundation) implementation including:
- ✅ Project structure setup
- ✅ Backend API with FastAPI
- ✅ Frontend with React + TypeScript
- ✅ File upload functionality
- ✅ Basic UI components
- ⏳ Document parsing (placeholder)
- ⏳ Grammar checking (placeholder)
- ⏳ ATS optimization (placeholder)
- ⏳ Claude AI integration (placeholder)

## Roadmap

See [plan.md](plan.md) for detailed implementation roadmap including:
- Phase 2: Document Processing
- Phase 3: Grammar and Basic Analysis
- Phase 4: Claude API Integration
- Phase 5: ATS Optimization
- Phase 6: Format Standardization
- Phase 7: Polish and Testing
- Phase 8: Deployment

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

[To be added]

## Support

For issues and questions, please create an issue in the repository.
