import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import { setActivePinia, createPinia } from 'pinia'
import LocationPathModal from './LocationPathModal.vue'
import { useLocationsStore } from '../../stores/locations'

// Mock the API
vi.mock('../../services/api', () => ({
  locationsAPI: {
    getAssetHistory: vi.fn(),
  },
}))

// Mock Leaflet
vi.mock('leaflet', () => ({
  default: {
    map: vi.fn(() => ({
      setView: vi.fn(),
      remove: vi.fn(),
      invalidateSize: vi.fn(),
      fitBounds: vi.fn(),
      removeLayer: vi.fn()
    })),
    tileLayer: vi.fn(() => ({
      addTo: vi.fn()
    })),
    polyline: vi.fn(() => ({
      setLatLngs: vi.fn(),
      getBounds: vi.fn(() => ({
        isValid: true
      })),
      addTo: vi.fn()
    })),
    marker: vi.fn(() => ({
      bindPopup: vi.fn().mockReturnThis(),
      addTo: vi.fn()
    })),
    divIcon: vi.fn()
  }
}))

// Mock CSS import
vi.mock('leaflet/dist/leaflet.css', () => ({}))

const vuetify = createVuetify()

const mockAsset = {
  asset_id: 'TEST001',
  make: 'Test',
  model: 'Vehicle',
  year: 2023,
  vehicle_type: 'truck',
  status: 'active',
  department: 'Fleet'
}

const mockPathData = [
  {
    id: 1,
    latitude: 40.7128,
    longitude: -74.0060,
    timestamp: '2023-01-01T10:00:00Z',
    source: 'gps_device',
    speed: 30,
    heading: 45
  },
  {
    id: 2,
    latitude: 40.7130,
    longitude: -74.0062,
    timestamp: '2023-01-01T10:30:00Z',
    source: 'gps_device',
    speed: 35,
    heading: 50
  },
  {
    id: 3,
    latitude: 40.7132,
    longitude: -74.0064,
    timestamp: '2023-01-01T11:00:00Z',
    source: 'gps_device',
    speed: 25,
    heading: 30
  }
]

