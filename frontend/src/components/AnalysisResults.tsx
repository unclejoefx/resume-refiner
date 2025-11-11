/**
 * Analysis results component for displaying resume analysis.
 */

import React from 'react';
import { Analysis } from '../types/resume';
import { ScoreDisplay } from './ScoreDisplay';
import { SuggestionCard } from './SuggestionCard';

interface AnalysisResultsProps {
  analysis: Analysis;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ analysis }) => {
  return (
    <div className="analysis-results" style={{ padding: '20px' }}>
      <h2>Analysis Results</h2>

      {/* Overall Score */}
      <div style={{ marginBottom: '30px' }}>
        <ScoreDisplay
          label="Overall Score"
          score={analysis.overall_score}
        />

        {analysis.grammar_score !== undefined && (
          <ScoreDisplay
            label="Grammar Score"
            score={analysis.grammar_score}
          />
        )}

        {analysis.ats_score !== undefined && (
          <ScoreDisplay
            label="ATS Compatibility Score"
            score={analysis.ats_score}
          />
        )}

        {analysis.content_score !== undefined && (
          <ScoreDisplay
            label="Content Quality Score"
            score={analysis.content_score}
          />
        )}
      </div>

      {/* Grammar Issues */}
      {analysis.grammar_issues.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h3>Grammar Issues ({analysis.grammar_issues.length})</h3>
          {analysis.grammar_issues.map((issue, index) => (
            <SuggestionCard
              key={index}
              title={issue.category || 'Grammar Issue'}
              description={issue.message}
              suggestions={issue.suggestions}
            />
          ))}
        </div>
      )}

      {/* ATS Suggestions */}
      {analysis.ats_suggestions.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h3>ATS Optimization Suggestions ({analysis.ats_suggestions.length})</h3>
          {analysis.ats_suggestions.map((suggestion, index) => (
            <SuggestionCard
              key={index}
              title={`${suggestion.category} (${suggestion.importance} priority)`}
              description={suggestion.message}
              currentValue={suggestion.current_value}
              suggestedValue={suggestion.suggested_value}
            />
          ))}
        </div>
      )}

      {/* Content Suggestions */}
      {analysis.content_suggestions.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h3>Content Improvement Suggestions ({analysis.content_suggestions.length})</h3>
          {analysis.content_suggestions.map((suggestion, index) => (
            <SuggestionCard
              key={index}
              title={`${suggestion.section} (${suggestion.impact} impact)`}
              description={suggestion.explanation}
              currentValue={suggestion.original_text}
              suggestedValue={suggestion.suggested_text}
            />
          ))}
        </div>
      )}

      {/* Formatting Issues */}
      {analysis.formatting_issues.length > 0 && (
        <div>
          <h3>Formatting Issues ({analysis.formatting_issues.length})</h3>
          <ul>
            {analysis.formatting_issues.map((issue, index) => (
              <li key={index}>{issue}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
