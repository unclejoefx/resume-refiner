# Phase 2: Document Processing - Detailed Specification

**Timeline**: Week 2-3
**Status**: Not Started
**Dependencies**: Phase 1 (Foundation)

## Objectives

Implement document parsing functionality to extract text and structured data from PDF and DOCX files. Create data models to represent resume sections and display parsed content in the UI.

## Tasks Breakdown

### 2.1 Install Document Processing Libraries

**Task**: Add required libraries for PDF and DOCX parsing

**Steps**:
1. Update `backend/requirements.txt` to add:
   ```
   pypdf2==3.0.1
   pdfplumber==0.10.3
   python-docx==1.1.0
   ```

2. Install dependencies:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

**Deliverables**:
- Updated requirements.txt
- Libraries installed and importable

**Acceptance Criteria**:
- Can import pypdf2, pdfplumber, and python-docx without errors
- No dependency conflicts

---

### 2.2 Create Resume Data Models

**Task**: Define Pydantic models for structured resume data

**Steps**:
1. Update `backend/app/models/resume.py` to add:
   ```python
   from pydantic import BaseModel, EmailStr
   from datetime import datetime
   from typing import List, Optional, Dict, Any

   class ContactInfo(BaseModel):
       name: Optional[str] = None
       email: Optional[str] = None
       phone: Optional[str] = None
       location: Optional[str] = None
       linkedin: Optional[str] = None
       website: Optional[str] = None

   class ExperienceItem(BaseModel):
       company: Optional[str] = None
       title: Optional[str] = None
       start_date: Optional[str] = None
       end_date: Optional[str] = None
       location: Optional[str] = None
       description: List[str] = []

   class EducationItem(BaseModel):
       institution: Optional[str] = None
       degree: Optional[str] = None
       field: Optional[str] = None
       start_date: Optional[str] = None
       end_date: Optional[str] = None
       location: Optional[str] = None
       gpa: Optional[str] = None

   class ResumeSection(BaseModel):
       title: str
       content: str

   class ResumeContent(BaseModel):
       raw_text: str
       contact_info: ContactInfo
       summary: Optional[str] = None
       experience: List[ExperienceItem] = []
       education: List[EducationItem] = []
       skills: List[str] = []
       sections: List[ResumeSection] = []

   class Resume(BaseModel):
       id: str
       filename: str
       file_type: str
       upload_date: datetime
       file_path: str
       content: Optional[ResumeContent] = None
       is_parsed: bool = False

   class ParseResponse(BaseModel):
       resume_id: str
       filename: str
       is_parsed: bool
       content: ResumeContent
       message: str
   ```

**Deliverables**:
- Complete data models for resume structure
- Type-safe models with validation

**Acceptance Criteria**:
- Models can be instantiated with sample data
- FastAPI auto-generates correct schemas
- Validation works for required fields

---

### 2.3 Implement PDF Parser

**Task**: Create service to extract text and structure from PDF files

**Steps**:
1. Create `backend/app/services/__init__.py` (empty file)