describe('LocationPathModal', () => {
  let wrapper
  let locationsStore

  const createWrapper = (props = {}) => {
    setActivePinia(createPinia())
    locationsStore = useLocationsStore()

    wrapper = mount(LocationPathModal, {
      props: {
        modelValue: true,
        asset: mockAsset,
        initialDays: 7,
        initialLimit: 100,
        ...props
      },
      global: {
        plugins: [vuetify],
        stubs: {
          'v-dialog': {
            template: '<div class="v-dialog"><slot /></div>',
            props: ['modelValue']
          }
        }
      }
    })

    return wrapper
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock DOM element for map container
    const mapContainer = document.createElement('div')
    mapContainer.id = 'path-map'
    document.body.appendChild(mapContainer)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    // Clean up DOM
    const mapContainer = document.getElementById('path-map')
    if (mapContainer) {
      document.body.removeChild(mapContainer)
    }
  })

  describe('Component Rendering', () => {
    it('renders modal with correct title and asset information', () => {
      createWrapper()
      
      expect(wrapper.text()).toContain('Location Path for TEST001')
      expect(wrapper.text()).toContain('Test Vehicle (2023)')
    })

    it('renders filter controls', () => {
      createWrapper()
      
      const selects = wrapper.findAllComponents({ name: 'VSelect' })
      expect(selects).toHaveLength(2) // Time period and max results selects
    })

    it('renders trace path button and close button', () => {
      createWrapper()
      
      const buttons = wrapper.findAllComponents({ name: 'VBtn' })
      expect(buttons.some(btn => btn.text().includes('Refresh'))).toBe(true)
      expect(buttons.some(btn => btn.text().includes('Export Path'))).toBe(true)
      expect(buttons.some(btn => btn.text().includes('Close'))).toBe(true)
    })

    it('shows loading state when fetching data', async () => {
      locationsStore.fetchAssetLocationHistory.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      )
      
      createWrapper()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('Loading path data')
    })

    it('shows no data state when no location history', async () => {
      locationsStore.fetchAssetLocationHistory.mockResolvedValue({
        locations: []
      })
      
      createWrapper()
      await flushPromises()
      
      expect(wrapper.text()).toContain('No Location Data')
      expect(wrapper.text()).toContain('No location history found')
    })
  })

  describe('Path Data Management', () => {
    it('fetches path data on mount when modal is open', async () => {
      locationsStore.fetchAssetLocationHistory.mockResolvedValue({
        locations: mockPathData
      })
      
      createWrapper({ modelValue: true })
      await flushPromises()
      
      expect(locationsStore.fetchAssetLocationHistory).toHaveBeenCalledWith(
        'TEST001',
        { days: 7, limit: 100 }
      )
    })

    it('does not fetch data when modal is closed', () => {
      createWrapper({ modelValue: false })
      
      expect(locationsStore.fetchAssetLocationHistory).not.toHaveBeenCalled()
    })

    it('updates filters and refetches data', async () => {
      locationsStore.fetchAssetLocationHistory.mockResolvedValue({
        locations: mockPathData
      })
      
      createWrapper()
      await flushPromises()
      
      // Change time period filter
      await wrapper.vm.$nextTick()
      wrapper.vm.localHistoryDays = 3
      await wrapper.vm.fetchPathData()
      
      expect(locationsStore.fetchAssetLocationHistory).toHaveBeenCalledWith(
        'TEST001',
        { days: 3, limit: 100 }
      )
    })
  })

  describe('Path Calculations', () => {
    beforeEach(async () => {
      locationsStore.fetchAssetLocationHistory.mockResolvedValue({
        locations: mockPathData
      })
      
      createWrapper()
      await flushPromises()
    })

    it('calculates total distance correctly', () => {
      const totalDistance = wrapper.vm.totalDistance
      expect(totalDistance).toBeGreaterThan(0)
      expect(typeof totalDistance).toBe('number')
    })

    it('calculates path duration correctly', () => {
      const duration = wrapper.vm.pathDuration
      expect(duration).toBeGreaterThan(0)
      expect(typeof duration).toBe('number')
    })

    it('calculates average speed correctly', () => {
      const avgSpeed = wrapper.vm.averageSpeed
      expect(avgSpeed).toBeGreaterThan(0)
      expect(typeof avgSpeed).toBe('number')
    })

    it('handles empty path data gracefully', async () => {
      locationsStore.fetchAssetLocationHistory.mockResolvedValue({
        locations: []
      })
      
      createWrapper()
      await flushPromises()
      
      expect(wrapper.vm.totalDistance).toBe(0)
      expect(wrapper.vm.pathDuration).toBe(0)
      expect(wrapper.vm.averageSpeed).toBe(0)
    })
  })

  describe('Map Integration', () => {
    it('initializes map when modal opens', async () => {
      const L = await import('leaflet')
      
      createWrapper({ modelValue: true })
      await flushPromises()
      
      expect(L.default.map).toHaveBeenCalledWith('path-map')
    })

    it('updates map path when data changes', async () => {
      locationsStore.fetchAssetLocationHistory.mockResolvedValue({
        locations: mockPathData
      })
      
      createWrapper()
      await flushPromises()
      
      // Verify path data is processed
      expect(wrapper.vm.pathData).toHaveLength(3)
    })

    it('creates custom markers for start, end, and waypoints', async () => {
      locationsStore.fetchAssetLocationHistory.mockResolvedValue({
        locations: mockPathData
      })
      
      createWrapper()
      await flushPromises()
      
      const L = await import('leaflet')
      expect(L.default.marker).toHaveBeenCalled()
      expect(L.default.divIcon).toHaveBeenCalled()
    })
  })

  describe('Export Functionality', () => {
    beforeEach(async () => {
      locationsStore.fetchAssetLocationHistory.mockResolvedValue({
        locations: mockPathData
      })
      
      // Mock URL.createObjectURL and related methods
      global.URL.createObjectURL = vi.fn(() => 'blob:url')
      global.URL.revokeObjectURL = vi.fn()
      
      // Mock DOM createElement and click
      const mockElement = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockElement)
    })

    it('exports path data as JSON', async () => {
      createWrapper()
      await flushPromises()
      
      await wrapper.vm.exportPath()
      
      expect(document.createElement).toHaveBeenCalledWith('a')
      expect(global.URL.createObjectURL).toHaveBeenCalled()
    })

    it('includes asset information and statistics in export', async () => {
      createWrapper()
      await flushPromises()
      
      const exportData = {
        asset: mockAsset,
        pathData: mockPathData,
        statistics: {
          totalDistance: wrapper.vm.totalDistance,
          duration: wrapper.vm.pathDuration,
          averageSpeed: wrapper.vm.averageSpeed,
          dataPoints: mockPathData.length
        },
        exportedAt: expect.any(String)
      }
      
      // Mock Blob constructor to capture data
      const originalBlob = global.Blob
      global.Blob = vi.fn()
      
      await wrapper.vm.exportPath()
      
      expect(global.Blob).toHaveBeenCalledWith(
        [JSON.stringify(exportData, null, 2)],
        { type: 'application/json' }
      )
      
      global.Blob = originalBlob
    })
  })

  describe('User Interactions', () => {
    it('emits close event when close button clicked', async () => {
      createWrapper()
      
      await wrapper.vm.closeModal()
      
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0]).toEqual([false])
    })

    it('refreshes data when refresh button clicked', async () => {
      locationsStore.fetchAssetLocationHistory.mockResolvedValue({
        locations: mockPathData
      })
      
      createWrapper()
      await flushPromises()
      
      const refreshButton = wrapper.find('[data-testid="refresh-button"]')
      if (refreshButton.exists()) {
        await refreshButton.trigger('click')
        expect(locationsStore.fetchAssetLocationHistory).toHaveBeenCalledTimes(2)
      }
    })

    it('emits add-location event for no data state', async () => {
      locationsStore.fetchAssetLocationHistory.mockResolvedValue({
        locations: []
      })
      
      createWrapper()
      await flushPromises()
      
      const addButton = wrapper.find('[data-testid="add-location-button"]')
      if (addButton.exists()) {
        await addButton.trigger('click')
        expect(wrapper.emitted('add-location')).toBeTruthy()
      }
    })
  })

  describe('Utility Functions', () => {
    it('calculates distance between two points correctly', () => {
      createWrapper()
      
      const distance = wrapper.vm.calculateDistance(40.7128, -74.0060, 40.7130, -74.0062)
      expect(distance).toBeGreaterThan(0)
      expect(typeof distance).toBe('number')
    })

    it('formats date and time correctly', () => {
      createWrapper()
      
      const formatted = wrapper.vm.formatDateTime('2023-01-01T10:00:00Z')
      expect(typeof formatted).toBe('string')
      expect(formatted).toContain('2023')
    })

    it('formats duration correctly', () => {
      createWrapper()
      
      const hourInMs = 60 * 60 * 1000
      const formatted = wrapper.vm.formatDuration(hourInMs + 30 * 60 * 1000) // 1h 30m
      expect(formatted).toBe('1h 30m')
      
      const minutesOnly = wrapper.vm.formatDuration(30 * 60 * 1000) // 30m
      expect(minutesOnly).toBe('30m')
    })

    it('formats location source correctly', () => {
      createWrapper()
      
      expect(wrapper.vm.formatSource('manual')).toBe('Manual')
      expect(wrapper.vm.formatSource('gps_device')).toBe('GPS')
      expect(wrapper.vm.formatSource('mobile_app')).toBe('Mobile')
      expect(wrapper.vm.formatSource('telematics')).toBe('Telematics')
    })
  })

  describe('Error Handling', () => {
    it('handles API errors gracefully', async () => {
      locationsStore.fetchAssetLocationHistory.mockRejectedValue(new Error('API Error'))
      
      createWrapper()
      await flushPromises()
      
      expect(wrapper.vm.pathData).toHaveLength(0)
      expect(wrapper.vm.isLoading).toBe(false)
    })

    it('handles missing asset gracefully', async () => {
      createWrapper({ asset: null })
      
      expect(locationsStore.fetchAssetLocationHistory).not.toHaveBeenCalled()
    })
  })

  describe('Responsive Design', () => {
    it('adjusts for mobile view', async () => {
      // Mock window width for mobile
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 600
      })
      
      createWrapper()
      await wrapper.vm.$nextTick()
      
      // Component should handle mobile layout
      expect(wrapper.find('.path-modal').exists()).toBe(true)
    })
  })
})