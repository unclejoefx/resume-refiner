# Phase 3: Grammar and Basic Analysis - Detailed Specification

**Timeline**: Week 3-4
**Status**: Not Started
**Dependencies**: Phase 2 (Document Processing)

## Objectives

Implement grammar checking, spell checking, and basic resume scoring functionality. Create UI components to display grammar issues and suggestions, and establish a foundation for resume quality assessment.

## Tasks Breakdown

### 3.1 Install Grammar Checking Library

**Task**: Add grammar checking capabilities to the backend

**Steps**:
1. Update `backend/requirements.txt` to add:
   ```
   language-tool-python==2.7.1
   ```

2. Install dependencies:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Note: language-tool-python will download LanguageTool on first use (~200MB)

**Deliverables**:
- Grammar checking library installed
- Dependencies documented

**Acceptance Criteria**:
- Can import language_tool_python without errors
- LanguageTool initializes successfully

---

### 3.2 Create Grammar Checking Service

**Task**: Implement service to check grammar and spelling

**Steps**:
1. Create `backend/app/services/grammar_checker.py`:
   ```python
   import language_tool_python
   from typing import List, Dict, Optional
   from pydantic import BaseModel

   class GrammarIssue(BaseModel):
       message: str
       context: str
       offset: int
       length: int
       rule_id: str
       category: str
       suggestions: List[str] = []
       severity: str  # "error", "warning", "info"

   class GrammarCheckResult(BaseModel):
       text: str
       issues: List[GrammarIssue]
       total_issues: int
       error_count: int
       warning_count: int

   class GrammarChecker:
       def __init__(self):
           # Initialize with English language
           self.tool = language_tool_python.LanguageTool('en-US')

       def check_text(self, text: str) -> GrammarCheckResult:
           """Check text for grammar and spelling issues"""
           if not text or not text.strip():
               return GrammarCheckResult(
                   text=text,
                   issues=[],
                   total_issues=0,
                   error_count=0,
                   warning_count=0
               )

           matches = self.tool.check(text)
           issues = []

           for match in matches:
               # Determine severity based on rule category
               severity = self._determine_severity(match)

               issue = GrammarIssue(
                   message=match.message,
                   context=match.context,
                   offset=match.offset,
                   length=match.errorLength,
                   rule_id=match.ruleId,
                   category=match.category,
                   suggestions=match.replacements[:3],  # Limit to top 3
                   severity=severity
               )
               issues.append(issue)

           # Count by severity
           error_count = sum(1 for issue in issues if issue.severity == "error")
           warning_count = sum(1 for issue in issues if issue.severity == "warning")

           return GrammarCheckResult(
               text=text,
               issues=issues,
               total_issues=len(issues),
               error_count=error_count,
               warning_count=warning_count
           )

       def _determine_severity(self, match) -> str:
           """Determine severity based on rule category"""
           error_categories = [
               "TYPOS",
               "GRAMMAR",
               "COMPOUNDING"
           ]

           if match.category in error_categories:
               return "error"
           elif "STYLE" in match.category or "REDUNDANCY" in match.category:
               return "warning"
           else:
               return "info"

       def check_resume_sections(
           self,
           contact_info: Optional[str] = None,
           summary: Optional[str] = None,
           experience_items: List[str] = [],
           education_items: List[str] = [],
       ) -> Dict[str, GrammarCheckResult]:
           """Check multiple resume sections and return results for each"""
           results = {}

           if summary:
               results["summary"] = self.check_text(summary)

           # Check experience descriptions
           for i, exp_text in enumerate(experience_items):
               if exp_text:
                   results[f"experience_{i}"] = self.check_text(exp_text)

           return results

       def __del__(self):
           """Clean up LanguageTool instance"""
           if hasattr(self, 'tool'):
               self.tool.close()
   ```

