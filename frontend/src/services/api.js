import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dataset API
export const uploadDataset = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/dataset/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDatasetInfo = async () => {
  const response = await api.get('/dataset/info');
  return response.data;
};

export const getDatasetPreview = async (rows = 10) => {
  const response = await api.get(`/dataset/preview?rows=${rows}`);
  return response.data;
};

export const clearDataset = async () => {
  const response = await api.post('/dataset/clear');
  return response.data;
};

export const getColumns = async () => {
  const response = await api.get('/dataset/columns');
  return response.data;
};

// Analysis API
export const analyzeQuestion = async (question) => {
  const response = await api.post('/analyze', { question });
  return response.data;
};

export const getIntents = async () => {
  const response = await api.get('/analyze/intents');
  return response.data;
};

export const getTools = async () => {
  const response = await api.get('/analyze/tools');
  return response.data;
};

// History API
export const getHistory = async (limit = 20) => {
  const response = await api.get(`/history?limit=${limit}`);
  return response.data;
};

export const getHistoryItem = async (id) => {
  const response = await api.get(`/history/${id}`);
  return response.data;
};

export const saveToHistory = async (data) => {
  const response = await api.post('/history', data);
  return response.data;
};

export const deleteHistoryItem = async (id) => {
  const response = await api.delete(`/history/${id}`);
  return response.data;
};

export const clearHistory = async () => {
  const response = await api.delete('/history/clear');
  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await axios.get('http://localhost:5000/api/health');
  return response.data;
};

export default api;