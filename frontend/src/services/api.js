import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available (Django Token Auth format)
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

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Authentication API
export const authAPI = {
  login: (credentials) => api.post('/auth/token/', credentials),
  register: (userData) => api.post('/accounts/register/', userData),
  logout: () => {
    localStorage.removeItem('token')
    return Promise.resolve()
  },
  checkAuth: () => api.get('/accounts/check-auth/')
}

// Assets API
export const assetsAPI = {
  // Departments
  getDepartments: (params) => api.get('/assets/departments/', { params }),
  createDepartment: (data) => api.post('/assets/departments/', data),
  updateDepartment: (id, data) => api.put(`/assets/departments/${id}/`, data),
  deleteDepartment: (id) => api.delete(`/assets/departments/${id}/`),

  // Assets
  getAssets: (params) => api.get('/assets/assets/', { params }),
  getAsset: (id) => api.get(`/assets/assets/${id}/`),
  createAsset: (data) => api.post('/assets/assets/', data),
  updateAsset: (id, data) => api.put(`/assets/assets/${id}/`, data),
  deleteAsset: (id) => api.delete(`/assets/assets/${id}/`),
  getAssetStatistics: () => api.get('/assets/assets/statistics/'),
  getExpiringAssets: (params) => api.get('/assets/assets/expiring_documents/', { params }),
  updateOdometer: (id, data) => api.patch(`/assets/assets/${id}/update_odometer/`, data),

  // Asset Documents & Images
  getAssetDocuments: (assetId) => api.get(`/assets/assets/${assetId}/documents/`),
  getAssetImages: (assetId) => api.get(`/assets/assets/${assetId}/images/`),
  uploadAssetDocument: (assetId, formData) => api.post(`/assets/assets/${assetId}/upload_document/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  uploadAssetImage: (assetId, formData) => api.post(`/assets/assets/${assetId}/upload_image/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteAssetDocument: (assetId, documentId) => api.delete(`/assets/assets/${assetId}/documents/${documentId}/`),
  deleteAssetImage: (assetId, imageId) => api.delete(`/assets/assets/${assetId}/images/${imageId}/`)
}

// Drivers API
export const driversAPI = {
  getDrivers: (params) => api.get('/drivers/drivers/', { params }),
  getDriver: (id) => api.get(`/drivers/drivers/${id}/`),
  createDriver: (data) => api.post('/drivers/drivers/', data),
  updateDriver: (id, data) => api.put(`/drivers/drivers/${id}/`, data),
  deleteDriver: (id) => api.delete(`/drivers/drivers/${id}/`),
  getDriverStatistics: () => api.get('/drivers/drivers/statistics/'),
  getLicenseAlerts: (params) => api.get('/drivers/drivers/license_alerts/', { params }),
  getCertificationAlerts: (params) => api.get('/drivers/drivers/certification_alerts/', { params }),
  getDriverSafetyReport: (id) => api.get(`/drivers/drivers/${id}/safety_report/`),

  // Driver Certifications
  getCertifications: (params) => api.get('/drivers/certifications/', { params }),
  createCertification: (data) => api.post('/drivers/certifications/', data),
  updateCertification: (id, data) => api.put(`/drivers/certifications/${id}/`, data),
  deleteCertification: (id) => api.delete(`/drivers/certifications/${id}/`),

  // Driver Incidents
  getIncidents: (params) => api.get('/drivers/incidents/', { params }),
  createIncident: (data) => api.post('/drivers/incidents/', data),
  updateIncident: (id, data) => api.put(`/drivers/incidents/${id}/`, data),
  deleteIncident: (id) => api.delete(`/drivers/incidents/${id}/`),

  // Driver Training
  getTraining: (params) => api.get('/drivers/training/', { params }),
  createTraining: (data) => api.post('/drivers/training/', data),
  updateTraining: (id, data) => api.put(`/drivers/training/${id}/`, data),
  deleteTraining: (id) => api.delete(`/drivers/training/${id}/`)
}

// Maintenance API
export const maintenanceAPI = {
  // Maintenance Types
  getMaintenanceTypes: (params) => api.get('/maintenance/maintenance-types/', { params }),
  createMaintenanceType: (data) => api.post('/maintenance/maintenance-types/', data),

  // Maintenance Schedules
  getSchedules: (params) => api.get('/maintenance/schedules/', { params }),
  getMaintenanceSchedules: (params) => api.get('/maintenance/schedules/', { params }),
  getSchedule: (id) => api.get(`/maintenance/schedules/${id}/`),
  createSchedule: (data) => api.post('/maintenance/schedules/', data),
  updateSchedule: (id, data) => api.put(`/maintenance/schedules/${id}/`, data),
  deleteSchedule: (id) => api.delete(`/maintenance/schedules/${id}/`),
  getScheduleStatistics: () => api.get('/maintenance/schedules/statistics/'),
  getDueMaintenance: (params) => api.get('/maintenance/schedules/due_maintenance/', { params }),

  // Maintenance Records
  getRecords: (params) => api.get('/maintenance/records/', { params }),
  getMaintenanceRecords: (params) => api.get('/maintenance/records/', { params }),
  getRecord: (id) => api.get(`/maintenance/records/${id}/`),
  createRecord: (data) => api.post('/maintenance/records/', data),
  updateRecord: (id, data) => api.put(`/maintenance/records/${id}/`, data),
  getRecordStatistics: () => api.get('/maintenance/records/statistics/'),
  getCostAnalysis: (params) => api.get('/maintenance/records/cost_analysis/', { params }),

  // Maintenance Parts
  getParts: (params) => api.get('/maintenance/parts/', { params }),
  createPart: (data) => api.post('/maintenance/parts/', data),
  updatePart: (id, data) => api.put(`/maintenance/parts/${id}/`, data),
  getLowStockAlerts: () => api.get('/maintenance/parts/low_stock_alerts/'),
  getInventorySummary: () => api.get('/maintenance/parts/inventory_summary/')
}

// Work Orders API
export const workOrdersAPI = {
  getWorkOrders: (params) => api.get('/work-orders/work-orders/', { params }),
  getWorkOrder: (id) => api.get(`/work-orders/work-orders/${id}/`),
  createWorkOrder: (data) => api.post('/work-orders/work-orders/', data),
  updateWorkOrder: (id, data) => api.put(`/work-orders/work-orders/${id}/`, data),
  deleteWorkOrder: (id) => api.delete(`/work-orders/work-orders/${id}/`),
  getWorkOrderStatistics: () => api.get('/work-orders/work-orders/statistics/'),
  getDashboard: () => api.get('/work-orders/work-orders/dashboard/'),
  
  // Work Order Actions
  updateStatus: (id, data) => api.patch(`/work-orders/work-orders/${id}/update_status/`, data),
  updateProgress: (id, data) => api.patch(`/work-orders/work-orders/${id}/update_progress/`, data),
  addComment: (id, data) => api.post(`/work-orders/work-orders/${id}/add_comment/`, data),
  uploadPhoto: (id, formData) => api.post(`/work-orders/work-orders/${id}/upload_photo/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  uploadDocument: (id, formData) => api.post(`/work-orders/work-orders/${id}/upload_document/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// Tracking API
export const trackingAPI = {
  // Location Points (GPS Data)
  getLocationPoints: (params) => api.get('/tracking/location-points/', { params }),
  getLocationHistory: (params) => api.get('/tracking/location-points/', { params }),
  createLocationPoints: (data) => api.post('/tracking/location-points/bulk_create/', data),
  getLatestPositions: () => api.get('/tracking/location-points/latest_positions/'),

  // Zones (Geofences)
  getZones: (params) => api.get('/tracking/zones/', { params }),
  createZone: (data) => api.post('/tracking/zones/', data),
  updateZone: (id, data) => api.put(`/tracking/zones/${id}/`, data),
  deleteZone: (id) => api.delete(`/tracking/zones/${id}/`),
  getActiveZones: () => api.get('/tracking/zones/active_zones/'),

  // Zone Events
  getZoneEvents: (params) => api.get('/tracking/zone-events/', { params }),
  getRecentAlerts: (params) => api.get('/tracking/zone-events/recent_alerts/', { params }),
  getZoneEventStatistics: (params) => api.get('/tracking/zone-events/statistics/', { params }),

  // Routes
  getRoutes: (params) => api.get('/tracking/routes/', { params }),
  createRoute: (data) => api.post('/tracking/routes/', data),
  updateRoute: (id, data) => api.put(`/tracking/routes/${id}/`, data),
  getActiveRoutes: () => api.get('/tracking/routes/active_routes/'),

  // Trips
  getTrips: (params) => api.get('/tracking/trips/', { params }),
  getTrip: (id) => api.get(`/tracking/trips/${id}/`),
  createTrip: (data) => api.post('/tracking/trips/', data),
  updateTrip: (id, data) => api.put(`/tracking/trips/${id}/`, data),
  getTripStatistics: (params) => api.get('/tracking/trips/statistics/', { params }),
  getActiveTrips: () => api.get('/tracking/trips/active_trips/'),
  getLiveTracking: () => api.get('/tracking/trips/live_tracking/'),
  startTrip: (id, data) => api.patch(`/tracking/trips/${id}/start_trip/`, data),
  endTrip: (id, data) => api.patch(`/tracking/trips/${id}/end_trip/`, data),
  getRouteReplay: (id) => api.get(`/tracking/trips/${id}/route_replay/`)
}

export default api