2. Create `backend/app/services/parser.py`:
   ```python
   import re
   from typing import Optional, List
   import pdfplumber
   from pypdf import PdfReader
   from docx import Document
   from app.models.resume import (
       ResumeContent,
       ContactInfo,
       ExperienceItem,
       EducationItem,
       ResumeSection
   )

   class ResumeParser:
       def __init__(self):
           self.section_headers = [
               "experience",
               "work experience",
               "professional experience",
               "employment history",
               "education",
               "skills",
               "technical skills",
               "summary",
               "professional summary",
               "objective",
               "projects",
               "certifications",
               "awards",
               "publications",
           ]

       def parse_pdf(self, file_path: str) -> ResumeContent:
           """Parse PDF file and extract content"""
           try:
               # Try pdfplumber first (better for text extraction)
               with pdfplumber.open(file_path) as pdf:
                   raw_text = ""
                   for page in pdf.pages:
                       text = page.extract_text()
                       if text:
                           raw_text += text + "\n"
           except Exception:
               # Fallback to pypdf
               reader = PdfReader(file_path)
               raw_text = ""
               for page in reader.pages:
                   raw_text += page.extract_text() + "\n"

           return self._parse_text(raw_text)

       def parse_docx(self, file_path: str) -> ResumeContent:
           """Parse DOCX file and extract content"""
           doc = Document(file_path)
           raw_text = "\n".join([para.text for para in doc.paragraphs])
           return self._parse_text(raw_text)

       def _parse_text(self, text: str) -> ResumeContent:
           """Parse raw text and extract structured data"""
           lines = [line.strip() for line in text.split("\n") if line.strip()]

           contact_info = self._extract_contact_info(text)
           summary = self._extract_summary(lines)
           experience = self._extract_experience(lines)
           education = self._extract_education(lines)
           skills = self._extract_skills(lines)
           sections = self._extract_sections(lines)

           return ResumeContent(
               raw_text=text,
               contact_info=contact_info,
               summary=summary,
               experience=experience,
               education=education,
               skills=skills,
               sections=sections,
           )

       def _extract_contact_info(self, text: str) -> ContactInfo:
           """Extract contact information from text"""
           contact = ContactInfo()

           # Extract email
           email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
           email_match = re.search(email_pattern, text)
           if email_match:
               contact.email = email_match.group()

           # Extract phone
           phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
           phone_match = re.search(phone_pattern, text)
           if phone_match:
               contact.phone = phone_match.group()

           # Extract LinkedIn
           linkedin_pattern = r'linkedin\.com/in/[\w-]+'
           linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
           if linkedin_match:
               contact.linkedin = linkedin_match.group()

           # Extract name (assume first line with more than 2 words)
           lines = text.split("\n")
           for line in lines[:5]:  # Check first 5 lines
               line = line.strip()
               words = line.split()
               if len(words) >= 2 and len(line) < 50 and not any(char.isdigit() for char in line):
                   contact.name = line
                   break

           return contact

       def _extract_summary(self, lines: List[str]) -> Optional[str]:
           """Extract professional summary or objective"""
           summary_keywords = ["summary", "objective", "profile", "about"]
           summary_text = []
           capturing = False

           for i, line in enumerate(lines):
               line_lower = line.lower()

               # Check if this is a summary section header
               if any(keyword in line_lower for keyword in summary_keywords) and len(line.split()) <= 4:
                   capturing = True
                   continue

               # Stop capturing if we hit another section
               if capturing:
                   if self._is_section_header(line):
                       break
                   summary_text.append(line)

           return " ".join(summary_text) if summary_text else None

       def _extract_experience(self, lines: List[str]) -> List[ExperienceItem]:
           """Extract work experience items"""
           experience = []
           in_experience_section = False
           current_item = None

           for line in lines:
               line_lower = line.lower()

               # Check for experience section header
               if any(keyword in line_lower for keyword in ["experience", "employment", "work history"]):
                   if len(line.split()) <= 4:
                       in_experience_section = True
                       continue

               # Exit if we hit another major section
               if in_experience_section and self._is_section_header(line):
                   if not any(keyword in line_lower for keyword in ["experience", "employment"]):
                       if current_item:
                           experience.append(current_item)
                       break

               # Look for job title/company patterns
               if in_experience_section:
                   # This is a simplified extraction - could be enhanced with NLP
                   if current_item and ("|" in line or "–" in line or "-" in line):
                       # Likely a new position
                       experience.append(current_item)
                       current_item = ExperienceItem()
                       parts = re.split(r'[|–-]', line)
                       if len(parts) >= 2:
                           current_item.title = parts[0].strip()
                           current_item.company = parts[1].strip()
                   elif current_item:
                       # Add to description
                       if line.startswith("•") or line.startswith("-") or line.startswith("*"):
                           current_item.description.append(line.lstrip("•-* "))
                   elif "|" in line or "–" in line or "-" in line:
                       current_item = ExperienceItem()
                       parts = re.split(r'[|–-]', line)
                       if len(parts) >= 2:
                           current_item.title = parts[0].strip()
                           current_item.company = parts[1].strip()

           if current_item:
               experience.append(current_item)

           return experience

       def _extract_education(self, lines: List[str]) -> List[EducationItem]:
           """Extract education items"""
           education = []
           in_education_section = False
           current_item = None

           for line in lines:
               line_lower = line.lower()

               # Check for education section header
               if "education" in line_lower and len(line.split()) <= 3:
                   in_education_section = True
                   continue

               # Exit if we hit another major section
               if in_education_section and self._is_section_header(line):
                   if "education" not in line_lower:
                       if current_item:
                           education.append(current_item)
                       break

               if in_education_section:
                   # Look for degree keywords
                   degree_keywords = ["bachelor", "master", "phd", "b.s.", "m.s.", "b.a.", "m.a."]
                   if any(keyword in line_lower for keyword in degree_keywords):
                       if current_item:
                           education.append(current_item)
                       current_item = EducationItem()
                       current_item.degree = line
                   elif current_item and not current_item.institution:
                       # Next line is likely institution
                       current_item.institution = line

           if current_item:
               education.append(current_item)

           return education

       def _extract_skills(self, lines: List[str]) -> List[str]:
           """Extract skills list"""
           skills = []
           in_skills_section = False

           for line in lines:
               line_lower = line.lower()

               # Check for skills section header
               if "skill" in line_lower and len(line.split()) <= 3:
                   in_skills_section = True
                   continue

               # Exit if we hit another major section
               if in_skills_section and self._is_section_header(line):
                   if "skill" not in line_lower:
                       break

               if in_skills_section:
                   # Split by common delimiters
                   items = re.split(r'[,|•·]', line)
                   for item in items:
                       item = item.strip().strip("-*•")
                       if item and len(item) > 1:
                           skills.append(item)

           return skills

       def _extract_sections(self, lines: List[str]) -> List[ResumeSection]:
           """Extract all sections with their content"""
           sections = []
           current_section = None
           current_content = []

           for line in lines:
               if self._is_section_header(line):
                   # Save previous section
                   if current_section:
                       sections.append(ResumeSection(
                           title=current_section,
                           content="\n".join(current_content)
                       ))
                   # Start new section
                   current_section = line
                   current_content = []
               elif current_section:
                   current_content.append(line)

           # Add last section
           if current_section:
               sections.append(ResumeSection(
                   title=current_section,
                   content="\n".join(current_content)
               ))

           return sections

       def _is_section_header(self, line: str) -> bool:
           """Check if line is likely a section header"""
           line_lower = line.lower().strip()
           return (
               any(header in line_lower for header in self.section_headers)
               and len(line.split()) <= 4
               and not line.endswith(".")
           )
   ```

