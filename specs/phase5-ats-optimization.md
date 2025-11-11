# Phase 5: ATS Optimization - Detailed Specification

**Timeline**: Week 5-6
**Status**: Not Started
**Dependencies**: Phase 2 (Document Processing), Phase 4 (Claude API Integration)

## Objectives

Implement Applicant Tracking System (ATS) optimization features including keyword analysis, format compatibility checking, and tailored suggestions based on job descriptions. Help users create ATS-friendly resumes that pass automated screening.

## Tasks Breakdown

### 5.1 Research ATS Best Practices

**Task**: Document ATS requirements and common issues

**Steps**:
1. Create `backend/docs/ats-guidelines.md`:
   ```markdown
   # ATS Guidelines and Best Practices

   ## Common ATS Systems
   - Workday
   - Taleo
   - iCIMS
   - Greenhouse
   - Lever

   ## ATS-Friendly Format Requirements

   ### File Format
   - PDF (modern, text-based)
   - DOCX (preferred by many ATS)
   - Avoid: Images, tables, headers/footers, text boxes

   ### Section Headers
   Standard headers ATS recognize:
   - Work Experience / Professional Experience / Employment History
   - Education
   - Skills / Technical Skills
   - Certifications
   - Summary / Professional Summary / Objective

   ### Formatting Rules
   - Use standard fonts (Arial, Calibri, Times New Roman)
   - Font size 10-12pt
   - Simple bullet points (•, -, *)
   - No graphics, images, or logos
   - No columns or text boxes
   - No headers/footers for important info
   - Clear section separation

   ### Content Best Practices
   - Use keywords from job description
   - Include both acronyms and full terms (e.g., "AI" and "Artificial Intelligence")
   - Avoid uncommon abbreviations
   - Use standard job titles
   - Include dates in standard format (MM/YYYY)
   - List skills explicitly

   ## Keyword Optimization
   - Extract keywords from job description
   - Match technical skills exactly
   - Include industry-specific terms
   - Use action verbs from job posting
   ```

2. Research common ATS parsing errors and solutions

**Deliverables**:
- ATS guidelines documentation
- List of ATS-friendly vs problematic elements

**Acceptance Criteria**:
- Guidelines based on actual ATS systems
- Cover all major formatting issues

---

### 5.2 Create ATS Scoring Service

**Task**: Implement service to score ATS compatibility

