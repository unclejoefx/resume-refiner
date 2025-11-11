# Phase 4: Claude API Integration - Detailed Specification

**Timeline**: Week 4-5
**Status**: Not Started
**Dependencies**: Phase 2 (Document Processing), Phase 3 (Grammar and Basic Analysis)

## Objectives

Integrate Anthropic's Claude API to provide AI-powered content analysis and improvement suggestions for resumes. Implement prompts for analyzing professional summaries, experience descriptions, and overall content quality.

## Tasks Breakdown

### 4.1 Install Claude API Client

**Task**: Add Anthropic SDK to the backend

**Steps**:
1. Update `backend/requirements.txt` to add:
   ```
   anthropic==0.18.1
   ```

2. Install dependencies:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Update `backend/.env.example`:
   ```
   CLAUDE_API_KEY=sk-ant-xxxxx
   ```

4. Ensure `backend/app/config.py` has CLAUDE_API_KEY in settings (already added in Phase 1)

**Deliverables**:
- Anthropic SDK installed
- API key configuration ready

**Acceptance Criteria**:
- Can import anthropic library without errors
- Configuration loads API key from environment

---

### 4.2 Create Claude Service

**Task**: Implement service to interact with Claude API

**Steps**:
1. Create `backend/app/services/claude_service.py`:
   ```python
   from anthropic import Anthropic, APIError
   from typing import List, Dict, Optional
   from pydantic import BaseModel
   from app.config import settings
   from app.models.resume import ResumeContent, ExperienceItem

   class ContentSuggestion(BaseModel):
       section: str
       original: str
       suggestion: str
       reason: str
       priority: str  # "high", "medium", "low"

   class ClaudeAnalysis(BaseModel):
       summary_analysis: Optional[str] = None
       summary_suggestions: List[str] = []
       experience_suggestions: List[ContentSuggestion] = []
       overall_feedback: str
       strengths: List[str] = []
       areas_for_improvement: List[str] = []

   class ClaudeService:
       def __init__(self):
           if not settings.CLAUDE_API_KEY:
               raise ValueError("CLAUDE_API_KEY not set in environment")
           self.client = Anthropic(api_key=settings.CLAUDE_API_KEY)
           self.model = "claude-3-5-sonnet-20241022"

       def analyze_resume(self, content: ResumeContent) -> ClaudeAnalysis:
           """Perform comprehensive resume analysis using Claude"""
           prompt = self._build_full_analysis_prompt(content)

           try:
               response = self.client.messages.create(
                   model=self.model,
                   max_tokens=4096,
                   messages=[{
                       "role": "user",
                       "content": prompt
                   }]
               )

               # Parse Claude's response
               analysis_text = response.content[0].text
               return self._parse_analysis_response(analysis_text, content)

           except APIError as e:
               raise Exception(f"Claude API error: {str(e)}")

       def analyze_summary(self, summary: str) -> Dict[str, any]:
           """Analyze and improve professional summary"""
           if not summary:
               return {
                   "analysis": "No professional summary found",
                   "suggestions": ["Add a professional summary to introduce yourself"],
                   "improved_version": None
               }

           prompt = f"""Analyze this professional summary from a resume and provide feedback:

   SUMMARY:
   {summary}

   Please provide:
   1. What works well (strengths)
   2. What could be improved
   3. An improved version that:
      - Uses strong action verbs
      - Quantifies achievements where possible
      - Is concise (2-3 sentences)
      - Highlights unique value proposition
      - Avoids clichés

   Format your response as:
   STRENGTHS:
   - [strength 1]
   - [strength 2]

   IMPROVEMENTS:
   - [improvement 1]
   - [improvement 2]

   IMPROVED VERSION:
   [your improved summary]
   """

           try:
               response = self.client.messages.create(
                   model=self.model,
                   max_tokens=1024,
                   messages=[{"role": "user", "content": prompt}]
               )

               result = self._parse_summary_response(response.content[0].text)
               return result

           except APIError as e:
               raise Exception(f"Claude API error: {str(e)}")

       def improve_experience_bullet(self, bullet: str, job_title: str = None) -> Dict[str, str]:
           """Improve a single experience bullet point"""
           context = f" for a {job_title}" if job_title else ""

           prompt = f"""Improve this resume bullet point{context}:

   ORIGINAL:
   {bullet}

   Create an improved version that:
   1. Starts with a strong action verb
   2. Quantifies impact where possible (even if estimated)
   3. Highlights results, not just responsibilities
   4. Is concise and impactful
   5. Uses professional language

   Also explain why your version is better.

   Format:
   IMPROVED:
   [improved bullet point]

   REASON:
   [brief explanation]
   """

           try:
               response = self.client.messages.create(
                   model=self.model,
                   max_tokens=512,
                   messages=[{"role": "user", "content": prompt}]
               )

               return self._parse_bullet_response(response.content[0].text, bullet)

           except APIError as e:
               raise Exception(f"Claude API error: {str(e)}")

       def analyze_all_experience(self, experience: List[ExperienceItem]) -> List[ContentSuggestion]:
           """Analyze all experience items and provide suggestions"""
           suggestions = []

           for i, exp in enumerate(experience):
               if not exp.description:
                   continue

               for bullet in exp.description[:3]:  # Analyze up to 3 bullets per job
                   try:
                       result = self.improve_experience_bullet(
                           bullet,
                           exp.title or "this position"
                       )

                       if result["improved"] != bullet:  # Only add if different
                           suggestions.append(ContentSuggestion(
                               section=f"{exp.company or 'Company'} - {exp.title or 'Position'}",
                               original=bullet,
                               suggestion=result["improved"],
                               reason=result["reason"],
                               priority="high"
                           ))
                   except Exception:
                       # Continue even if one bullet fails
                       continue

           return suggestions

       def get_overall_feedback(self, content: ResumeContent) -> str:
           """Get high-level feedback on the entire resume"""
           prompt = f"""Review this resume content and provide overall feedback:

   CONTACT: {content.contact_info.name or 'Not provided'}
   EMAIL: {content.contact_info.email or 'Not provided'}

   SUMMARY:
   {content.summary or 'Not provided'}

   EXPERIENCE:
   {self._format_experience_for_prompt(content.experience)}

   EDUCATION:
   {self._format_education_for_prompt(content.education)}

   SKILLS:
   {', '.join(content.skills) if content.skills else 'Not provided'}

   Provide concise overall feedback focusing on:
   1. First impressions
   2. Content quality and relevance
   3. Professional presentation
   4. Key areas needing improvement
   5. Standout elements

   Keep feedback actionable and encouraging (3-4 paragraphs).
   """

           try:
               response = self.client.messages.create(
                   model=self.model,
                   max_tokens=1024,
                   messages=[{"role": "user", "content": prompt}]
               )

               return response.content[0].text.strip()

           except APIError as e:
               return "Unable to generate overall feedback at this time."

       def _build_full_analysis_prompt(self, content: ResumeContent) -> str:
           """Build comprehensive analysis prompt"""
           return f"""As a professional resume reviewer, analyze this resume comprehensively:

   RESUME CONTENT:
   ---
   Name: {content.contact_info.name or 'Not provided'}
   Email: {content.contact_info.email or 'Not provided'}
   Phone: {content.contact_info.phone or 'Not provided'}
   LinkedIn: {content.contact_info.linkedin or 'Not provided'}

   Professional Summary:
   {content.summary or 'Not provided'}

   Work Experience:
   {self._format_experience_for_prompt(content.experience)}

   Education:
   {self._format_education_for_prompt(content.education)}

   Skills:
   {', '.join(content.skills[:15]) if content.skills else 'Not provided'}
   ---

   Provide analysis in this format:

   STRENGTHS:
   - [List 3-5 key strengths]

   AREAS FOR IMPROVEMENT:
   - [List 3-5 priority improvements]

   SUMMARY FEEDBACK:
   [Brief analysis of the professional summary]

   EXPERIENCE FEEDBACK:
   [Brief analysis of work experience section]

   OVERALL FEEDBACK:
   [2-3 paragraphs of encouraging, actionable feedback]
   """

       def _format_experience_for_prompt(self, experience: List[ExperienceItem]) -> str:
           """Format experience items for prompt"""
           if not experience:
               return "Not provided"

           formatted = []
           for exp in experience:
               exp_text = f"\n{exp.title or 'Position'} at {exp.company or 'Company'}"
               if exp.description:
                   exp_text += "\n" + "\n".join(f"• {desc}" for desc in exp.description[:5])
               formatted.append(exp_text)

           return "\n".join(formatted)

       def _format_education_for_prompt(self, education: List) -> str:
           """Format education items for prompt"""
           if not education:
               return "Not provided"

           formatted = []
           for edu in education:
               formatted.append(
                   f"{edu.degree or 'Degree'} - {edu.institution or 'Institution'}"
               )

           return "\n".join(formatted)

       def _parse_analysis_response(
           self,
           analysis_text: str,
           content: ResumeContent
       ) -> ClaudeAnalysis:
           """Parse Claude's analysis response into structured format"""
           sections = {
               "STRENGTHS:": "strengths",
               "AREAS FOR IMPROVEMENT:": "improvements",
               "SUMMARY FEEDBACK:": "summary_analysis",
               "OVERALL FEEDBACK:": "overall_feedback"
           }

           parsed = {
               "strengths": [],
               "improvements": [],
               "summary_analysis": "",
               "overall_feedback": ""
           }

           current_section = None
           lines = analysis_text.split("\n")

           for line in lines:
               line = line.strip()

               # Check if line is a section header
               for header, section_key in sections.items():
                   if header in line.upper():
                       current_section = section_key
                       break

               if not line:
                   continue

               # Parse content based on current section
               if current_section in ["strengths", "improvements"]:
                   if line.startswith("-") or line.startswith("•"):
                       parsed[current_section].append(line.lstrip("-•").strip())
               elif current_section in ["summary_analysis", "overall_feedback"]:
                   if not any(header in line.upper() for header in sections.keys()):
                       parsed[current_section] += line + " "

           return ClaudeAnalysis(
               summary_analysis=parsed["summary_analysis"].strip() or None,
               summary_suggestions=[],
               experience_suggestions=[],
               overall_feedback=parsed["overall_feedback"].strip() or "Analysis complete.",
               strengths=parsed["strengths"],
               areas_for_improvement=parsed["improvements"]
           )

       def _parse_summary_response(self, response_text: str) -> Dict[str, any]:
           """Parse summary analysis response"""
           strengths = []
           improvements = []
           improved_version = None

           current_section = None
           lines = response_text.split("\n")

           for line in lines:
               line = line.strip()

               if "STRENGTHS:" in line.upper():
                   current_section = "strengths"
                   continue
               elif "IMPROVEMENTS:" in line.upper():
                   current_section = "improvements"
                   continue
               elif "IMPROVED VERSION:" in line.upper():
                   current_section = "improved"
                   continue

               if not line:
                   continue

               if current_section == "strengths":
                   if line.startswith("-") or line.startswith("•"):
                       strengths.append(line.lstrip("-•").strip())
               elif current_section == "improvements":
                   if line.startswith("-") or line.startswith("•"):
                       improvements.append(line.lstrip("-•").strip())
               elif current_section == "improved":
                   if improved_version is None:
                       improved_version = line
                   else:
                       improved_version += " " + line

           return {
               "strengths": strengths,
               "improvements": improvements,
               "improved_version": improved_version
           }

       def _parse_bullet_response(self, response_text: str, original: str) -> Dict[str, str]:
           """Parse bullet point improvement response"""
           improved = original
           reason = ""

           current_section = None
           lines = response_text.split("\n")

           for line in lines:
               line = line.strip()

               if "IMPROVED:" in line.upper():
                   current_section = "improved"
                   # Check if improved text is on same line
                   if len(line) > len("IMPROVED:"):
                       improved = line.split(":", 1)[1].strip()
                   continue
               elif "REASON:" in line.upper():
                   current_section = "reason"
                   # Check if reason is on same line
                   if len(line) > len("REASON:"):
                       reason = line.split(":", 1)[1].strip()
                   continue

               if not line:
                   continue

               if current_section == "improved" and not improved:
                   improved = line
               elif current_section == "reason":
                   reason += " " + line if reason else line

           return {
               "improved": improved.strip(),
               "reason": reason.strip()
           }
   ```

