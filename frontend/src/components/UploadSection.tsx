/**
 * Upload section component for uploading resume files.
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadResume } from '../services/api';
import { ResumeUpload } from '../types/resume';

interface UploadSectionProps {
  onUploadComplete: (upload: ResumeUpload) => void;
}

export const UploadSection: React.FC<UploadSectionProps> = ({ onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setError(null);

    try {
      const upload = await uploadResume(file);
      onUploadComplete(upload);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  }, [onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div className="upload-section">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'disabled' : ''}`}
        style={{
          border: '2px dashed #ccc',
          borderRadius: '8px',
          padding: '40px',
          textAlign: 'center',
          cursor: uploading ? 'not-allowed' : 'pointer',
          backgroundColor: isDragActive ? '#f0f0f0' : 'white',
        }}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <p>Uploading...</p>
        ) : isDragActive ? (
          <p>Drop the file here...</p>
        ) : (
          <div>
            <p>Drag and drop your resume here, or click to select</p>
            <p style={{ fontSize: '14px', color: '#666' }}>Supported formats: PDF, DOCX (max 10MB)</p>
          </div>
        )}
      </div>
      {error && (
        <div style={{ color: 'red', marginTop: '10px' }}>
          Error: {error}
        </div>
      )}
    </div>
  );
};
