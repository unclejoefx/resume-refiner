/**
 * Document preview component for displaying parsed resume content.
 */

import React from 'react';
import { ResumeContent } from '../types/resume';

interface DocumentPreviewProps {
  content: ResumeContent;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({ content }) => {
  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '20px',
      backgroundColor: 'white',
      marginBottom: '20px'
    }}>
      <h2 style={{ marginTop: 0 }}>Parsed Resume Content</h2>

      {/* Contact Information */}
      {content.contact_info && (
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ color: '#1976d2', borderBottom: '2px solid #1976d2', paddingBottom: '5px' }}>
            Contact Information
          </h3>
          <div style={{ marginTop: '10px' }}>
            {content.contact_info.name && (
              <p><strong>Name:</strong> {content.contact_info.name}</p>
            )}
            {content.contact_info.email && (
              <p><strong>Email:</strong> {content.contact_info.email}</p>
            )}
            {content.contact_info.phone && (
              <p><strong>Phone:</strong> {content.contact_info.phone}</p>
            )}
            {content.contact_info.location && (
              <p><strong>Location:</strong> {content.contact_info.location}</p>
            )}
            {content.contact_info.linkedin && (
              <p><strong>LinkedIn:</strong> {content.contact_info.linkedin}</p>
            )}
            {content.contact_info.website && (
              <p><strong>Website:</strong> {content.contact_info.website}</p>
            )}
          </div>
        </div>
      )}

      {/* Professional Summary */}
      {content.summary && (
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ color: '#1976d2', borderBottom: '2px solid #1976d2', paddingBottom: '5px' }}>
            Professional Summary
          </h3>
          <p style={{ marginTop: '10px', lineHeight: '1.6' }}>{content.summary}</p>
        </div>
      )}

      {/* Experience */}
      {content.experience && content.experience.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ color: '#1976d2', borderBottom: '2px solid #1976d2', paddingBottom: '5px' }}>
            Experience
          </h3>
          {content.experience.map((exp, index) => (
            <div key={index} style={{ marginTop: '15px', paddingLeft: '10px' }}>
              <h4 style={{ marginBottom: '5px' }}>
                {exp.position} {exp.company && `at ${exp.company}`}
              </h4>
              {(exp.start_date || exp.end_date) && (
                <p style={{ color: '#666', fontSize: '14px', marginBottom: '10px' }}>
                  {exp.start_date} - {exp.is_current ? 'Present' : exp.end_date}
                  {exp.location && ` | ${exp.location}`}
                </p>
              )}
              {exp.description && (
                <p style={{ marginBottom: '10px' }}>{exp.description}</p>
              )}
              {exp.bullets && exp.bullets.length > 0 && (
                <ul style={{ marginLeft: '20px' }}>
                  {exp.bullets.map((bullet, idx) => (
                    <li key={idx} style={{ marginBottom: '5px' }}>{bullet}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Education */}
      {content.education && content.education.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ color: '#1976d2', borderBottom: '2px solid #1976d2', paddingBottom: '5px' }}>
            Education
          </h3>
          {content.education.map((edu, index) => (
            <div key={index} style={{ marginTop: '15px', paddingLeft: '10px' }}>
              <h4 style={{ marginBottom: '5px' }}>{edu.institution}</h4>
              {edu.degree && (
                <p style={{ marginBottom: '5px' }}>
                  {edu.degree} {edu.field && `in ${edu.field}`}
                </p>
              )}
              {(edu.start_date || edu.end_date) && (
                <p style={{ color: '#666', fontSize: '14px', marginBottom: '10px' }}>
                  {edu.start_date} - {edu.end_date}
                  {edu.location && ` | ${edu.location}`}
                </p>
              )}
              {edu.gpa && (
                <p style={{ fontSize: '14px' }}>GPA: {edu.gpa}</p>
              )}
              {edu.achievements && edu.achievements.length > 0 && (
                <ul style={{ marginLeft: '20px', marginTop: '10px' }}>
                  {edu.achievements.map((achievement, idx) => (
                    <li key={idx} style={{ fontSize: '14px' }}>{achievement}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Skills */}
      {content.skills && content.skills.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ color: '#1976d2', borderBottom: '2px solid #1976d2', paddingBottom: '5px' }}>
            Skills
          </h3>
          {content.skills.map((skillGroup, index) => (
            <div key={index} style={{ marginTop: '15px', paddingLeft: '10px' }}>
              {skillGroup.category && (
                <h4 style={{ marginBottom: '10px' }}>{skillGroup.category}</h4>
              )}
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '8px'
              }}>
                {skillGroup.skills.map((skill, idx) => (
                  <span
                    key={idx}
                    style={{
                      backgroundColor: '#e3f2fd',
                      color: '#1976d2',
                      padding: '5px 12px',
                      borderRadius: '16px',
                      fontSize: '14px'
                    }}
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Raw Text Preview (Collapsible) */}
      {content.raw_text && (
        <details style={{ marginTop: '20px' }}>
          <summary style={{
            cursor: 'pointer',
            fontWeight: 'bold',
            padding: '10px',
            backgroundColor: '#f5f5f5',
            borderRadius: '4px'
          }}>
            View Raw Text
          </summary>
          <pre style={{
            marginTop: '10px',
            padding: '15px',
            backgroundColor: '#f9f9f9',
            borderRadius: '4px',
            overflow: 'auto',
            maxHeight: '300px',
            fontSize: '12px',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word'
          }}>
            {content.raw_text}
          </pre>
        </details>
      )}

      {/* Sections Info */}
      {content.sections && Object.keys(content.sections).length > 0 && (
        <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
          <strong>Detected Sections:</strong>{' '}
          {Object.keys(content.sections).join(', ')}
        </div>
      )}
    </div>
  );
};