**Deliverables**:
- PDF parsing functionality
- DOCX parsing functionality
- Text extraction with structure preservation
- Contact information extraction
- Section identification

**Acceptance Criteria**:
- Can extract text from PDF files
- Can extract text from DOCX files
- Identifies common resume sections
- Extracts email, phone, and LinkedIn from text
- Handles malformed PDFs gracefully

---

### 2.4 Create Parse Endpoint

**Task**: Add API endpoint to parse uploaded resumes

**Steps**:
1. Create `backend/app/routers/parse.py`:
   ```python
   from fastapi import APIRouter, HTTPException
   from app.models.resume import ParseResponse, Resume
   from app.services.parser import ResumeParser
   from app.config import settings
   import os

   router = APIRouter()
   parser = ResumeParser()

   @router.post("/parse/{upload_id}", response_model=ParseResponse)
   async def parse_resume(upload_id: str):
       """Parse an uploaded resume and extract structured content"""
       # Find the file
       file_path = None
       for ext in [".pdf", ".docx"]:
           potential_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}{ext}")
           if os.path.exists(potential_path):
               file_path = potential_path
               file_type = ext[1:]  # Remove the dot
               break

       if not file_path:
           raise HTTPException(status_code=404, detail="Upload not found")

       # Parse the document
       try:
           if file_type == "pdf":
               content = parser.parse_pdf(file_path)
           elif file_type == "docx":
               content = parser.parse_docx(file_path)
           else:
               raise HTTPException(status_code=400, detail="Unsupported file type")

           return ParseResponse(
               resume_id=upload_id,
               filename=os.path.basename(file_path),
               is_parsed=True,
               content=content,
               message="Resume parsed successfully"
           )
       except Exception as e:
           raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")
   ```

