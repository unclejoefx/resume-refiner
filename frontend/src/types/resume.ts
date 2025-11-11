/**
 * TypeScript type definitions for resume data.
 */

export interface ContactInfo {
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  website?: string;
}

export interface Experience {
  company: string;
  position: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
  bullets: string[];
}

export interface Education {
  institution: string;
  degree?: string;
  field?: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  gpa?: string;
  achievements: string[];
}

export interface Skill {
  category?: string;
  skills: string[];
}

export interface ResumeContent {
  contact_info?: ContactInfo;
  summary?: string;
  experience: Experience[];
  education: Education[];
  skills: Skill[];
  raw_text: string;
  sections: Record<string, any>;
}

export interface ResumeUpload {
  id: string;
  user_id?: string;
  filename: string;
  upload_date: string;
  file_type: string;
  file_path: string;
  content?: ResumeContent;
}

export interface GrammarIssue {
  text: string;
  message: string;
  suggestions: string[];
  category?: string;
  line?: number;
  offset?: number;
}

export interface ATSSuggestion {
  category: string;
  message: string;
  importance: string;
  current_value?: string;
  suggested_value?: string;
}

export interface ContentSuggestion {
  section: string;
  original_text: string;
  suggested_text: string;
  explanation: string;
  impact: string;
}

export interface Analysis {
  id: string;
  resume_id: string;
  analysis_date: string;
  overall_score: number;
  grammar_score?: number;
  ats_score?: number;
  content_score?: number;
  grammar_issues: GrammarIssue[];
  ats_suggestions: ATSSuggestion[];
  content_suggestions: ContentSuggestion[];
  formatting_issues: string[];
}
