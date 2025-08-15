import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { mockAssets, mockAssetDetails, mockAssetStats } from '../test/mocks'

// Mock the API service
const mockAssetsAPI = {
  getAssets: vi.fn(),
  getAsset: vi.fn(),
  createAsset: vi.fn(),
  updateAsset: vi.fn(),
  partialUpdateAsset: vi.fn(),
  deleteAsset: vi.fn(),
  getAssetDocuments: vi.fn(),
  uploadDocument: vi.fn(),
  getStats: vi.fn(),
}

vi.mock('../services/api', () => ({
  assetsAPI: mockAssetsAPI
}))

// Import after mocking
const { useAssetsStore } = await import('./assets')

describe('Assets Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useAssetsStore()
    
    // Reset all mocks
    vi.clearAllMocks()
    
    // Setup default mock responses
    mockAssetsAPI.getAssets.mockResolvedValue({
      data: {
        count: mockAssets.length,
        next: null,
        previous: null,
        results: mockAssets
      }
    })
    
    mockAssetsAPI.getAsset.mockResolvedValue({
      data: mockAssetDetails
    })
    
    mockAssetsAPI.getStats.mockResolvedValue({
      data: mockAssetStats
    })
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      expect(store.assets).toEqual([])
      expect(store.totalAssets).toBe(0)
      expect(store.currentPage).toBe(1)
      expect(store.searchQuery).toBe('')
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('Getters', () => {
    it('should calculate hasAssets correctly', () => {
      expect(store.hasAssets).toBe(false)
      
      store.assets = mockAssets
      expect(store.hasAssets).toBe(true)
    })

    it('should calculate totalPages correctly', () => {
      store.totalAssets = 45
      store.pageSize = 20
      expect(store.totalPages).toBe(3)
    })

    it('should detect active filters correctly', () => {
      expect(store.hasActiveFilters).toBe(false)
      
      store.searchQuery = 'Ford'
      expect(store.hasActiveFilters).toBe(true)
      
      store.searchQuery = ''
      store.filters.vehicle_type = 'truck'
      expect(store.hasActiveFilters).toBe(true)
    })

    it('should detect loading states correctly', () => {
      expect(store.isAnyLoading).toBe(false)
      
      store.isLoading = true
      expect(store.isAnyLoading).toBe(true)
      
      store.isLoading = false
      store.isCreating = true
      expect(store.isAnyLoading).toBe(true)
    })
  })

  describe('Asset List Actions', () => {
    it('should fetch assets successfully', async () => {
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      await store.fetchAssets()

      expect(mockAssetsAPI.getAssets).toHaveBeenCalledWith({
        page: 1,
        page_size: 20,
        ordering: 'asset_id'
      })
      
      expect(store.assets).toEqual(mockAssets)
      expect(store.totalAssets).toBe(mockAssets.length)
      expect(store.isLoading).toBe(false)
      expect(mockEmit).toHaveBeenCalledWith('assets:fetched', {
        assets: mockAssets,
        total: mockAssets.length
      })
    })

    it('should handle fetch assets error', async () => {
      const error = { response: { data: 'API Error' } }
      mockAssetsAPI.getAssets.mockRejectedValue(error)
      
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      await expect(store.fetchAssets()).rejects.toThrow()
      
      expect(store.error).toBe('API Error')
      expect(store.isLoading).toBe(false)
      expect(mockEmit).toHaveBeenCalledWith('assets:error', 'API Error')
    })

    it('should include search and filter params', async () => {
      store.searchQuery = 'Ford'
      store.filters.vehicle_type = 'truck'
      store.sortBy = 'make'
      store.sortDesc = true

      await store.fetchAssets()

      expect(mockAssetsAPI.getAssets).toHaveBeenCalledWith({
        page: 1,
        page_size: 20,
        ordering: '-make',
        search: 'Ford',
        vehicle_type: 'truck'
      })
    })

    it('should create asset successfully', async () => {
      const newAssetData = {
        vehicle_type: 'car',
        make: 'Toyota',
        model: 'Camry',
        year: 2023
      }
      
      const createdAsset = { ...newAssetData, id: 'new-id' }
      mockAssetsAPI.createAsset.mockResolvedValue({ data: createdAsset })
      
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      const result = await store.createAsset(newAssetData)

      expect(mockAssetsAPI.createAsset).toHaveBeenCalledWith(newAssetData)
      expect(result).toEqual(createdAsset)
      expect(store.assets[0]).toEqual(createdAsset)
      expect(store.totalAssets).toBe(1)
      expect(mockEmit).toHaveBeenCalledWith('asset:created', createdAsset)
    })

    it('should update asset successfully', async () => {
      // Setup initial asset
      store.assets = [...mockAssets]
      store.currentAsset = mockAssets[0]
      
      const updatedAsset = { ...mockAssets[0], make: 'Updated Ford' }
      mockAssetsAPI.updateAsset.mockResolvedValue({ data: updatedAsset })
      
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      const result = await store.updateAsset(mockAssets[0].id, updatedAsset)

      expect(result).toEqual(updatedAsset)
      expect(store.assets[0]).toEqual(updatedAsset)
      expect(store.currentAsset).toEqual(updatedAsset)
      expect(mockEmit).toHaveBeenCalledWith('asset:updated', updatedAsset)
    })

    it('should delete asset successfully', async () => {
      // Setup initial assets
      store.assets = [...mockAssets]
      store.currentAsset = mockAssets[0]
      store.totalAssets = mockAssets.length
      
      mockAssetsAPI.deleteAsset.mockResolvedValue()
      
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      await store.deleteAsset(mockAssets[0].id)

      expect(store.assets).toHaveLength(mockAssets.length - 1)
      expect(store.totalAssets).toBe(mockAssets.length - 1)
      expect(store.currentAsset).toBeNull()
      expect(mockEmit).toHaveBeenCalledWith('asset:deleted', { id: mockAssets[0].id })
    })
  })

  describe('Asset Detail Actions', () => {
    it('should fetch asset successfully', async () => {
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      const result = await store.fetchAsset(mockAssetDetails.id)

      expect(mockAssetsAPI.getAsset).toHaveBeenCalledWith(mockAssetDetails.id)
      expect(result).toEqual(mockAssetDetails)
      expect(store.currentAsset).toEqual(mockAssetDetails)
      expect(mockEmit).toHaveBeenCalledWith('asset:fetched', mockAssetDetails)
    })

    it('should fetch asset documents successfully', async () => {
      const documents = mockAssetDetails.documents
      mockAssetsAPI.getAssetDocuments.mockResolvedValue({ data: documents })
      
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      const result = await store.fetchAssetDocuments(mockAssetDetails.id)

      expect(result).toEqual(documents)
      expect(store.assetDocuments).toEqual(documents)
      expect(mockEmit).toHaveBeenCalledWith('documents:fetched', documents)
    })

    it('should upload document successfully', async () => {
      const documentData = new FormData()
      documentData.append('title', 'Test Document')
      documentData.append('document_type', 'manual')
      
      const uploadedDoc = { id: 3, title: 'Test Document', document_type: 'manual' }
      mockAssetsAPI.uploadDocument.mockResolvedValue({ data: uploadedDoc })
      
      // Setup current asset
      store.currentAsset = { ...mockAssetDetails }
      store.assets = [{ ...mockAssetDetails, documents_count: 2 }]
      
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      const result = await store.uploadDocument(mockAssetDetails.id, documentData)

      expect(result).toEqual(uploadedDoc)
      expect(store.assetDocuments[0]).toEqual(uploadedDoc)
      expect(store.assets[0].documents_count).toBe(3)
      expect(mockEmit).toHaveBeenCalledWith('document:uploaded', uploadedDoc)
    })
  })

  describe('Search and Filter Actions', () => {
    it('should set search query', () => {
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      store.setSearchQuery('Ford')

      expect(store.searchQuery).toBe('Ford')
      expect(mockEmit).toHaveBeenCalledWith('search:changed', 'Ford')
    })

    it('should set individual filter', () => {
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      store.setFilter('vehicle_type', 'truck')

      expect(store.filters.vehicle_type).toBe('truck')
      expect(mockEmit).toHaveBeenCalledWith('filter:changed', {
        key: 'vehicle_type',
        value: 'truck'
      })
    })

    it('should clear all filters', () => {
      // Set some filters first
      store.searchQuery = 'Ford'
      store.filters.vehicle_type = 'truck'
      store.filters.status = 'active'
      
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      store.clearFilters()

      expect(store.searchQuery).toBe('')
      expect(store.filters.vehicle_type).toBe('')
      expect(store.filters.status).toBe('')
      expect(mockEmit).toHaveBeenCalledWith('filters:cleared')
    })

    it('should build filter params correctly', () => {
      store.searchQuery = 'Ford'
      store.filters.vehicle_type = 'truck'
      store.filters.status = ''  // Should be excluded
      store.filters.year = 2022

      const params = store.buildFilterParams()

      expect(params).toEqual({
        search: 'Ford',
        vehicle_type: 'truck',
        year: 2022
      })
    })
  })

  describe('Statistics Actions', () => {
    it('should fetch asset statistics successfully', async () => {
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      const result = await store.fetchAssetStats()

      expect(result).toEqual(mockAssetStats)
      expect(store.assetStats).toEqual(mockAssetStats)
      expect(mockEmit).toHaveBeenCalledWith('stats:fetched', mockAssetStats)
    })

    it('should handle statistics fetch error gracefully', async () => {
      mockAssetsAPI.getStats.mockRejectedValue(new Error('API Error'))
      
      const result = await store.fetchAssetStats()

      expect(result).toBeNull()
      expect(store.assetStats.total_assets).toBe(0) // Should remain unchanged
    })
  })

  describe('Utility Actions', () => {
    it('should clear errors', () => {
      store.error = 'Some error'
      store.assetError = 'Asset error'
      store.documentError = 'Document error'

      store.clearError()

      expect(store.error).toBeNull()
      expect(store.assetError).toBeNull()
      expect(store.documentError).toBeNull()
    })

    it('should clear current asset', () => {
      store.currentAsset = mockAssetDetails
      store.assetDocuments = mockAssetDetails.documents

      store.clearCurrentAsset()

      expect(store.currentAsset).toBeNull()
      expect(store.assetDocuments).toEqual([])
    })

    it('should set page correctly', () => {
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      store.setPage(3)

      expect(store.currentPage).toBe(3)
      expect(mockEmit).toHaveBeenCalledWith('page:changed', 3)
    })

    it('should set sorting correctly', () => {
      const mockEmit = vi.fn()
      store.$emit = mockEmit

      store.setSorting('make', true)

      expect(store.sortBy).toBe('make')
      expect(store.sortDesc).toBe(true)
      expect(mockEmit).toHaveBeenCalledWith('sort:changed', {
        sortBy: 'make',
        sortDesc: true
      })
    })
  })
})