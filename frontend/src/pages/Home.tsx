/**
 * Home page component.
 */

import React, { useState } from 'react';
import { UploadSection } from '../components/UploadSection';
import { AnalysisResults } from '../components/AnalysisResults';
import { DocumentPreview } from '../components/DocumentPreview';
import { ResumeUpload, Analysis } from '../types/resume';
import { analyzeResume } from '../services/api';

export const Home: React.FC = () => {
  const [upload, setUpload] = useState<ResumeUpload | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUploadComplete = (uploadData: ResumeUpload) => {
    setUpload(uploadData);
    setError(null);
    // Don't automatically analyze - let user review parsed content first
  };

  const handleAnalyze = async () => {
    if (!upload) return;

    setAnalyzing(true);
    setError(null);
    try {
      const analysisResult = await analyzeResume(upload.id);
      setAnalysis(analysisResult);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze resume');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleReset = () => {
    setUpload(null);
    setAnalysis(null);
    setError(null);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1>Resume Refiner</h1>
        <p>AI-powered resume analysis and optimization</p>
      </header>

      {!upload && (
        <UploadSection onUploadComplete={handleUploadComplete} />
      )}

      {upload && !analyzing && !analysis && upload.content && (
        <div>
          <div style={{ marginBottom: '20px' }}>
            <h3>Upload Successful!</h3>
            <p>File: {upload.filename}</p>
          </div>

          <DocumentPreview content={upload.content} />

          <div style={{ textAlign: 'center', marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <button onClick={handleAnalyze} style={{ fontSize: '16px', padding: '12px 24px' }}>
              Analyze Resume
            </button>
            <button onClick={handleReset} style={{ backgroundColor: '#757575' }}>
              Upload Another Resume
            </button>
          </div>
        </div>
      )}

      {analyzing && (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p>Analyzing your resume...</p>
          <div>This may take a moment.</div>
        </div>
      )}

      {error && (
        <div style={{
          backgroundColor: '#ffebee',
          color: '#c62828',
          padding: '15px',
          borderRadius: '8px',
          marginTop: '20px'
        }}>
          Error: {error}
        </div>
      )}

      {analysis && (
        <div>
          <AnalysisResults analysis={analysis} />
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <button onClick={handleReset}>Analyze Another Resume</button>
          </div>
        </div>
      )}
    </div>
  );
};