**Deliverables**:
- Claude API client wrapper
- Methods for resume analysis
- Summary improvement
- Experience bullet enhancement
- Response parsing logic

**Acceptance Criteria**:
- Can successfully call Claude API
- Handles API errors gracefully
- Parses responses into structured format
- Returns meaningful suggestions

---

### 4.3 Create AI Analysis Models

**Task**: Define data models for AI analysis results

**Steps**:
1. Update `backend/app/models/analysis.py`:
   ```python
   # Add to existing file

   class ContentSuggestionModel(BaseModel):
       section: str
       original: str
       suggestion: str
       reason: str
       priority: str

   class SummaryAnalysis(BaseModel):
       strengths: List[str] = []
       improvements: List[str] = []
       improved_version: Optional[str] = None

   class AIAnalysisResult(BaseModel):
       resume_id: str
       summary_analysis: Optional[SummaryAnalysis] = None
       experience_suggestions: List[ContentSuggestionModel] = []
       overall_feedback: str
       strengths: List[str] = []
       areas_for_improvement: List[str] = []
       processing_time: float
   ```

**Deliverables**:
- Pydantic models for AI analysis
- Type-safe response structures

**Acceptance Criteria**:
- Models validate correctly
- FastAPI generates proper schemas

---

### 4.4 Create AI Analysis Endpoint

