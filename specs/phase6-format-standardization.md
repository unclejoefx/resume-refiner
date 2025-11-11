# Phase 6: Format Standardization - Detailed Specification

**Timeline**: Week 6-7
**Status**: Not Started
**Dependencies**: Phase 2 (Document Processing), Phase 5 (ATS Optimization)

## Objectives

Implement functionality to convert resumes to standardized, ATS-friendly formats. Generate clean, professional PDF and DOCX files with consistent formatting, applying best practices from ATS analysis.

## Tasks Breakdown

### 6.1 Install Document Generation Libraries

**Task**: Add libraries for creating PDF and DOCX files

**Steps**:
1. Update `backend/requirements.txt`:
   ```
   reportlab==4.0.7
   weasyprint==60.1
   python-docx==1.1.0  # Already added in Phase 2
   ```

2. Install system dependencies for WeasyPrint (if using):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

   # macOS
   brew install python cairo pango gdk-pixbuf libffi
   ```

3. Install Python dependencies:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

**Deliverables**:
- Document generation libraries installed
- System dependencies configured

**Acceptance Criteria**:
- Can import reportlab and python-docx
- Libraries initialize without errors

---

### 6.2 Create Resume Templates

**Task**: Design standardized resume templates

**Steps**:
1. Create `backend/app/templates/resume_styles.py`:
   ```python
   from typing import Dict

   class ResumeStyles:
       """Standard resume styles for consistent formatting"""

       COLORS = {
           "primary": "#2C3E50",
           "secondary": "#34495E",
           "accent": "#3498DB",
           "text": "#2C3E50",
           "light_text": "#7F8C8D",
       }

       FONTS = {
           "heading": "Helvetica-Bold",
           "body": "Helvetica",
           "size": {
               "name": 18,
               "heading": 12,
               "subheading": 10,
               "body": 10,
               "small": 9,
           }
       }

       SPACING = {
           "section_margin": 12,
           "item_margin": 6,
           "line_height": 1.2,
       }

       @classmethod
       def get_docx_styles(cls) -> Dict:
           """Get styles for DOCX generation"""
           return {
               "font_name": "Calibri",
               "font_sizes": {
                   "name": 16,
                   "heading": 12,
                   "subheading": 11,
                   "body": 11,
               },
               "colors": cls.COLORS,
               "spacing": cls.SPACING,
           }
   ```

**Deliverables**:
- Standardized style definitions
- Color schemes
- Font specifications
- Spacing guidelines

**Acceptance Criteria**:
- Styles follow ATS best practices
- Consistent across PDF and DOCX
- Professional appearance

---

### 6.3 Implement PDF Generator

**Task**: Create service to generate PDF resumes

**Steps**:
1. Create `backend/app/services/pdf_generator.py`:
   ```python
   from reportlab.lib.pagesizes import letter
   from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
   from reportlab.lib.units import inch
   from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
   from reportlab.lib import colors
   from reportlab.lib.enums import TA_LEFT, TA_CENTER
   from app.models.resume import ResumeContent
   from app.templates.resume_styles import ResumeStyles
   import os

   class PDFGenerator:
       def __init__(self):
           self.styles = getSampleStyleSheet()
           self._setup_custom_styles()

       def _setup_custom_styles(self):
           """Setup custom paragraph styles"""
           # Name style
           self.styles.add(ParagraphStyle(
               name='Name',
               parent=self.styles['Heading1'],
               fontSize=ResumeStyles.FONTS["size"]["name"],
               textColor=colors.HexColor(ResumeStyles.COLORS["primary"]),
               alignment=TA_CENTER,
               spaceAfter=6,
           ))

           # Section heading style
           self.styles.add(ParagraphStyle(
               name='SectionHeading',
               parent=self.styles['Heading2'],
               fontSize=ResumeStyles.FONTS["size"]["heading"],
               textColor=colors.HexColor(ResumeStyles.COLORS["primary"]),
               borderColor=colors.HexColor(ResumeStyles.COLORS["accent"]),
               borderWidth=0,
               borderPadding=0,
               spaceBefore=12,
               spaceAfter=6,
               borderBottom=2,
           ))

           # Job title style
           self.styles.add(ParagraphStyle(
               name='JobTitle',
               parent=self.styles['Normal'],
               fontSize=ResumeStyles.FONTS["size"]["subheading"],
               textColor=colors.HexColor(ResumeStyles.COLORS["text"]),
               fontName='Helvetica-Bold',
               spaceAfter=2,
           ))

           # Company style
           self.styles.add(ParagraphStyle(
               name='Company',
               parent=self.styles['Normal'],
               fontSize=ResumeStyles.FONTS["size"]["body"],
               textColor=colors.HexColor(ResumeStyles.COLORS["secondary"]),
               fontName='Helvetica-Bold',
               spaceAfter=4,
           ))

           # Bullet style
           self.styles.add(ParagraphStyle(
               name='Bullet',
               parent=self.styles['Normal'],
               fontSize=ResumeStyles.FONTS["size"]["body"],
               textColor=colors.HexColor(ResumeStyles.COLORS["text"]),
               leftIndent=20,
               bulletIndent=10,
               spaceAfter=3,
           ))

       def generate_pdf(self, content: ResumeContent, output_path: str) -> str:
           """Generate a formatted PDF resume"""
           doc = SimpleDocTemplate(
               output_path,
               pagesize=letter,
               rightMargin=0.75*inch,
               leftMargin=0.75*inch,
               topMargin=0.75*inch,
               bottomMargin=0.75*inch,
           )

           story = []

           # Contact Information
           if content.contact_info.name:
               story.append(Paragraph(content.contact_info.name, self.styles['Name']))

           contact_parts = []
           if content.contact_info.email:
               contact_parts.append(content.contact_info.email)
           if content.contact_info.phone:
               contact_parts.append(content.contact_info.phone)
           if content.contact_info.linkedin:
               contact_parts.append(content.contact_info.linkedin)

           if contact_parts:
               contact_text = " • ".join(contact_parts)
               contact_style = ParagraphStyle(
                   'Contact',
                   parent=self.styles['Normal'],
                   fontSize=10,
                   alignment=TA_CENTER,
                   spaceAfter=12,
               )
               story.append(Paragraph(contact_text, contact_style))

           # Professional Summary
           if content.summary:
               story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeading']))
               story.append(Paragraph(content.summary, self.styles['Normal']))
               story.append(Spacer(1, 6))

           # Work Experience
           if content.experience:
               story.append(Paragraph("WORK EXPERIENCE", self.styles['SectionHeading']))

               for exp in content.experience:
                   if exp.title:
                       story.append(Paragraph(exp.title, self.styles['JobTitle']))
                   if exp.company:
                       company_text = exp.company
                       if exp.start_date or exp.end_date:
                           dates = f"{exp.start_date or ''} - {exp.end_date or 'Present'}"
                           company_text += f" | {dates}"
                       story.append(Paragraph(company_text, self.styles['Company']))

                   if exp.description:
                       for bullet in exp.description:
                           bullet_text = f"• {bullet}"
                           story.append(Paragraph(bullet_text, self.styles['Bullet']))

                   story.append(Spacer(1, 8))

           # Education
           if content.education:
               story.append(Paragraph("EDUCATION", self.styles['SectionHeading']))

               for edu in content.education:
                   if edu.degree:
                       story.append(Paragraph(edu.degree, self.styles['JobTitle']))
                   if edu.institution:
                       institution_text = edu.institution
                       if edu.start_date or edu.end_date:
                           dates = f"{edu.start_date or ''} - {edu.end_date or ''}"
                           institution_text += f" | {dates}"
                       story.append(Paragraph(institution_text, self.styles['Company']))

                   if edu.gpa:
                       story.append(Paragraph(f"GPA: {edu.gpa}", self.styles['Normal']))

                   story.append(Spacer(1, 6))

           # Skills
           if content.skills:
               story.append(Paragraph("SKILLS", self.styles['SectionHeading']))
               skills_text = ", ".join(content.skills)
               story.append(Paragraph(skills_text, self.styles['Normal']))

           # Build PDF
           doc.build(story)
           return output_path
   ```

**Deliverables**:
- PDF generation service
- Custom styles for resume sections
- Proper formatting and spacing
- Contact info, summary, experience, education, skills sections

**Acceptance Criteria**:
- Generates valid PDF files
- Formatting is clean and professional
- ATS-friendly layout (no tables, headers/footers)
- All sections render correctly

---

### 6.4 Implement DOCX Generator

**Task**: Create service to generate DOCX resumes

**Steps**:
1. Create `backend/app/services/docx_generator.py`:
   ```python
   from docx import Document
   from docx.shared import Pt, RGBColor, Inches
   from docx.enum.text import WD_ALIGN_PARAGRAPH
   from app.models.resume import ResumeContent
   from app.templates.resume_styles import ResumeStyles

   class DOCXGenerator:
       def __init__(self):
           self.styles = ResumeStyles.get_docx_styles()

       def generate_docx(self, content: ResumeContent, output_path: str) -> str:
           """Generate a formatted DOCX resume"""
           doc = Document()

           # Set margins
           sections = doc.sections
           for section in sections:
               section.top_margin = Inches(0.75)
               section.bottom_margin = Inches(0.75)
               section.left_margin = Inches(0.75)
               section.right_margin = Inches(0.75)

           # Contact Information
           if content.contact_info.name:
               name_para = doc.add_paragraph(content.contact_info.name)
               name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
               self._format_run(
                   name_para.runs[0],
                   size=self.styles["font_sizes"]["name"],
                   bold=True,
                   color=self.styles["colors"]["primary"]
               )

           # Contact details
           contact_parts = []
           if content.contact_info.email:
               contact_parts.append(content.contact_info.email)
           if content.contact_info.phone:
               contact_parts.append(content.contact_info.phone)
           if content.contact_info.linkedin:
               contact_parts.append(content.contact_info.linkedin)

           if contact_parts:
               contact_para = doc.add_paragraph(" • ".join(contact_parts))
               contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
               self._format_run(
                   contact_para.runs[0],
                   size=self.styles["font_sizes"]["body"]
               )

           # Professional Summary
           if content.summary:
               self._add_section_heading(doc, "PROFESSIONAL SUMMARY")
               summary_para = doc.add_paragraph(content.summary)
               self._format_run(
                   summary_para.runs[0],
                   size=self.styles["font_sizes"]["body"]
               )

           # Work Experience
           if content.experience:
               self._add_section_heading(doc, "WORK EXPERIENCE")

               for exp in content.experience:
                   if exp.title:
                       title_para = doc.add_paragraph(exp.title)
                       self._format_run(
                           title_para.runs[0],
                           size=self.styles["font_sizes"]["subheading"],
                           bold=True
                       )

                   if exp.company:
                       company_text = exp.company
                       if exp.start_date or exp.end_date:
                           dates = f"{exp.start_date or ''} - {exp.end_date or 'Present'}"
                           company_text += f" | {dates}"

                       company_para = doc.add_paragraph(company_text)
                       self._format_run(
                           company_para.runs[0],
                           size=self.styles["font_sizes"]["body"],
                           italic=True
                       )

                   if exp.description:
                       for bullet in exp.description:
                           bullet_para = doc.add_paragraph(bullet, style='List Bullet')
                           self._format_run(
                               bullet_para.runs[0],
                               size=self.styles["font_sizes"]["body"]
                           )

                   doc.add_paragraph()  # Spacing

           # Education
           if content.education:
               self._add_section_heading(doc, "EDUCATION")

               for edu in content.education:
                   if edu.degree:
                       degree_para = doc.add_paragraph(edu.degree)
                       self._format_run(
                           degree_para.runs[0],
                           size=self.styles["font_sizes"]["subheading"],
                           bold=True
                       )

                   if edu.institution:
                       institution_text = edu.institution
                       if edu.start_date or edu.end_date:
                           dates = f"{edu.start_date or ''} - {edu.end_date or ''}"
                           institution_text += f" | {dates}"

                       inst_para = doc.add_paragraph(institution_text)
                       self._format_run(
                           inst_para.runs[0],
                           size=self.styles["font_sizes"]["body"],
                           italic=True
                       )

                   if edu.gpa:
                       gpa_para = doc.add_paragraph(f"GPA: {edu.gpa}")
                       self._format_run(
                           gpa_para.runs[0],
                           size=self.styles["font_sizes"]["body"]
                       )

                   doc.add_paragraph()  # Spacing

           # Skills
           if content.skills:
               self._add_section_heading(doc, "SKILLS")
               skills_text = ", ".join(content.skills)
               skills_para = doc.add_paragraph(skills_text)
               self._format_run(
                   skills_para.runs[0],
                   size=self.styles["font_sizes"]["body"]
               )

           # Save document
           doc.save(output_path)
           return output_path

       def _add_section_heading(self, doc: Document, text: str):
           """Add a formatted section heading"""
           para = doc.add_paragraph(text)
           self._format_run(
               para.runs[0],
               size=self.styles["font_sizes"]["heading"],
               bold=True,
               color=self.styles["colors"]["primary"]
           )
           # Add line below heading
           para.add_run("\n" + "_" * 80)

       def _format_run(self, run, size=None, bold=False, italic=False, color=None):
           """Apply formatting to a run"""
           run.font.name = self.styles["font_name"]

           if size:
               run.font.size = Pt(size)

           if bold:
               run.font.bold = True

           if italic:
               run.font.italic = True

           if color:
               # Convert hex color to RGB
               hex_color = color.lstrip('#')
               rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
               run.font.color.rgb = RGBColor(*rgb)
   ```

**Deliverables**:
- DOCX generation service
- Formatted sections with proper styling
- Bullet points and spacing
- Professional appearance

**Acceptance Criteria**:
- Generates valid DOCX files
- Opens correctly in Microsoft Word and Google Docs
- Formatting is consistent with PDF version
- ATS-friendly structure

---

### 6.5 Create Export Endpoints

**Task**: Add API endpoints for exporting formatted resumes

**Steps**:
1. Update `backend/app/routers/export.py`:
   ```python
   from fastapi import APIRouter, HTTPException
   from fastapi.responses import FileResponse
   from app.services.parser import ResumeParser
   from app.services.pdf_generator import PDFGenerator
   from app.services.docx_generator import DOCXGenerator
   from app.config import settings
   import os

   router = APIRouter()
   parser = ResumeParser()
   pdf_generator = PDFGenerator()
   docx_generator = DOCXGenerator()

   @router.get("/export/{upload_id}/pdf")
   async def export_pdf(upload_id: str):
       """Export resume as formatted PDF"""
       # Find the original file
       file_path = None
       for ext in [".pdf", ".docx"]:
           potential_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}{ext}")
           if os.path.exists(potential_path):
               file_path = potential_path
               file_type = ext[1:]
               break

       if not file_path:
           raise HTTPException(status_code=404, detail="Upload not found")

       try:
           # Parse the document
           if file_type == "pdf":
               content = parser.parse_pdf(file_path)
           else:
               content = parser.parse_docx(file_path)

           # Generate formatted PDF
           output_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}_formatted.pdf")
           pdf_generator.generate_pdf(content, output_path)

           # Return file
           return FileResponse(
               output_path,
               media_type="application/pdf",
               filename=f"resume_formatted.pdf"
           )

       except Exception as e:
           raise HTTPException(
               status_code=500,
               detail=f"Error generating PDF: {str(e)}"
           )

   @router.get("/export/{upload_id}/docx")
   async def export_docx(upload_id: str):
       """Export resume as formatted DOCX"""
       # Find the original file
       file_path = None
       for ext in [".pdf", ".docx"]:
           potential_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}{ext}")
           if os.path.exists(potential_path):
               file_path = potential_path
               file_type = ext[1:]
               break

       if not file_path:
           raise HTTPException(status_code=404, detail="Upload not found")

       try:
           # Parse the document
           if file_type == "pdf":
               content = parser.parse_pdf(file_path)
           else:
               content = parser.parse_docx(file_path)

           # Generate formatted DOCX
           output_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}_formatted.docx")
           docx_generator.generate_docx(content, output_path)

           # Return file
           return FileResponse(
               output_path,
               media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
               filename=f"resume_formatted.docx"
           )

       except Exception as e:
           raise HTTPException(
               status_code=500,
               detail=f"Error generating DOCX: {str(e)}"
           )
   ```

2. Update `backend/app/main.py`:
   ```python
   from app.routers import upload, parse, analyze, export

   # ... existing code ...

   app.include_router(export.router, prefix="/api", tags=["export"])
   ```

**Deliverables**:
- PDF export endpoint
- DOCX export endpoint
- File download responses
- Error handling

**Acceptance Criteria**:
- Endpoints return downloadable files
- Files have appropriate MIME types
- Downloads work in browser
- Errors handled gracefully

---

### 6.6 Create Export UI

**Task**: Add download buttons to UI

**Steps**:
1. Create `src/components/ExportOptions.tsx`:
   ```typescript
   import { useState } from 'react';
   import { api } from '../services/api';

   interface ExportOptionsProps {
     resumeId: string;
   }

   const ExportOptions = ({ resumeId }: ExportOptionsProps) => {
     const [downloading, setDownloading] = useState<string | null>(null);

     const handleDownload = async (format: 'pdf' | 'docx') => {
       setDownloading(format);

       try {
         const response = await api.get(`/api/export/${resumeId}/${format}`, {
           responseType: 'blob',
         });

         // Create download link
         const url = window.URL.createObjectURL(new Blob([response.data]));
         const link = document.createElement('a');
         link.href = url;
         link.setAttribute('download', `resume_formatted.${format}`);
         document.body.appendChild(link);
         link.click();
         link.remove();
         window.URL.revokeObjectURL(url);
       } catch (err) {
         console.error(`Error downloading ${format}:`, err);
         alert(`Failed to download ${format.toUpperCase()} file`);
       } finally {
         setDownloading(null);
       }
     };

     return (
       <div className="bg-white rounded-lg shadow-md p-6 mb-6">
         <h2 className="text-2xl font-bold text-gray-900 mb-4">
           Download Formatted Resume
         </h2>
         <p className="text-gray-600 mb-4">
           Download your resume in a professional, ATS-friendly format.
         </p>

         <div className="flex gap-4">
           <button
             onClick={() => handleDownload('pdf')}
             disabled={downloading !== null}
             className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
           >
             {downloading === 'pdf' ? 'Downloading...' : 'Download PDF'}
           </button>

           <button
             onClick={() => handleDownload('docx')}
             disabled={downloading !== null}
             className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
           >
             {downloading === 'docx' ? 'Downloading...' : 'Download DOCX'}
           </button>
         </div>

         <p className="text-sm text-gray-500 mt-4">
           Both formats are optimized for Applicant Tracking Systems (ATS).
         </p>
       </div>
     );
   };

   export default ExportOptions;
   ```

2. Update `src/pages/Results.tsx`:
   ```typescript
   import ExportOptions from '../components/ExportOptions';

   const Results = () => {
     // ... existing code ...

     return (
       <div className="container mx-auto px-4 py-16">
         {/* ... existing content ... */}

         {resumeData && <ExportOptions resumeId={resumeData.resume_id} />}

         {/* ... rest of content ... */}
       </div>
     );
   };
   ```

**Deliverables**:
- Export options component
- Download buttons for PDF and DOCX
- Loading states
- Error handling

**Acceptance Criteria**:
- Download buttons work correctly
- Files download with appropriate names
- Loading states shown during download
- Errors displayed to user

---

## Testing Checklist

- [ ] PDF generation works without errors
- [ ] DOCX generation works without errors
- [ ] Generated PDFs open correctly
- [ ] Generated DOCX files open in Word/Google Docs
- [ ] Formatting is consistent and professional
- [ ] All resume sections included
- [ ] Download buttons work in UI
- [ ] Files download with correct names
- [ ] ATS-friendly formatting maintained
- [ ] No tables, headers, or footers in output

## Dependencies

- Phase 2 (Document Processing) for parsed content
- Phase 5 (ATS Optimization) for formatting guidelines

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| PDF generation errors on complex content | Implement fallbacks; test with various resumes |
| DOCX formatting differs across applications | Use standard styles; test in multiple apps |
| Large file sizes | Optimize fonts and images; compress if needed |
| Missing content in generated files | Validate parsed content before generation |

## Success Metrics

- Generated files pass ATS parsers
- Files render correctly in 95% of viewers
- Generation completes in <5 seconds
- User satisfaction with formatting
- Files maintain all original content

## Next Steps

After completing Phase 6:
- Polish UI and fix bugs (Phase 7)
- Deploy application (Phase 8)
- Consider adding custom templates
- Allow manual editing before export
