import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAssetsStore } from './assets'
import * as api from '@/services/api'

// Mock the API module
vi.mock('@/services/api', () => ({
  assetsAPI: {
    bulkImport: vi.fn(),
    downloadTemplate: vi.fn(),
    uploadDocument: vi.fn(),
    getAssetDocuments: vi.fn(),
    fetchAssets: vi.fn(),
    getStats: vi.fn()
  }
}))

describe('Assets Store - Bulk Import & Document Upload', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useAssetsStore()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('bulkImportAssets', () => {
    it('should successfully import assets', async () => {
      const mockFormData = new FormData()
      mockFormData.append('file', new Blob(['csv content']))
      
      const mockResponse = {
        data: {
          success_count: 5,
          error_count: 0,
          total_rows: 5
        }
      }

      api.assetsAPI.bulkImport.mockResolvedValue(mockResponse)
      api.assetsAPI.fetchAssets = vi.fn().mockResolvedValue({ data: { results: [] } })

      const result = await store.bulkImportAssets(mockFormData)

      expect(api.assetsAPI.bulkImport).toHaveBeenCalledWith(mockFormData)
      expect(result).toEqual(mockResponse.data)
      expect(result.success_count).toBe(5)
      expect(result.error_count).toBe(0)
    })

    it('should handle import with errors', async () => {
      const mockFormData = new FormData()
      const mockResponse = {
        data: {
          success_count: 3,
          error_count: 2,
          total_rows: 5,
          errors: [
            { row: 2, asset_id: 'TEST-001', error: 'Invalid vehicle type' },
            { row: 4, asset_id: 'TEST-002', error: 'Duplicate asset ID' }
          ]
        }
      }

      api.assetsAPI.bulkImport.mockResolvedValue(mockResponse)

      const result = await store.bulkImportAssets(mockFormData)

      expect(result.success_count).toBe(3)
      expect(result.error_count).toBe(2)
      expect(result.errors).toHaveLength(2)
      expect(result.errors[0].error).toContain('Invalid vehicle type')
    })

    it('should handle import failure', async () => {
      const mockFormData = new FormData()
      const mockError = new Error('Network error')

      api.assetsAPI.bulkImport.mockRejectedValue(mockError)

      await expect(store.bulkImportAssets(mockFormData)).rejects.toThrow('Network error')
      expect(api.assetsAPI.bulkImport).toHaveBeenCalledWith(mockFormData)
    })

    it('should refresh assets after successful import', async () => {
      const mockFormData = new FormData()
      const mockResponse = {
        data: {
          success_count: 1,
          error_count: 0,
          total_rows: 1
        }
      }

      api.assetsAPI.bulkImport.mockResolvedValue(mockResponse)
      
      // Mock fetchAssets as a store method
      store.fetchAssets = vi.fn().mockResolvedValue()

      await store.bulkImportAssets(mockFormData)

      expect(store.fetchAssets).toHaveBeenCalled()
    })
  })

  describe('downloadCSVTemplate', () => {
    it('should successfully download CSV template', async () => {
      const mockCSVContent = 'asset_id,vehicle_type,make,model,year\nTEST-001,bus,Blue Bird,Vision,2023'
      const mockResponse = {
        data: mockCSVContent
      }

      api.assetsAPI.downloadTemplate.mockResolvedValue(mockResponse)

      const result = await store.downloadCSVTemplate()

      expect(api.assetsAPI.downloadTemplate).toHaveBeenCalled()
      expect(result.data).toBe(mockCSVContent)
      expect(result.data).toContain('asset_id')
    })

    it('should handle template download failure', async () => {
      const mockError = new Error('Download failed')

      api.assetsAPI.downloadTemplate.mockRejectedValue(mockError)

      await expect(store.downloadCSVTemplate()).rejects.toThrow('Download failed')
      expect(api.assetsAPI.downloadTemplate).toHaveBeenCalled()
    })
  })

  describe('uploadDocument', () => {
    it('should successfully upload a document', async () => {
      const assetId = 'test-asset-id'
      const mockFormData = new FormData()
      mockFormData.append('file', new Blob(['file content']))
      mockFormData.append('document_type', 'registration')
      mockFormData.append('title', 'Vehicle Registration')

      const mockDocument = {
        id: 'doc-123',
        asset: assetId,
        document_type: 'registration',
        title: 'Vehicle Registration',
        file: '/media/documents/registration.pdf',
        uploaded_at: '2023-08-16T12:00:00Z'
      }

      api.assetsAPI.uploadDocument.mockResolvedValue({ data: mockDocument })

      const result = await store.uploadDocument(assetId, mockFormData)

      expect(api.assetsAPI.uploadDocument).toHaveBeenCalledWith(assetId, mockFormData)
      expect(result).toEqual(mockDocument)
      expect(store.assetDocuments).toContain(mockDocument)
    })

    it('should update current asset documents after upload', async () => {
      const assetId = 'test-asset-id'
      store.currentAsset = { id: assetId, documents: [] }
      
      const mockFormData = new FormData()
      const mockDocument = {
        id: 'doc-456',
        title: 'Insurance Certificate'
      }

      api.assetsAPI.uploadDocument.mockResolvedValue({ data: mockDocument })

      await store.uploadDocument(assetId, mockFormData)

      expect(store.currentAsset.documents).toContain(mockDocument)
    })

    it('should update document count in assets list', async () => {
      const assetId = 'test-asset-id'
      store.assets = [
        { id: assetId, documents_count: 2 },
        { id: 'other-id', documents_count: 0 }
      ]

      const mockFormData = new FormData()
      const mockDocument = { id: 'doc-789' }

      api.assetsAPI.uploadDocument.mockResolvedValue({ data: mockDocument })

      await store.uploadDocument(assetId, mockFormData)

      expect(store.assets[0].documents_count).toBe(3)
      expect(store.assets[1].documents_count).toBe(0)
    })

    it('should handle upload failure', async () => {
      const assetId = 'test-asset-id'
      const mockFormData = new FormData()
      const mockError = {
        response: {
          data: 'File size exceeds limit'
        }
      }

      api.assetsAPI.uploadDocument.mockRejectedValue(mockError)

      await expect(store.uploadDocument(assetId, mockFormData)).rejects.toEqual(mockError)
      expect(store.documentError).toBe('File size exceeds limit')
    })

    it('should set and clear loading state', async () => {
      const assetId = 'test-asset-id'
      const mockFormData = new FormData()

      api.assetsAPI.uploadDocument.mockImplementation(() => {
        expect(store.isUploadingDocument).toBe(true)
        return Promise.resolve({ data: {} })
      })

      await store.uploadDocument(assetId, mockFormData)

      expect(store.isUploadingDocument).toBe(false)
    })
  })

  describe('fetchAssetDocuments', () => {
    it('should fetch documents for an asset', async () => {
      const assetId = 'test-asset-id'
      const mockDocuments = [
        { id: 'doc-1', title: 'Registration' },
        { id: 'doc-2', title: 'Insurance' },
        { id: 'doc-3', title: 'Manual' }
      ]

      api.assetsAPI.getAssetDocuments.mockResolvedValue({ data: mockDocuments })

      await store.fetchAssetDocuments(assetId)

      expect(api.assetsAPI.getAssetDocuments).toHaveBeenCalledWith(assetId)
      expect(store.assetDocuments).toEqual(mockDocuments)
      expect(store.assetDocuments).toHaveLength(3)
    })

    it('should handle empty documents list', async () => {
      const assetId = 'test-asset-id'

      api.assetsAPI.getAssetDocuments.mockResolvedValue({ data: [] })

      await store.fetchAssetDocuments(assetId)

      expect(store.assetDocuments).toEqual([])
      expect(store.assetDocuments).toHaveLength(0)
    })

    it('should handle fetch error silently', async () => {
      const assetId = 'test-asset-id'
      const mockError = new Error('Network error')

      api.assetsAPI.getAssetDocuments.mockRejectedValue(mockError)

      await store.fetchAssetDocuments(assetId)

      // Should fail silently without throwing
      expect(store.assetDocuments).toEqual([])
    })
  })
})

