// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.origin.includes('localhost')
    ? 'http://localhost:8000/api'
    : 'https://crooks-command-center-v2.onrender.com/api'
  );

export const api = {
  // Intelligence endpoints
  uploadFile: async (file: File, source: string, brand: string, description?: string) => {
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

  getFiles: async (source?: string) => {
    const url = source 
      ? `${API_BASE_URL}/intelligence/files?source=${source}`
      : `${API_BASE_URL}/intelligence/files`;
    
    const response = await fetch(url);
    return response.json();
  },

  getFileAnalysis: async (fileId: number) => {
    const response = await fetch(`${API_BASE_URL}/intelligence/files/${fileId}`);
    return response.json();
  },

  getInsights: async (source?: string, days?: number) => {
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

export default api;