**Task**: Add API endpoint for AI-powered analysis

**Steps**:
1. Update `backend/app/routers/analyze.py`:
   ```python
   from app.services.claude_service import ClaudeService
   from app.models.analysis import AIAnalysisResult, SummaryAnalysis, ContentSuggestionModel
   import time

   # Initialize Claude service
   try:
       claude_service = ClaudeService()
   except ValueError:
       claude_service = None

   @router.post("/analyze/ai/{upload_id}", response_model=AIAnalysisResult)
   async def analyze_with_ai(upload_id: str):
       """Perform AI-powered analysis using Claude"""
       if not claude_service:
           raise HTTPException(
               status_code=503,
               detail="AI analysis not available - API key not configured"
           )

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
           start_time = time.time()

           # Parse the document
           if file_type == "pdf":
               content = parser.parse_pdf(file_path)
           else:
               content = parser.parse_docx(file_path)

           # Analyze with Claude
           analysis = claude_service.analyze_resume(content)

           # Analyze summary separately for detailed feedback
           summary_analysis = None
           if content.summary:
               summary_result = claude_service.analyze_summary(content.summary)
               summary_analysis = SummaryAnalysis(
                   strengths=summary_result.get("strengths", []),
                   improvements=summary_result.get("improvements", []),
                   improved_version=summary_result.get("improved_version")
               )

           # Analyze experience bullets
           experience_suggestions = claude_service.analyze_all_experience(
               content.experience[:2]  # Limit to first 2 jobs to manage API costs
           )

           processing_time = time.time() - start_time

           return AIAnalysisResult(
               resume_id=upload_id,
               summary_analysis=summary_analysis,
               experience_suggestions=[s.dict() for s in experience_suggestions],
               overall_feedback=analysis.overall_feedback,
               strengths=analysis.strengths,
               areas_for_improvement=analysis.areas_for_improvement,
               processing_time=round(processing_time, 2)
           )

       except Exception as e:
           raise HTTPException(
               status_code=500,
               detail=f"Error in AI analysis: {str(e)}"
           )

   @router.post("/analyze/complete/{upload_id}")
   async def complete_analysis(upload_id: str):
       """Perform complete analysis: basic + AI"""
       # Get basic analysis
       basic = await analyze_basic(upload_id)

       # Get AI analysis if available
       ai_analysis = None
       if claude_service:
           try:
               ai_analysis = await analyze_with_ai(upload_id)
           except Exception as e:
               # Continue without AI analysis if it fails
               print(f"AI analysis failed: {e}")

       return {
           "basic_analysis": basic,
           "ai_analysis": ai_analysis
       }
   ```