2. Update `backend/app/main.py` to include the parse router:
   ```python
   from app.routers import upload, parse

   # ... existing code ...

   app.include_router(parse.router, prefix="/api", tags=["parse"])
   ```

**Deliverables**:
- Parse endpoint that accepts upload ID
- Integration with ResumeParser service
- Error handling for missing files and parse errors

**Acceptance Criteria**:
- Endpoint returns structured resume data
- Handles both PDF and DOCX files
- Returns 404 for non-existent uploads
- Returns 500 with error message for parsing failures

---

### 2.5 Create Unit Tests for Parser

**Task**: Write comprehensive tests for document parsing

**Steps**:
1. Create `backend/tests/test_parser.py`:
   ```python
   import pytest
   from app.services.parser import ResumeParser

   def test_extract_email():
       parser = ResumeParser()
       text = "Contact me at john.doe@example.com for more info"
       contact = parser._extract_contact_info(text)
       assert contact.email == "john.doe@example.com"

   def test_extract_phone():
       parser = ResumeParser()
       text = "Phone: (555) 123-4567"
       contact = parser._extract_contact_info(text)
       assert contact.phone is not None
       assert "555" in contact.phone

   def test_extract_linkedin():
       parser = ResumeParser()
       text = "Find me on linkedin.com/in/johndoe"
       contact = parser._extract_contact_info(text)
       assert "linkedin.com/in/johndoe" in contact.linkedin

   def test_is_section_header():
       parser = ResumeParser()
       assert parser._is_section_header("WORK EXPERIENCE")
       assert parser._is_section_header("Education")
       assert parser._is_section_header("Skills")
       assert not parser._is_section_header("This is a longer sentence that is not a header.")

   def test_extract_skills():
       parser = ResumeParser()
       lines = [
           "Skills",
           "Python, JavaScript, React",
           "AWS, Docker, Kubernetes",
           "Next Section"
       ]
       skills = parser._extract_skills(lines)
       assert "Python" in skills
       assert "JavaScript" in skills
       assert "React" in skills
   ```

2. Create sample test files in `backend/tests/fixtures/`:
   ```bash
   mkdir -p backend/tests/fixtures
   ```

3. Add integration test for full parsing:
   ```python
   # In test_parser.py
   def test_parse_text_full():
       parser = ResumeParser()
       sample_text = """
       John Doe
       john.doe@example.com | (555) 123-4567 | linkedin.com/in/johndoe

       PROFESSIONAL SUMMARY
       Experienced software engineer with 5 years of expertise.

       WORK EXPERIENCE
       Senior Developer | Tech Corp
       • Led team of 5 developers
       • Implemented CI/CD pipeline

       EDUCATION
       Bachelor of Science in Computer Science
       University of Technology

       SKILLS
       Python, JavaScript, React, AWS, Docker
       """
       content = parser._parse_text(sample_text)

       assert content.contact_info.email == "john.doe@example.com"
       assert content.contact_info.name == "John Doe"
       assert content.summary is not None
       assert len(content.experience) > 0
       assert len(content.education) > 0
       assert len(content.skills) > 0
   ```

**Deliverables**:
- Unit tests for all parser methods
- Test fixtures with sample data
- Integration tests for full parsing flow

**Acceptance Criteria**:
- All parser tests pass
- Test coverage > 80% for parser module
- Tests handle edge cases (empty text, missing sections)

---

### 2.6 Display Parsed Resume in UI

**Task**: Create React components to display parsed resume content

