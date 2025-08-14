import { defineStore } from 'pinia'
import { assetsAPI } from '@/services/api'

export const useAssetsStore = defineStore('assets', {
  state: () => ({
    assets: [],
    departments: [],
    selectedAsset: null,
    loading: false,
    error: null,
    statistics: null,
    expiringAssets: [],
    filters: {
      search: '',
      status: '',
      department: '',
      vehicle_type: '',
      make: ''
    },
    pagination: {
      page: 1,
      pageSize: 20,
      total: 0
    }
  }),

  getters: {
    activeAssets: (state) => state.assets.filter(asset => asset.status === 'active'),
    assetsByDepartment: (state) => (departmentId) => 
      state.assets.filter(asset => asset.department === departmentId),
    assetsByStatus: (state) => (status) => 
      state.assets.filter(asset => asset.status === status),
    getAssetById: (state) => (id) => 
      state.assets.find(asset => asset.asset_id === id)
  },

  actions: {
    setLoading(loading) {
      this.loading = loading
    },

    setError(error) {
      this.error = error
    },

    async fetchAssets(params = {}) {
      this.setLoading(true)
      this.setError(null)
      
      try {
        const queryParams = {
          ...this.filters,
          page: this.pagination.page,
          page_size: this.pagination.pageSize,
          ...params
        }
        
        const response = await assetsAPI.getAssets(queryParams)
        this.assets = response.data.results
        this.pagination.total = response.data.count
        return response.data
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to fetch assets')
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    async fetchAsset(id) {
      this.setLoading(true)
      this.setError(null)
      
      try {
        const response = await assetsAPI.getAsset(id)
        this.selectedAsset = response.data
        return response.data
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to fetch asset')
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    async createAsset(assetData) {
      this.setLoading(true)
      this.setError(null)
      
      try {
        const response = await assetsAPI.createAsset(assetData)
        this.assets.unshift(response.data)
        return response.data
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to create asset')
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    async updateAsset(id, assetData) {
      this.setLoading(true)
      this.setError(null)
      
      try {
        const response = await assetsAPI.updateAsset(id, assetData)
        const index = this.assets.findIndex(asset => asset.asset_id === id)
        if (index !== -1) {
          this.assets[index] = response.data
        }
        if (this.selectedAsset?.asset_id === id) {
          this.selectedAsset = response.data
        }
        return response.data
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to update asset')
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    async deleteAsset(id) {
      this.setLoading(true)
      this.setError(null)
      
      try {
        await assetsAPI.deleteAsset(id)
        this.assets = this.assets.filter(asset => asset.asset_id !== id)
        if (this.selectedAsset?.asset_id === id) {
          this.selectedAsset = null
        }
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to delete asset')
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    async fetchDepartments() {
      try {
        const response = await assetsAPI.getDepartments()
        this.departments = response.data.results || response.data
        return response.data
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to fetch departments')
        throw error
      }
    },

    async fetchStatistics() {
      try {
        const response = await assetsAPI.getAssetStatistics()
        this.statistics = response.data
        return response.data
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to fetch statistics')
        throw error
      }
    },

    async fetchExpiringAssets(daysAhead = 30) {
      try {
        const response = await assetsAPI.getExpiringAssets({ days_ahead: daysAhead })
        this.expiringAssets = response.data
        return response.data
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to fetch expiring assets')
        throw error
      }
    },

    async updateOdometer(assetId, odometerReading) {
      try {
        const response = await assetsAPI.updateOdometer(assetId, { odometer_reading: odometerReading })
        
        // Update local state
        const asset = this.assets.find(a => a.asset_id === assetId)
        if (asset) {
          asset.current_odometer_reading = response.data.current_reading
        }
        
        if (this.selectedAsset?.asset_id === assetId) {
          this.selectedAsset.current_odometer_reading = response.data.current_reading
        }
        
        return response.data
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to update odometer')
        throw error
      }
    },

    async uploadDocument(assetId, file, documentType, title, description) {
      const formData = new FormData()
      formData.append('document', file)
      formData.append('document_type', documentType)
      formData.append('title', title)
      formData.append('description', description || '')
      
      try {
        const response = await assetsAPI.uploadAssetDocument(assetId, formData)
        return response.data
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to upload document')
        throw error
      }
    },

    async uploadImage(assetId, file, title, description) {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('title', title)
      formData.append('description', description || '')
      
      try {
        const response = await assetsAPI.uploadAssetImage(assetId, formData)
        return response.data
      } catch (error) {
        this.setError(error.response?.data?.message || 'Failed to upload image')
        throw error
      }
    },

    // Filter and search actions
    setFilter(key, value) {
      this.filters[key] = value
      this.pagination.page = 1 // Reset to first page when filtering
    },

    clearFilters() {
      this.filters = {
        search: '',
        status: '',
        department: '',
        vehicle_type: '',
        make: ''
      }
      this.pagination.page = 1
    },

    setPage(page) {
      this.pagination.page = page
    },

    setPageSize(size) {
      this.pagination.pageSize = size
      this.pagination.page = 1
    }
  }
})