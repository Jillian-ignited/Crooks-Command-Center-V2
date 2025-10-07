// frontend/lib/api.js - COMPLETE VERSION

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export const api = {
  // Intelligence endpoints
  uploadFile: async (file, source, brand, description) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source', source);
    formData.append('brand', brand);
    if (description) formData.append('description', description);

    const response = await fetch(`${API_BASE_URL}/intelligence/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }
    
    return response.json();
  },

  getFiles: async (source) => {
    const url = source 
      ? `${API_BASE_URL}/intelligence/files?source=${source}`
      : `${API_BASE_URL}/intelligence/files`;
    
    const response = await fetch(url);
    return response.json();
  },

  getFileAnalysis: async (fileId) => {
    const response = await fetch(`${API_BASE_URL}/intelligence/files/${fileId}`);
    return response.json();
  },

  getInsights: async (source, days) => {
    const params = new URLSearchParams();
    if (source) params.append('source', source);
    if (days) params.append('days', days.toString());
    
    const response = await fetch(`${API_BASE_URL}/intelligence/insights?${params}`);
    return response.json();
  },

  // Health check
  healthCheck: async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  }
};

// Generic POST helper function
export const apiPost = async (endpoint, data) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`POST ${endpoint} failed: ${response.statusText}`);
  }

  return response.json();
};

// Generic GET helper function
export const apiGet = async (endpoint) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  
  if (!response.ok) {
    throw new Error(`GET ${endpoint} failed: ${response.statusText}`);
  }

  return response.json();
};

// Generic PUT helper function
export const apiPut = async (endpoint, data) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`PUT ${endpoint} failed: ${response.statusText}`);
  }

  return response.json();
};

// Generic DELETE helper function
export const apiDelete = async (endpoint) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`DELETE ${endpoint} failed: ${response.statusText}`);
  }

  return response.json();
};

export default api;
