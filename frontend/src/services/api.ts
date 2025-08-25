import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  register: async (userData: any) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  logout: async () => {
    // Optional: Call logout endpoint
    // await api.post('/auth/logout');
    localStorage.removeItem('token');
  },
};

// Documents API
export const documentsApi = {
  upload: async (file: File, title?: string, subject?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (subject) formData.append('subject', subject);

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (skip = 0, limit = 100, subject?: string) => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (subject) params.append('subject', subject);

    const response = await api.get(`/documents/?${params}`);
    return response.data;
  },

  get: async (documentId: number) => {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  },

  getAnalysis: async (documentId: number) => {
    const response = await api.get(`/documents/${documentId}/analysis`);
    return response.data;
  },

  delete: async (documentId: number) => {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
  },

  reprocess: async (documentId: number) => {
    const response = await api.post(`/documents/${documentId}/reprocess`);
    return response.data;
  },
};

// Chat API
export const chatApi = {
  createConversation: async (conversation: any) => {
    const response = await api.post('/chat/conversations', conversation);
    return response.data;
  },

  listConversations: async (skip = 0, limit = 100) => {
    const response = await api.get(`/chat/conversations?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getConversation: async (conversationId: number) => {
    const response = await api.get(`/chat/conversations/${conversationId}`);
    return response.data;
  },

  sendMessage: async (conversationId: number, message: any) => {
    const response = await api.post(`/chat/conversations/${conversationId}/messages`, message);
    return response.data;
  },

  getMessages: async (conversationId: number, skip = 0, limit = 100) => {
    const response = await api.get(
      `/chat/conversations/${conversationId}/messages?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  deleteConversation: async (conversationId: number) => {
    const response = await api.delete(`/chat/conversations/${conversationId}`);
    return response.data;
  },

  provideFeedback: async (conversationId: number, messageId: number, feedback: any) => {
    const response = await api.post(
      `/chat/conversations/${conversationId}/feedback`,
      { message_id: messageId, ...feedback }
    );
    return response.data;
  },
};

// Progress API
export const progressApi = {
  getSkillHeatmap: async (subject?: string) => {
    const params = subject ? `?subject=${encodeURIComponent(subject)}` : '';
    const response = await api.get(`/progress/heatmap${params}`);
    return response.data;
  },

  getRecommendations: async (limit = 10) => {
    const response = await api.get(`/progress/recommendations?limit=${limit}`);
    return response.data;
  },

  recordSkillAssessment: async (assessment: any) => {
    const response = await api.post('/progress/assess-skill', assessment);
    return response.data;
  },

  updateProgress: async (progress: any) => {
    const response = await api.post('/progress/update-progress', progress);
    return response.data;
  },

  getTopicMastery: async (topicId: number) => {
    const response = await api.get(`/progress/topics/${topicId}/mastery`);
    return response.data;
  },

  getAnalytics: async (days = 30) => {
    const response = await api.get(`/progress/analytics?days=${days}`);
    return response.data;
  },

  recordStudySession: async (session: any) => {
    const response = await api.post('/progress/study-session', session);
    return response.data;
  },

  getStudySessions: async (days = 30, skip = 0, limit = 100) => {
    const response = await api.get(
      `/progress/study-sessions?days=${days}&skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  getStudyStreak: async () => {
    const response = await api.get('/progress/streak');
    return response.data;
  },

  getLearningGoals: async (activeOnly = true) => {
    const response = await api.get(`/progress/goals?active_only=${activeOnly}`);
    return response.data;
  },

  createLearningGoal: async (goal: any) => {
    const response = await api.post('/progress/goals', goal);
    return response.data;
  },

  getDifficultyAnalysis: async (subject?: string) => {
    const params = subject ? `?subject=${encodeURIComponent(subject)}` : '';
    const response = await api.get(`/progress/difficulty-analysis${params}`);
    return response.data;
  },
};

export default api;