**Steps**:
1. Create `backend/app/services/ats_optimizer.py`:
   ```python
   from typing import List, Dict, Set, Tuple
   from pydantic import BaseModel
   from app.models.resume import ResumeContent
   import re

   class ATSIssue(BaseModel):
       category: str
       severity: str  # "error", "warning", "info"
       message: str
       suggestion: str

   class KeywordMatch(BaseModel):
       keyword: str
       found: bool
       context: str = ""

   class ATSScore(BaseModel):
       overall_score: int  # 0-100
       format_score: int
       keyword_score: int
       section_score: int
       issues: List[ATSIssue]
       matched_keywords: List[KeywordMatch]
       missing_keywords: List[str]

   class ATSOptimizer:
       def __init__(self):
           self.standard_sections = [
               "work experience",
               "professional experience",
               "employment",
               "education",
               "skills",
               "summary",
           ]

           self.problematic_terms = [
               "references available upon request",
               "curriculum vitae",
               "cv",
           ]

       def analyze_ats_compatibility(
           self,
           content: ResumeContent,
           job_description: str = None
       ) -> ATSScore:
           """Analyze resume for ATS compatibility"""
           issues = []

           # Check format compatibility
           format_score, format_issues = self._check_format(content)
           issues.extend(format_issues)

           # Check section headers
           section_score, section_issues = self._check_sections(content)
           issues.extend(section_issues)

           # Check keywords if job description provided
           keyword_score = 100
           matched_keywords = []
           missing_keywords = []

           if job_description:
               keyword_score, matched, missing = self._analyze_keywords(
                   content,
                   job_description
               )
               matched_keywords = matched
               missing_keywords = missing

               if missing_keywords:
                   issues.append(ATSIssue(
                       category="Keywords",
                       severity="warning",
                       message=f"Missing {len(missing_keywords)} key terms from job description",
                       suggestion=f"Consider adding: {', '.join(missing_keywords[:5])}"
                   ))

           # Calculate overall score
           weights = {
               "format": 0.4,
               "sections": 0.3,
               "keywords": 0.3
           }

           overall_score = int(
               format_score * weights["format"] +
               section_score * weights["sections"] +
               keyword_score * weights["keywords"]
           )

           return ATSScore(
               overall_score=overall_score,
               format_score=format_score,
               keyword_score=keyword_score,
               section_score=section_score,
               issues=issues,
               matched_keywords=matched_keywords,
               missing_keywords=missing_keywords
           )

       def _check_format(self, content: ResumeContent) -> Tuple[int, List[ATSIssue]]:
           """Check formatting compatibility"""
           score = 100
           issues = []

           # Check for problematic terms
           raw_text_lower = content.raw_text.lower()
           for term in self.problematic_terms:
               if term in raw_text_lower:
                   score -= 5
                   issues.append(ATSIssue(
                       category="Format",
                       severity="warning",
                       message=f"Contains potentially problematic term: '{term}'",
                       suggestion=f"Remove '{term}' as it may confuse ATS"
                   ))

           # Check for unusual characters
           unusual_chars = re.findall(r'[^\x00-\x7F]+', content.raw_text)
           if len(unusual_chars) > 10:
               score -= 10
               issues.append(ATSIssue(
                   category="Format",
                   severity="warning",
                   message="Contains many special characters",
                   suggestion="Use standard ASCII characters for better ATS compatibility"
               ))

           # Check text length (too short might indicate parsing issues)
           if len(content.raw_text) < 500:
               score -= 15
               issues.append(ATSIssue(
                   category="Format",
                   severity="error",
                   message="Resume appears very short",
                   suggestion="Ensure your resume has sufficient content and detail"
               ))

           return max(0, score), issues

       def _check_sections(self, content: ResumeContent) -> Tuple[int, List[ATSIssue]]:
           """Check section structure"""
           score = 100
           issues = []

           section_titles = [s.title.lower() for s in content.sections]

           # Check for standard sections
           required_sections = {
               "experience": ["experience", "work", "employment"],
               "education": ["education"],
               "skills": ["skills"],
           }

           for section_name, keywords in required_sections.items():
               found = any(
                   any(keyword in title for keyword in keywords)
                   for title in section_titles
               )

               if not found:
                   score -= 20
                   issues.append(ATSIssue(
                       category="Sections",
                       severity="error",
                       message=f"Missing standard section: {section_name}",
                       suggestion=f"Add a clearly labeled '{section_name.title()}' section"
                   ))

           # Check for non-standard section headers
           for section in content.sections:
               title_lower = section.title.lower()
               is_standard = any(
                   std in title_lower for std in self.standard_sections
               )

               if not is_standard and len(section.content) > 50:
                   score -= 5
                   issues.append(ATSIssue(
                       category="Sections",
                       severity="info",
                       message=f"Non-standard section header: '{section.title}'",
                       suggestion="Use standard headers like 'Work Experience' or 'Skills'"
                   ))

           # Check contact info completeness
           if not content.contact_info.email:
               score -= 15
               issues.append(ATSIssue(
                   category="Contact",
                   severity="error",
                   message="Missing email address",
                   suggestion="Add a professional email address"
               ))

           if not content.contact_info.phone:
               score -= 10
               issues.append(ATSIssue(
                   category="Contact",
                   severity="warning",
                   message="Missing phone number",
                   suggestion="Add a phone number for contact"
               ))

           return max(0, score), issues

       def _analyze_keywords(
           self,
           content: ResumeContent,
           job_description: str
       ) -> Tuple[int, List[KeywordMatch], List[str]]:
           """Analyze keyword matching with job description"""
           # Extract keywords from job description
           keywords = self._extract_keywords(job_description)

           # Check which keywords are in resume
           resume_text_lower = content.raw_text.lower()
           matched = []
           missing = []

           for keyword in keywords:
               keyword_lower = keyword.lower()
               if keyword_lower in resume_text_lower:
                   # Find context
                   context = self._find_keyword_context(resume_text_lower, keyword_lower)
                   matched.append(KeywordMatch(
                       keyword=keyword,
                       found=True,
                       context=context
                   ))
               else:
                   missing.append(keyword)

           # Calculate score based on match rate
           match_rate = len(matched) / len(keywords) if keywords else 1.0
           score = int(match_rate * 100)

           return score, matched, missing

       def _extract_keywords(self, job_description: str) -> List[str]:
           """Extract important keywords from job description"""
           # Common technical and professional terms
           keywords = set()

           # Extract capitalized words (potential skills/tools)
           capitalized = re.findall(r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b', job_description)
           keywords.update([w for w in capitalized if len(w) > 2])

           # Extract acronyms
           acronyms = re.findall(r'\b[A-Z]{2,}\b', job_description)
           keywords.update(acronyms)

           # Common skill categories
           skill_patterns = [
               r'\b\w+(?:Script|SQL|QL)\b',  # Programming languages
               r'\b(?:Python|Java|C\+\+|JavaScript|TypeScript|Ruby|Go|Rust|Swift)\b',
               r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Git)\b',  # Tech tools
               r'\b(?:React|Angular|Vue|Django|Flask|Node\.js|Express)\b',  # Frameworks
           ]

           for pattern in skill_patterns:
               matches = re.findall(pattern, job_description, re.IGNORECASE)
               keywords.update(matches)

           # Extract phrases after "experience with" or "knowledge of"
           phrases = re.findall(
               r'(?:experience with|knowledge of|proficiency in|expertise in)\s+([^,.]+)',
               job_description,
               re.IGNORECASE
           )
           for phrase in phrases:
               # Split and clean
               words = phrase.strip().split()
               if 1 <= len(words) <= 4:
                   keywords.add(phrase.strip())

           # Remove common words
           common_words = {'the', 'and', 'or', 'in', 'to', 'of', 'for', 'a', 'an', 'The', 'And'}
           keywords = {k for k in keywords if k not in common_words and len(k) > 2}

           return list(keywords)[:30]  # Limit to top 30

       def _find_keyword_context(self, text: str, keyword: str, context_length: int = 50) -> str:
           """Find context around keyword in text"""
           index = text.find(keyword)
           if index == -1:
               return ""

           start = max(0, index - context_length)
           end = min(len(text), index + len(keyword) + context_length)

           context = text[start:end].strip()
           if start > 0:
               context = "..." + context
           if end < len(text):
               context = context + "..."

           return context

       def generate_ats_suggestions(self, ats_score: ATSScore) -> List[str]:
           """Generate actionable ATS optimization suggestions"""
           suggestions = []

           if ats_score.overall_score < 70:
               suggestions.append(
                   "Your resume needs significant ATS optimization to improve chances of passing automated screening"
               )

           if ats_score.format_score < 80:
               suggestions.append(
                   "Simplify formatting: avoid tables, text boxes, headers/footers, and unusual fonts"
               )

           if ats_score.section_score < 80:
               suggestions.append(
                   "Use standard section headers like 'Work Experience', 'Education', and 'Skills'"
               )

           if ats_score.keyword_score < 70:
               suggestions.append(
                   f"Add more keywords from the job description. Missing: {', '.join(ats_score.missing_keywords[:5])}"
               )

           if len(ats_score.missing_keywords) > 0:
               suggestions.append(
                   "Review the job description and incorporate relevant keywords naturally into your experience"
               )

           # Add specific issue-based suggestions
           for issue in ats_score.issues[:3]:  # Top 3 issues
               if issue.severity == "error":
                   suggestions.append(issue.suggestion)

           return suggestions[:6]  # Limit to 6 suggestions
   ```