2. Add models to `backend/app/models/analysis.py`:
   ```python
   from pydantic import BaseModel
   from typing import List, Dict, Optional

   class GrammarIssueModel(BaseModel):
       message: str
       context: str
       offset: int
       length: int
       rule_id: str
       category: str
       suggestions: List[str] = []
       severity: str

   class SectionGrammarResult(BaseModel):
       section_name: str
       issues: List[GrammarIssueModel]
       issue_count: int

   class ResumeScore(BaseModel):
       overall_score: int  # 0-100
       grammar_score: int  # 0-100
       completeness_score: int  # 0-100
       section_scores: Dict[str, int] = {}

   class BasicAnalysisResult(BaseModel):
       resume_id: str
       grammar_results: List[SectionGrammarResult]
       total_grammar_issues: int
       score: ResumeScore
       suggestions: List[str] = []
   ```

**Deliverables**:
- Grammar checking service with issue detection
- Severity classification for issues
- Support for checking multiple sections

**Acceptance Criteria**:
- Can detect spelling errors
- Can detect grammar mistakes
- Returns suggestions for corrections
- Classifies issues by severity
- Handles empty or None text gracefully

---

### 3.3 Implement Basic Scoring Algorithm

**Task**: Create algorithm to score resume quality

**Steps**:
1. Create `backend/app/services/scorer.py`:
   ```python
   from typing import Dict, List
   from app.models.resume import ResumeContent
   from app.services.grammar_checker import GrammarCheckResult

   class ResumeScorer:
       def __init__(self):
           self.weights = {
               "grammar": 0.3,
               "completeness": 0.4,
               "structure": 0.3
           }

       def calculate_score(
           self,
           content: ResumeContent,
           grammar_results: Dict[str, GrammarCheckResult]
       ) -> Dict[str, any]:
           """Calculate overall resume score"""
           grammar_score = self._calculate_grammar_score(grammar_results)
           completeness_score = self._calculate_completeness_score(content)
           structure_score = self._calculate_structure_score(content)

           overall_score = (
               grammar_score * self.weights["grammar"] +
               completeness_score * self.weights["completeness"] +
               structure_score * self.weights["structure"]
           )

           return {
               "overall_score": round(overall_score),
               "grammar_score": grammar_score,
               "completeness_score": completeness_score,
               "structure_score": structure_score,
               "section_scores": {
                   "contact_info": self._score_contact_info(content.contact_info),
                   "summary": self._score_summary(content.summary),
                   "experience": self._score_experience(content.experience),
                   "education": self._score_education(content.education),
                   "skills": self._score_skills(content.skills),
               }
           }

       def _calculate_grammar_score(
           self,
           grammar_results: Dict[str, GrammarCheckResult]
       ) -> int:
           """Score based on grammar issues (fewer issues = higher score)"""
           if not grammar_results:
               return 100

           total_issues = sum(result.total_issues for result in grammar_results.values())
           total_errors = sum(result.error_count for result in grammar_results.values())

           # Penalize errors more than warnings
           penalty = (total_errors * 5) + (total_issues - total_errors) * 2
           score = max(0, 100 - penalty)

           return score

       def _calculate_completeness_score(self, content: ResumeContent) -> int:
           """Score based on presence of key sections"""
           score = 0

           # Contact info (20 points)
           if content.contact_info.name:
               score += 5
           if content.contact_info.email:
               score += 5
           if content.contact_info.phone:
               score += 5
           if content.contact_info.linkedin:
               score += 5

           # Summary (15 points)
           if content.summary and len(content.summary) > 50:
               score += 15

           # Experience (30 points)
           if len(content.experience) > 0:
               score += 15
           if len(content.experience) >= 2:
               score += 10
           if any(exp.description for exp in content.experience):
               score += 5

           # Education (20 points)
           if len(content.education) > 0:
               score += 20

           # Skills (15 points)
           if len(content.skills) >= 3:
               score += 10
           if len(content.skills) >= 8:
               score += 5

           return min(100, score)

       def _calculate_structure_score(self, content: ResumeContent) -> int:
           """Score based on resume structure and organization"""
           score = 100

           # Penalize if sections are out of order or missing
           expected_sections = ["summary", "experience", "education", "skills"]
           section_titles = [s.title.lower() for s in content.sections]

           # Check if major sections exist
           for expected in expected_sections:
               if not any(expected in title for title in section_titles):
                   score -= 10

           # Bonus for having clear section headers
           if len(content.sections) >= 3:
               score += 10

           return max(0, min(100, score))

       def _score_contact_info(self, contact_info) -> int:
           """Score contact information section"""
           score = 0
           if contact_info.name:
               score += 25
           if contact_info.email:
               score += 25
           if contact_info.phone:
               score += 25
           if contact_info.linkedin:
               score += 25
           return score

       def _score_summary(self, summary: str) -> int:
           """Score professional summary"""
           if not summary:
               return 0
           if len(summary) < 50:
               return 30
           if len(summary) > 500:
               return 70
           return 100

       def _score_experience(self, experience: List) -> int:
           """Score work experience section"""
           if not experience:
               return 0

           score = min(50, len(experience) * 25)

           # Bonus for detailed descriptions
           has_descriptions = sum(1 for exp in experience if exp.description)
           score += min(50, has_descriptions * 15)

           return min(100, score)

       def _score_education(self, education: List) -> int:
           """Score education section"""
           if not education:
               return 0
           return min(100, len(education) * 50)

       def _score_skills(self, skills: List[str]) -> int:
           """Score skills section"""
           if not skills:
               return 0
           if len(skills) < 3:
               return 30
           if len(skills) < 8:
               return 70
           return 100

       def generate_suggestions(
           self,
           content: ResumeContent,
           scores: Dict[str, any]
       ) -> List[str]:
           """Generate improvement suggestions based on scores"""
           suggestions = []

           # Grammar suggestions
           if scores["grammar_score"] < 80:
               suggestions.append("Review and fix grammar and spelling errors throughout your resume")

           # Completeness suggestions
           if not content.contact_info.email:
               suggestions.append("Add a professional email address to your contact information")

           if not content.contact_info.phone:
               suggestions.append("Include a phone number for employers to contact you")

           if not content.summary or len(content.summary) < 50:
               suggestions.append("Add a professional summary that highlights your key qualifications")

           if len(content.experience) == 0:
               suggestions.append("Include your work experience with detailed descriptions")

           if len(content.experience) > 0:
               no_descriptions = [exp for exp in content.experience if not exp.description]
               if no_descriptions:
                   suggestions.append("Add bullet points describing your achievements in each role")

           if len(content.education) == 0:
               suggestions.append("Add your educational background")

           if len(content.skills) < 5:
               suggestions.append("Expand your skills section to include more relevant technical and soft skills")

           # Structure suggestions
           if scores["structure_score"] < 80:
               suggestions.append("Ensure your resume follows a clear structure: Summary, Experience, Education, Skills")

           return suggestions[:8]  # Limit to top 8 suggestions
   ```

