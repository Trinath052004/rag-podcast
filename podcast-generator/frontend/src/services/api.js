import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Handle specific error statuses
      if (error.response.status === 401) {
        // Handle unauthorized - redirect to login or refresh token
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// PDF Upload API
export const uploadPDF = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/pdf/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('PDF upload error:', error);
    throw error;
  }
};

// Podcast Generation API
export const generatePodcast = async (pdfId, query = null, agentConfigs = null) => {
  try {
    const response = await api.post('/podcast/generate', {
      pdf_id: pdfId,
      query: query,
      agent_configs: agentConfigs || getDefaultAgentConfigs(),
    });

    return response.data;
  } catch (error) {
    console.error('Podcast generation error:', error);
    throw error;
  }
};

// Get RAG Response API
export const generateRagResponse = async (pdfId, query) => {
  try {
    const response = await api.post('/podcast/rag-response', null, {
      params: {
        pdf_id: pdfId,
        query: query,
      },
    });

    return response.data;
  } catch (error) {
    console.error('RAG response error:', error);
    throw error;
  }
};

// Voice Processing API
export const processVoiceInput = async (audioFile, conversationId) => {
  try {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    formData.append('conversation_id', conversationId);

    const response = await api.post('/voice/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Voice processing error:', error);
    throw error;
  }
};

// Audio Generation API
export const generateAudio = async (text, voiceId, agentId, format = 'mp3') => {
  try {
    const response = await api.post('/voice/generate', {
      text,
      voice_id: voiceId,
      agent_id: agentId,
      format,
    });

    return response.data;
  } catch (error) {
    console.error('Audio generation error:', error);
    throw error;
  }
};

// Get Available Voices API
export const getAvailableVoices = async () => {
  try {
    const response = await api.get('/voice/voices');
    return response.data;
  } catch (error) {
    console.error('Get voices error:', error);
    throw error;
  }
};

// Get Default Agent Configurations
export const getDefaultAgentConfigs = () => {
  return [
    {
      name: 'Dr. Knowledge',
      role: 'explainer',
      personality: 'Expert in the subject matter, patient, and thorough in explanations',
      voice_id: '21m00Tcm4TlvDq8ikWAM',
    },
    {
      name: 'Curious Carl',
      role: 'curious',
      personality: 'Inquisitive, asks insightful questions, represents the audience\'s perspective',
      voice_id: 'AZCnJ6YX1Dv9e0J9z4Jm',
    },
    {
      name: 'You',
      role: 'user',
      personality: 'The actual user who can ask questions during the conversation',
      voice_id: 'EXAVITQu4vr4xnSDxMaL',
    },
  ];
};

// Authentication API
export const login = async (username, password) => {
  try {
    const response = await api.post('/auth/token', {
      username,
      password,
    });

    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }

    return response.data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem('access_token');
  window.location.href = '/login';
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get('/auth/users/me');
    return response.data;
  } catch (error) {
    console.error('Get current user error:', error);
    throw error;
  }
};

export const register = async (username, password, email) => {
  try {
    const response = await api.post('/auth/users/', null, {
      params: {
        username,
        password,
        email,
      },
    });

    return response.data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

// Health Check
export const checkApiHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
};

export default api;
