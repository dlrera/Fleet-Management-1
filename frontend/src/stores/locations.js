import { defineStore } from 'pinia'
import { locationsAPI } from '../services/api'

export const useLocationsStore = defineStore('locations', {
  state: () => ({
    // Location updates state
    locationUpdates: [],
    totalUpdates: 0,
    currentPage: 1,
    pageSize: 20,
    
    // Current asset location data
    assetLocations: [],
    mapData: null,
    
    // Location zones state
    locationZones: [],
    currentZone: null,
    
    // Filters and search
    searchQuery: '',
    filters: {
      source: '',
      asset_status: '',
      vehicle_type: '',
      zone_id: '',
      within_hours: 24
    },
    sortBy: 'timestamp',
    sortDesc: true,
    
    // Loading states
    isLoading: false,
    isLoadingAsset: false,
    isLoadingZones: false,
    isLoadingMap: false,
    isCreating: false,
    isUpdating: false,
    isDeleting: false,
    
    // Statistics
    locationStats: {
      total_updates: 0,
      today_updates: 0,
      assets_with_recent_locations: 0,
      total_trackable_assets: 0,
      tracking_coverage: 0,
      source_breakdown: {}
    },
    
    // Error handling
    error: null,
    locationError: null,
    zoneError: null,
    mapError: null,
  }),

  getters: {
    // Location updates getters
    hasLocationUpdates: (state) => state.locationUpdates.length > 0,
    totalPages: (state) => Math.ceil(state.totalUpdates / state.pageSize),
    hasNextPage: (state) => state.currentPage < Math.ceil(state.totalUpdates / state.pageSize),
    hasPreviousPage: (state) => state.currentPage > 1,
    
    // Asset locations getters
    hasAssetLocations: (state) => state.assetLocations.length > 0,
    hasMapData: (state) => !!state.mapData,
    
    // Zones getters
    hasZones: (state) => state.locationZones.length > 0,
    activeZones: (state) => state.locationZones.filter(zone => zone.is_active),
    hasCurrentZone: (state) => !!state.currentZone,
    
    // Filter getters
    hasActiveFilters: (state) => {
      return Object.values(state.filters).some(value => 
        value !== '' && value !== null && value !== undefined
      ) || state.searchQuery !== ''
    },
    
    // Statistics getters
    hasStats: (state) => state.locationStats.total_updates > 0,
    trackingCoveragePercent: (state) => 
      Math.round(state.locationStats.tracking_coverage || 0),
    
    // Status getters
    isAnyLoading: (state) => 
      state.isLoading || state.isLoadingAsset || state.isLoadingZones ||
      state.isLoadingMap || state.isCreating || state.isUpdating || state.isDeleting,
      
    hasError: (state) => !!state.error || !!state.locationError || !!state.zoneError || !!state.mapError,
  },

  actions: {
    // Location updates actions
    async fetchLocationUpdates(options = {}) {
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
        
        const response = await locationsAPI.getLocationUpdates(params)
        
        this.locationUpdates = response.data.results
        this.totalUpdates = response.data.count
        this.currentPage = options.page || this.currentPage
        
        this.$emit?.('locations:fetched', { locations: this.locationUpdates, total: this.totalUpdates })
        
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch location updates'
        this.$emit?.('locations:error', this.error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async fetchAssetLocations(options = {}) {
      this.isLoadingAsset = true
      this.locationError = null
      
      try {
        const params = {
          ...this.buildFilterParams(),
          ...options.params
        }
        
        const response = await locationsAPI.getCurrentLocations(params)
        this.assetLocations = response.data.results || response.data
        
        this.$emit?.('asset-locations:fetched', this.assetLocations)
        
        return response.data
      } catch (error) {
        this.locationError = error.response?.data || 'Failed to fetch asset locations'
        this.$emit?.('asset-locations:error', this.locationError)
        throw error
      } finally {
        this.isLoadingAsset = false
      }
    },

    async fetchMapData(options = {}) {
      this.isLoadingMap = true
      this.mapError = null
      
      try {
        const params = {
          within_hours: options.within_hours || this.filters.within_hours,
          ...options.params
        }
        
        const response = await locationsAPI.getMapData(params)
        this.mapData = response.data
        
        this.$emit?.('map-data:fetched', this.mapData)
        
        return response.data
      } catch (error) {
        this.mapError = error.response?.data || 'Failed to fetch map data'
        this.$emit?.('map-data:error', this.mapError)
        throw error
      } finally {
        this.isLoadingMap = false
      }
    },

    async createLocationUpdate(locationData) {
      this.isCreating = true
      this.error = null
      
      try {
        const response = await locationsAPI.createLocationUpdate(locationData)
        
        // Add to local list if on first page
        if (this.currentPage === 1) {
          this.locationUpdates.unshift(response.data)
          this.totalUpdates += 1
        }
        
        this.$emit?.('location:created', response.data)
        
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to create location update'
        this.$emit?.('location:error', this.error)
        throw error
      } finally {
        this.isCreating = false
      }
    },

    async createManualLocationEntry(entryData) {
      this.isCreating = true
      this.error = null
      
      try {
        const response = await locationsAPI.createManualEntry(entryData)
        
        // Refresh map data to show new location
        await this.fetchMapData()
        
        this.$emit?.('manual-location:created', response.data)
        
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to create manual location entry'
        this.$emit?.('manual-location:error', this.error)
        throw error
      } finally {
        this.isCreating = false
      }
    },

    async fetchAssetLocationHistory(assetId, options = {}) {
      this.isLoadingAsset = true
      this.locationError = null
      
      try {
        const params = {
          days: options.days || 7,
          limit: options.limit || 100,
          ...options.params
        }
        
        const response = await locationsAPI.getAssetHistory(assetId, params)
        
        this.$emit?.('asset-history:fetched', response.data)
        
        return response.data
      } catch (error) {
        this.locationError = error.response?.data || 'Failed to fetch asset location history'
        this.$emit?.('asset-history:error', this.locationError)
        throw error
      } finally {
        this.isLoadingAsset = false
      }
    },

    async fetchLatestLocations(options = {}) {
      this.isLoadingAsset = true
      this.locationError = null
      
      try {
        const params = {
          status: options.status,
          ...options.params
        }
        
        const response = await locationsAPI.getLatestLocations(params)
        this.assetLocations = response.data
        
        this.$emit?.('latest-locations:fetched', this.assetLocations)
        
        return response.data
      } catch (error) {
        this.locationError = error.response?.data || 'Failed to fetch latest locations'
        this.$emit?.('latest-locations:error', this.locationError)
        throw error
      } finally {
        this.isLoadingAsset = false
      }
    },

    // Location zones actions
    async fetchLocationZones(options = {}) {
      this.isLoadingZones = true
      this.zoneError = null
      
      try {
        const params = {
          ...options.params
        }
        
        const response = await locationsAPI.getLocationZones(params)
        this.locationZones = response.data.results || response.data
        
        this.$emit?.('zones:fetched', this.locationZones)
        
        return response.data
      } catch (error) {
        this.zoneError = error.response?.data || 'Failed to fetch location zones'
        this.$emit?.('zones:error', this.zoneError)
        throw error
      } finally {
        this.isLoadingZones = false
      }
    },

    async createLocationZone(zoneData) {
      this.isCreating = true
      this.zoneError = null
      
      try {
        const response = await locationsAPI.createLocationZone(zoneData)
        
        // Add to local list
        this.locationZones.unshift(response.data)
        
        this.$emit?.('zone:created', response.data)
        
        return response.data
      } catch (error) {
        this.zoneError = error.response?.data || 'Failed to create location zone'
        this.$emit?.('zone:error', this.zoneError)
        throw error
      } finally {
        this.isCreating = false
      }
    },

    async updateLocationZone(id, zoneData) {
      this.isUpdating = true
      this.zoneError = null
      
      try {
        const response = await locationsAPI.updateLocationZone(id, zoneData)
        
        // Update in local list
        const index = this.locationZones.findIndex(zone => zone.id === id)
        if (index !== -1) {
          this.locationZones[index] = response.data
        }
        
        // Update current zone if it's the same
        if (this.currentZone?.id === id) {
          this.currentZone = response.data
        }
        
        this.$emit?.('zone:updated', response.data)
        
        return response.data
      } catch (error) {
        this.zoneError = error.response?.data || 'Failed to update location zone'
        this.$emit?.('zone:error', this.zoneError)
        throw error
      } finally {
        this.isUpdating = false
      }
    },

    async deleteLocationZone(id) {
      this.isDeleting = true
      this.zoneError = null
      
      try {
        await locationsAPI.deleteLocationZone(id)
        
        // Remove from local list
        this.locationZones = this.locationZones.filter(zone => zone.id !== id)
        
        // Clear current zone if it's the same
        if (this.currentZone?.id === id) {
          this.currentZone = null
        }
        
        this.$emit?.('zone:deleted', { id })
        
        return true
      } catch (error) {
        this.zoneError = error.response?.data || 'Failed to delete location zone'
        this.$emit?.('zone:error', this.zoneError)
        throw error
      } finally {
        this.isDeleting = false
      }
    },

    async fetchAssetsInZone(zoneId) {
      this.isLoadingZones = true
      this.zoneError = null
      
      try {
        const response = await locationsAPI.getAssetsInZone(zoneId)
        
        this.$emit?.('zone-assets:fetched', response.data)
        
        return response.data
      } catch (error) {
        this.zoneError = error.response?.data || 'Failed to fetch assets in zone'
        this.$emit?.('zone-assets:error', this.zoneError)
        throw error
      } finally {
        this.isLoadingZones = false
      }
    },

    async checkPointInZone(zoneId, latitude, longitude) {
      try {
        const response = await locationsAPI.checkPointInZone(zoneId, { latitude, longitude })
        
        this.$emit?.('point-check:completed', response.data)
        
        return response.data
      } catch (error) {
        this.zoneError = error.response?.data || 'Failed to check point in zone'
        this.$emit?.('point-check:error', this.zoneError)
        throw error
      }
    },

    // Statistics actions
    async fetchLocationStats() {
      try {
        const response = await locationsAPI.getLocationStats()
        this.locationStats = response.data
        
        this.$emit?.('location-stats:fetched', this.locationStats)
        
        return response.data
      } catch (error) {
        console.error('Failed to fetch location statistics:', error)
        // Don't throw here as stats are not critical
        return null
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
        source: '',
        asset_status: '',
        vehicle_type: '',
        zone_id: '',
        within_hours: 24
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
      this.locationError = null
      this.zoneError = null
      this.mapError = null
    },

    clearCurrentZone() {
      this.currentZone = null
    },

    // Real-time updates (for future websocket integration)
    handleLocationUpdate(locationData) {
      // Add to beginning of updates list if on first page
      if (this.currentPage === 1) {
        this.locationUpdates.unshift(locationData)
        // Keep list size manageable
        if (this.locationUpdates.length > this.pageSize) {
          this.locationUpdates.pop()
        }
      }
      
      // Update asset locations if asset is already tracked
      const assetIndex = this.assetLocations.findIndex(
        loc => loc.asset.id === locationData.asset.id
      )
      if (assetIndex !== -1) {
        this.assetLocations[assetIndex] = locationData
      }
      
      this.$emit?.('location:real-time-update', locationData)
    },

    // Event emission helper (for pure component testing)
    $emit(event, payload) {
      // This will be overridden by components that need event emission
      // Allows for pure testing without side effects
    }
  }
})