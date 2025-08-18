import { defineStore } from 'pinia'
import { assetsAPI } from '../services/api'

export const useAssetsStore = defineStore('assets', {
  state: () => ({
    // Asset list state
    assets: [],
    totalAssets: 0,
    currentPage: 1,
    pageSize: 20,
    
    // Current asset details
    currentAsset: null,
    assetDocuments: [],
    
    // Search and filter state
    searchQuery: '',
    filters: {
      vehicle_type: '',
      status: '',
      department: '',
      year: null,
      make: ''
    },
    sortBy: 'asset_id',
    sortDesc: false,
    
    // Loading states
    isLoading: false,
    isLoadingAsset: false,
    isLoadingDocuments: false,
    isCreating: false,
    isUpdating: false,
    isDeleting: false,
    isUploadingDocument: false,
    isUploadingImage: false,
    
    // Statistics
    assetStats: {
      total_assets: 0,
      active_assets: 0,
      maintenance_assets: 0,
      retired_assets: 0,
      vehicle_types: {}
    },
    
    // Error handling
    error: null,
    assetError: null,
    documentError: null,
    imageError: null,
  }),

  getters: {
    // Asset list getters
    hasAssets: (state) => state.assets.length > 0,
    totalPages: (state) => Math.ceil(state.totalAssets / state.pageSize),
    hasNextPage: (state) => state.currentPage < Math.ceil(state.totalAssets / state.pageSize),
    hasPreviousPage: (state) => state.currentPage > 1,
    
    // Current asset getters
    hasCurrentAsset: (state) => !!state.currentAsset,
    currentAssetId: (state) => state.currentAsset?.id,
    hasDocuments: (state) => state.assetDocuments.length > 0,
    
    // Filter getters
    hasActiveFilters: (state) => {
      return Object.values(state.filters).some(value => 
        value !== '' && value !== null && value !== undefined
      ) || state.searchQuery !== ''
    },
    
    // Statistics getters
    hasStats: (state) => state.assetStats.total_assets > 0,
    vehicleTypeList: (state) => Object.keys(state.assetStats.vehicle_types || {}),
    
    // Status getters
    isAnyLoading: (state) => 
      state.isLoading || state.isLoadingAsset || state.isLoadingDocuments ||
      state.isCreating || state.isUpdating || state.isDeleting || state.isUploadingDocument,
      
    hasError: (state) => !!state.error || !!state.assetError || !!state.documentError,
  },

  actions: {
    // Asset list actions
    async fetchAssets(options = {}) {
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
        
        const response = await assetsAPI.getAssets(params)
        
        this.assets = response.data.results
        this.totalAssets = response.data.count
        this.currentPage = options.page || this.currentPage
        
        // Emit success event for components
        this.$emit?.('assets:fetched', { assets: this.assets, total: this.totalAssets })
        
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch assets'
        this.$emit?.('assets:error', this.error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async fetchAsset(id) {
      this.isLoadingAsset = true
      this.assetError = null
      
      try {
        const response = await assetsAPI.getAsset(id)
        this.currentAsset = response.data
        
        this.$emit?.('asset:fetched', this.currentAsset)
        
        return response.data
      } catch (error) {
        this.assetError = error.response?.data || 'Failed to fetch asset'
        this.$emit?.('asset:error', this.assetError)
        throw error
      } finally {
        this.isLoadingAsset = false
      }
    },

    async createAsset(assetData) {
      this.isCreating = true
      this.error = null
      
      try {
        const response = await assetsAPI.createAsset(assetData)
        
        // Add to local list if on first page
        if (this.currentPage === 1) {
          this.assets.unshift(response.data)
          this.totalAssets += 1
        }
        
        this.$emit?.('asset:created', response.data)
        
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to create asset'
        this.$emit?.('asset:error', this.error)
        throw error
      } finally {
        this.isCreating = false
      }
    },

    async updateAsset(id, assetData) {
      this.isUpdating = true
      this.assetError = null
      
      try {
        const response = await assetsAPI.updateAsset(id, assetData)
        
        // Update in local list
        const index = this.assets.findIndex(asset => asset.id === id)
        if (index !== -1) {
          this.assets[index] = response.data
        }
        
        // Update current asset if it's the same
        if (this.currentAsset?.id === id) {
          this.currentAsset = response.data
        }
        
        this.$emit?.('asset:updated', response.data)
        
        return response.data
      } catch (error) {
        this.assetError = error.response?.data || 'Failed to update asset'
        this.$emit?.('asset:error', this.assetError)
        throw error
      } finally {
        this.isUpdating = false
      }
    },

    async partialUpdateAsset(id, assetData) {
      this.isUpdating = true
      this.assetError = null
      
      try {
        const response = await assetsAPI.partialUpdateAsset(id, assetData)
        
        // Update in local list
        const index = this.assets.findIndex(asset => asset.id === id)
        if (index !== -1) {
          this.assets[index] = { ...this.assets[index], ...response.data }
        }
        
        // Update current asset if it's the same
        if (this.currentAsset?.id === id) {
          this.currentAsset = { ...this.currentAsset, ...response.data }
        }
        
        this.$emit?.('asset:updated', response.data)
        
        return response.data
      } catch (error) {
        this.assetError = error.response?.data || 'Failed to update asset'
        this.$emit?.('asset:error', this.assetError)
        throw error
      } finally {
        this.isUpdating = false
      }
    },

    async deleteAsset(id) {
      this.isDeleting = true
      this.error = null
      
      try {
        await assetsAPI.deleteAsset(id)
        
        // Remove from local list
        this.assets = this.assets.filter(asset => asset.id !== id)
        this.totalAssets -= 1
        
        // Clear current asset if it's the same
        if (this.currentAsset?.id === id) {
          this.currentAsset = null
        }
        
        this.$emit?.('asset:deleted', { id })
        
        return true
      } catch (error) {
        this.error = error.response?.data || 'Failed to delete asset'
        this.$emit?.('asset:error', this.error)
        throw error
      } finally {
        this.isDeleting = false
      }
    },

    // Document actions
    async fetchAssetDocuments(assetId) {
      this.isLoadingDocuments = true
      this.documentError = null
      
      try {
        const response = await assetsAPI.getAssetDocuments(assetId)
        this.assetDocuments = response.data
        
        this.$emit?.('documents:fetched', this.assetDocuments)
        
        return response.data
      } catch (error) {
        this.documentError = error.response?.data || 'Failed to fetch documents'
        this.$emit?.('documents:error', this.documentError)
        throw error
      } finally {
        this.isLoadingDocuments = false
      }
    },

    async uploadDocument(assetId, documentData) {
      this.isUploadingDocument = true
      this.documentError = null
      
      try {
        const response = await assetsAPI.uploadDocument(assetId, documentData)
        
        // Add to local documents list
        this.assetDocuments.unshift(response.data)
        
        // Update documents count in current asset
        if (this.currentAsset?.id === assetId) {
          this.currentAsset.documents = [...(this.currentAsset.documents || []), response.data]
        }
        
        // Update documents count in assets list
        const assetIndex = this.assets.findIndex(asset => asset.id === assetId)
        if (assetIndex !== -1 && this.assets[assetIndex].documents_count !== undefined) {
          this.assets[assetIndex].documents_count += 1
        }
        
        this.$emit?.('document:uploaded', response.data)
        
        return response.data
      } catch (error) {
        this.documentError = error.response?.data || 'Failed to upload document'
        this.$emit?.('document:error', this.documentError)
        throw error
      } finally {
        this.isUploadingDocument = false
      }
    },

    async uploadImage(assetId, imageData) {
      this.isUploadingImage = true
      this.imageError = null
      
      try {
        const response = await assetsAPI.uploadImage(assetId, imageData)
        
        // Update current asset if it's the same
        if (this.currentAsset?.id === assetId) {
          this.currentAsset.image = response.data.image
          this.currentAsset.thumbnail = response.data.thumbnail
        }
        
        // Update asset in assets list
        const assetIndex = this.assets.findIndex(asset => asset.id === assetId)
        if (assetIndex !== -1) {
          this.assets[assetIndex].thumbnail = response.data.thumbnail
        }
        
        this.$emit?.('image:uploaded', response.data)
        
        return response.data
      } catch (error) {
        this.imageError = error.response?.data?.error || 'Failed to upload image'
        this.$emit?.('image:error', this.imageError)
        throw error
      } finally {
        this.isUploadingImage = false
      }
    },

    async deleteImage(assetId) {
      this.isUploadingImage = true
      this.imageError = null
      
      try {
        const response = await assetsAPI.deleteImage(assetId)
        
        // Update current asset if it's the same
        if (this.currentAsset?.id === assetId) {
          this.currentAsset.image = null
          this.currentAsset.thumbnail = null
        }
        
        // Update asset in assets list
        const assetIndex = this.assets.findIndex(asset => asset.id === assetId)
        if (assetIndex !== -1) {
          this.assets[assetIndex].image = null
          this.assets[assetIndex].thumbnail = null
        }
        
        this.$emit?.('image:deleted', response.data)
        
        return response.data
      } catch (error) {
        this.imageError = error.response?.data?.error || 'Failed to delete image'
        this.$emit?.('image:error', this.imageError)
        throw error
      } finally {
        this.isUploadingImage = false
      }
    },

    // Statistics actions
    async fetchAssetStats() {
      try {
        const response = await assetsAPI.getStats()
        this.assetStats = response.data
        
        this.$emit?.('stats:fetched', this.assetStats)
        
        return response.data
      } catch (error) {
        console.error('Failed to fetch asset statistics:', error)
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
        vehicle_type: '',
        status: '',
        department: '',
        year: null,
        make: ''
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
      this.assetError = null
      this.documentError = null
      this.imageError = null
    },

    clearCurrentAsset() {
      this.currentAsset = null
      this.assetDocuments = []
    },

    // CSV Import/Export actions
    async bulkImportAssets(formData) {
      try {
        const response = await assetsAPI.bulkImport(formData)
        
        // Refresh assets list after successful import
        if (response.data.success_count > 0) {
          await this.fetchAssets()
        }
        
        this.$emit?.('assets:imported', response.data)
        
        return response.data
      } catch (error) {
        console.error('Failed to import assets:', error)
        throw error
      }
    },

    async downloadCSVTemplate() {
      try {
        const response = await assetsAPI.downloadTemplate()
        
        this.$emit?.('template:downloaded')
        
        return response
      } catch (error) {
        console.error('Failed to download template:', error)
        throw error
      }
    },

    // Event emission helper (for pure component testing)
    $emit(event, payload) {
      // This will be overridden by components that need event emission
      // Allows for pure testing without side effects
    }
  }
})