**Steps**:
1. Create `src/components/ResumeDisplay.tsx`:
   ```typescript
   import { ParseResponse } from '../types/resume';

   interface ResumeDisplayProps {
     resume: ParseResponse;
   }

   const ResumeDisplay = ({ resume }: ResumeDisplayProps) => {
     const { content } = resume;

     return (
       <div className="bg-white rounded-lg shadow-md p-6">
         <h2 className="text-2xl font-bold text-gray-900 mb-6">
           Parsed Resume Content
         </h2>

         {/* Contact Info */}
         {content.contact_info && (
           <div className="mb-6">
             <h3 className="text-lg font-semibold text-gray-800 mb-2">
               Contact Information
             </h3>
             <div className="text-gray-600 space-y-1">
               {content.contact_info.name && <p><strong>Name:</strong> {content.contact_info.name}</p>}
               {content.contact_info.email && <p><strong>Email:</strong> {content.contact_info.email}</p>}
               {content.contact_info.phone && <p><strong>Phone:</strong> {content.contact_info.phone}</p>}
               {content.contact_info.linkedin && (
                 <p><strong>LinkedIn:</strong> {content.contact_info.linkedin}</p>
               )}
             </div>
           </div>
         )}

         {/* Summary */}
         {content.summary && (
           <div className="mb-6">
             <h3 className="text-lg font-semibold text-gray-800 mb-2">
               Professional Summary
             </h3>
             <p className="text-gray-600">{content.summary}</p>
           </div>
         )}

         {/* Experience */}
         {content.experience.length > 0 && (
           <div className="mb-6">
             <h3 className="text-lg font-semibold text-gray-800 mb-2">
               Work Experience
             </h3>
             <div className="space-y-4">
               {content.experience.map((exp, index) => (
                 <div key={index} className="border-l-2 border-blue-500 pl-4">
                   {exp.title && <p className="font-semibold">{exp.title}</p>}
                   {exp.company && <p className="text-gray-600">{exp.company}</p>}
                   {exp.description.length > 0 && (
                     <ul className="list-disc list-inside text-gray-600 mt-2">
                       {exp.description.map((item, i) => (
                         <li key={i}>{item}</li>
                       ))}
                     </ul>
                   )}
                 </div>
               ))}
             </div>
           </div>
         )}

         {/* Education */}
         {content.education.length > 0 && (
           <div className="mb-6">
             <h3 className="text-lg font-semibold text-gray-800 mb-2">
               Education
             </h3>
             <div className="space-y-2">
               {content.education.map((edu, index) => (
                 <div key={index}>
                   {edu.degree && <p className="font-semibold">{edu.degree}</p>}
                   {edu.institution && <p className="text-gray-600">{edu.institution}</p>}
                 </div>
               ))}
             </div>
           </div>
         )}

         {/* Skills */}
         {content.skills.length > 0 && (
           <div className="mb-6">
             <h3 className="text-lg font-semibold text-gray-800 mb-2">
               Skills
             </h3>
             <div className="flex flex-wrap gap-2">
               {content.skills.map((skill, index) => (
                 <span
                   key={index}
                   className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                 >
                   {skill}
                 </span>
               ))}
             </div>
           </div>
         )}

         {/* Raw Text (collapsible) */}
         <details className="mt-6">
           <summary className="cursor-pointer text-gray-700 font-semibold">
             View Raw Text
           </summary>
           <pre className="mt-2 p-4 bg-gray-50 rounded text-sm overflow-x-auto whitespace-pre-wrap">
             {content.raw_text}
           </pre>
         </details>
       </div>
     );
   };

   export default ResumeDisplay;
   ```

2. Update `src/types/resume.ts` to add parse response types:
   ```typescript
   export interface ContactInfo {
     name?: string;
     email?: string;
     phone?: string;
     location?: string;
     linkedin?: string;
     website?: string;
   }

   export interface ExperienceItem {
     company?: string;
     title?: string;
     start_date?: string;
     end_date?: string;
     location?: string;
     description: string[];
   }

   export interface EducationItem {
     institution?: string;
     degree?: string;
     field?: string;
     start_date?: string;
     end_date?: string;
     location?: string;
     gpa?: string;
   }

   export interface ResumeSection {
     title: string;
     content: string;
   }

   export interface ResumeContent {
     raw_text: string;
     contact_info: ContactInfo;
     summary?: string;
     experience: ExperienceItem[];
     education: EducationItem[];
     skills: string[];
     sections: ResumeSection[];
   }

   export interface ParseResponse {
     resume_id: string;
     filename: string;
     is_parsed: boolean;
     content: ResumeContent;
     message: string;
   }
   ```

