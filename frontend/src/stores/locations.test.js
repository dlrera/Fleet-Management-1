import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useLocationsStore } from './locations'
import { locationsAPI } from '../services/api'

// Mock the API
vi.mock('../services/api', () => ({
  locationsAPI: {
    getLocationUpdates: vi.fn(),
    getCurrentLocations: vi.fn(),
    getMapData: vi.fn(),
    createLocationUpdate: vi.fn(),
    createManualEntry: vi.fn(),
    getAssetHistory: vi.fn(),
    getLatestLocations: vi.fn(),
    getLocationZones: vi.fn(),
    createLocationZone: vi.fn(),
    updateLocationZone: vi.fn(),
    deleteLocationZone: vi.fn(),
    getAssetsInZone: vi.fn(),
    checkPointInZone: vi.fn(),
    getLocationStats: vi.fn(),
  },
}))

describe('Locations Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useLocationsStore()
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      expect(store.locationUpdates).toEqual([])
      expect(store.totalUpdates).toBe(0)
      expect(store.currentPage).toBe(1)
      expect(store.pageSize).toBe(20)
      expect(store.assetLocations).toEqual([])
      expect(store.mapData).toBeNull()
      expect(store.locationZones).toEqual([])
      expect(store.currentZone).toBeNull()
      expect(store.searchQuery).toBe('')
      expect(store.filters).toEqual({
        source: '',
        asset_status: '',
        vehicle_type: '',
        zone_id: '',
        within_hours: 24
      })
      expect(store.sortBy).toBe('timestamp')
      expect(store.sortDesc).toBe(true)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('Getters', () => {
    it('should calculate hasLocationUpdates correctly', () => {
      expect(store.hasLocationUpdates).toBe(false)
      
      store.locationUpdates = [{ id: '1' }]
      expect(store.hasLocationUpdates).toBe(true)
    })

    it('should calculate totalPages correctly', () => {
      expect(store.totalPages).toBe(0)
      
      store.totalUpdates = 50
      store.pageSize = 20
      expect(store.totalPages).toBe(3)
    })

    it('should calculate hasNextPage correctly', () => {
      store.totalUpdates = 50
      store.pageSize = 20
      store.currentPage = 1
      expect(store.hasNextPage).toBe(true)
      
      store.currentPage = 3
      expect(store.hasNextPage).toBe(false)
    })

    it('should calculate hasPreviousPage correctly', () => {
      store.currentPage = 1
      expect(store.hasPreviousPage).toBe(false)
      
      store.currentPage = 2
      expect(store.hasPreviousPage).toBe(true)
    })

    it('should calculate hasAssetLocations correctly', () => {
      expect(store.hasAssetLocations).toBe(false)
      
      store.assetLocations = [{ id: '1' }]
      expect(store.hasAssetLocations).toBe(true)
    })

    it('should calculate hasMapData correctly', () => {
      expect(store.hasMapData).toBe(false)
      
      store.mapData = { assets: [], zones: [] }
      expect(store.hasMapData).toBe(true)
    })

    it('should calculate hasZones correctly', () => {
      expect(store.hasZones).toBe(false)
      
      store.locationZones = [{ id: '1' }]
      expect(store.hasZones).toBe(true)
    })

    it('should calculate activeZones correctly', () => {
      store.locationZones = [
        { id: '1', is_active: true },
        { id: '2', is_active: false },
        { id: '3', is_active: true }
      ]
      
      expect(store.activeZones).toHaveLength(2)
      expect(store.activeZones.every(zone => zone.is_active)).toBe(true)
    })

    it('should calculate hasActiveFilters correctly', () => {
      // Reset filters to known state
      store.filters = {
        source: '',
        asset_status: '',
        vehicle_type: '',
        zone_id: '',
        within_hours: 24  // This has a default value
      }
      store.searchQuery = ''
      
      // Should be true because within_hours has a value
      expect(store.hasActiveFilters).toBe(true)
      
      store.filters.source = 'manual'
      expect(store.hasActiveFilters).toBe(true)
      
      store.filters.source = ''
      store.searchQuery = 'test'
      expect(store.hasActiveFilters).toBe(true)
    })

    it('should calculate isAnyLoading correctly', () => {
      expect(store.isAnyLoading).toBe(false)
      
      store.isLoading = true
      expect(store.isAnyLoading).toBe(true)
      
      store.isLoading = false
      store.isCreating = true
      expect(store.isAnyLoading).toBe(true)
    })

    it('should calculate hasError correctly', () => {
      expect(store.hasError).toBe(false)
      
      store.error = 'Some error'
      expect(store.hasError).toBe(true)
      
      store.error = null
      store.locationError = 'Location error'
      expect(store.hasError).toBe(true)
    })
  })

  describe('Location Updates Actions', () => {
    it('should fetch location updates successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: '1', asset: { asset_id: 'TEST001' }, latitude: 40.7128, longitude: -74.0060 }
          ],
          count: 1
        }
      }
      
      locationsAPI.getLocationUpdates.mockResolvedValue(mockResponse)
      
      const result = await store.fetchLocationUpdates()
      
      expect(locationsAPI.getLocationUpdates).toHaveBeenCalledWith({
        page: 1,
        page_size: 20,
        ordering: '-timestamp',
        within_hours: 24
      })
      expect(store.locationUpdates).toEqual(mockResponse.data.results)
      expect(store.totalUpdates).toBe(1)
      expect(store.isLoading).toBe(false)
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle fetch location updates error', async () => {
      const mockError = new Error('API Error')
      mockError.response = { data: 'Failed to fetch' }
      
      locationsAPI.getLocationUpdates.mockRejectedValue(mockError)
      
      await expect(store.fetchLocationUpdates()).rejects.toThrow()
      expect(store.error).toBe('Failed to fetch')
      expect(store.isLoading).toBe(false)
    })

    it('should create location update successfully', async () => {
      const mockLocationData = {
        asset_id: 'TEST001',
        latitude: 40.7128,
        longitude: -74.0060,
        source: 'manual'
      }
      
      const mockResponse = {
        data: { id: '1', ...mockLocationData }
      }
      
      locationsAPI.createLocationUpdate.mockResolvedValue(mockResponse)
      store.currentPage = 1
      
      const result = await store.createLocationUpdate(mockLocationData)
      
      expect(locationsAPI.createLocationUpdate).toHaveBeenCalledWith(mockLocationData)
      expect(store.locationUpdates).toContain(mockResponse.data)
      expect(store.totalUpdates).toBe(1)
      expect(result).toEqual(mockResponse.data)
    })

    it('should create manual location entry successfully', async () => {
      const mockEntryData = {
        asset_id: 'TEST001',
        latitude: 40.7128,
        longitude: -74.0060,
        address: 'New York, NY'
      }
      
      const mockResponse = {
        data: { id: '1', ...mockEntryData }
      }
      
      locationsAPI.createManualEntry.mockResolvedValue(mockResponse)
      locationsAPI.getMapData.mockResolvedValue({ data: { assets: [], zones: [] } })
      
      const result = await store.createManualLocationEntry(mockEntryData)
      
      expect(locationsAPI.createManualEntry).toHaveBeenCalledWith(mockEntryData)
      expect(locationsAPI.getMapData).toHaveBeenCalled()
      expect(result).toEqual(mockResponse.data)
    })

    it('should fetch asset location history', async () => {
      const assetId = 'TEST001'
      const mockResponse = {
        data: {
          asset: { id: '1', asset_id: assetId },
          locations: [
            { id: '1', latitude: 40.7128, longitude: -74.0060 }
          ]
        }
      }
      
      locationsAPI.getAssetHistory.mockResolvedValue(mockResponse)
      
      const result = await store.fetchAssetLocationHistory(assetId)
      
      expect(locationsAPI.getAssetHistory).toHaveBeenCalledWith(assetId, {
        days: 7,
        limit: 100
      })
      expect(result).toEqual(mockResponse.data)
    })

    it('should fetch latest locations', async () => {
      const mockResponse = {
        data: [
          { id: '1', asset: { asset_id: 'TEST001' }, latitude: 40.7128 }
        ]
      }
      
      locationsAPI.getLatestLocations.mockResolvedValue(mockResponse)
      
      const result = await store.fetchLatestLocations()
      
      expect(locationsAPI.getLatestLocations).toHaveBeenCalledWith({})
      expect(store.assetLocations).toEqual(mockResponse.data)
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('Map Data Actions', () => {
    it('should fetch map data successfully', async () => {
      const mockResponse = {
        data: {
          assets: [
            { id: '1', asset: { asset_id: 'TEST001' }, latitude: 40.7128, longitude: -74.0060 }
          ],
          zones: [
            { id: '1', name: 'Test Zone', center_lat: 40.7128, center_lng: -74.0060 }
          ],
          last_updated: '2023-01-01T00:00:00Z'
        }
      }
      
      locationsAPI.getMapData.mockResolvedValue(mockResponse)
      
      const result = await store.fetchMapData()
      
      expect(locationsAPI.getMapData).toHaveBeenCalledWith({
        within_hours: 24
      })
      expect(store.mapData).toEqual(mockResponse.data)
      expect(result).toEqual(mockResponse.data)
    })

    it('should fetch asset locations', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: '1', asset: { asset_id: 'TEST001' }, latitude: 40.7128 }
          ]
        }
      }
      
      locationsAPI.getCurrentLocations.mockResolvedValue(mockResponse)
      
      const result = await store.fetchAssetLocations()
      
      expect(locationsAPI.getCurrentLocations).toHaveBeenCalled()
      expect(store.assetLocations).toEqual(mockResponse.data.results)
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('Location Zones Actions', () => {
    it('should fetch location zones successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: '1', name: 'Test Zone', zone_type: 'depot' }
          ]
        }
      }
      
      locationsAPI.getLocationZones.mockResolvedValue(mockResponse)
      
      const result = await store.fetchLocationZones()
      
      expect(locationsAPI.getLocationZones).toHaveBeenCalledWith({})
      expect(store.locationZones).toEqual(mockResponse.data.results)
      expect(result).toEqual(mockResponse.data)
    })

    it('should create location zone successfully', async () => {
      const mockZoneData = {
        name: 'Test Zone',
        center_lat: 40.7128,
        center_lng: -74.0060,
        radius: 1000,
        zone_type: 'depot'
      }
      
      const mockResponse = {
        data: { id: '1', ...mockZoneData }
      }
      
      locationsAPI.createLocationZone.mockResolvedValue(mockResponse)
      
      const result = await store.createLocationZone(mockZoneData)
      
      expect(locationsAPI.createLocationZone).toHaveBeenCalledWith(mockZoneData)
      expect(store.locationZones).toContain(mockResponse.data)
      expect(result).toEqual(mockResponse.data)
    })

    it('should update location zone successfully', async () => {
      const zoneId = '1'
      const initialZone = { id: zoneId, name: 'Old Name' }
      const updatedData = { name: 'New Name' }
      const updatedZone = { id: zoneId, name: 'New Name' }
      
      store.locationZones = [initialZone]
      store.currentZone = initialZone
      
      locationsAPI.updateLocationZone.mockResolvedValue({ data: updatedZone })
      
      const result = await store.updateLocationZone(zoneId, updatedData)
      
      expect(locationsAPI.updateLocationZone).toHaveBeenCalledWith(zoneId, updatedData)
      expect(store.locationZones[0]).toEqual(updatedZone)
      expect(store.currentZone).toEqual(updatedZone)
      expect(result).toEqual(updatedZone)
    })

    it('should delete location zone successfully', async () => {
      const zoneId = '1'
      const zone = { id: zoneId, name: 'Test Zone' }
      
      store.locationZones = [zone]
      store.currentZone = zone
      
      locationsAPI.deleteLocationZone.mockResolvedValue({})
      
      const result = await store.deleteLocationZone(zoneId)
      
      expect(locationsAPI.deleteLocationZone).toHaveBeenCalledWith(zoneId)
      expect(store.locationZones).toHaveLength(0)
      expect(store.currentZone).toBeNull()
      expect(result).toBe(true)
    })

    it('should fetch assets in zone', async () => {
      const zoneId = '1'
      const mockResponse = {
        data: {
          zone: { id: zoneId, name: 'Test Zone' },
          assets: [
            { id: '1', asset: { asset_id: 'TEST001' } }
          ],
          count: 1
        }
      }
      
      locationsAPI.getAssetsInZone.mockResolvedValue(mockResponse)
      
      const result = await store.fetchAssetsInZone(zoneId)
      
      expect(locationsAPI.getAssetsInZone).toHaveBeenCalledWith(zoneId)
      expect(result).toEqual(mockResponse.data)
    })

    it('should check point in zone', async () => {
      const zoneId = '1'
      const latitude = 40.7128
      const longitude = -74.0060
      const mockResponse = {
        data: {
          zone: 'Test Zone',
          point: { latitude, longitude },
          is_within_zone: true
        }
      }
      
      locationsAPI.checkPointInZone.mockResolvedValue(mockResponse)
      
      const result = await store.checkPointInZone(zoneId, latitude, longitude)
      
      expect(locationsAPI.checkPointInZone).toHaveBeenCalledWith(zoneId, { latitude, longitude })
      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('Statistics Actions', () => {
    it('should fetch location stats successfully', async () => {
      const mockStats = {
        total_updates: 100,
        today_updates: 10,
        assets_with_recent_locations: 25,
        total_trackable_assets: 30,
        tracking_coverage: 83.3,
        source_breakdown: {
          manual: 20,
          gps_device: 50,
          telematics: 30
        }
      }
      
      locationsAPI.getLocationStats.mockResolvedValue({ data: mockStats })
      
      const result = await store.fetchLocationStats()
      
      expect(locationsAPI.getLocationStats).toHaveBeenCalled()
      expect(store.locationStats).toEqual(mockStats)
      expect(result).toEqual(mockStats)
    })

    it('should handle stats fetch error gracefully', async () => {
      locationsAPI.getLocationStats.mockRejectedValue(new Error('API Error'))
      
      const result = await store.fetchLocationStats()
      
      expect(result).toBeNull()
      // Should not throw error
    })
  })

  describe('Search and Filter Actions', () => {
    it('should set search query', () => {
      const query = 'test search'
      store.setSearchQuery(query)
      
      expect(store.searchQuery).toBe(query)
    })

    it('should set individual filter', () => {
      store.setFilter('source', 'manual')
      
      expect(store.filters.source).toBe('manual')
    })

    it('should set multiple filters', () => {
      const newFilters = { source: 'manual', vehicle_type: 'truck' }
      store.setFilters(newFilters)
      
      expect(store.filters.source).toBe('manual')
      expect(store.filters.vehicle_type).toBe('truck')
      expect(store.filters.asset_status).toBe('') // Should preserve other filters
    })

    it('should clear all filters', () => {
      store.searchQuery = 'test'
      store.filters = { source: 'manual', vehicle_type: 'truck' }
      
      store.clearFilters()
      
      expect(store.searchQuery).toBe('')
      expect(store.filters).toEqual({
        source: '',
        asset_status: '',
        vehicle_type: '',
        zone_id: '',
        within_hours: 24
      })
    })

    it('should set sorting', () => {
      store.setSorting('created_at', true)
      
      expect(store.sortBy).toBe('created_at')
      expect(store.sortDesc).toBe(true)
    })

    it('should set page', () => {
      store.setPage(3)
      
      expect(store.currentPage).toBe(3)
    })
  })

  describe('Utility Actions', () => {
    it('should build filter params correctly', () => {
      store.searchQuery = 'test search'
      store.filters = {
        source: 'manual',
        asset_status: 'active',
        vehicle_type: '',
        zone_id: null,
        within_hours: 24
      }
      
      const params = store.buildFilterParams()
      
      expect(params).toEqual({
        search: 'test search',
        source: 'manual',
        asset_status: 'active',
        within_hours: 24
      })
    })

    it('should clear errors', () => {
      store.error = 'Some error'
      store.locationError = 'Location error'
      store.zoneError = 'Zone error'
      store.mapError = 'Map error'
      
      store.clearError()
      
      expect(store.error).toBeNull()
      expect(store.locationError).toBeNull()
      expect(store.zoneError).toBeNull()
      expect(store.mapError).toBeNull()
    })

    it('should clear current zone', () => {
      store.currentZone = { id: '1', name: 'Test Zone' }
      
      store.clearCurrentZone()
      
      expect(store.currentZone).toBeNull()
    })
  })

  describe('Real-time Updates', () => {
    it('should handle location update correctly', () => {
      const locationData = {
        id: '1',
        asset: { id: '1', asset_id: 'TEST001' },
        latitude: 40.7128,
        longitude: -74.0060
      }
      
      store.currentPage = 1
      store.pageSize = 20
      
      store.handleLocationUpdate(locationData)
      
      expect(store.locationUpdates).toContain(locationData)
    })

    it('should not add to list if not on first page', () => {
      const locationData = {
        id: '1',
        asset: { id: '1', asset_id: 'TEST001' },
        latitude: 40.7128,
        longitude: -74.0060
      }
      
      store.currentPage = 2
      
      store.handleLocationUpdate(locationData)
      
      expect(store.locationUpdates).not.toContain(locationData)
    })

    it('should update existing asset location', () => {
      const existingLocation = {
        asset: { id: '1', asset_id: 'TEST001' },
        latitude: 40.7128,
        longitude: -74.0060
      }
      
      const updatedLocation = {
        asset: { id: '1', asset_id: 'TEST001' },
        latitude: 40.7130,
        longitude: -74.0062
      }
      
      store.assetLocations = [existingLocation]
      store.handleLocationUpdate(updatedLocation)
      
      expect(store.assetLocations[0]).toEqual(updatedLocation)
    })
  })
})