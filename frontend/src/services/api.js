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
  // Generic methods for user management
  get: (url) => api.get(url),
  post: (url, data) => api.post(url, data),
  delete: (url) => api.delete(url)
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
  uploadImage: (id, data) => api.post(`/assets/${id}/upload_image/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteImage: (id) => api.delete(`/assets/${id}/delete_image/`),
  getStats: () => api.get('/assets/stats/'),
  bulkImport: (data) => api.post('/assets/bulk_import/', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  downloadTemplate: () => api.get('/assets/download_template/', {
    responseType: 'text'
  }),
}

export const documentsAPI = {
  getDocuments: (params = {}) => api.get('/documents/', { params }),
  getDocument: (id) => api.get(`/documents/${id}/`),
  updateDocument: (id, data) => api.put(`/documents/${id}/`, data),
  deleteDocument: (id) => api.delete(`/documents/${id}/`),
}

export const locationsAPI = {
  // Location updates endpoints
  getLocationUpdates: (params = {}) => api.get('/locations/updates/', { params }),
  getLocationUpdate: (id) => api.get(`/locations/updates/${id}/`),
  createLocationUpdate: (data) => api.post('/locations/updates/', data),
  updateLocationUpdate: (id, data) => api.put(`/locations/updates/${id}/`, data),
  deleteLocationUpdate: (id) => api.delete(`/locations/updates/${id}/`),
  
  // Specialized location endpoints
  getLatestLocations: (params = {}) => api.get('/locations/updates/latest/', { params }),
  createManualEntry: (data) => api.post('/locations/updates/manual_entry/', data),
  bulkCreateLocations: (data) => api.post('/locations/updates/bulk_create/', data),
  getAssetHistory: (assetId, params = {}) => api.get(`/locations/updates/asset/${assetId}/`, { params }),
  getLocationStats: () => api.get('/locations/updates/stats/'),
  
  // Location zones endpoints
  getLocationZones: (params = {}) => api.get('/locations/zones/', { params }),
  getLocationZone: (id) => api.get(`/locations/zones/${id}/`),
  createLocationZone: (data) => api.post('/locations/zones/', data),
  updateLocationZone: (id, data) => api.put(`/locations/zones/${id}/`, data),
  deleteLocationZone: (id) => api.delete(`/locations/zones/${id}/`),
  getAssetsInZone: (zoneId) => api.get(`/locations/zones/${zoneId}/assets_in_zone/`),
  checkPointInZone: (zoneId, data) => api.post(`/locations/zones/${zoneId}/check_point/`, data),
  
  // Current locations endpoints
  getCurrentLocations: (params = {}) => api.get('/locations/current/', { params }),
  getCurrentLocation: (id) => api.get(`/locations/current/${id}/`),
  getMapData: (params = {}) => api.get('/locations/current/map_data/', { params }),
}

export const driversAPI = {
  // Driver CRUD endpoints
  getDrivers: (params = {}) => api.get('/drivers/drivers/', { params }),
  getDriver: (id) => api.get(`/drivers/drivers/${id}/`),
  createDriver: (data) => api.post('/drivers/drivers/', data),
  updateDriver: (id, data) => api.put(`/drivers/drivers/${id}/`, data),
  partialUpdateDriver: (id, data) => api.patch(`/drivers/drivers/${id}/`, data),
  deleteDriver: (id) => api.delete(`/drivers/drivers/${id}/`),
  
  // Driver photo management
  uploadPhoto: (id, data) => api.post(`/drivers/drivers/${id}/upload_photo/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deletePhoto: (id) => api.delete(`/drivers/drivers/${id}/delete_photo/`),
  
  // Driver certifications
  getDriverCertifications: (driverId) => api.get(`/drivers/drivers/${driverId}/certifications/`),
  addDriverCertification: (driverId, data) => api.post(`/drivers/drivers/${driverId}/add_certification/`, data),
  
  // Driver asset assignments
  getDriverAssignments: (driverId) => api.get(`/drivers/drivers/${driverId}/assignments/`),
  assignAsset: (driverId, data) => api.post(`/drivers/drivers/${driverId}/assign_asset/`, data),
  unassignAsset: (driverId, data) => api.post(`/drivers/drivers/${driverId}/unassign_asset/`, data),
  
  // Driver violations
  getDriverViolations: (driverId) => api.get(`/drivers/drivers/${driverId}/violations/`),
  
  // Driver statistics and reports
  getStats: () => api.get('/drivers/drivers/stats/'),
  getExpirationAlerts: (params = {}) => api.get('/drivers/drivers/expiration_alerts/', { params }),
  getAvailableDrivers: () => api.get('/drivers/drivers/available_drivers/'),
  
  // Certification management (standalone)
  getCertifications: (params = {}) => api.get('/drivers/certifications/', { params }),
  getCertification: (id) => api.get(`/drivers/certifications/${id}/`),
  createCertification: (data) => api.post('/drivers/certifications/', data),
  updateCertification: (id, data) => api.put(`/drivers/certifications/${id}/`, data),
  deleteCertification: (id) => api.delete(`/drivers/certifications/${id}/`),
  
  // Assignment management (standalone)
  getAssignments: (params = {}) => api.get('/drivers/assignments/', { params }),
  getAssignment: (id) => api.get(`/drivers/assignments/${id}/`),
  createAssignment: (data) => api.post('/drivers/assignments/', data),
  updateAssignment: (id, data) => api.put(`/drivers/assignments/${id}/`, data),
  deleteAssignment: (id) => api.delete(`/drivers/assignments/${id}/`),
  getCurrentAssignments: () => api.get('/drivers/assignments/current_assignments/'),
  
  // Violation management (standalone)
  getViolations: (params = {}) => api.get('/drivers/violations/', { params }),
  getViolation: (id) => api.get(`/drivers/violations/${id}/`),
  createViolation: (data) => api.post('/drivers/violations/', data),
  updateViolation: (id, data) => api.put(`/drivers/violations/${id}/`, data),
  deleteViolation: (id) => api.delete(`/drivers/violations/${id}/`),
}

