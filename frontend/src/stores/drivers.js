import { defineStore } from 'pinia'
import { driversAPI } from '../services/api'

export const useDriversStore = defineStore('drivers', {
  state: () => ({
    // Driver list state
    drivers: [],
    totalDrivers: 0,
    currentPage: 1,
    pageSize: 20,
    
    // Current driver details
    currentDriver: null,
    driverCertifications: [],
    driverAssignments: [],
    driverViolations: [],
    
    // Search and filter state
    searchQuery: '',
    filters: {
      employment_status: '',
      license_type: '',
      department: '',
      position: '',
      license_status: '',
      min_age: null,
      max_age: null
    },
    sortBy: 'driver_id',
    sortDesc: false,
    
    // Loading states
    isLoading: false,
    isLoadingDriver: false,
    isLoadingCertifications: false,
    isLoadingAssignments: false,
    isLoadingViolations: false,
    isCreating: false,
    isUpdating: false,
    isDeleting: false,
    isUploadingPhoto: false,
    
    // Statistics
    driverStats: {
      total_drivers: 0,
      active_drivers: 0,
      inactive_drivers: 0,
      suspended_drivers: 0,
      expired_licenses: 0,
      expiring_licenses: 0,
      license_types: {},
      age_ranges: {}
    },
    
    // Available drivers for assignment
    availableDrivers: [],
    
    // Expiration alerts
    expirationAlerts: {
      expiring_licenses: [],
      expiring_certifications: [],
      days_ahead: 30
    },
    
    // Error handling
    error: null,
    driverError: null,
    certificationError: null,
    assignmentError: null,
    violationError: null,
    photoError: null
  }),

  getters: {
    // Driver list getters
    hasDrivers: (state) => state.drivers.length > 0,
    totalPages: (state) => Math.ceil(state.totalDrivers / state.pageSize),
    hasNextPage: (state) => state.currentPage < Math.ceil(state.totalDrivers / state.pageSize),
    hasPreviousPage: (state) => state.currentPage > 1,
    
    // Current driver getters
    hasCurrentDriver: (state) => !!state.currentDriver,
    currentDriverId: (state) => state.currentDriver?.id,
    hasCertifications: (state) => state.driverCertifications.length > 0,
    hasAssignments: (state) => state.driverAssignments.length > 0,
    hasViolations: (state) => state.driverViolations.length > 0,
    
    // Filter getters
    hasActiveFilters: (state) => {
      return Object.values(state.filters).some(value => 
        value !== '' && value !== null && value !== undefined
      ) || state.searchQuery !== ''
    },
    
    // Statistics getters
    hasStats: (state) => state.driverStats.total_drivers > 0,
    licenseTypeList: (state) => Object.keys(state.driverStats.license_types || {}),
    ageRangeList: (state) => Object.keys(state.driverStats.age_ranges || {}),
    
    // Alert getters
    hasExpirationAlerts: (state) => 
      state.expirationAlerts.expiring_licenses.length > 0 || 
      state.expirationAlerts.expiring_certifications.length > 0,
    
    totalExpirationAlerts: (state) =>
      state.expirationAlerts.expiring_licenses.length + 
      state.expirationAlerts.expiring_certifications.length,
    
    // Status getters
    isAnyLoading: (state) => 
      state.isLoading || state.isLoadingDriver || state.isLoadingCertifications ||
      state.isLoadingAssignments || state.isLoadingViolations || state.isCreating || 
      state.isUpdating || state.isDeleting || state.isUploadingPhoto,
      
    hasError: (state) => !!(state.error || state.driverError || state.certificationError || 
      state.assignmentError || state.violationError || state.photoError)
  },

  actions: {
    // Driver list actions
    async fetchDrivers(options = {}) {
      this.isLoading = true
      this.error = null
      
      try {
        const params = {
          page: options.page || this.currentPage,
          page_size: this.pageSize,
          ordering: this.sortDesc ? `-${this.sortBy}` : this.sortBy,
          ...this.buildFilterParams(),
          ...options.params
        }
        
        const response = await driversAPI.getDrivers(params)
        
        this.drivers = response.data.results
        this.totalDrivers = response.data.count
        this.currentPage = options.page || this.currentPage
        
        this.$emit?.('drivers:fetched', { drivers: this.drivers, total: this.totalDrivers })
        
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch drivers'
        this.$emit?.('drivers:error', this.error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async fetchDriver(id) {
      this.isLoadingDriver = true
      this.driverError = null
      
      try {
        const response = await driversAPI.getDriver(id)
        this.currentDriver = response.data
        
        this.$emit?.('driver:fetched', this.currentDriver)
        
        return response.data
      } catch (error) {
        this.driverError = error.response?.data || 'Failed to fetch driver'
        this.$emit?.('driver:error', this.driverError)
        throw error
      } finally {
        this.isLoadingDriver = false
      }
    },

    async createDriver(driverData) {
      this.isCreating = true
      this.error = null
      
      try {
        const response = await driversAPI.createDriver(driverData)
        
        // Add to local list if on first page
        if (this.currentPage === 1) {
          this.drivers.unshift(response.data)
          this.totalDrivers += 1
        }
        
        this.$emit?.('driver:created', response.data)
        
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to create driver'
        this.$emit?.('driver:error', this.error)
        throw error
      } finally {
        this.isCreating = false
      }
    },

    async updateDriver(id, driverData) {
      this.isUpdating = true
      this.driverError = null
      
      try {
        const response = await driversAPI.updateDriver(id, driverData)
        
        // Update in local list
        const index = this.drivers.findIndex(driver => driver.id === id)
        if (index !== -1) {
          this.drivers[index] = response.data
        }
        
        // Update current driver if it's the same
        if (this.currentDriver?.id === id) {
          this.currentDriver = response.data
        }
        
        this.$emit?.('driver:updated', response.data)
        
        return response.data
      } catch (error) {
        this.driverError = error.response?.data || 'Failed to update driver'
        this.$emit?.('driver:error', this.driverError)
        throw error
      } finally {
        this.isUpdating = false
      }
    },

    async partialUpdateDriver(id, driverData) {
      this.isUpdating = true
      this.driverError = null
      
      try {
        const response = await driversAPI.partialUpdateDriver(id, driverData)
        
        // Update in local list
        const index = this.drivers.findIndex(driver => driver.id === id)
        if (index !== -1) {
          this.drivers[index] = { ...this.drivers[index], ...response.data }
        }
        
        // Update current driver if it's the same
        if (this.currentDriver?.id === id) {
          this.currentDriver = { ...this.currentDriver, ...response.data }
        }
        
        this.$emit?.('driver:updated', response.data)
        
        return response.data
      } catch (error) {
        this.driverError = error.response?.data || 'Failed to update driver'
        this.$emit?.('driver:error', this.driverError)
        throw error
      } finally {
        this.isUpdating = false
      }
    },

    async uploadDriverPhoto(id, formData) {
      this.isUploadingPhoto = true
      this.error = null
      
      try {
        const response = await driversAPI.uploadPhoto(id, formData)
        
        // Update current driver if it's the same
        if (this.currentDriver?.id === id) {
          this.currentDriver.profile_photo = response.data.photo
        }
        
        // Update in local list
        const index = this.drivers.findIndex(driver => driver.id === id)
        if (index !== -1) {
          this.drivers[index].profile_photo = response.data.photo
        }
        
        this.$emit?.('driver:photo_uploaded', { id, photo: response.data.photo })
        
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to upload photo'
        this.$emit?.('driver:error', this.error)
        throw error
      } finally {
        this.isUploadingPhoto = false
      }
    },

    async deleteDriver(id) {
      this.isDeleting = true
      this.error = null
      
      try {
        await driversAPI.deleteDriver(id)
        
        // Remove from local list
        this.drivers = this.drivers.filter(driver => driver.id !== id)
        this.totalDrivers -= 1
        
        // Clear current driver if it's the same
        if (this.currentDriver?.id === id) {
          this.currentDriver = null
        }
        
        this.$emit?.('driver:deleted', { id })
        
        return true
      } catch (error) {
        this.error = error.response?.data || 'Failed to delete driver'
        this.$emit?.('driver:error', this.error)
        throw error
      } finally {
        this.isDeleting = false
      }
    },

    // Certification actions
    async fetchDriverCertifications(driverId) {
      this.isLoadingCertifications = true
      this.certificationError = null
      
      try {
        const response = await driversAPI.getDriverCertifications(driverId)
        this.driverCertifications = response.data
        
        this.$emit?.('certifications:fetched', this.driverCertifications)
        
        return response.data
      } catch (error) {
        this.certificationError = error.response?.data || 'Failed to fetch certifications'
        this.$emit?.('certifications:error', this.certificationError)
        throw error
      } finally {
        this.isLoadingCertifications = false
      }
    },

    async addDriverCertification(driverId, certificationData) {
      this.certificationError = null
      
      try {
        const response = await driversAPI.addDriverCertification(driverId, certificationData)
        
        // Add to local certifications list
        this.driverCertifications.unshift(response.data)
        
        this.$emit?.('certification:added', response.data)
        
        return response.data
      } catch (error) {
        this.certificationError = error.response?.data || 'Failed to add certification'
        this.$emit?.('certification:error', this.certificationError)
        throw error
      }
    },

    // Assignment actions
    async fetchDriverAssignments(driverId) {
      this.isLoadingAssignments = true
      this.assignmentError = null
      
      try {
        const response = await driversAPI.getDriverAssignments(driverId)
        this.driverAssignments = response.data
        
        this.$emit?.('assignments:fetched', this.driverAssignments)
        
        return response.data
      } catch (error) {
        this.assignmentError = error.response?.data || 'Failed to fetch assignments'
        this.$emit?.('assignments:error', this.assignmentError)
        throw error
      } finally {
        this.isLoadingAssignments = false
      }
    },

    async assignAssetToDriver(driverId, assignmentData) {
      this.assignmentError = null
      
      try {
        const response = await driversAPI.assignAsset(driverId, assignmentData)
        
        // Add to local assignments list
        this.driverAssignments.unshift(response.data)
        
        this.$emit?.('assignment:created', response.data)
        
        return response.data
      } catch (error) {
        this.assignmentError = error.response?.data || 'Failed to assign asset'
        this.$emit?.('assignment:error', this.assignmentError)
        throw error
      }
    },

    async unassignAssetFromDriver(driverId, assetId) {
      this.assignmentError = null
      
      try {
        const response = await driversAPI.unassignAsset(driverId, { asset_id: assetId })
        
        // Update local assignments list
        const index = this.driverAssignments.findIndex(
          assignment => assignment.asset_details.id === assetId && assignment.is_current
        )
        if (index !== -1) {
          this.driverAssignments[index] = response.data
        }
        
        this.$emit?.('assignment:updated', response.data)
        
        return response.data
      } catch (error) {
        this.assignmentError = error.response?.data || 'Failed to unassign asset'
        this.$emit?.('assignment:error', this.assignmentError)
        throw error
      }
    },

    async createDriverAssetAssignment(assignmentData) {
      this.assignmentError = null
      
      try {
        const response = await driversAPI.createAssignment(assignmentData)
        
        this.$emit?.('assignment:created', response.data)
        
        return response.data
      } catch (error) {
        this.assignmentError = error.response?.data || 'Failed to create assignment'
        this.$emit?.('assignment:error', this.assignmentError)
        throw error
      }
    },

    // Violation actions
    async fetchDriverViolations(driverId) {
      this.isLoadingViolations = true
      this.violationError = null
      
      try {
        const response = await driversAPI.getDriverViolations(driverId)
        this.driverViolations = response.data
        
        this.$emit?.('violations:fetched', this.driverViolations)
        
        return response.data
      } catch (error) {
        this.violationError = error.response?.data || 'Failed to fetch violations'
        this.$emit?.('violations:error', this.violationError)
        throw error
      } finally {
        this.isLoadingViolations = false
      }
    },

    // Photo actions
    async uploadDriverPhoto(driverId, formData) {
      this.isUploadingPhoto = true
      this.photoError = null
      
      try {
        const response = await driversAPI.uploadPhoto(driverId, formData)
        
        // Update current driver if it's the same
        if (this.currentDriver?.id === driverId) {
          this.currentDriver.profile_photo = response.data.photo
        }
        
        // Update driver in drivers list
        const driverIndex = this.drivers.findIndex(driver => driver.id === driverId)
        if (driverIndex !== -1) {
          this.drivers[driverIndex].profile_photo = response.data.photo
        }
        
        this.$emit?.('photo:uploaded', response.data)
        
        return response.data
      } catch (error) {
        this.photoError = error.response?.data?.error || 'Failed to upload photo'
        this.$emit?.('photo:error', this.photoError)
        throw error
      } finally {
        this.isUploadingPhoto = false
      }
    },

    // Statistics actions
    async fetchDriverStats() {
      try {
        const response = await driversAPI.getStats()
        this.driverStats = response.data
        
        this.$emit?.('stats:fetched', this.driverStats)
        
        return response.data
      } catch (error) {
        console.error('Failed to fetch driver statistics:', error)
        return null
      }
    },

    // Available drivers actions
    async fetchAvailableDrivers() {
      try {
        const response = await driversAPI.getAvailableDrivers()
        this.availableDrivers = response.data
        
        this.$emit?.('available-drivers:fetched', this.availableDrivers)
        
        return response.data
      } catch (error) {
        console.error('Failed to fetch available drivers:', error)
        throw error
      }
    },

    // Expiration alerts actions
    async fetchExpirationAlerts(days = 30) {
      try {
        const response = await driversAPI.getExpirationAlerts({ days })
        this.expirationAlerts = response.data
        
        this.$emit?.('alerts:fetched', this.expirationAlerts)
        
        return response.data
      } catch (error) {
        console.error('Failed to fetch expiration alerts:', error)
        throw error
      }
    },

    // Search and filter actions
    setSearchQuery(query) {
      this.searchQuery = query
      this.$emit?.('search:changed', query)
    },

    setFilter(key, value) {
      this.filters[key] = value
      this.$emit?.('filter:changed', { key, value })
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      this.$emit?.('filters:changed', this.filters)
    },

    clearFilters() {
      this.filters = {
        employment_status: '',
        license_type: '',
        department: '',
        position: '',
        license_status: '',
        min_age: null,
        max_age: null
      }
      this.searchQuery = ''
      this.$emit?.('filters:cleared')
    },

    setSorting(sortBy, sortDesc = false) {
      this.sortBy = sortBy
      this.sortDesc = sortDesc
      this.$emit?.('sort:changed', { sortBy, sortDesc })
    },

    setPage(page) {
      this.currentPage = page
      this.$emit?.('page:changed', page)
    },

    // Utility actions
    buildFilterParams() {
      const params = {}
      
      if (this.searchQuery) {
        params.search = this.searchQuery
      }
      
      Object.entries(this.filters).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          params[key] = value
        }
      })
      
      return params
    },

    clearError() {
      this.error = null
      this.driverError = null
      this.certificationError = null
      this.assignmentError = null
      this.violationError = null
      this.photoError = null
    },

    clearCurrentDriver() {
      this.currentDriver = null
      this.driverCertifications = []
      this.driverAssignments = []
      this.driverViolations = []
    },

    // Event emission helper (for pure component testing)
    $emit(event, payload) {
      // This will be overridden by components that need event emission
      // Allows for pure testing without side effects
    }
  }
})