**Deliverables**:
- ATS compatibility scoring
- Format checking
- Section header validation
- Keyword extraction and matching
- Issue detection and suggestions

**Acceptance Criteria**:
- Scores resumes on ATS compatibility
- Identifies common ATS issues
- Extracts relevant keywords from job descriptions
- Provides actionable suggestions

---

### 5.3 Create ATS Models and Endpoint

**Task**: Add models and API endpoint for ATS analysis

**Steps**:
1. Update `backend/app/models/analysis.py`:
   ```python
   # Add to existing file

   class ATSIssueModel(BaseModel):
       category: str
       severity: str
       message: str
       suggestion: str

   class KeywordMatchModel(BaseModel):
       keyword: str
       found: bool
       context: str = ""

   class ATSScoreModel(BaseModel):
       overall_score: int
       format_score: int
       keyword_score: int
       section_score: int
       issues: List[ATSIssueModel]
       matched_keywords: List[KeywordMatchModel] = []
       missing_keywords: List[str] = []

   class ATSAnalysisResult(BaseModel):
       resume_id: str
       ats_score: ATSScoreModel
       suggestions: List[str]
       job_description_provided: bool
   ```

2. Update `backend/app/routers/analyze.py`:
   ```python
   from app.services.ats_optimizer import ATSOptimizer
   from app.models.analysis import ATSAnalysisResult, ATSScoreModel
   from pydantic import BaseModel

   ats_optimizer = ATSOptimizer()

   class ATSAnalysisRequest(BaseModel):
       job_description: Optional[str] = None

   @router.post("/analyze/ats/{upload_id}", response_model=ATSAnalysisResult)
   async def analyze_ats(upload_id: str, request: ATSAnalysisRequest = ATSAnalysisRequest()):
       """Analyze resume for ATS compatibility"""
       # Find and parse the file
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

           # Analyze ATS compatibility
           ats_score = ats_optimizer.analyze_ats_compatibility(
               content,
               request.job_description
           )

           # Generate suggestions
           suggestions = ats_optimizer.generate_ats_suggestions(ats_score)

           return ATSAnalysisResult(
               resume_id=upload_id,
               ats_score=ats_score.dict(),
               suggestions=suggestions,
               job_description_provided=request.job_description is not None
           )

       except Exception as e:
           raise HTTPException(
               status_code=500,
               detail=f"Error in ATS analysis: {str(e)}"
           )
   ```