export const fuelAPI = {
  // Fuel transactions
  getFuelTransactions: (params = {}) => api.get('/fuel/transactions/', { params }),
  getFuelTransaction: (id) => api.get(`/fuel/transactions/${id}/`),
  createFuelTransaction: (data) => api.post('/fuel/transactions/', data),
  updateFuelTransaction: (id, data) => api.put(`/fuel/transactions/${id}/`, data),
  deleteFuelTransaction: (id) => api.delete(`/fuel/transactions/${id}/`),
  
  // Fuel statistics and reporting
  getFuelStats: (params = {}) => api.get('/fuel/transactions/stats/', { params }),
  bulkCreateTransactions: (data) => api.post('/fuel/transactions/bulk_create/', data),
  
  // CSV import
  importFuelCSV: (formData, previewOnly = false) => {
    if (previewOnly) {
      formData.append('preview_only', 'true')
    }
    return api.post('/fuel/transactions/import_csv/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // Fuel sites
  getFuelSites: (params = {}) => api.get('/fuel/sites/', { params }),
  getFuelSite: (id) => api.get(`/fuel/sites/${id}/`),
  createFuelSite: (data) => api.post('/fuel/sites/', data),
  updateFuelSite: (id, data) => api.put(`/fuel/sites/${id}/`, data),
  deleteFuelSite: (id) => api.delete(`/fuel/sites/${id}/`),
  
  // Fuel cards
  getFuelCards: (params = {}) => api.get('/fuel/cards/', { params }),
  getFuelCard: (id) => api.get(`/fuel/cards/${id}/`),
  createFuelCard: (data) => api.post('/fuel/cards/', data),
  updateFuelCard: (id, data) => api.put(`/fuel/cards/${id}/`, data),
  deleteFuelCard: (id) => api.delete(`/fuel/cards/${id}/`),
  
  // Fuel alerts
  getFuelAlerts: (params = {}) => api.get('/fuel/alerts/', { params }),
  getFuelAlert: (id) => api.get(`/fuel/alerts/${id}/`),
  createFuelAlert: (data) => api.post('/fuel/alerts/', data),
  updateFuelAlert: (id, data) => api.put(`/fuel/alerts/${id}/`, data),
  deleteFuelAlert: (id) => api.delete(`/fuel/alerts/${id}/`),
  resolveFuelAlert: (id, data) => api.post(`/fuel/alerts/${id}/resolve/`, data),
  acknowledgeFuelAlert: (id) => api.post(`/fuel/alerts/${id}/acknowledge/`),
  
  // Units policy
  getUnitsPolicy: () => api.get('/fuel/policy/current/'),
  updateUnitsPolicy: (id, data) => api.put(`/fuel/policy/${id}/`, data),
}

export default api