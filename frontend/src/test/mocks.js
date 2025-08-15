import { vi } from 'vitest'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

// Mock data
export const mockAssets = [
  {
    id: '123e4567-e89b-12d3-a456-426614174000',
    asset_id: 'TRUCK-001',
    vehicle_type: 'truck',
    make: 'Ford',
    model: 'F-150',
    year: 2022,
    vin: '1FTFW1ET5DFC10312',
    license_plate: 'ABC123',
    department: 'Operations',
    purchase_date: '2022-01-15',
    purchase_cost: '35000.00',
    current_odometer: 15000,
    status: 'active',
    notes: 'Primary fleet vehicle',
    created_at: '2022-01-15T10:00:00Z',
    updated_at: '2023-06-01T14:30:00Z',
    documents_count: 2
  },
  {
    id: '456e7890-e89b-12d3-a456-426614174001',
    asset_id: 'BUS-001',
    vehicle_type: 'bus',
    make: 'Mercedes',
    model: 'Sprinter',
    year: 2021,
    license_plate: 'XYZ789',
    department: 'Transportation',
    current_odometer: 25000,
    status: 'maintenance',
    created_at: '2021-08-10T09:00:00Z',
    updated_at: '2023-05-15T11:20:00Z',
    documents_count: 1
  }
]

export const mockAssetDetails = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  asset_id: 'TRUCK-001',
  vehicle_type: 'truck',
  make: 'Ford',
  model: 'F-150',
  year: 2022,
  vin: '1FTFW1ET5DFC10312',
  license_plate: 'ABC123',
  department: 'Operations',
  purchase_date: '2022-01-15',
  purchase_cost: '35000.00',
  current_odometer: 15000,
  status: 'active',
  notes: 'Primary fleet vehicle for operations department',
  created_at: '2022-01-15T10:00:00Z',
  updated_at: '2023-06-01T14:30:00Z',
  documents: [
    {
      id: 1,
      document_type: 'registration',
      title: 'Vehicle Registration',
      file: '/media/assets/documents/registration.pdf',
      description: 'Primary vehicle registration',
      uploaded_at: '2022-01-15T10:30:00Z'
    },
    {
      id: 2,
      document_type: 'insurance',
      title: 'Insurance Policy',
      file: '/media/assets/documents/insurance.pdf',
      description: 'Current insurance policy',
      uploaded_at: '2022-02-01T09:15:00Z'
    }
  ]
}

export const mockAssetStats = {
  total_assets: 25,
  active_assets: 20,
  maintenance_assets: 3,
  retired_assets: 2,
  vehicle_types: {
    'Truck': 8,
    'Bus': 5,
    'Van': 7,
    'Car': 3,
    'Equipment': 2
  }
}

// API request handlers
export const handlers = [
  // Assets list
  http.get('/api/assets/', ({ request }) => {
    const url = new URL(request.url)
    const search = url.searchParams.get('search')
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = 20
    
    let filteredAssets = [...mockAssets]
    
    if (search) {
      filteredAssets = mockAssets.filter(asset => 
        asset.asset_id.toLowerCase().includes(search.toLowerCase()) ||
        asset.make.toLowerCase().includes(search.toLowerCase()) ||
        asset.model.toLowerCase().includes(search.toLowerCase())
      )
    }
    
    const startIndex = (page - 1) * pageSize
    const endIndex = startIndex + pageSize
    const paginatedAssets = filteredAssets.slice(startIndex, endIndex)
    
    return HttpResponse.json({
      count: filteredAssets.length,
      next: endIndex < filteredAssets.length ? `/api/assets/?page=${page + 1}` : null,
      previous: page > 1 ? `/api/assets/?page=${page - 1}` : null,
      results: paginatedAssets
    })
  }),

  // Asset detail
  http.get('/api/assets/:id/', ({ params }) => {
    if (params.id === mockAssetDetails.id) {
      return HttpResponse.json(mockAssetDetails)
    }
    return new HttpResponse(null, { status: 404 })
  }),

  // Create asset
  http.post('/api/assets/', async ({ request }) => {
    const newAsset = await request.json()
    return HttpResponse.json({
      ...newAsset,
      id: crypto.randomUUID(),
      asset_id: newAsset.asset_id || 'AUTO-001',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      documents: []
    }, { status: 201 })
  }),

  // Update asset
  http.put('/api/assets/:id/', async ({ params, request }) => {
    const updatedAsset = await request.json()
    return HttpResponse.json({
      ...mockAssetDetails,
      ...updatedAsset,
      id: params.id,
      updated_at: new Date().toISOString()
    })
  }),

  // Delete asset
  http.delete('/api/assets/:id/', () => {
    return new HttpResponse(null, { status: 204 })
  }),

  // Asset statistics
  http.get('/api/assets/stats/', () => {
    return HttpResponse.json(mockAssetStats)
  }),

  // Asset documents
  http.get('/api/assets/:id/documents/', ({ params }) => {
    if (params.id === mockAssetDetails.id) {
      return HttpResponse.json(mockAssetDetails.documents)
    }
    return HttpResponse.json([])
  }),

  // Upload document
  http.post('/api/assets/:id/upload_document/', async ({ params, request }) => {
    const formData = await request.formData()
    const title = formData.get('title')
    const documentType = formData.get('document_type')
    
    return HttpResponse.json({
      id: Date.now(),
      document_type: documentType,
      title: title,
      file: '/media/assets/documents/uploaded_file.pdf',
      description: formData.get('description') || '',
      uploaded_at: new Date().toISOString()
    }, { status: 201 })
  }),

  // Authentication endpoints
  http.post('/api/auth/login/', async ({ request }) => {
    const credentials = await request.json()
    if (credentials.username === 'testuser' && credentials.password === 'testpass') {
      return HttpResponse.json({
        token: 'mock-token',
        user: { id: 1, username: 'testuser', email: 'test@example.com' }
      })
    }
    return new HttpResponse(null, { status: 401 })
  }),

  http.get('/api/auth/user/', () => {
    return HttpResponse.json({
      id: 1,
      username: 'testuser',
      email: 'test@example.com'
    })
  }),

  http.post('/api/auth/logout/', () => {
    return new HttpResponse(null, { status: 200 })
  })
]

// Create test server
export const server = setupServer(...handlers)

// Mock localStorage
export const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

// Mock API service
export const mockAPI = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
}

export const mockAssetsAPI = {
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