**Deliverables**:
- ATS analysis models
- ATS analysis endpoint accepting optional job description
- Integration with parser and optimizer

**Acceptance Criteria**:
- Endpoint accepts job description optionally
- Returns ATS score and suggestions
- Handles errors gracefully

---

### 5.4 Create ATS Analysis UI Components

**Task**: Build UI for ATS optimization features

**Steps**:
1. Update `src/types/resume.ts`:
   ```typescript
   export interface ATSIssue {
     category: string;
     severity: string;
     message: string;
     suggestion: string;
   }

   export interface KeywordMatch {
     keyword: string;
     found: boolean;
     context: string;
   }

   export interface ATSScore {
     overall_score: number;
     format_score: number;
     keyword_score: number;
     section_score: number;
     issues: ATSIssue[];
     matched_keywords: KeywordMatch[];
     missing_keywords: string[];
   }

   export interface ATSAnalysisResult {
     resume_id: string;
     ats_score: ATSScore;
     suggestions: string[];
     job_description_provided: boolean;
   }
   ```

2. Create `src/components/JobDescriptionInput.tsx`:
   ```typescript
   import { useState } from 'react';

   interface JobDescriptionInputProps {
     onAnalyze: (jobDescription: string) => void;
     loading: boolean;
   }

   const JobDescriptionInput = ({ onAnalyze, loading }: JobDescriptionInputProps) => {
     const [jobDescription, setJobDescription] = useState('');

     const handleSubmit = (e: React.FormEvent) => {
       e.preventDefault();
       if (jobDescription.trim()) {
         onAnalyze(jobDescription);
       }
     };

     return (
       <div className="bg-white rounded-lg shadow-md p-6 mb-6">
         <h2 className="text-2xl font-bold text-gray-900 mb-4">
           ATS Optimization
         </h2>
         <p className="text-gray-600 mb-4">
           Paste a job description to see how well your resume matches and get
           keyword optimization suggestions.
         </p>

         <form onSubmit={handleSubmit}>
           <textarea
             className="w-full border border-gray-300 rounded-lg p-3 mb-4 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
             rows={8}
             placeholder="Paste job description here (optional)..."
             value={jobDescription}
             onChange={(e) => setJobDescription(e.target.value)}
           />

           <button
             type="submit"
             disabled={loading || !jobDescription.trim()}
             className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
           >
             {loading ? 'Analyzing...' : 'Analyze for ATS'}
           </button>
         </form>
       </div>
     );
   };

   export default JobDescriptionInput;
   ```

