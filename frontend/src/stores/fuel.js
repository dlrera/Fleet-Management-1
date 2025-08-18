import { defineStore } from 'pinia'
import { fuelAPI } from '../services/api'

export const useFuelStore = defineStore('fuel', {
  state: () => ({
    // Transaction state
    transactions: [],
    currentTransaction: null,
    totalTransactions: 0,
    currentPage: 1,
    pageSize: 10,
    
    // Statistics state
    fuelStats: {
      total_transactions: 0,
      total_volume: 0,
      total_cost: 0,
      average_mpg: 0,
      average_cost_per_mile: 0,
      product_breakdown: {},
      monthly_trends: [],
      open_alerts: 0,
      critical_alerts: 0,
      most_efficient_assets: [],
      least_efficient_assets: []
    },
    
    // Sites state
    fuelSites: [],
    currentSite: null,
    
    // Cards state (Phase 2)
    fuelCards: [],
    currentCard: null,
    
    // Alerts state
    fuelAlerts: [],
    currentAlert: null,
    totalAlerts: 0,
    
    // Units policy
    unitsPolicy: {
      distance_unit: 'mi',
      volume_unit: 'gal',
      currency: 'USD',
      low_mpg_threshold_percent: 25.00,
      high_price_percentile: 95.00
    },
    
    // Filters and search
    filters: {
      asset_id: '',
      product_type: '',
      entry_source: '',
      start_date: '',
      end_date: '',
      min_cost: '',
      max_cost: ''
    },
    searchQuery: '',
    sortBy: 'timestamp',
    sortDesc: true,
    
    // Loading states
    isLoading: false,
    isLoadingTransaction: false,
    isLoadingStats: false,
    isLoadingSites: false,
    isLoadingCards: false,
    isLoadingAlerts: false,
    isCreating: false,
    isUpdating: false,
    isDeleting: false,
    isImporting: false,
    
    // Error states
    error: null,
    transactionError: null,
    statsError: null,
    siteError: null,
    cardError: null,
    alertError: null,
    importError: null
  }),

  getters: {
    // Transaction getters
    transactionsList: (state) => state.transactions,
    hasTransactions: (state) => state.transactions.length > 0,
    
    // Statistics getters
    hasStats: (state) => state.fuelStats.total_transactions > 0,
    totalFuelCost: (state) => state.fuelStats.total_cost || 0,
    totalFuelVolume: (state) => state.fuelStats.total_volume || 0,
    averageMPG: (state) => state.fuelStats.average_mpg || 0,
    averageCostPerMile: (state) => state.fuelStats.average_cost_per_mile || 0,
    
    // Product breakdown getters
    productTypes: (state) => Object.keys(state.fuelStats.product_breakdown || {}),
    topFuelType: (state) => {
      const breakdown = state.fuelStats.product_breakdown || {}
      return Object.entries(breakdown).reduce((top, [type, data]) => 
        (data.volume || 0) > (top.volume || 0) ? { type, ...data } : top, {}
      )
    },
    
    // Alert getters
    hasAlerts: (state) => state.fuelAlerts.length > 0,
    openAlertsCount: (state) => state.fuelStats.open_alerts || 0,
    criticalAlertsCount: (state) => state.fuelStats.critical_alerts || 0,
    
    // Filter getters
    hasActiveFilters: (state) => {
      return Object.values(state.filters).some(value => 
        value !== '' && value !== null && value !== undefined
      ) || state.searchQuery !== ''
    },
    
    // Status getters
    isAnyLoading: (state) => 
      state.isLoading || state.isLoadingTransaction || state.isLoadingStats ||
      state.isLoadingSites || state.isLoadingCards || state.isLoadingAlerts ||
      state.isCreating || state.isUpdating || state.isDeleting || state.isImporting,
      
    hasError: (state) => !!(state.error || state.transactionError || 
      state.statsError || state.siteError || state.cardError || 
      state.alertError || state.importError)
  },

  actions: {
    // Transaction actions
    async fetchTransactions(options = {}) {
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
        
        const response = await fuelAPI.getFuelTransactions(params)
        
        this.transactions = response.data.results
        this.totalTransactions = response.data.count
        this.currentPage = options.page || this.currentPage
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch fuel transactions'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async fetchTransaction(id) {
      this.isLoadingTransaction = true
      this.transactionError = null
      
      try {
        const response = await fuelAPI.getFuelTransaction(id)
        this.currentTransaction = response.data
        return response.data
      } catch (error) {
        this.transactionError = error.response?.data?.message || 'Failed to fetch fuel transaction'
        throw error
      } finally {
        this.isLoadingTransaction = false
      }
    },

    async createTransaction(transactionData) {
      this.isCreating = true
      this.transactionError = null
      
      try {
        const response = await fuelAPI.createFuelTransaction(transactionData)
        
        // Add to local list if we're on the first page
        if (this.currentPage === 1) {
          this.transactions.unshift(response.data)
          this.totalTransactions += 1
        }
        
        // Refresh stats
        this.fetchStats()
        
        return response.data
      } catch (error) {
        this.transactionError = error.response?.data?.message || 'Failed to create fuel transaction'
        throw error
      } finally {
        this.isCreating = false
      }
    },

    async updateTransaction(id, transactionData) {
      this.isUpdating = true
      this.transactionError = null
      
      try {
        const response = await fuelAPI.updateFuelTransaction(id, transactionData)
        
        // Update in local list
        const index = this.transactions.findIndex(t => t.id === id)
        if (index !== -1) {
          this.transactions[index] = response.data
        }
        
        // Update current transaction if it's the same
        if (this.currentTransaction?.id === id) {
          this.currentTransaction = response.data
        }
        
        // Refresh stats
        this.fetchStats()
        
        return response.data
      } catch (error) {
        this.transactionError = error.response?.data?.message || 'Failed to update fuel transaction'
        throw error
      } finally {
        this.isUpdating = false
      }
    },

    async deleteTransaction(id) {
      this.isDeleting = true
      this.transactionError = null
      
      try {
        await fuelAPI.deleteFuelTransaction(id)
        
        // Remove from local list
        this.transactions = this.transactions.filter(t => t.id !== id)
        this.totalTransactions -= 1
        
        // Clear current transaction if it's the deleted one
        if (this.currentTransaction?.id === id) {
          this.currentTransaction = null
        }
        
        // Refresh stats
        this.fetchStats()
        
        return true
      } catch (error) {
        this.transactionError = error.response?.data?.message || 'Failed to delete fuel transaction'
        throw error
      } finally {
        this.isDeleting = false
      }
    },

    // Statistics actions
    async fetchStats(options = {}) {
      this.isLoadingStats = true
      this.statsError = null
      
      try {
        const params = {
          days: 30,
          ...options
        }
        
        const response = await fuelAPI.getFuelStats(params)
        this.fuelStats = response.data
        
        return response.data
      } catch (error) {
        this.statsError = error.response?.data?.message || 'Failed to fetch fuel statistics'
        throw error
      } finally {
        this.isLoadingStats = false
      }
    },

    // Import actions
    async importCSV(file, previewOnly = false) {
      this.isImporting = true
      this.importError = null
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await fuelAPI.importFuelCSV(formData, previewOnly)
        
        if (!previewOnly) {
          // Refresh transactions and stats after successful import
          this.fetchTransactions()
          this.fetchStats()
        }
        
        return response.data
      } catch (error) {
        this.importError = error.response?.data?.message || 'Failed to import CSV'
        throw error
      } finally {
        this.isImporting = false
      }
    },

    // Site actions
    async fetchSites(options = {}) {
      this.isLoadingSites = true
      this.siteError = null
      
      try {
        const response = await fuelAPI.getFuelSites(options.params || {})
        this.fuelSites = response.data.results || response.data
        return response.data
      } catch (error) {
        this.siteError = error.response?.data?.message || 'Failed to fetch fuel sites'
        throw error
      } finally {
        this.isLoadingSites = false
      }
    },

    async createSite(siteData) {
      this.isCreating = true
      this.siteError = null
      
      try {
        const response = await fuelAPI.createFuelSite(siteData)
        this.fuelSites.push(response.data)
        return response.data
      } catch (error) {
        this.siteError = error.response?.data?.message || 'Failed to create fuel site'
        throw error
      } finally {
        this.isCreating = false
      }
    },

    // Alert actions
    async fetchAlerts(options = {}) {
      this.isLoadingAlerts = true
      this.alertError = null
      
      try {
        const response = await fuelAPI.getFuelAlerts(options.params || {})
        this.fuelAlerts = response.data.results || response.data
        this.totalAlerts = response.data.count || this.fuelAlerts.length
        return response.data
      } catch (error) {
        this.alertError = error.response?.data?.message || 'Failed to fetch fuel alerts'
        throw error
      } finally {
        this.isLoadingAlerts = false
      }
    },

    async resolveAlert(id, resolutionData) {
      this.isUpdating = true
      this.alertError = null
      
      try {
        const response = await fuelAPI.resolveFuelAlert(id, resolutionData)
        
        // Update in local list
        const index = this.fuelAlerts.findIndex(a => a.id === id)
        if (index !== -1) {
          this.fuelAlerts[index] = response.data
        }
        
        // Refresh stats to update alert counts
        this.fetchStats()
        
        return response.data
      } catch (error) {
        this.alertError = error.response?.data?.message || 'Failed to resolve alert'
        throw error
      } finally {
        this.isUpdating = false
      }
    },

    // Units policy actions
    async fetchUnitsPolicy() {
      try {
        const response = await fuelAPI.getUnitsPolicy()
        this.unitsPolicy = response.data
        return response.data
      } catch (error) {
        // If no policy exists, keep defaults
        console.log('Using default units policy')
        return this.unitsPolicy
      }
    },

    // Utility actions
    buildFilterParams() {
      const params = {}
      
      Object.entries(this.filters).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          params[key] = value
        }
      })
      
      if (this.searchQuery) {
        params.search = this.searchQuery
      }
      
      return params
    },

    setFilter(key, value) {
      this.filters[key] = value
      this.currentPage = 1 // Reset to first page when filtering
    },

    clearFilters() {
      this.filters = {
        asset_id: '',
        product_type: '',
        entry_source: '',
        start_date: '',
        end_date: '',
        min_cost: '',
        max_cost: ''
      }
      this.searchQuery = ''
      this.currentPage = 1
    },

    setSorting(sortBy, sortDesc = false) {
      this.sortBy = sortBy
      this.sortDesc = sortDesc
      this.currentPage = 1 // Reset to first page when sorting
    },

    setPage(page) {
      this.currentPage = page
    },

    clearErrors() {
      this.error = null
      this.transactionError = null
      this.statsError = null
      this.siteError = null
      this.cardError = null
      this.alertError = null
      this.importError = null
    }
  }
})