**Deliverables**:
- Scoring algorithm for resume quality
- Section-by-section scoring
- Weighted overall score calculation
- Suggestion generation based on scores

**Acceptance Criteria**:
- Generates scores between 0-100
- Considers grammar, completeness, and structure
- Provides actionable suggestions
- Handles incomplete resumes gracefully

---

### 3.4 Create Analysis Endpoint

**Task**: Add API endpoint for grammar checking and scoring

**Steps**:
1. Create `backend/app/routers/analyze.py`:
   ```python
   from fastapi import APIRouter, HTTPException
   from app.models.analysis import BasicAnalysisResult, SectionGrammarResult
   from app.models.resume import ResumeScore
   from app.services.grammar_checker import GrammarChecker
   from app.services.scorer import ResumeScorer
   from app.services.parser import ResumeParser
   from app.config import settings
   import os

   router = APIRouter()
   grammar_checker = GrammarChecker()
   scorer = ResumeScorer()
   parser = ResumeParser()

   @router.post("/analyze/basic/{upload_id}", response_model=BasicAnalysisResult)
   async def analyze_basic(upload_id: str):
       """Perform basic analysis: grammar check and scoring"""
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

           # Check grammar for each section
           grammar_results_list = []

           if content.summary:
               result = grammar_checker.check_text(content.summary)
               grammar_results_list.append(SectionGrammarResult(
                   section_name="Professional Summary",
                   issues=[issue.dict() for issue in result.issues],
                   issue_count=result.total_issues
               ))

           # Check each experience item
           for i, exp in enumerate(content.experience):
               if exp.description:
                   exp_text = " ".join(exp.description)
                   result = grammar_checker.check_text(exp_text)
                   grammar_results_list.append(SectionGrammarResult(
                       section_name=f"Experience: {exp.company or f'Position {i+1}'}",
                       issues=[issue.dict() for issue in result.issues],
                       issue_count=result.total_issues
                   ))

           # Calculate grammar results dict for scoring
           grammar_dict = {}
           if content.summary:
               grammar_dict["summary"] = grammar_checker.check_text(content.summary)

           # Calculate scores
           scores = scorer.calculate_score(content, grammar_dict)
           suggestions = scorer.generate_suggestions(content, scores)

           # Total grammar issues
           total_issues = sum(gr.issue_count for gr in grammar_results_list)

           return BasicAnalysisResult(
               resume_id=upload_id,
               grammar_results=grammar_results_list,
               total_grammar_issues=total_issues,
               score=ResumeScore(**scores),
               suggestions=suggestions
           )

       except Exception as e:
           raise HTTPException(
               status_code=500,
               detail=f"Error analyzing resume: {str(e)}"
           )
   ```