3. Create `src/components/ATSScoreDisplay.tsx`:
   ```typescript
   import { ATSScore } from '../types/resume';

   interface ATSScoreDisplayProps {
     score: ATSScore;
     jobDescriptionProvided: boolean;
   }

   const ATSScoreDisplay = ({ score, jobDescriptionProvided }: ATSScoreDisplayProps) => {
     const getScoreColor = (value: number) => {
       if (value >= 80) return 'text-green-600';
       if (value >= 60) return 'text-yellow-600';
       return 'text-red-600';
     };

     const getScoreBackground = (value: number) => {
       if (value >= 80) return 'bg-green-100';
       if (value >= 60) return 'bg-yellow-100';
       return 'bg-red-100';
     };

     return (
       <div className="bg-white rounded-lg shadow-md p-6 mb-6">
         <h2 className="text-2xl font-bold text-gray-900 mb-4">
           ATS Compatibility Score
         </h2>

         {/* Overall Score */}
         <div className="mb-6">
           <div className="flex items-center justify-between mb-2">
             <span className="text-lg font-semibold">ATS Friendly Score</span>
             <span className={`text-3xl font-bold ${getScoreColor(score.overall_score)}`}>
               {score.overall_score}/100
             </span>
           </div>
           <div className="w-full bg-gray-200 rounded-full h-3">
             <div
               className={`h-3 rounded-full ${
                 score.overall_score >= 80
                   ? 'bg-green-500'
                   : score.overall_score >= 60
                   ? 'bg-yellow-500'
                   : 'bg-red-500'
               }`}
               style={{ width: `${score.overall_score}%` }}
             ></div>
           </div>
           <p className="text-sm text-gray-600 mt-2">
             {score.overall_score >= 80
               ? 'Excellent! Your resume should pass most ATS systems.'
               : score.overall_score >= 60
               ? 'Good, but there is room for improvement.'
               : 'Needs work. Consider the suggestions below.'}
           </p>
         </div>

         {/* Subscores */}
         <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
           <div className={`p-4 rounded-lg ${getScoreBackground(score.format_score)}`}>
             <div className="text-sm text-gray-600 mb-1">Format</div>
             <div className={`text-2xl font-bold ${getScoreColor(score.format_score)}`}>
               {score.format_score}
             </div>
           </div>

           <div className={`p-4 rounded-lg ${getScoreBackground(score.section_score)}`}>
             <div className="text-sm text-gray-600 mb-1">Sections</div>
             <div className={`text-2xl font-bold ${getScoreColor(score.section_score)}`}>
               {score.section_score}
             </div>
           </div>

           {jobDescriptionProvided && (
             <div className={`p-4 rounded-lg ${getScoreBackground(score.keyword_score)}`}>
               <div className="text-sm text-gray-600 mb-1">Keywords</div>
               <div className={`text-2xl font-bold ${getScoreColor(score.keyword_score)}`}>
                 {score.keyword_score}
               </div>
             </div>
           )}
         </div>

         {/* Issues */}
         {score.issues.length > 0 && (
           <div>
             <h3 className="text-lg font-semibold text-gray-800 mb-3">
               Issues Found ({score.issues.length})
             </h3>
             <div className="space-y-2">
               {score.issues.map((issue, index) => {
                 const severityColor =
                   issue.severity === 'error'
                     ? 'border-red-300 bg-red-50'
                     : issue.severity === 'warning'
                     ? 'border-yellow-300 bg-yellow-50'
                     : 'border-blue-300 bg-blue-50';

                 return (
                   <div key={index} className={`border rounded-lg p-3 ${severityColor}`}>
                     <div className="font-medium text-gray-800">{issue.message}</div>
                     <div className="text-sm text-gray-600 mt-1">{issue.suggestion}</div>
                   </div>
                 );
               })}
             </div>
           </div>
         )}

         {/* Keywords */}
         {jobDescriptionProvided && (
           <div className="mt-6">
             {score.matched_keywords.length > 0 && (
               <div className="mb-4">
                 <h3 className="text-lg font-semibold text-gray-800 mb-2">
                   Matched Keywords ({score.matched_keywords.length})
                 </h3>
                 <div className="flex flex-wrap gap-2">
                   {score.matched_keywords.map((match, index) => (
                     <span
                       key={index}
                       className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm"
                       title={match.context}
                     >
                       ✓ {match.keyword}
                     </span>
                   ))}
                 </div>
               </div>
             )}

             {score.missing_keywords.length > 0 && (
               <div>
                 <h3 className="text-lg font-semibold text-gray-800 mb-2">
                   Missing Keywords ({score.missing_keywords.length})
                 </h3>
                 <div className="flex flex-wrap gap-2">
                   {score.missing_keywords.map((keyword, index) => (
                     <span
                       key={index}
                       className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm"
                     >
                       ✗ {keyword}
                     </span>
                   ))}
                 </div>
                 <p className="text-sm text-gray-600 mt-2">
                   Consider adding these keywords where relevant to your experience.
                 </p>
               </div>
             )}
           </div>
         )}
       </div>
     );
   };

   export default ATSScoreDisplay;
   ```

