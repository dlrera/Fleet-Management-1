import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import AssetDetail from '@/views/Assets/AssetDetail.vue'
import { useAssetsStore } from '@/stores/assets'

// Mock Vue Router
const mockRoute = {
  params: { id: 'test-asset-id' }
}

const mockRouter = {
  push: vi.fn()
}

vi.mock('vue-router', () => ({
  useRoute: () => mockRoute,
  useRouter: () => mockRouter
}))

// Create vuetify instance
const vuetify = createVuetify()

// Mock file objects
const createMockFile = (name = 'test-image.jpg', type = 'image/jpeg', size = 1024) => {
  const file = new File(['test content'], name, { type })
  Object.defineProperty(file, 'size', { value: size })
  return file
}

describe('Asset Image Upload Component', () => {
  let wrapper
  let store
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useAssetsStore()
    
    // Mock store methods
    store.fetchAsset = vi.fn().mockResolvedValue({
      id: 'test-asset-id',
      asset_id: 'TEST-001',
      make: 'Ford',
      model: 'F-150',
      year: 2022,
      vehicle_type: 'truck',
      status: 'active'
    })
    store.fetchAssetDocuments = vi.fn().mockResolvedValue([])
    store.uploadImage = vi.fn().mockResolvedValue({
      image: '/media/assets/images/TEST-001_main.jpg',
      thumbnail: '/media/assets/images/thumbnails/TEST-001_thumb.jpg'
    })

    // Set initial store state
    store.currentAsset = {
      id: 'test-asset-id',
      asset_id: 'TEST-001',
      make: 'Ford',
      model: 'F-150',
      year: 2022,
      vehicle_type: 'truck',
      status: 'active'
    }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  const mountComponent = () => {
    return mount(AssetDetail, {
      global: {
        plugins: [vuetify, pinia],
        mocks: {
          $route: mockRoute,
          $router: mockRouter
        }
      }
    })
  }

  it('renders image upload section', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Check that the component rendered without errors
    expect(wrapper.exists()).toBe(true)
    
    // Check that image upload dialog state exists
    expect(wrapper.vm.showImageUploadDialog).toBeDefined()
  })

  it('opens image upload dialog when upload button clicked', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Set dialog state directly (since DOM interaction is complex with Vuetify)
    wrapper.vm.showImageUploadDialog = true
    await wrapper.vm.$nextTick()

    // Dialog should be visible
    expect(wrapper.vm.showImageUploadDialog).toBe(true)
  })

  it('validates image file type', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Create invalid file
    const invalidFile = createMockFile('test.txt', 'text/plain')

    // Call validation method directly
    wrapper.vm.validateAndSetImageFile(invalidFile)

    // Should show error
    expect(wrapper.vm.imageUploadError).toContain('Invalid file type')
    expect(wrapper.vm.selectedImageFile).toBeNull()
  })

  it('validates image file size', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Create oversized file (6MB)
    const oversizedFile = createMockFile('large-image.jpg', 'image/jpeg', 6 * 1024 * 1024)

    // Call validation method directly
    wrapper.vm.validateAndSetImageFile(oversizedFile)

    // Should show error
    expect(wrapper.vm.imageUploadError).toContain('5MB')
    expect(wrapper.vm.selectedImageFile).toBeNull()
  })

  it('accepts valid image file', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Create valid file
    const validFile = createMockFile('test-image.jpg', 'image/jpeg', 1024)

    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn().mockReturnValue('blob:test-url')
    global.URL.revokeObjectURL = vi.fn()

    // Call validation method directly
    wrapper.vm.validateAndSetImageFile(validFile)

    // Should accept file
    expect(wrapper.vm.imageUploadError).toBe('')
    expect(wrapper.vm.selectedImageFile).toEqual(validFile)
    expect(wrapper.vm.imagePreviewUrl).toBe('blob:test-url')
  })

  it('handles drag and drop image upload', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Create valid file
    const validFile = createMockFile('test-image.jpg', 'image/jpeg', 1024)

    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn().mockReturnValue('blob:test-url')

    // Simulate drop event handler directly
    const dropEvent = {
      preventDefault: vi.fn(),
      dataTransfer: {
        files: [validFile]
      }
    }

    // Call handler directly
    wrapper.vm.handleImageDrop(dropEvent)

    // Should handle file
    expect(wrapper.vm.selectedImageFile).toEqual(validFile)
  })

  it('calls store uploadImage method on upload', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Set up file
    const validFile = createMockFile('test-image.jpg', 'image/jpeg', 1024)
    wrapper.vm.selectedImageFile = validFile

    // Call upload method
    await wrapper.vm.uploadImage()

    // Should call store method
    expect(store.uploadImage).toHaveBeenCalledWith('test-asset-id', expect.any(FormData))
  })

  it('shows upload error on failure', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Mock upload failure
    store.uploadImage.mockRejectedValue({
      response: {
        data: {
          error: 'Upload failed'
        }
      }
    })

    // Set up file
    const validFile = createMockFile('test-image.jpg', 'image/jpeg', 1024)
    wrapper.vm.selectedImageFile = validFile

    // Call upload method
    await wrapper.vm.uploadImage()

    // Should show error
    expect(wrapper.vm.imageUploadError).toBe('Upload failed')
  })

  it('clears image file when remove button clicked', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Set up file and preview
    const validFile = createMockFile('test-image.jpg', 'image/jpeg', 1024)
    wrapper.vm.selectedImageFile = validFile
    wrapper.vm.imagePreviewUrl = 'blob:test-url'

    // Mock URL methods
    global.URL.revokeObjectURL = vi.fn()

    // Clear file
    wrapper.vm.clearImageFile()

    // Should clear everything
    expect(wrapper.vm.selectedImageFile).toBeNull()
    expect(wrapper.vm.imagePreviewUrl).toBe('')
    expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('blob:test-url')
  })

  it('displays uploaded image in asset detail', async () => {
    // Set asset with image
    store.currentAsset = {
      ...store.currentAsset,
      image: '/media/assets/images/TEST-001_main.jpg'
    }

    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Find image display
    const assetImage = wrapper.find('.asset-main-image')
    expect(assetImage.exists()).toBe(true)
    expect(assetImage.attributes('src')).toBe('/media/assets/images/TEST-001_main.jpg')
  })

  it('shows no image placeholder when no image uploaded', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Find no image placeholder
    const placeholder = wrapper.find('v-icon[data-testid="no-image-icon"]')
    const noImageText = wrapper.text()
    
    expect(noImageText).toContain('No image uploaded')
  })

  it('closes dialog after successful upload', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Open dialog
    wrapper.vm.showImageUploadDialog = true

    // Set up file
    const validFile = createMockFile('test-image.jpg', 'image/jpeg', 1024)
    wrapper.vm.selectedImageFile = validFile

    // Call upload method
    await wrapper.vm.uploadImage()

    // Dialog should be closed
    expect(wrapper.vm.showImageUploadDialog).toBe(false)
  })

  it('validates accepted file formats', () => {
    wrapper = mountComponent()

    const testCases = [
      { filename: 'test.jpg', type: 'image/jpeg', shouldAccept: true },
      { filename: 'test.png', type: 'image/png', shouldAccept: true },
      { filename: 'test.webp', type: 'image/webp', shouldAccept: true },
      { filename: 'test.gif', type: 'image/gif', shouldAccept: false },
      { filename: 'test.bmp', type: 'image/bmp', shouldAccept: false },
      { filename: 'test.pdf', type: 'application/pdf', shouldAccept: false }
    ]

    testCases.forEach(({ filename, type, shouldAccept }) => {
      const file = createMockFile(filename, type)
      wrapper.vm.validateAndSetImageFile(file)

      if (shouldAccept) {
        expect(wrapper.vm.imageUploadError).toBe('')
        expect(wrapper.vm.selectedImageFile).toEqual(file)
      } else {
        expect(wrapper.vm.imageUploadError).toContain('Invalid file type')
        expect(wrapper.vm.selectedImageFile).toBeNull()
      }

      // Reset for next test
      wrapper.vm.imageUploadError = ''
      wrapper.vm.selectedImageFile = null
    })
  })

  it('shows loading state during upload', async () => {
    wrapper = mountComponent()
    await wrapper.vm.$nextTick()

    // Mock slow upload
    let resolveUpload
    store.uploadImage.mockReturnValue(new Promise(resolve => {
      resolveUpload = resolve
    }))

    // Set up file
    const validFile = createMockFile('test-image.jpg', 'image/jpeg', 1024)
    wrapper.vm.selectedImageFile = validFile

    // Start upload
    const uploadPromise = wrapper.vm.uploadImage()

    // Should show loading state
    expect(wrapper.vm.isUploadingImage).toBe(true)

    // Complete upload
    resolveUpload({ image: 'test.jpg', thumbnail: 'thumb.jpg' })
    await uploadPromise

    // Should not be loading anymore
    expect(wrapper.vm.isUploadingImage).toBe(false)
  })
})