2. Update `backend/app/main.py` to include analyze router:
   ```python
   from app.routers import upload, parse, analyze

   # ... existing code ...

   app.include_router(analyze.router, prefix="/api", tags=["analyze"])
   ```

**Deliverables**:
- Analysis endpoint that combines grammar checking and scoring
- Structured response with all analysis results
- Error handling

**Acceptance Criteria**:
- Endpoint returns grammar issues by section
- Returns overall score and subscores
- Includes actionable suggestions
- Handles missing sections gracefully

---

### 3.5 Create Analysis Results UI Components

**Task**: Build React components to display analysis results

**Steps**:
1. Update `src/types/resume.ts`:
   ```typescript
   export interface GrammarIssue {
     message: string;
     context: string;
     offset: number;
     length: number;
     rule_id: string;
     category: string;
     suggestions: string[];
     severity: string;
   }

   export interface SectionGrammarResult {
     section_name: string;
     issues: GrammarIssue[];
     issue_count: number;
   }

   export interface ResumeScore {
     overall_score: number;
     grammar_score: number;
     completeness_score: number;
     structure_score: number;
     section_scores: {
       contact_info: number;
       summary: number;
       experience: number;
       education: number;
       skills: number;
     };
   }

   export interface BasicAnalysisResult {
     resume_id: string;
     grammar_results: SectionGrammarResult[];
     total_grammar_issues: number;
     score: ResumeScore;
     suggestions: string[];
   }
   ```

2. Create `src/components/ScoreDisplay.tsx`:
   ```typescript
   import { ResumeScore } from '../types/resume';

   interface ScoreDisplayProps {
     score: ResumeScore;
   }

   const ScoreDisplay = ({ score }: ScoreDisplayProps) => {
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
           Resume Score
         </h2>

         {/* Overall Score */}
         <div className="mb-6">
           <div className="flex items-center justify-between mb-2">
             <span className="text-lg font-semibold">Overall Score</span>
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
         </div>

         {/* Subscores */}
         <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
           <div className={`p-4 rounded-lg ${getScoreBackground(score.grammar_score)}`}>
             <div className="text-sm text-gray-600 mb-1">Grammar</div>
             <div className={`text-2xl font-bold ${getScoreColor(score.grammar_score)}`}>
               {score.grammar_score}
             </div>
           </div>

           <div className={`p-4 rounded-lg ${getScoreBackground(score.completeness_score)}`}>
             <div className="text-sm text-gray-600 mb-1">Completeness</div>
             <div className={`text-2xl font-bold ${getScoreColor(score.completeness_score)}`}>
               {score.completeness_score}
             </div>
           </div>

           <div className={`p-4 rounded-lg ${getScoreBackground(score.structure_score)}`}>
             <div className="text-sm text-gray-600 mb-1">Structure</div>
             <div className={`text-2xl font-bold ${getScoreColor(score.structure_score)}`}>
               {score.structure_score}
             </div>
           </div>
         </div>
       </div>
     );
   };

   export default ScoreDisplay;
   ```