**Deliverables**:
- AI analysis endpoint
- Complete analysis endpoint combining basic + AI
- Error handling for API failures
- Cost optimization (limit analyzed items)

**Acceptance Criteria**:
- Endpoint returns AI-generated suggestions
- Handles API key not configured gracefully
- Completes analysis in <30 seconds
- Returns 503 if Claude API unavailable

---

### 4.5 Create AI Suggestions UI Components

**Task**: Build UI to display AI-powered suggestions

**Steps**:
1. Update `src/types/resume.ts`:
   ```typescript
   export interface ContentSuggestion {
     section: string;
     original: string;
     suggestion: string;
     reason: string;
     priority: string;
   }

   export interface SummaryAnalysis {
     strengths: string[];
     improvements: string[];
     improved_version?: string;
   }

   export interface AIAnalysisResult {
     resume_id: string;
     summary_analysis?: SummaryAnalysis;
     experience_suggestions: ContentSuggestion[];
     overall_feedback: string;
     strengths: string[];
     areas_for_improvement: string[];
     processing_time: number;
   }

   export interface CompleteAnalysis {
     basic_analysis: BasicAnalysisResult;
     ai_analysis?: AIAnalysisResult;
   }
   ```

2. Create `src/components/AIFeedback.tsx`:
   ```typescript
   import { AIAnalysisResult } from '../types/resume';

   interface AIFeedbackProps {
     analysis: AIAnalysisResult;
   }

   const AIFeedback = ({ analysis }: AIFeedbackProps) => {
     return (
       <div className="bg-white rounded-lg shadow-md p-6 mb-6">
         <div className="flex items-center justify-between mb-4">
           <h2 className="text-2xl font-bold text-gray-900">
             AI-Powered Analysis
           </h2>
           <span className="text-sm text-gray-500">
             Powered by Claude
           </span>
         </div>

         {/* Overall Feedback */}
         <div className="mb-6">
           <h3 className="text-lg font-semibold text-gray-800 mb-2">
             Overall Feedback
           </h3>
           <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
             <p className="text-gray-700 whitespace-pre-line">
               {analysis.overall_feedback}
             </p>
           </div>
         </div>

         {/* Strengths */}
         {analysis.strengths.length > 0 && (
           <div className="mb-6">
             <h3 className="text-lg font-semibold text-gray-800 mb-2">
               Strengths
             </h3>
             <div className="space-y-2">
               {analysis.strengths.map((strength, index) => (
                 <div
                   key={index}
                   className="flex items-start p-3 bg-green-50 border border-green-200 rounded-lg"
                 >
                   <span className="text-green-600 font-bold mr-3">✓</span>
                   <span className="text-gray-700">{strength}</span>
                 </div>
               ))}
             </div>
           </div>
         )}

         {/* Areas for Improvement */}
         {analysis.areas_for_improvement.length > 0 && (
           <div className="mb-6">
             <h3 className="text-lg font-semibold text-gray-800 mb-2">
               Areas for Improvement
             </h3>
             <div className="space-y-2">
               {analysis.areas_for_improvement.map((area, index) => (
                 <div
                   key={index}
                   className="flex items-start p-3 bg-orange-50 border border-orange-200 rounded-lg"
                 >
                   <span className="text-orange-600 font-bold mr-3">→</span>
                   <span className="text-gray-700">{area}</span>
                 </div>
               ))}
             </div>
           </div>
         )}
       </div>
     );
   };

   export default AIFeedback;
   ```

