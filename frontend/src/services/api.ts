import axios, { type AxiosResponse, type AxiosError, type InternalAxiosRequestConfig } from 'axios';

interface ErrorResponse {
  detail?: string;
  message?: string;
}

// Get API base URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// API configuration

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include JWT token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token is invalid or expired, redirect to login
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    } else if (error.response?.status === 422) {
      // Handle validation errors more gracefully
      const errorData = error.response.data as ErrorResponse;
      const errorMessage = errorData?.detail || errorData?.message || 'Invalid request data';
      error.message = errorMessage;
    }
    return Promise.reject(error);
  }
);

// Create a separate instance for file uploads
export const uploadApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Add auth token to upload API as well
uploadApi.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Check Google Calendar connection status
export const getCalendarStatus = async () => {
  const response = await api.get('/calendar/status');
  return response.data;
};

// Initiate Google OAuth flow
export const initiateGoogleAuth = async () => {
  const response = await api.get('/calendar/auth/google');
  return response.data;
};

// Sync syllabus to Google Calendar
export const syncSyllabusToGoogleCalendar = async (syllabusId: string) => {
  const response = await api.post('/calendar/sync-syllabus', { syllabus_id: syllabusId });
  return response.data;
};

// Complete Google OAuth flow
export const completeGoogleAuth = async (code: string) => {
  const response = await api.post('/calendar/auth/google/complete', { code });
  return response.data;
};

export default api;