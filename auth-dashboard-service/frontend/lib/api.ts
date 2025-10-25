/**
 * API Client for Auth Dashboard Service
 *
 * Handles all HTTP requests to the backend API with automatic token management
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
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

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest: any = error.config;

    // If 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: any) => apiClient.post('/auth/register', data),
  login: (data: any) => apiClient.post('/auth/login', data),
  logout: () => apiClient.post('/auth/logout'),
  getMe: () => apiClient.get('/auth/me'),
  changePassword: (data: any) => apiClient.post('/auth/change-password', data),
  setupMFA: () => apiClient.post('/auth/mfa/setup'),
  verifyMFA: (data: any) => apiClient.post('/auth/mfa/verify', data),
  disableMFA: () => apiClient.post('/auth/mfa/disable'),
};

// Patient API
export const patientAPI = {
  list: (params?: any) => apiClient.get('/api/patients', { params }),
  get: (id: number) => apiClient.get(`/api/patients/${id}`),
  create: (data: any) => apiClient.post('/api/patients', data),
  update: (id: number, data: any) => apiClient.put(`/api/patients/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/patients/${id}`),
  search: (data: any) => apiClient.post('/api/patients/search', data),
};

// Prediction API
export const predictionAPI = {
  list: (params?: any) => apiClient.get('/api/predictions', { params }),
  get: (id: number) => apiClient.get(`/api/predictions/${id}`),
  getByPatient: (patientId: number, params?: any) =>
    apiClient.get(`/api/predictions/patient/${patientId}`, { params }),
  review: (id: number, data: any) => apiClient.post(`/api/predictions/${id}/review`, data),
  filter: (data: any) => apiClient.post('/api/predictions/filter', data),
  stats: () => apiClient.get('/api/predictions/stats'),
};

// User API (Admin)
export const userAPI = {
  list: (params?: any) => apiClient.get('/api/users', { params }),
  get: (id: number) => apiClient.get(`/api/users/${id}`),
  create: (data: any) => apiClient.post('/api/users', data),
  update: (id: number, data: any) => apiClient.put(`/api/users/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/users/${id}`),
  resetPassword: (id: number, data: any) => apiClient.post(`/api/users/${id}/reset-password`, data),
  stats: () => apiClient.get('/api/users/stats'),
};

// Admin API
export const adminAPI = {
  permissions: () => apiClient.get('/api/admin/permissions'),
  rolePermissions: (role: string) => apiClient.get(`/api/admin/permissions/role/${role}`),
  auditLogs: (params?: any) => apiClient.get('/api/admin/audit-logs', { params }),
  securityEvents: (params?: any) => apiClient.get('/api/admin/audit-logs/security-events', { params }),
  phiAccess: (params?: any) => apiClient.get('/api/admin/audit-logs/phi-access', { params }),
  systemHealth: () => apiClient.get('/api/admin/system/health'),
};

export default apiClient;