3. Create `src/components/ContentSuggestions.tsx`:
   ```typescript
   import { useState } from 'react';
   import { ContentSuggestion, SummaryAnalysis } from '../types/resume';

   interface ContentSuggestionsProps {
     summaryAnalysis?: SummaryAnalysis;
     experienceSuggestions: ContentSuggestion[];
   }

   const ContentSuggestions = ({
     summaryAnalysis,
     experienceSuggestions,
   }: ContentSuggestionsProps) => {
     const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());

     const toggleItem = (index: number) => {
       const newExpanded = new Set(expandedItems);
       if (newExpanded.has(index)) {
         newExpanded.delete(index);
       } else {
         newExpanded.add(index);
       }
       setExpandedItems(newExpanded);
     };

     return (
       <div className="bg-white rounded-lg shadow-md p-6 mb-6">
         <h2 className="text-2xl font-bold text-gray-900 mb-4">
           Content Improvement Suggestions
         </h2>

         {/* Summary Analysis */}
         {summaryAnalysis && (
           <div className="mb-6 border-b pb-6">
             <h3 className="text-lg font-semibold text-gray-800 mb-3">
               Professional Summary
             </h3>

             {summaryAnalysis.improved_version && (
               <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-3">
                 <div className="font-semibold text-purple-900 mb-2">
                   Suggested Improvement:
                 </div>
                 <p className="text-gray-700">{summaryAnalysis.improved_version}</p>
               </div>
             )}

             {summaryAnalysis.improvements.length > 0 && (
               <div className="mb-2">
                 <div className="text-sm font-medium text-gray-600 mb-1">
                   Improvements:
                 </div>
                 <ul className="list-disc list-inside text-gray-700 space-y-1">
                   {summaryAnalysis.improvements.map((imp, idx) => (
                     <li key={idx}>{imp}</li>
                   ))}
                 </ul>
               </div>
             )}
           </div>
         )}

         {/* Experience Suggestions */}
         {experienceSuggestions.length > 0 && (
           <div>
             <h3 className="text-lg font-semibold text-gray-800 mb-3">
               Experience Bullet Points ({experienceSuggestions.length} suggestions)
             </h3>

             <div className="space-y-3">
               {experienceSuggestions.map((suggestion, index) => (
                 <div
                   key={index}
                   className="border border-gray-200 rounded-lg overflow-hidden"
                 >
                   <div
                     className="bg-gray-50 p-3 cursor-pointer hover:bg-gray-100"
                     onClick={() => toggleItem(index)}
                   >
                     <div className="flex items-center justify-between">
                       <span className="font-medium text-gray-800">
                         {suggestion.section}
                       </span>
                       <span className="text-gray-500">
                         {expandedItems.has(index) ? '▼' : '▶'}
                       </span>
                     </div>
                   </div>

                   {expandedItems.has(index) && (
                     <div className="p-4 bg-white">
                       <div className="mb-3">
                         <div className="text-sm font-medium text-gray-600 mb-1">
                           Original:
                         </div>
                         <div className="bg-red-50 border-l-4 border-red-400 p-3 text-gray-700">
                           {suggestion.original}
                         </div>
                       </div>

                       <div className="mb-3">
                         <div className="text-sm font-medium text-gray-600 mb-1">
                           Improved:
                         </div>
                         <div className="bg-green-50 border-l-4 border-green-400 p-3 text-gray-700">
                           {suggestion.suggestion}
                         </div>
                       </div>

                       <div className="bg-blue-50 border border-blue-200 rounded p-3">
                         <div className="text-sm font-medium text-blue-900 mb-1">
                           Why this is better:
                         </div>
                         <p className="text-sm text-gray-700">{suggestion.reason}</p>
                       </div>
                     </div>
                   )}
                 </div>
               ))}
             </div>
           </div>
         )}

         {!summaryAnalysis && experienceSuggestions.length === 0 && (
           <p className="text-gray-500 text-center py-8">
             No AI suggestions available at this time.
           </p>
         )}
       </div>
     );
   };

   export default ContentSuggestions;
   ```

