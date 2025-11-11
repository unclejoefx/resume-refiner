/**
 * Suggestion card component for displaying individual suggestions.
 */

import React from 'react';

interface SuggestionCardProps {
  title: string;
  description: string;
  suggestions?: string[];
  currentValue?: string;
  suggestedValue?: string;
}

export const SuggestionCard: React.FC<SuggestionCardProps> = ({
  title,
  description,
  suggestions,
  currentValue,
  suggestedValue,
}) => {
  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '15px',
      marginBottom: '15px',
      backgroundColor: '#f9f9f9'
    }}>
      <h4 style={{ marginTop: 0 }}>{title}</h4>
      <p>{description}</p>

      {currentValue && (
        <div style={{ marginBottom: '10px' }}>
          <strong>Current:</strong>
          <div style={{
            backgroundColor: '#ffebee',
            padding: '10px',
            borderRadius: '4px',
            marginTop: '5px'
          }}>
            {currentValue}
          </div>
        </div>
      )}

      {suggestedValue && (
        <div style={{ marginBottom: '10px' }}>
          <strong>Suggested:</strong>
          <div style={{
            backgroundColor: '#e8f5e9',
            padding: '10px',
            borderRadius: '4px',
            marginTop: '5px'
          }}>
            {suggestedValue}
          </div>
        </div>
      )}

      {suggestions && suggestions.length > 0 && (
        <div>
          <strong>Suggestions:</strong>
          <ul>
            {suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
