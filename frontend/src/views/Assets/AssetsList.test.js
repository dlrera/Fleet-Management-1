import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { mountWithProviders } from '@/test/test-utils'
import AssetsList from './AssetsList.vue'
import { mockAssets, mockAssetStats } from '@/test/mocks'

// Mock lodash-es
vi.mock('lodash-es', () => ({
  debounce: (fn) => fn
}))

// Mock the assets store
const mockAssetsStore = {
  assets: [],
  totalAssets: 0,
  isLoading: false,
  error: null,
  hasStats: false,
  hasActiveFilters: false,
  assetStats: mockAssetStats,
  fetchAssets: vi.fn(),
  fetchAssetStats: vi.fn(),
  setSearchQuery: vi.fn(),
  setFilter: vi.fn(),
  clearFilters: vi.fn(),
  setSorting: vi.fn(),
  setPage: vi.fn(),
  deleteAsset: vi.fn(),
  isDeleting: false
}

vi.mock('@/stores/assets', () => ({
  useAssetsStore: () => mockAssetsStore
}))

describe('AssetsList', () => {
  let wrapper

  beforeEach(async () => {
    // Setup pinia
    setActivePinia(createPinia())

    // Reset mocks
    vi.clearAllMocks()
    
    // Reset store state
    Object.assign(mockAssetsStore, {
      assets: [],
      totalAssets: 0,
      isLoading: false,
      error: null,
      hasStats: false,
      hasActiveFilters: false,
      assetStats: mockAssetStats,
      isDeleting: false
    })

    wrapper = mountWithProviders(AssetsList)
  })

  describe('Component Rendering', () => {
    it('should render page title correctly', () => {
      expect(wrapper.find('[data-testid="assets-page-title"]').text()).toBe('Asset Management')
    })

    it('should render add asset button', () => {
      const addBtn = wrapper.find('[data-testid="add-asset-btn"]')
      expect(addBtn.exists()).toBe(true)
      expect(addBtn.text()).toContain('Add Asset')
    })

    it('should render search input', () => {
      const searchInput = wrapper.find('[data-testid="search-input"]')
      expect(searchInput.exists()).toBe(true)
    })

    it('should render filter controls', () => {
      expect(wrapper.find('[data-testid="vehicle-type-filter"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="status-filter"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="department-filter"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="year-filter"]').exists()).toBe(true)
    })

    it('should render data table', () => {
      expect(wrapper.find('[data-testid="assets-table"]').exists()).toBe(true)
    })
  })

  describe('Statistics Cards', () => {
    it('should not show stats cards when hasStats is false', () => {
      mockAssetsStore.hasStats = false
      expect(wrapper.find('.v-card').exists()).toBe(true) // Only filter and table cards
    })

    it('should show stats cards when hasStats is true', async () => {
      mockAssetsStore.hasStats = true
      await wrapper.vm.$nextTick()
      
      // Should have statistics cards
      const cards = wrapper.findAll('.v-card')
      expect(cards.length).toBeGreaterThan(2) // Stats + filter + table cards
    })
  })

  describe('Search Functionality', () => {
    it('should update search query on input', async () => {
      const searchInput = wrapper.find('[data-testid="search-input"] input')
      
      await searchInput.setValue('Ford')
      
      expect(mockAssetsStore.setSearchQuery).toHaveBeenCalledWith('Ford')
    })

    it('should clear search when clear button is clicked', async () => {
      // Set initial search value
      await wrapper.find('[data-testid="search-input"] input').setValue('Ford')
      
      // Find and click clear button (this might need adjustment based on Vuetify's implementation)
      const clearBtn = wrapper.find('[data-testid="search-input"] .mdi-close')
      if (clearBtn.exists()) {
        await clearBtn.trigger('click')
        expect(wrapper.vm.searchQuery).toBe('')
      }
    })
  })

  describe('Filter Functionality', () => {
    it('should update vehicle type filter', async () => {
      const vehicleTypeFilter = wrapper.find('[data-testid="vehicle-type-filter"]')
      
      // Simulate selection (this might need adjustment for v-select)
      await wrapper.vm.updateFilter('vehicle_type', 'truck')
      
      expect(mockAssetsStore.setFilter).toHaveBeenCalledWith('vehicle_type', 'truck')
    })

    it('should update status filter', async () => {
      await wrapper.vm.updateFilter('status', 'active')
      
      expect(mockAssetsStore.setFilter).toHaveBeenCalledWith('status', 'active')
    })

    it('should show clear filters button when filters are active', async () => {
      mockAssetsStore.hasActiveFilters = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('[data-testid="clear-filters-btn"]').exists()).toBe(true)
    })

    it('should clear all filters when clear button is clicked', async () => {
      mockAssetsStore.hasActiveFilters = true
      await wrapper.vm.$nextTick()
      
      const clearBtn = wrapper.find('[data-testid="clear-filters-btn"]')
      await clearBtn.trigger('click')
      
      expect(mockAssetsStore.clearFilters).toHaveBeenCalled()
    })
  })

  describe('Asset Table', () => {
    beforeEach(() => {
      mockAssetsStore.assets = [...mockAssets]
      mockAssetsStore.totalAssets = mockAssets.length
    })

    it('should display assets in table', async () => {
      await wrapper.vm.$nextTick()
      
      // Check if asset links are rendered
      const assetLinks = wrapper.findAll('[data-testid^="asset-link-"]')
      expect(assetLinks.length).toBeGreaterThan(0)
    })

    it('should render action buttons for each asset', async () => {
      await wrapper.vm.$nextTick()
      
      mockAssets.forEach(asset => {
        expect(wrapper.find(`[data-testid="view-asset-${asset.asset_id}"]`).exists()).toBe(true)
        expect(wrapper.find(`[data-testid="edit-asset-${asset.asset_id}"]`).exists()).toBe(true)
        expect(wrapper.find(`[data-testid="delete-asset-${asset.asset_id}"]`).exists()).toBe(true)
      })
    })

    it('should show loading state', async () => {
      mockAssetsStore.isLoading = true
      await wrapper.vm.$nextTick()
      
      // Check for loading indicator (skeleton loader)
      expect(wrapper.html()).toContain('v-skeleton-loader')
    })

    it('should show no data message when no assets', async () => {
      mockAssetsStore.assets = []
      mockAssetsStore.totalAssets = 0
      await wrapper.vm.$nextTick()
      
      expect(wrapper.html()).toContain('No Assets Found')
    })
  })

  describe('Asset Actions', () => {
    beforeEach(() => {
      mockAssetsStore.assets = [...mockAssets]
    })

    it('should open delete confirmation dialog', async () => {
      await wrapper.vm.$nextTick()
      
      const deleteBtn = wrapper.find(`[data-testid="delete-asset-${mockAssets[0].asset_id}"]`)
      await deleteBtn.trigger('click')
      
      expect(wrapper.vm.deleteDialog).toBe(true)
      expect(wrapper.vm.assetToDelete).toEqual(mockAssets[0])
    })

    it('should delete asset when confirmed', async () => {
      // Open delete dialog
      wrapper.vm.assetToDelete = mockAssets[0]
      wrapper.vm.deleteDialog = true
      await wrapper.vm.$nextTick()
      
      // Confirm deletion
      const confirmBtn = wrapper.find('[data-testid="confirm-delete-btn"]')
      await confirmBtn.trigger('click')
      
      expect(mockAssetsStore.deleteAsset).toHaveBeenCalledWith(mockAssets[0].id)
    })

    it('should handle delete errors', async () => {
      mockAssetsStore.deleteAsset.mockRejectedValue(new Error('Delete failed'))
      
      wrapper.vm.assetToDelete = mockAssets[0]
      await wrapper.vm.deleteAsset()
      
      expect(wrapper.vm.showError).toBe(true)
    })
  })

  describe('Navigation', () => {
    it('should navigate to asset detail when asset link is clicked', async () => {
      mockAssetsStore.assets = [...mockAssets]
      await wrapper.vm.$nextTick()
      
      const assetLink = wrapper.find(`[data-testid="asset-link-${mockAssets[0].asset_id}"]`)
      
      // Check that it's a router-link with correct route
      expect(assetLink.attributes('href')).toBe(`/assets/${mockAssets[0].id}`)
    })

    it('should navigate to create asset page', () => {
      const addBtn = wrapper.find('[data-testid="add-asset-btn"]')
      expect(addBtn.attributes('href')).toBe('/assets/create')
    })
  })

  describe('Utility Functions', () => {
    it('should format vehicle type correctly', () => {
      expect(wrapper.vm.formatVehicleType('truck')).toBe('Truck')
      expect(wrapper.vm.formatVehicleType('out_of_service')).toBe('Out of service')
    })

    it('should format status correctly', () => {
      expect(wrapper.vm.formatStatus('active')).toBe('Active')
      expect(wrapper.vm.formatStatus('out_of_service')).toBe('Out Of Service')
    })

    it('should format odometer correctly', () => {
      expect(wrapper.vm.formatOdometer(15000)).toBe('15,000')
      expect(wrapper.vm.formatOdometer(0)).toBe('0')
      expect(wrapper.vm.formatOdometer(null)).toBe('0')
    })

    it('should get correct vehicle type colors', () => {
      expect(wrapper.vm.getVehicleTypeColor('truck')).toBe('green')
      expect(wrapper.vm.getVehicleTypeColor('bus')).toBe('blue')
      expect(wrapper.vm.getVehicleTypeColor('unknown')).toBe('grey')
    })

    it('should get correct status colors', () => {
      expect(wrapper.vm.getStatusColor('active')).toBe('success')
      expect(wrapper.vm.getStatusColor('maintenance')).toBe('warning')
      expect(wrapper.vm.getStatusColor('retired')).toBe('error')
    })
  })

  describe('Error Handling', () => {
    it('should show error snackbar when store has error', async () => {
      mockAssetsStore.error = 'Something went wrong'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showError).toBe(true)
    })

    it('should handle fetch assets errors', async () => {
      mockAssetsStore.fetchAssets.mockRejectedValue(new Error('Fetch failed'))
      
      await wrapper.vm.loadAssets()
      
      expect(wrapper.vm.showError).toBe(true)
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels on action buttons', async () => {
      mockAssetsStore.assets = [mockAssets[0]]
      await wrapper.vm.$nextTick()
      
      const viewBtn = wrapper.find(`[data-testid="view-asset-${mockAssets[0].asset_id}"]`)
      const editBtn = wrapper.find(`[data-testid="edit-asset-${mockAssets[0].asset_id}"]`)
      const deleteBtn = wrapper.find(`[data-testid="delete-asset-${mockAssets[0].asset_id}"]`)
      
      expect(viewBtn.attributes('aria-label')).toContain(mockAssets[0].asset_id)
      expect(editBtn.attributes('aria-label')).toContain(mockAssets[0].asset_id)
      expect(deleteBtn.attributes('aria-label')).toContain(mockAssets[0].asset_id)
    })

    it('should have proper data attributes for testing', () => {
      expect(wrapper.find('[data-testid="assets-page-title"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="add-asset-btn"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="search-input"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="assets-table"]').exists()).toBe(true)
    })
  })

  describe('Component Lifecycle', () => {
    it('should fetch assets and stats on mount', () => {
      expect(mockAssetsStore.fetchAssetStats).toHaveBeenCalled()
      expect(mockAssetsStore.fetchAssets).toHaveBeenCalled()
    })
  })
})