4. Update `src/components/AnalysisResults.tsx`:
   ```typescript
   import { CompleteAnalysis } from '../types/resume';
   import ScoreDisplay from './ScoreDisplay';
   import GrammarIssues from './GrammarIssues';
   import SuggestionCard from './SuggestionCard';
   import AIFeedback from './AIFeedback';
   import ContentSuggestions from './ContentSuggestions';

   interface AnalysisResultsProps {
     analysis: CompleteAnalysis;
   }

   const AnalysisResults = ({ analysis }: AnalysisResultsProps) => {
     return (
       <div>
         <ScoreDisplay score={analysis.basic_analysis.score} />

         {analysis.ai_analysis && (
           <>
             <AIFeedback analysis={analysis.ai_analysis} />
             <ContentSuggestions
               summaryAnalysis={analysis.ai_analysis.summary_analysis}
               experienceSuggestions={analysis.ai_analysis.experience_suggestions}
             />
           </>
         )}

         <GrammarIssues grammarResults={analysis.basic_analysis.grammar_results} />
         <SuggestionCard suggestions={analysis.basic_analysis.suggestions} />
       </div>
     );
   };

   export default AnalysisResults;
   ```

5. Update `src/components/UploadSection.tsx`:
   ```typescript
   // Replace basic analysis call with complete analysis
   const analysisResponse = await api.post<CompleteAnalysis>(
     `/api/analyze/complete/${uploadResponse.data.upload_id}`
   );

   navigate('/results', {
     state: {
       resumeData: parseResponse.data,
       analysisData: analysisResponse.data
     }
   });
   ```