3. Update `src/components/UploadSection.tsx` to trigger parsing:
   ```typescript
   // Add after successful upload
   const onDrop = useCallback(async (acceptedFiles: File[]) => {
     // ... existing upload code ...

     try {
       const uploadResponse = await uploadApi.post<UploadResponse>('/api/upload', formData);
       setUploadResult(uploadResponse.data);

       // Automatically trigger parsing
       try {
         const parseResponse = await api.post<ParseResponse>(
           `/api/parse/${uploadResponse.data.upload_id}`
         );
         onParseComplete(parseResponse.data);
       } catch (parseErr) {
         console.error('Parse error:', parseErr);
         setError('File uploaded but parsing failed');
       }
     } catch (err: any) {
       // ... existing error handling ...
     }
   }, [onParseComplete]);
   ```

4. Create `src/pages/Results.tsx`:
   ```typescript
   import { useState } from 'react';
   import { useLocation, Link } from 'react-router-dom';
   import ResumeDisplay from '../components/ResumeDisplay';
   import { ParseResponse } from '../types/resume';

   const Results = () => {
     const location = useLocation();
     const [resumeData] = useState<ParseResponse | null>(
       location.state?.resumeData || null
     );

     if (!resumeData) {
       return (
         <div className="container mx-auto px-4 py-16">
           <p className="text-gray-600">No resume data available.</p>
           <Link to="/upload" className="text-blue-600 hover:underline mt-4 inline-block">
             Upload a resume
           </Link>
         </div>
       );
     }

     return (
       <div className="container mx-auto px-4 py-16">
         <div className="mb-8">
           <Link to="/upload" className="text-blue-600 hover:underline">
             ← Upload another resume
           </Link>
         </div>

         <ResumeDisplay resume={resumeData} />
       </div>
     );
   };

   export default Results;
   ```

5. Update `src/App.tsx` to add Results route:
   ```typescript
   import Results from './pages/Results';

   // In Routes
   <Route path="/results" element={<Results />} />
   ```

6. Update `src/components/UploadSection.tsx` to navigate on success:
   ```typescript
   import { useNavigate } from 'react-router-dom';

   const UploadSection = () => {
     const navigate = useNavigate();

     const handleParseComplete = (data: ParseResponse) => {
       navigate('/results', { state: { resumeData: data } });
     };

     // Use handleParseComplete in upload logic
   };
   ```

**Deliverables**:
- Resume display component with all sections
- Results page to show parsed content
- Navigation flow from upload to results
- Visual styling for resume sections

**Acceptance Criteria**:
- Parsed resume displays correctly
- All sections (contact, summary, experience, education, skills) render
- Can view raw text in collapsible section
- Can navigate back to upload new resume
- Responsive design works on mobile

---

## Testing Checklist

- [ ] Can parse PDF files without errors
- [ ] Can parse DOCX files without errors
- [ ] Contact information extracted correctly
- [ ] Work experience items identified
- [ ] Education items identified
- [ ] Skills list extracted
- [ ] Parse endpoint returns structured data
- [ ] UI displays all resume sections
- [ ] Can navigate from upload to results
- [ ] All unit tests pass
- [ ] Raw text viewable in UI

## Dependencies

- Phase 1 (Foundation) must be completed
- File upload functionality must work
- Backend API must be accessible from frontend

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| PDF parsing fails for complex layouts | Use multiple libraries (pdfplumber, pypdf) as fallbacks |
| Resume formats vary significantly | Use regex patterns with flexibility; accept imperfect parsing |
| Large files cause performance issues | Add progress indicators; consider async processing |
| Parsing accuracy low | Start with basic extraction; improve iteratively |

## Success Metrics

- Successfully parse 80% of standard resume formats
- Extract contact info with >90% accuracy
- Identify major sections (experience, education) with >85% accuracy
- Parse time <5 seconds for typical resume
- Zero crashes on malformed documents

## Next Steps

After completing Phase 2:
- Use parsed content as input for grammar checking (Phase 3)
- Feed structured data to Claude API for analysis (Phase 4)
- Optimize section identification for ATS (Phase 5)
