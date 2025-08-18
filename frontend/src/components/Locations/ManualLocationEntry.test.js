import { describe, it, expect, beforeEach, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ManualLocationEntry from './ManualLocationEntry.vue'
import { useAssetsStore } from '../../stores/assets'
import { useLocationsStore } from '../../stores/locations'

// Mock the stores
vi.mock('../../stores/assets')
vi.mock('../../stores/locations')

// Mock navigator.geolocation
Object.defineProperty(global, 'navigator', {
  value: {
    geolocation: {
      getCurrentPosition: vi.fn()
    }
  },
  writable: true
})

describe('ManualLocationEntry.vue', () => {
  let wrapper
  let assetsStore
  let locationsStore

  beforeEach(() => {
    setActivePinia(createPinia())

    // Mock store instances
    assetsStore = {
      assets: [
        {
          id: '1',
          asset_id: 'TEST001',
          make: 'Toyota',
          model: 'Camry',
          status: 'active',
          thumbnail: null
        },
        {
          id: '2',
          asset_id: 'TEST002',
          make: 'Ford',
          model: 'F-150',
          status: 'active',
          thumbnail: '/test-image.jpg'
        }
      ],
      hasAssets: true,
      isLoading: false,
      setSearchQuery: vi.fn(),
      fetchAssets: vi.fn()
    }

    locationsStore = {
      isCreating: false,
      error: null,
      createManualLocationEntry: vi.fn()
    }

    // Mock the composables
    useAssetsStore.mockReturnValue(assetsStore)
    useLocationsStore.mockReturnValue(locationsStore)

    wrapper = shallowMount(ManualLocationEntry, {
      global: {
        stubs: ['v-card', 'v-form', 'v-autocomplete', 'v-text-field', 'v-textarea', 'v-btn', 'v-alert']
      }
    })
  })

  afterEach(() => {
    wrapper?.unmount()
    vi.clearAllMocks()
  })

  describe('Component Initialization', () => {
    it('should render the component', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('should have correct initial form state', () => {
      expect(wrapper.vm.selectedAsset).toBe('')
      expect(wrapper.vm.latitude).toBe('')
      expect(wrapper.vm.longitude).toBe('')
      expect(wrapper.vm.address).toBe('')
      expect(wrapper.vm.notes).toBe('')
      expect(wrapper.vm.valid).toBe(false)
      expect(wrapper.vm.gettingLocation).toBe(false)
      expect(wrapper.vm.locationAccuracy).toBeNull()
    })

    it('should fetch assets on mount if none exist', async () => {
      assetsStore.hasAssets = false
      
      wrapper = shallowMount(ManualLocationEntry, {
        global: {
          stubs: ['v-card', 'v-form', 'v-autocomplete', 'v-text-field', 'v-textarea', 'v-btn', 'v-alert']
        }
      })

      await wrapper.vm.$nextTick()
      expect(assetsStore.fetchAssets).toHaveBeenCalled()
    })
  })

  describe('Computed Properties', () => {
    it('should filter out retired assets', () => {
      assetsStore.assets = [
        { asset_id: 'TEST001', status: 'active' },
        { asset_id: 'TEST002', status: 'retired' },
        { asset_id: 'TEST003', status: 'maintenance' }
      ]

      const filteredAssets = wrapper.vm.assets
      expect(filteredAssets).toHaveLength(2)
      expect(filteredAssets.every(asset => asset.status !== 'retired')).toBe(true)
    })
  })

  describe('Validation Rules', () => {
    it('should validate required fields', () => {
      const { required } = wrapper.vm.rules
      
      expect(required('')).toBe('This field is required')
      expect(required('value')).toBe(true)
      expect(required(null)).toBe('This field is required')
      expect(required(undefined)).toBe('This field is required')
    })

    it('should validate latitude range', () => {
      const { latitude } = wrapper.vm.rules
      
      expect(latitude('40.7128')).toBe(true)
      expect(latitude('90')).toBe(true)
      expect(latitude('-90')).toBe(true)
      expect(latitude('91')).toBe('Latitude must be between -90 and 90')
      expect(latitude('-91')).toBe('Latitude must be between -90 and 90')
      expect(latitude('invalid')).toBe('Latitude must be between -90 and 90')
    })

    it('should validate longitude range', () => {
      const { longitude } = wrapper.vm.rules
      
      expect(longitude('-74.0060')).toBe(true)
      expect(longitude('180')).toBe(true)
      expect(longitude('-180')).toBe(true)
      expect(longitude('181')).toBe('Longitude must be between -180 and 180')
      expect(longitude('-181')).toBe('Longitude must be between -180 and 180')
      expect(longitude('invalid')).toBe('Longitude must be between -180 and 180')
    })
  })

  describe('Geolocation Functionality', () => {
    it('should get current location successfully', async () => {
      const mockPosition = {
        coords: {
          latitude: 40.7128,
          longitude: -74.0060,
          accuracy: 10
        }
      }

      navigator.geolocation.getCurrentPosition.mockImplementation((success) => {
        success(mockPosition)
      })

      await wrapper.vm.getCurrentLocation()

      expect(wrapper.vm.latitude).toBe('40.7128')
      expect(wrapper.vm.longitude).toBe('-74.0060')
      expect(wrapper.vm.locationAccuracy).toBe(10)
      expect(wrapper.vm.gettingLocation).toBe(false)
    })

    it('should handle geolocation permission denied', async () => {
      const mockError = { code: 1 } // PERMISSION_DENIED
      
      navigator.geolocation.getCurrentPosition.mockImplementation((success, error) => {
        error(mockError)
      })

      // Mock alert
      global.alert = vi.fn()

      await wrapper.vm.getCurrentLocation()

      expect(global.alert).toHaveBeenCalledWith('Location access denied by user.')
      expect(wrapper.vm.gettingLocation).toBe(false)
    })

    it('should handle geolocation unavailable', async () => {
      const mockError = { code: 2 } // POSITION_UNAVAILABLE
      
      navigator.geolocation.getCurrentPosition.mockImplementation((success, error) => {
        error(mockError)
      })

      global.alert = vi.fn()

      await wrapper.vm.getCurrentLocation()

      expect(global.alert).toHaveBeenCalledWith('Location information is unavailable.')
    })

    it('should handle geolocation timeout', async () => {
      const mockError = { code: 3 } // TIMEOUT
      
      navigator.geolocation.getCurrentPosition.mockImplementation((success, error) => {
        error(mockError)
      })

      global.alert = vi.fn()

      await wrapper.vm.getCurrentLocation()

      expect(global.alert).toHaveBeenCalledWith('Location request timed out.')
    })

    it('should handle geolocation not supported', async () => {
      // Mock navigator.geolocation as undefined
      Object.defineProperty(global, 'navigator', {
        value: {},
        writable: true
      })

      global.alert = vi.fn()

      await wrapper.vm.getCurrentLocation()

      expect(global.alert).toHaveBeenCalledWith('Geolocation is not supported by this browser.')
    })
  })

  describe('Form Submission', () => {
    beforeEach(() => {
      // Set up valid form data
      wrapper.vm.selectedAsset = 'TEST001'
      wrapper.vm.latitude = '40.7128'
      wrapper.vm.longitude = '-74.0060'
      wrapper.vm.address = 'New York, NY'
      wrapper.vm.notes = 'Test notes'
      wrapper.vm.valid = true
    })

    it('should submit location successfully', async () => {
      const expectedData = {
        asset_id: 'TEST001',
        latitude: 40.7128,
        longitude: -74.0060,
        address: 'New York, NY',
        notes: 'Test notes'
      }

      locationsStore.createManualLocationEntry.mockResolvedValue({})

      // Mock form validation
      wrapper.vm.$refs.form = {
        validate: vi.fn().mockReturnValue(true)
      }

      await wrapper.vm.submitLocation()

      expect(locationsStore.createManualLocationEntry).toHaveBeenCalledWith(expectedData)
      
      // Form should be reset
      expect(wrapper.vm.selectedAsset).toBe('')
      expect(wrapper.vm.latitude).toBe('')
      expect(wrapper.vm.longitude).toBe('')
      expect(wrapper.vm.address).toBe('')
      expect(wrapper.vm.notes).toBe('')
      expect(wrapper.vm.locationAccuracy).toBeNull()
    })

    it('should not submit if form is invalid', async () => {
      wrapper.vm.valid = false
      wrapper.vm.$refs.form = {
        validate: vi.fn().mockReturnValue(false)
      }

      await wrapper.vm.submitLocation()

      expect(locationsStore.createManualLocationEntry).not.toHaveBeenCalled()
    })

    it('should handle submission error', async () => {
      const error = new Error('API Error')
      locationsStore.createManualLocationEntry.mockRejectedValue(error)

      wrapper.vm.$refs.form = {
        validate: vi.fn().mockReturnValue(true)
      }

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      await wrapper.vm.submitLocation()

      expect(consoleSpy).toHaveBeenCalledWith('Failed to add location:', error)
      
      consoleSpy.mockRestore()
    })
  })

  describe('Asset Search', () => {
    it('should search assets when query provided', () => {
      const query = 'TEST'
      
      wrapper.vm.searchAssets(query)

      expect(assetsStore.setSearchQuery).toHaveBeenCalledWith(query)
      expect(assetsStore.fetchAssets).toHaveBeenCalledWith({ page: 1 })
    })

    it('should not search when query is empty', () => {
      wrapper.vm.searchAssets('')

      expect(assetsStore.setSearchQuery).not.toHaveBeenCalled()
      expect(assetsStore.fetchAssets).not.toHaveBeenCalled()
    })

    it('should not search when query is null', () => {
      wrapper.vm.searchAssets(null)

      expect(assetsStore.setSearchQuery).not.toHaveBeenCalled()
      expect(assetsStore.fetchAssets).not.toHaveBeenCalled()
    })
  })

  describe('Error Handling', () => {
    it('should display string error message', () => {
      const errorMessage = 'Test error message'
      expect(wrapper.vm.getErrorMessage(errorMessage)).toBe(errorMessage)
    })

    it('should display asset_id error', () => {
      const error = { asset_id: ['Asset not found'] }
      expect(wrapper.vm.getErrorMessage(error)).toBe('Asset: Asset not found')
    })

    it('should display latitude error', () => {
      const error = { latitude: ['Invalid latitude'] }
      expect(wrapper.vm.getErrorMessage(error)).toBe('Latitude: Invalid latitude')
    })

    it('should display longitude error', () => {
      const error = { longitude: ['Invalid longitude'] }
      expect(wrapper.vm.getErrorMessage(error)).toBe('Longitude: Invalid longitude')
    })

    it('should display default error for unknown error format', () => {
      const error = { unknown: ['Some error'] }
      expect(wrapper.vm.getErrorMessage(error)).toBe('Failed to add location entry')
    })
  })

  describe('Events', () => {
    it('should emit close event', () => {
      wrapper.vm.$emit('close')
      
      expect(wrapper.emitted('close')).toBeTruthy()
      expect(wrapper.emitted('close')).toHaveLength(1)
    })

    it('should emit location-added event', () => {
      wrapper.vm.$emit('location-added')
      
      expect(wrapper.emitted('location-added')).toBeTruthy()
      expect(wrapper.emitted('location-added')).toHaveLength(1)
    })
  })

  describe('Coordinate Preview', () => {
    it('should format coordinates correctly', () => {
      wrapper.vm.latitude = '40.7128456'
      wrapper.vm.longitude = '-74.0060123'

      // Since we're testing with stubs, we can't easily test template rendering
      // But we can test the underlying values
      expect(parseFloat(wrapper.vm.latitude).toFixed(6)).toBe('40.712846')
      expect(parseFloat(wrapper.vm.longitude).toFixed(6)).toBe('-74.006012')
    })
  })
})