describe('CSV Import File Validation', () => {
  it('should validate CSV file type', () => {
    const validateCSVFile = (file) => {
      if (!file.name.endsWith('.csv')) {
        return { valid: false, error: 'File must be in CSV format' }
      }
      return { valid: true }
    }

    const csvFile = new File(['content'], 'test.csv', { type: 'text/csv' })
    const txtFile = new File(['content'], 'test.txt', { type: 'text/plain' })

    expect(validateCSVFile(csvFile).valid).toBe(true)
    expect(validateCSVFile(txtFile).valid).toBe(false)
    expect(validateCSVFile(txtFile).error).toBe('File must be in CSV format')
  })

  it('should validate file size limit', () => {
    const validateFileSize = (file, maxSize = 5242880) => {
      if (file.size > maxSize) {
        return { valid: false, error: 'File size must be less than 5MB' }
      }
      return { valid: true }
    }

    const smallFile = new File(['a'.repeat(1000)], 'small.csv')
    const largeFile = new File(['a'.repeat(6000000)], 'large.csv')

    expect(validateFileSize(smallFile).valid).toBe(true)
    expect(validateFileSize(largeFile).valid).toBe(false)
    expect(validateFileSize(largeFile).error).toBe('File size must be less than 5MB')
  })
})

describe('Document Upload File Validation', () => {
  it('should validate document file types', () => {
    const allowedTypes = [
      'application/pdf',
      'image/jpeg',
      'image/jpg',
      'image/png',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]

    const validateDocumentType = (file) => {
      if (!allowedTypes.includes(file.type)) {
        return { valid: false, error: 'Invalid file type' }
      }
      return { valid: true }
    }

    const pdfFile = new File(['content'], 'doc.pdf', { type: 'application/pdf' })
    const jpgFile = new File(['content'], 'image.jpg', { type: 'image/jpeg' })
    const exeFile = new File(['content'], 'app.exe', { type: 'application/x-msdownload' })

    expect(validateDocumentType(pdfFile).valid).toBe(true)
    expect(validateDocumentType(jpgFile).valid).toBe(true)
    expect(validateDocumentType(exeFile).valid).toBe(false)
  })

  it('should validate document file size', () => {
    const validateDocumentSize = (file, maxSize = 10485760) => {
      if (file.size > maxSize) {
        return { valid: false, error: 'File size must be less than 10MB' }
      }
      return { valid: true }
    }

    const smallFile = new File(['a'.repeat(5000000)], 'doc.pdf')
    const largeFile = new File(['a'.repeat(11000000)], 'large.pdf')

    expect(validateDocumentSize(smallFile).valid).toBe(true)
    expect(validateDocumentSize(largeFile).valid).toBe(false)
    expect(validateDocumentSize(largeFile).error).toBe('File size must be less than 10MB')
  })
})