**Deliverables**:
- AI feedback display component
- Content suggestions with expand/collapse
- Before/after comparison for improvements
- Integration with existing analysis UI

**Acceptance Criteria**:
- AI suggestions display clearly
- Can expand/collapse individual suggestions
- Before/after comparison is easy to read
- Handles missing AI analysis gracefully
- Responsive design

---

## Testing Checklist

- [ ] Claude API key configured correctly
- [ ] Can call Claude API successfully
- [ ] Summary analysis returns useful feedback
- [ ] Experience bullet improvements are meaningful
- [ ] Overall feedback is encouraging and actionable
- [ ] UI displays all AI suggestions
- [ ] Expand/collapse functionality works
- [ ] Handles API errors gracefully
- [ ] Shows loading state during analysis
- [ ] Works when AI analysis unavailable

## Dependencies

- Phase 2 (Document Processing) for parsed content
- Valid Claude API key
- Internet connection for API calls

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| API costs too high | Limit analyzed items; cache results |
| API responses inconsistent | Robust parsing with fallbacks |
| Slow API response times | Show progress indicator; set timeouts |
| API rate limits hit | Implement retry logic with backoff |
| Generic/unhelpful suggestions | Refine prompts; provide more context |

## Success Metrics

- AI analysis completes in <30 seconds
- Suggestions are actionable >90% of time
- Improved content scores higher in subsequent analysis
- User satisfaction with AI feedback
- <5% API error rate

## Cost Considerations

- Estimate: $0.03-0.10 per resume analysis
- Implement caching for repeated analyses
- Consider tiered pricing: basic (free) vs AI-enhanced (paid)
- Monitor API usage and costs

## Next Steps

After completing Phase 4:
- Use AI analysis in ATS optimization (Phase 5)
- Apply AI suggestions to exported resumes (Phase 6)
- Consider adding more specialized prompts per industry
