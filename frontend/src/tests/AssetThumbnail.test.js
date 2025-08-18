import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import AssetsList from '@/views/Assets/AssetsList.vue'
import { useAssetsStore } from '@/stores/assets'

// Mock Vue Router
const mockRouter = {
  push: vi.fn()
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}))

// Create vuetify instance
const vuetify = createVuetify()

describe('Asset Thumbnail Display', () => {
  let wrapper
  let store
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useAssetsStore()
    
    // Mock store methods
    store.fetchAssets = vi.fn().mockResolvedValue({
      results: [],
      count: 0
    })
    store.fetchAssetStats = vi.fn().mockResolvedValue({
      total_assets: 0,
      active_assets: 0,
      maintenance_assets: 0,
      retired_assets: 0
    })

    // Set initial store state
    store.assets = []
    store.totalAssets = 0
    store.isLoading = false
    store.assetStats = {
      total_assets: 0,
      active_assets: 0,
      maintenance_assets: 0,
      retired_assets: 0
    }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  const mountComponent = () => {
    return mount(AssetsList, {
      global: {
        plugins: [vuetify, pinia],
        mocks: {
          $router: mockRouter
        }
      }
    })
  }

  it('displays thumbnail when asset has thumbnail URL', async () => {
    // Set up asset with thumbnail
    store.assets = [{
      id: 'test-id-1',
      asset_id: 'TEST-001',
      make: 'Ford',
      model: 'F-150',
      year: 2022,
      vehicle_type: 'truck',
      status: 'active',
      thumbnail: '/media/assets/images/thumbnails/TEST-001_thumb.jpg'
    }]
    store.totalAssets = 1

    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Find thumbnail container
    const thumbnailContainer = wrapper.find('.thumbnail-container')
    expect(thumbnailContainer.exists()).toBe(true)

    // Find thumbnail image
    const thumbnailImage = thumbnailContainer.find('.asset-thumbnail')
    expect(thumbnailImage.exists()).toBe(true)
    expect(thumbnailImage.attributes('src')).toBe('/media/assets/images/thumbnails/TEST-001_thumb.jpg')
  })

  it('displays vehicle type icon when no thumbnail available', async () => {
    // Set up asset without thumbnail
    store.assets = [{
      id: 'test-id-1',
      asset_id: 'TEST-001',
      make: 'Ford',
      model: 'F-150',
      year: 2022,
      vehicle_type: 'truck',
      status: 'active',
      thumbnail: null
    }]
    store.totalAssets = 1

    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Find thumbnail container
    const thumbnailContainer = wrapper.find('.thumbnail-container')
    expect(thumbnailContainer.exists()).toBe(true)

    // Find placeholder
    const placeholder = thumbnailContainer.find('.no-image-placeholder')
    expect(placeholder.exists()).toBe(true)

    // Find icon
    const icon = placeholder.find('v-icon')
    expect(icon.exists()).toBe(true)
  })

  it('shows correct vehicle type icons for different types', async () => {
    const testVehicles = [
      { vehicle_type: 'bus', expectedIcon: 'mdi-bus' },
      { vehicle_type: 'truck', expectedIcon: 'mdi-truck' },
      { vehicle_type: 'tractor', expectedIcon: 'mdi-tractor' },
      { vehicle_type: 'trailer', expectedIcon: 'mdi-truck-trailer' },
      { vehicle_type: 'van', expectedIcon: 'mdi-van-passenger' },
      { vehicle_type: 'car', expectedIcon: 'mdi-car' },
      { vehicle_type: 'equipment', expectedIcon: 'mdi-excavator' },
      { vehicle_type: 'other', expectedIcon: 'mdi-help-circle' }
    ]

    for (const { vehicle_type, expectedIcon } of testVehicles) {
      // Set up asset with specific vehicle type
      store.assets = [{
        id: 'test-id-1',
        asset_id: 'TEST-001',
        make: 'Test',
        model: 'Model',
        year: 2022,
        vehicle_type,
        status: 'active',
        thumbnail: null
      }]

      wrapper = mountComponent()
      await wrapper.vm.$nextTick()

      // Check icon matches vehicle type
      const actualIcon = wrapper.vm.getVehicleTypeIcon(vehicle_type)
      expect(actualIcon).toBe(expectedIcon)

      wrapper.unmount()
    }
  })

  it('thumbnail has correct styling classes', async () => {
    store.assets = [{
      id: 'test-id-1',
      asset_id: 'TEST-001',
      make: 'Ford',
      model: 'F-150',
      year: 2022,
      vehicle_type: 'truck',
      status: 'active',
      thumbnail: '/media/assets/images/thumbnails/TEST-001_thumb.jpg'
    }]
    store.totalAssets = 1

    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Check thumbnail container styling
    const thumbnailContainer = wrapper.find('.thumbnail-container')
    expect(thumbnailContainer.classes()).toContain('thumbnail-container')

    // Check thumbnail image styling
    const thumbnailImage = wrapper.find('.asset-thumbnail')
    expect(thumbnailImage.classes()).toContain('asset-thumbnail')
  })

  it('placeholder has correct styling classes', async () => {
    store.assets = [{
      id: 'test-id-1',
      asset_id: 'TEST-001',
      make: 'Ford',
      model: 'F-150',
      year: 2022,
      vehicle_type: 'truck',
      status: 'active',
      thumbnail: null
    }]
    store.totalAssets = 1

    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Check placeholder styling
    const placeholder = wrapper.find('.no-image-placeholder')
    expect(placeholder.classes()).toContain('no-image-placeholder')
  })

  it('handles multiple assets with mixed thumbnail states', async () => {
    store.assets = [
      {
        id: 'test-id-1',
        asset_id: 'TEST-001',
        make: 'Ford',
        model: 'F-150',
        year: 2022,
        vehicle_type: 'truck',
        status: 'active',
        thumbnail: '/media/assets/images/thumbnails/TEST-001_thumb.jpg'
      },
      {
        id: 'test-id-2',
        asset_id: 'TEST-002',
        make: 'Mercedes',
        model: 'Sprinter',
        year: 2021,
        vehicle_type: 'bus',
        status: 'active',
        thumbnail: null
      },
      {
        id: 'test-id-3',
        asset_id: 'TEST-003',
        make: 'Toyota',
        model: 'Camry',
        year: 2023,
        vehicle_type: 'car',
        status: 'active',
        thumbnail: '/media/assets/images/thumbnails/TEST-003_thumb.jpg'
      }
    ]
    store.totalAssets = 3

    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Should have 3 thumbnail containers
    const thumbnailContainers = wrapper.findAll('.thumbnail-container')
    expect(thumbnailContainers).toHaveLength(3)

    // First and third should have images
    const thumbnailImages = wrapper.findAll('.asset-thumbnail')
    expect(thumbnailImages).toHaveLength(2)

    // Second should have placeholder
    const placeholders = wrapper.findAll('.no-image-placeholder')
    expect(placeholders).toHaveLength(1)
  })

  it('thumbnail column is included in table headers', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Check that thumbnail column is in headers
    const headers = wrapper.vm.headers
    const thumbnailHeader = headers.find(h => h.key === 'thumbnail')
    
    expect(thumbnailHeader).toBeDefined()
    expect(thumbnailHeader.title).toBe('')
    expect(thumbnailHeader.sortable).toBe(false)
    expect(thumbnailHeader.width).toBe('60px')
  })

  it('thumbnail alt text includes asset ID', async () => {
    store.assets = [{
      id: 'test-id-1',
      asset_id: 'TEST-001',
      make: 'Ford',
      model: 'F-150',
      year: 2022,
      vehicle_type: 'truck',
      status: 'active',
      thumbnail: '/media/assets/images/thumbnails/TEST-001_thumb.jpg'
    }]
    store.totalAssets = 1

    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Find thumbnail image
    const thumbnailImage = wrapper.find('.asset-thumbnail')
    expect(thumbnailImage.attributes('alt')).toBe('TEST-001 thumbnail')
  })

  it('handles empty thumbnail URL gracefully', async () => {
    store.assets = [{
      id: 'test-id-1',
      asset_id: 'TEST-001',
      make: 'Ford',
      model: 'F-150',
      year: 2022,
      vehicle_type: 'truck',
      status: 'active',
      thumbnail: ''  // Empty string instead of null
    }]
    store.totalAssets = 1

    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Should show placeholder since thumbnail is falsy
    const placeholder = wrapper.find('.no-image-placeholder')
    expect(placeholder.exists()).toBe(true)

    const thumbnailImage = wrapper.find('.asset-thumbnail')
    expect(thumbnailImage.exists()).toBe(false)
  })

  it('thumbnail image uses cover mode for proper aspect ratio', async () => {
    store.assets = [{
      id: 'test-id-1',
      asset_id: 'TEST-001',
      make: 'Ford',
      model: 'F-150',
      year: 2022,
      vehicle_type: 'truck',
      status: 'active',
      thumbnail: '/media/assets/images/thumbnails/TEST-001_thumb.jpg'
    }]
    store.totalAssets = 1

    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Find thumbnail image and check cover attribute
    const thumbnailImage = wrapper.find('.asset-thumbnail')
    expect(thumbnailImage.attributes('cover')).toBeDefined()
  })
})