3. Create `src/components/GrammarIssues.tsx`:
   ```typescript
   import { SectionGrammarResult } from '../types/resume';

   interface GrammarIssuesProps {
     grammarResults: SectionGrammarResult[];
   }

   const GrammarIssues = ({ grammarResults }: GrammarIssuesProps) => {
     const getSeverityColor = (severity: string) => {
       switch (severity) {
         case 'error':
           return 'bg-red-100 text-red-800 border-red-200';
         case 'warning':
           return 'bg-yellow-100 text-yellow-800 border-yellow-200';
         default:
           return 'bg-blue-100 text-blue-800 border-blue-200';
       }
     };

     const totalIssues = grammarResults.reduce(
       (sum, result) => sum + result.issue_count,
       0
     );

     if (totalIssues === 0) {
       return (
         <div className="bg-white rounded-lg shadow-md p-6 mb-6">
           <h2 className="text-2xl font-bold text-gray-900 mb-4">
             Grammar Check
           </h2>
           <div className="bg-green-50 border border-green-200 rounded-lg p-4">
             <p className="text-green-700 font-semibold">
               ✓ No grammar or spelling issues found!
             </p>
           </div>
         </div>
       );
     }

     return (
       <div className="bg-white rounded-lg shadow-md p-6 mb-6">
         <h2 className="text-2xl font-bold text-gray-900 mb-2">
           Grammar Check
         </h2>
         <p className="text-gray-600 mb-4">
           Found {totalIssues} issue{totalIssues !== 1 ? 's' : ''} across your resume
         </p>

         <div className="space-y-4">
           {grammarResults.map((result, index) => (
             <div key={index}>
               <h3 className="font-semibold text-gray-800 mb-2">
                 {result.section_name} ({result.issue_count} issue{result.issue_count !== 1 ? 's' : ''})
               </h3>

               <div className="space-y-2">
                 {result.issues.map((issue, issueIndex) => (
                   <div
                     key={issueIndex}
                     className={`border rounded-lg p-3 ${getSeverityColor(issue.severity)}`}
                   >
                     <div className="font-medium mb-1">{issue.message}</div>
                     {issue.context && (
                       <div className="text-sm mb-2 font-mono bg-white bg-opacity-50 p-2 rounded">
                         {issue.context}
                       </div>
                     )}
                     {issue.suggestions.length > 0 && (
                       <div className="text-sm">
                         <strong>Suggestions:</strong>{' '}
                         {issue.suggestions.join(', ')}
                       </div>
                     )}
                   </div>
                 ))}
               </div>
             </div>
           ))}
         </div>
       </div>
     );
   };

   export default GrammarIssues;
   ```

4. Create `src/components/SuggestionCard.tsx`:
   ```typescript
   interface SuggestionCardProps {
     suggestions: string[];
   }

   const SuggestionCard = ({ suggestions }: SuggestionCardProps) => {
     if (suggestions.length === 0) {
       return null;
     }

     return (
       <div className="bg-white rounded-lg shadow-md p-6 mb-6">
         <h2 className="text-2xl font-bold text-gray-900 mb-4">
           Improvement Suggestions
         </h2>

         <ul className="space-y-2">
           {suggestions.map((suggestion, index) => (
             <li
               key={index}
               className="flex items-start p-3 bg-blue-50 border border-blue-200 rounded-lg"
             >
               <span className="text-blue-600 font-bold mr-3">→</span>
               <span className="text-gray-800">{suggestion}</span>
             </li>
           ))}
         </ul>
       </div>
     );
   };

   export default SuggestionCard;
   ```

