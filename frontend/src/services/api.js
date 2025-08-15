import axios from 'axios'

const API_URL = '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  logout: () => api.post('/auth/logout/'),
  getUser: () => api.get('/auth/user/'),
  checkAuth: () => api.get('/auth/check/'),
}

export const assetsAPI = {
  getAssets: (params = {}) => api.get('/assets/', { params }),
  getAsset: (id) => api.get(`/assets/${id}/`),
  createAsset: (data) => api.post('/assets/', data),
  updateAsset: (id, data) => api.put(`/assets/${id}/`, data),
  partialUpdateAsset: (id, data) => api.patch(`/assets/${id}/`, data),
  deleteAsset: (id) => api.delete(`/assets/${id}/`),
  getAssetDocuments: (id) => api.get(`/assets/${id}/documents/`),
  uploadDocument: (id, data) => api.post(`/assets/${id}/upload_document/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getStats: () => api.get('/assets/stats/'),
}

export const documentsAPI = {
  getDocuments: (params = {}) => api.get('/documents/', { params }),
  getDocument: (id) => api.get(`/documents/${id}/`),
  updateDocument: (id, data) => api.put(`/documents/${id}/`, data),
  deleteDocument: (id) => api.delete(`/documents/${id}/`),
}

export default api