import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type { TokenResponse, LoginRequest } from '../types/api'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Request interceptor to add auth token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for token refresh / auth errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (data: LoginRequest) => api.post<TokenResponse>('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
  oidcLogin: () => api.get('/auth/oidc/login'),
  oidcCallback: (code: string, state: string) => api.get('/auth/oidc/callback', { params: { code, state } }),
  oidcLogout: () => api.get('/auth/oidc/logout'),
}

export const healthApi = {
  check: () => api.get('/health'),
}

export const sessionsApi = {
  list: (params?: { page?: number; page_size?: number; space?: string }) =>
    api.get('/sessions', { params }),
  create: (data: { name: string; space?: string }) => api.post('/sessions', data),
  get: (id: number) => api.get(`/sessions/${id}`),
  update: (id: number, data: { name?: string; space?: string }) => api.patch(`/sessions/${id}`, data),
  delete: (id: number) => api.delete(`/sessions/${id}`),
  listSpaces: () => api.get('/sessions/spaces/list'),
}

export const windowsApi = {
  list: (params?: { session_id?: number; workspace?: number; page?: number; page_size?: number }) =>
    api.get('/windows', { params }),
  create: (data: { session_id: number; workspace?: number; index?: number; title?: string; command?: string; cwd?: string }) =>
    api.post('/windows', data),
  get: (id: number) => api.get(`/windows/${id}`),
  update: (id: number, data: { title?: string; command?: string; cwd?: string; agent_state?: string; quiet?: boolean }) =>
    api.patch(`/windows/${id}`, data),
  delete: (id: number) => api.delete(`/windows/${id}`),
  move: (id: number, to_session_id: number, to_workspace: number, to_index: number) =>
    api.post(`/windows/${id}/move`, null, { params: { to_session_id, to_workspace, to_index } }),
  setQuiet: (id: number, quiet: boolean) =>
    api.post(`/windows/${id}/quiet`, null, { params: { quiet } }),
}

export const attentionApi = {
  list: (params?: { kind?: string; dismissed?: boolean; page?: number; page_size?: number }) =>
    api.get('/attention', { params }),
  dismiss: (id: number, human_nonce: string) => api.post(`/attention/${id}/dismiss`, { human_nonce }),
  summary: () => api.get('/attention/stats/summary'),
}

export default api
