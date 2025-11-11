# Phase 1: Foundation - Detailed Specification

**Timeline**: Week 1-2
**Status**: Not Started

## Objectives

Establish the foundational infrastructure for the Resume Refiner application, including project structure, development environment, and basic file upload functionality.

## Tasks Breakdown

### 1.1 Project Structure Setup

**Task**: Create the complete directory structure for frontend and backend

**Steps**:
1. Create root directories:
   ```bash
   mkdir -p backend/app/{models,services,routers,utils}
   mkdir -p backend/tests
   mkdir -p frontend/src/{components,pages,services,types,utils}
   mkdir -p frontend/public
   mkdir -p uploads
   mkdir -p specs
   ```

2. Initialize git repository (already done)

3. Create `.gitignore` with:
   - Python virtual environment directories
   - Node modules
   - Environment files
   - Upload directories
   - Build artifacts
   - IDE files

**Deliverables**:
- Complete directory structure matching plan.md
- Configured .gitignore file

**Acceptance Criteria**:
- All directories exist and are properly organized
- .gitignore prevents committing sensitive files

---

### 1.2 Backend Initialization

**Task**: Set up FastAPI backend with basic configuration

**Steps**:
1. Create Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. Create `requirements.txt`:
   ```
   fastapi==0.104.1
   uvicorn[standard]==0.24.0
   python-multipart==0.0.6
   python-dotenv==1.0.0
   pydantic==2.5.0
   pydantic-settings==2.1.0
   aiofiles==23.2.1
   pytest==7.4.3
   pytest-asyncio==0.21.1
   httpx==0.25.1
   ```

3. Create `backend/app/__init__.py` (empty file)

