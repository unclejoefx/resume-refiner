/**
 * API client for Resume Refiner backend.
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload API
export const uploadResume = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getUpload = async (uploadId: string) => {
  const response = await api.get(`/api/upload/${uploadId}`);
  return response.data;
};

// Analysis API
export const analyzeResume = async (resumeId: string, jobDescription?: string) => {
  const response = await api.post('/api/analyze/', {
    resume_id: resumeId,
    job_description: jobDescription || '',
  });

  return response.data;
};

export const getAnalysis = async (analysisId: string) => {
  const response = await api.get(`/api/analyze/${analysisId}`);
  return response.data;
};

export const checkGrammar = async (text: string) => {
  const response = await api.post('/api/analyze/grammar', { text });
  return response.data;
};

export const checkATS = async (resumeId: string, jobDescription?: string) => {
  const response = await api.post('/api/analyze/ats', {
    resume_id: resumeId,
    job_description: jobDescription || '',
  });

  return response.data;
};

// Export API
export const exportPDF = async (analysisId: string) => {
  const response = await api.get(`/api/export/${analysisId}/pdf`, {
    responseType: 'blob',
  });

  return response.data;
};

export const exportDOCX = async (analysisId: string) => {
  const response = await api.get(`/api/export/${analysisId}/docx`, {
    responseType: 'blob',
  });

  return response.data;
};