4. Update `src/pages/Results.tsx`:
   ```typescript
   import { useState } from 'react';
   import JobDescriptionInput from '../components/JobDescriptionInput';
   import ATSScoreDisplay from '../components/ATSScoreDisplay';
   import { ATSAnalysisResult } from '../types/resume';
   import { api } from '../services/api';

   const Results = () => {
     // ... existing state ...
     const [atsAnalysis, setAtsAnalysis] = useState<ATSAnalysisResult | null>(null);
     const [atsLoading, setAtsLoading] = useState(false);

     const handleATSAnalysis = async (jobDescription: string) => {
       if (!resumeData) return;

       setAtsLoading(true);
       try {
         const response = await api.post<ATSAnalysisResult>(
           `/api/analyze/ats/${resumeData.resume_id}`,
           { job_description: jobDescription }
         );
         setAtsAnalysis(response.data);
       } catch (err) {
         console.error('ATS analysis error:', err);
       } finally {
         setAtsLoading(false);
       }
     };

     return (
       <div className="container mx-auto px-4 py-16">
         {/* ... existing content ... */}

         <JobDescriptionInput onAnalyze={handleATSAnalysis} loading={atsLoading} />

         {atsAnalysis && (
           <ATSScoreDisplay
             score={atsAnalysis.ats_score}
             jobDescriptionProvided={atsAnalysis.job_description_provided}
           />
         )}

         {/* ... rest of existing content ... */}
       </div>
     );
   };
   ```

**Deliverables**:
- Job description input component
- ATS score display with subscores
- Issue list with severity indicators
- Keyword matching visualization
- Missing keywords display

**Acceptance Criteria**:
- Can paste job description for analysis
- ATS score displays clearly
- Issues categorized by severity
- Matched/missing keywords shown
- Responsive design

---

## Testing Checklist

- [ ] ATS scoring produces reasonable results
- [ ] Keyword extraction works for various job descriptions
- [ ] Format issues detected correctly
- [ ] Section header validation works
- [ ] UI displays ATS score correctly
- [ ] Keyword matching visualization clear
- [ ] Can analyze with and without job description
- [ ] Suggestions are actionable
- [ ] Handles edge cases (short resumes, unusual formats)

## Dependencies

- Phase 2 (Document Processing) for parsed content
- Basic analysis for comparison

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Keyword extraction too generic/specific | Use multiple extraction strategies; allow manual keyword input |
| ATS scoring doesn't match real ATS | Test with actual ATS systems; gather user feedback |
| Job descriptions vary widely | Robust parsing with fallbacks; focus on common patterns |
| False positives in issue detection | Tune thresholds based on testing |

## Success Metrics

- ATS score correlates with actual ATS pass rate
- Keyword extraction accuracy >75%
- Users find suggestions actionable
- Improved scores after applying suggestions
- <5 second analysis time

## Next Steps

After completing Phase 5:
- Use ATS guidelines in format standardization (Phase 6)
- Export ATS-optimized versions
- Consider adding industry-specific keyword databases