5. Create `src/components/AnalysisResults.tsx`:
   ```typescript
   import { BasicAnalysisResult } from '../types/resume';
   import ScoreDisplay from './ScoreDisplay';
   import GrammarIssues from './GrammarIssues';
   import SuggestionCard from './SuggestionCard';

   interface AnalysisResultsProps {
     analysis: BasicAnalysisResult;
   }

   const AnalysisResults = ({ analysis }: AnalysisResultsProps) => {
     return (
       <div>
         <ScoreDisplay score={analysis.score} />
         <GrammarIssues grammarResults={analysis.grammar_results} />
         <SuggestionCard suggestions={analysis.suggestions} />
       </div>
     );
   };

   export default AnalysisResults;
   ```

6. Update `src/components/UploadSection.tsx` to trigger analysis:
   ```typescript
   // After parsing, trigger basic analysis
   const parseResponse = await api.post<ParseResponse>(`/api/parse/${uploadResponse.data.upload_id}`);

   const analysisResponse = await api.post<BasicAnalysisResult>(
     `/api/analyze/basic/${uploadResponse.data.upload_id}`
   );

   navigate('/results', {
     state: {
       resumeData: parseResponse.data,
       analysisData: analysisResponse.data
     }
   });
   ```

7. Update `src/pages/Results.tsx`:
   ```typescript
   import AnalysisResults from '../components/AnalysisResults';
   import { BasicAnalysisResult } from '../types/resume';

   const Results = () => {
     const location = useLocation();
     const [resumeData] = useState<ParseResponse | null>(
       location.state?.resumeData || null
     );
     const [analysisData] = useState<BasicAnalysisResult | null>(
       location.state?.analysisData || null
     );

     return (
       <div className="container mx-auto px-4 py-16">
         <div className="mb-8">
           <Link to="/upload" className="text-blue-600 hover:underline">
             ← Upload another resume
           </Link>
         </div>

         {analysisData && <AnalysisResults analysis={analysisData} />}
         {resumeData && <ResumeDisplay resume={resumeData} />}
       </div>
     );
   };
   ```

**Deliverables**:
- Score display component with visual indicators
- Grammar issues display with severity colors
- Suggestions list component
- Integrated analysis results view

**Acceptance Criteria**:
- Score displays with color coding (red/yellow/green)
- Grammar issues grouped by section
- Suggestions displayed in readable format
- Responsive design on all screen sizes
- Loading states during analysis

---

## Testing Checklist

- [ ] Grammar checker detects spelling errors
- [ ] Grammar checker detects grammar mistakes
- [ ] Scoring algorithm produces reasonable scores
- [ ] Suggestions are actionable and relevant
- [ ] Analysis endpoint returns complete results
- [ ] UI displays scores correctly
- [ ] Grammar issues display with proper formatting
- [ ] Can navigate through full upload-to-results flow
- [ ] Unit tests pass for grammar checker
- [ ] Unit tests pass for scorer

## Dependencies

- Phase 2 (Document Processing) must be completed
- Parsed resume content needed for analysis

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| LanguageTool download/initialization slow | Show loading indicator; consider caching |
| False positives in grammar checking | Allow users to dismiss issues; focus on high-confidence errors |
| Scoring algorithm too harsh/lenient | Iterate based on testing; make weights configurable |
| Large resumes slow to analyze | Add timeout handling; show progress |

## Success Metrics

- Grammar check completes in <10 seconds for typical resume
- Grammar detection accuracy >85%
- Score correlates with human evaluation
- Suggestions actionable in >90% of cases
- Zero crashes on edge cases

## Next Steps

After completing Phase 3:
- Integrate Claude API for advanced content analysis (Phase 4)
- Build on scoring for ATS optimization (Phase 5)
- Use grammar results in final export (Phase 6)