4. Create `backend/app/main.py`:
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   from app.config import settings
   from app.routers import upload

   app = FastAPI(
       title="Resume Refiner API",
       description="API for analyzing and improving resumes",
       version="0.1.0"
   )

   # CORS configuration
   app.add_middleware(
       CORSMiddleware,
       allow_origins=settings.ALLOWED_ORIGINS,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

   # Include routers
   app.include_router(upload.router, prefix="/api", tags=["upload"])

   @app.get("/")
   async def root():
       return {"message": "Resume Refiner API", "version": "0.1.0"}

   @app.get("/health")
   async def health_check():
       return {"status": "healthy"}
   ```

5. Create `backend/app/config.py`:
   ```python
   from pydantic_settings import BaseSettings
   from typing import List

   class Settings(BaseSettings):
       CLAUDE_API_KEY: str = ""
       DATABASE_URL: str = "sqlite:///./resume_refiner.db"
       ALLOWED_ORIGINS: List[str] = ["http://localhost:5173"]
       MAX_FILE_SIZE: int = 10485760  # 10MB
       UPLOAD_DIR: str = "./uploads"
       ALLOWED_FILE_TYPES: List[str] = [".pdf", ".docx"]

       class Config:
           env_file = ".env"

   settings = Settings()
   ```

6. Create `backend/.env.example`:
   ```
   CLAUDE_API_KEY=your_api_key_here
   DATABASE_URL=sqlite:///./resume_refiner.db
   ALLOWED_ORIGINS=["http://localhost:5173"]
   MAX_FILE_SIZE=10485760
   UPLOAD_DIR=./uploads
   ```

7. Create `backend/app/utils/__init__.py` (empty file)

8. Create `backend/app/utils/file_handler.py`:
   ```python
   import os
   import uuid
   from pathlib import Path
   from typing import Optional
   from fastapi import UploadFile
   from app.config import settings

   class FileHandler:
       @staticmethod
       def get_file_extension(filename: str) -> str:
           return Path(filename).suffix.lower()

       @staticmethod
       def is_allowed_file(filename: str) -> bool:
           ext = FileHandler.get_file_extension(filename)
           return ext in settings.ALLOWED_FILE_TYPES

       @staticmethod
       async def save_upload_file(file: UploadFile) -> tuple[str, str]:
           """Save uploaded file and return (file_id, file_path)"""
           file_id = str(uuid.uuid4())
           ext = FileHandler.get_file_extension(file.filename)
           file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")

           # Ensure upload directory exists
           os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

           # Save file
           with open(file_path, "wb") as f:
               content = await file.read()
               f.write(content)

           return file_id, file_path

       @staticmethod
       def delete_file(file_path: str) -> bool:
           """Delete a file if it exists"""
           try:
               if os.path.exists(file_path):
                   os.remove(file_path)
                   return True
               return False
           except Exception:
               return False
   ```

**Deliverables**:
- Working FastAPI application
- Configuration management with pydantic-settings
- File handling utilities
- Requirements file for dependencies

**Acceptance Criteria**:
- Backend starts without errors: `uvicorn app.main:app --reload`
- Health check endpoint returns 200 OK
- API documentation accessible at http://localhost:8000/docs
- CORS properly configured for frontend origin

---

### 1.3 Frontend Initialization

**Task**: Set up React + TypeScript frontend with Vite

**Steps**:
1. Initialize Vite project:
   ```bash
   cd frontend
   npm create vite@latest . -- --template react-ts
   ```

2. Install dependencies:
   ```bash
   npm install
   npm install axios react-router-dom
   npm install -D @types/react-router-dom
   npm install tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

3. Configure `tailwind.config.js`:
   ```javascript
   export default {
     content: [
       "./index.html",
       "./src/**/*.{js,ts,jsx,tsx}",
     ],
     theme: {
       extend: {},
     },
     plugins: [],
   }
   ```

4. Update `src/index.css`:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

5. Create `.env.example`:
   ```
   VITE_API_URL=http://localhost:8000
   ```

6. Create `src/services/api.ts`:
   ```typescript
   import axios from 'axios';

   const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

   export const api = axios.create({
     baseURL: API_URL,
     headers: {
       'Content-Type': 'application/json',
     },
   });

   export const uploadApi = axios.create({
     baseURL: API_URL,
     headers: {
       'Content-Type': 'multipart/form-data',
     },
   });
   ```

7. Create `src/types/resume.ts`:
   ```typescript
   export interface ResumeUpload {
     id: string;
     filename: string;
     fileType: 'pdf' | 'docx';
     uploadDate: string;
     status: 'uploading' | 'uploaded' | 'processing' | 'error';
   }

   export interface UploadResponse {
     upload_id: string;
     filename: string;
     file_type: string;
     message: string;
   }

   export interface ApiError {
     detail: string;
   }
   ```

8. Update `src/App.tsx` with basic routing:
   ```typescript
   import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
   import Home from './pages/Home';
   import Upload from './pages/Upload';

   function App() {
     return (
       <Router>
         <div className="min-h-screen bg-gray-50">
           <Routes>
             <Route path="/" element={<Home />} />
             <Route path="/upload" element={<Upload />} />
           </Routes>
         </div>
       </Router>
     );
   }

   export default App;
   ```

9. Create `src/pages/Home.tsx`:
   ```typescript
   import { Link } from 'react-router-dom';

   const Home = () => {
     return (
       <div className="container mx-auto px-4 py-16">
         <div className="max-w-3xl mx-auto text-center">
           <h1 className="text-5xl font-bold text-gray-900 mb-6">
             Resume Refiner
           </h1>
           <p className="text-xl text-gray-600 mb-8">
             AI-powered resume analysis and optimization tool
           </p>
           <Link
             to="/upload"
             className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition"
           >
             Get Started
           </Link>
         </div>
       </div>
     );
   };

   export default Home;
   ```

10. Create `src/pages/Upload.tsx` (placeholder):
    ```typescript
    const Upload = () => {
      return (
        <div className="container mx-auto px-4 py-16">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            Upload Your Resume
          </h1>
          <p className="text-gray-600">Upload functionality coming soon...</p>
        </div>
      );
    };

    export default Upload;
    ```

**Deliverables**:
- Working React application with TypeScript
- Tailwind CSS configured and working
- API client setup
- Basic routing with placeholder pages
- Type definitions for data models

**Acceptance Criteria**:
- Frontend starts without errors: `npm run dev`
- Application accessible at http://localhost:5173
- Can navigate between Home and Upload pages
- Tailwind CSS styling works correctly
- No TypeScript errors

---

### 1.4 Basic File Upload Endpoint

**Task**: Implement backend endpoint for file upload

**Steps**:
1. Create `backend/app/models/__init__.py` (empty file)

2. Create `backend/app/models/resume.py`:
   ```python
   from pydantic import BaseModel, Field
   from datetime import datetime
   from typing import Literal

   class UploadResponse(BaseModel):
       upload_id: str
       filename: str
       file_type: Literal["pdf", "docx"]
       message: str
       upload_date: datetime = Field(default_factory=datetime.now)

   class ErrorResponse(BaseModel):
       detail: str
   ```

3. Create `backend/app/routers/__init__.py` (empty file)

4. Create `backend/app/routers/upload.py`:
   ```python
   from fastapi import APIRouter, UploadFile, File, HTTPException
   from app.models.resume import UploadResponse, ErrorResponse
   from app.utils.file_handler import FileHandler
   from app.config import settings

   router = APIRouter()

   @router.post("/upload", response_model=UploadResponse)
   async def upload_resume(file: UploadFile = File(...)):
       # Validate file type
       if not FileHandler.is_allowed_file(file.filename):
           raise HTTPException(
               status_code=400,
               detail=f"File type not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
           )

       # Validate file size
       file.file.seek(0, 2)
       file_size = file.file.tell()
       file.file.seek(0)

       if file_size > settings.MAX_FILE_SIZE:
           raise HTTPException(
               status_code=400,
               detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
           )

       # Save file
       try:
           file_id, file_path = await FileHandler.save_upload_file(file)
           file_ext = FileHandler.get_file_extension(file.filename)

           return UploadResponse(
               upload_id=file_id,
               filename=file.filename,
               file_type="pdf" if file_ext == ".pdf" else "docx",
               message="File uploaded successfully"
           )
       except Exception as e:
           raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

   @router.get("/upload/{upload_id}")
   async def get_upload_status(upload_id: str):
       # Placeholder for future implementation
       return {"upload_id": upload_id, "status": "uploaded"}
   ```

5. Create `backend/tests/__init__.py` (empty file)

6. Create `backend/tests/test_upload.py`:
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from app.main import app
   import io

   client = TestClient(app)

   def test_health_check():
       response = client.get("/health")
       assert response.status_code == 200
       assert response.json() == {"status": "healthy"}

   def test_upload_pdf():
       # Create a dummy PDF file
       pdf_content = b"%PDF-1.4 dummy content"
       files = {"file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")}

       response = client.post("/api/upload", files=files)
       assert response.status_code == 200
       data = response.json()
       assert "upload_id" in data
       assert data["filename"] == "test_resume.pdf"
       assert data["file_type"] == "pdf"

   def test_upload_invalid_file_type():
       files = {"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}

       response = client.post("/api/upload", files=files)
       assert response.status_code == 400
   ```

**Deliverables**:
- Working file upload endpoint
- File validation (type and size)
- Response models with proper types
- Basic unit tests

**Acceptance Criteria**:
- Can upload PDF and DOCX files via API
- Files rejected if wrong type or too large
- Uploaded files saved in uploads directory
- Tests pass: `pytest backend/tests/`
- API documentation shows upload endpoint

---

### 1.5 File Upload UI

**Task**: Create React component for file upload

**Steps**:
1. Install react-dropzone:
   ```bash
   cd frontend
   npm install react-dropzone
   ```

2. Create `src/components/UploadSection.tsx`:
   ```typescript
   import { useCallback, useState } from 'react';
   import { useDropzone } from 'react-dropzone';
   import { uploadApi } from '../services/api';
   import { UploadResponse, ApiError } from '../types/resume';

   const UploadSection = () => {
     const [uploading, setUploading] = useState(false);
     const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
     const [error, setError] = useState<string | null>(null);

     const onDrop = useCallback(async (acceptedFiles: File[]) => {
       if (acceptedFiles.length === 0) return;

       const file = acceptedFiles[0];
       const formData = new FormData();
       formData.append('file', file);

       setUploading(true);
       setError(null);
       setUploadResult(null);

       try {
         const response = await uploadApi.post<UploadResponse>('/api/upload', formData);
         setUploadResult(response.data);
       } catch (err: any) {
         const errorMsg = err.response?.data?.detail || 'Error uploading file';
         setError(errorMsg);
       } finally {
         setUploading(false);
       }
     }, []);

     const { getRootProps, getInputProps, isDragActive } = useDropzone({
       onDrop,
       accept: {
         'application/pdf': ['.pdf'],
         'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
       },
       maxFiles: 1,
       maxSize: 10485760, // 10MB
     });

     return (
       <div className="max-w-2xl mx-auto">
         <div
           {...getRootProps()}
           className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition ${
             isDragActive
               ? 'border-blue-500 bg-blue-50'
               : 'border-gray-300 hover:border-gray-400'
           }`}
         >
           <input {...getInputProps()} />
           {uploading ? (
             <p className="text-gray-600">Uploading...</p>
           ) : isDragActive ? (
             <p className="text-blue-600">Drop your resume here...</p>
           ) : (
             <div>
               <p className="text-lg text-gray-600 mb-2">
                 Drag and drop your resume here, or click to select
               </p>
               <p className="text-sm text-gray-500">
                 Supports PDF and DOCX files (max 10MB)
               </p>
             </div>
           )}
         </div>

         {error && (
           <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
             <p className="text-red-600">{error}</p>
           </div>
         )}

         {uploadResult && (
           <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
             <p className="text-green-600 font-semibold">Upload successful!</p>
             <p className="text-sm text-gray-600 mt-1">
               File: {uploadResult.filename}
             </p>
             <p className="text-sm text-gray-600">
               Upload ID: {uploadResult.upload_id}
             </p>
           </div>
         )}
       </div>
     );
   };

   export default UploadSection;
   ```

3. Update `src/pages/Upload.tsx`:
   ```typescript
   import { Link } from 'react-router-dom';
   import UploadSection from '../components/UploadSection';

   const Upload = () => {
     return (
       <div className="container mx-auto px-4 py-16">
         <div className="mb-8">
           <Link to="/" className="text-blue-600 hover:underline">
             ← Back to Home
           </Link>
         </div>

         <h1 className="text-3xl font-bold text-gray-900 mb-2">
           Upload Your Resume
         </h1>
         <p className="text-gray-600 mb-8">
           Upload your resume to get AI-powered feedback and optimization suggestions
         </p>

         <UploadSection />
       </div>
     );
   };

   export default Upload;
   ```

**Deliverables**:
- Drag-and-drop file upload component
- Visual feedback for upload status
- Error handling and display
- Success message with upload details

**Acceptance Criteria**:
- Can drag and drop files to upload
- Can click to browse and select files
- Shows loading state during upload
- Displays error messages for invalid files
- Shows success message with upload details
- Only accepts PDF and DOCX files

---

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can upload a PDF file successfully
- [ ] Can upload a DOCX file successfully
- [ ] Invalid file types are rejected
- [ ] Files larger than 10MB are rejected
- [ ] Uploaded files appear in uploads directory
- [ ] CORS allows frontend to communicate with backend
- [ ] Unit tests pass
- [ ] API documentation is accessible and accurate

## Dependencies

- None (this is the foundation phase)

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| CORS issues between frontend and backend | Test early and configure properly in backend config |
| File upload size limits | Implement both client and server-side validation |
| Cross-platform path issues (Windows vs Linux) | Use Path from pathlib consistently |

## Documentation Requirements

- Update README.md with setup instructions
- Document environment variables in .env.example
- Add API endpoint documentation in docstrings
- Create development setup guide

## Success Metrics

- Backend responds to requests in <100ms
- File upload completes in <2s for 5MB file
- Zero console errors in browser
- All unit tests pass
- Code follows Python (PEP 8) and TypeScript style guidelines
