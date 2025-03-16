
import axios from 'axios';

// Base URL from environment variable
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const uploadPaper = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const uploadResponse = await api.post('/papers/', formData);
  return uploadResponse.data;
};

// this function sends a put request to create paper with this fields: summary, keywords and title
export const createPaper = async (paperId, title, summary, key_words) => {
  return await api.put(`/papers/${paperId}/`, {
    title,
    summary,
    key_words
  });
};

export const getPapers = async () => {
  const response = await api.get('/papers/');
  return response.data;
};

export const getPaperSummary = async (paperId) => {
  const response = await api.get(`/papers/${paperId}/get-summary/`);
  return response.data;
};

export const getPaperSummaryLatex = async (paperId) => {
  // This will return a file to download
  const response = await api.get(`/papers/${paperId}/get-summary-latex/`, {
    responseType: 'blob'
  });
  return response.data;
};

export const searchLabels = async (paperId) => {
  const response = await api.get(`/papers/${paperId}/related-labels/`);
  return response.data;
};

export const getKeywords = async (paperId) => {
  const response = await api.get(`/papers/${paperId}/get-keywords/`);
  return response.data;
};

export const addLabel = async (paperId, name) => {
  const response = await api.put(`/papers/${paperId}/add-label/`, {
    name: name
  });
  return response.data;
};

export const removeLabel = async (paperId, name) => {
  const response = await api.put(`/papers/${paperId}/remove-label/`, {
    name: name
  });
  return response.data;
};

export const getPaperLabels = async (paperId) => {
  const response = await api.get(`/papers/${paperId}/get-labels/`);
  return response.data
}

export const getAllLabels = async () => {
  const response = await api.get('/labels/');
  return response.data;
};

export const createLabel = async (name) => {
  const response = await api.post('/labels/', { name });
  return response.data;
};

export const getSummarySpeech = async (paperId) => {
  const response = await api.get(`/papers/${paperId}/summary-to-speech/`, { responseType: 'blob' });
  return response.data
}

export default api;
