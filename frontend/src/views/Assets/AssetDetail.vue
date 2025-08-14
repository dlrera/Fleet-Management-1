<template>
  <div class="asset-detail" v-if="!loading">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/assets">Assets</router-link>
            </li>
            <li class="breadcrumb-item active">{{ asset.asset_number }}</li>
          </ol>
        </nav>
        <h1 class="mb-1">{{ asset.make }} {{ asset.model }} {{ asset.year }}</h1>
        <p class="text-muted mb-0">Asset #{{ asset.asset_number }}</p>
      </div>
      <div class="d-flex gap-2">
        <router-link :to="`/assets/${asset.asset_id}/edit`" class="btn btn-primary">
          <i class="bi bi-pencil me-2"></i>Edit Asset
        </router-link>
        <div class="dropdown">
          <button class="btn btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
            Actions
          </button>
          <ul class="dropdown-menu">
            <li>
              <button @click="createWorkOrder" class="dropdown-item">
                <i class="bi bi-wrench me-2"></i>Create Work Order
              </button>
            </li>
            <li>
              <button @click="scheduleMaintenance" class="dropdown-item">
                <i class="bi bi-calendar-plus me-2"></i>Schedule Maintenance
              </button>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <router-link :to="`/tracking/asset/${asset.asset_id}`" class="dropdown-item">
                <i class="bi bi-geo-alt me-2"></i>View on Map
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Status and Key Metrics -->
    <div class="row g-4 mb-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-3 text-center">
                <h6 class="text-muted mb-1">Status</h6>
                <span class="badge fs-6 px-3 py-2" :class="getStatusClass(asset.status)">
                  {{ formatStatus(asset.status) }}
                </span>
              </div>
              <div class="col-md-3 text-center">
                <h6 class="text-muted mb-1">Current Mileage</h6>
                <h5 class="mb-0">
                  {{ asset.current_odometer_reading ? asset.current_odometer_reading.toLocaleString() : 'N/A' }}
                  <small class="text-muted">miles</small>
                </h5>
              </div>
              <div class="col-md-3 text-center">
                <h6 class="text-muted mb-1">Engine Hours</h6>
                <h5 class="mb-0">
                  {{ asset.engine_hours ? asset.engine_hours.toLocaleString() : 'N/A' }}
                  <small class="text-muted">hrs</small>
                </h5>
              </div>
              <div class="col-md-3 text-center">
                <h6 class="text-muted mb-1">Department</h6>
                <h5 class="mb-0">{{ asset.department?.name || 'Unassigned' }}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-light">
          <div class="card-body">
            <h6 class="card-title">Next Maintenance Due</h6>
            <div v-if="nextMaintenance">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <strong>{{ nextMaintenance.maintenance_type_name }}</strong>
                  <div class="small text-muted">
                    Due: {{ formatDate(nextMaintenance.next_due_date) }}
                  </div>
                </div>
                <span class="badge" :class="getMaintenanceStatusClass(nextMaintenance.is_overdue)">
                  {{ nextMaintenance.is_overdue ? 'Overdue' : 'Upcoming' }}
                </span>
              </div>
            </div>
            <div v-else class="text-muted">
              No scheduled maintenance
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <div class="card">
      <div class="card-header">
        <ul class="nav nav-tabs card-header-tabs" role="tablist">
          <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#overview-tab">
              <i class="bi bi-info-circle me-2"></i>Overview
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#maintenance-tab">
              <i class="bi bi-tools me-2"></i>Maintenance
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#workorders-tab">
              <i class="bi bi-clipboard-check me-2"></i>Work Orders
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#documents-tab">
              <i class="bi bi-file-text me-2"></i>Documents
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#location-tab">
              <i class="bi bi-geo-alt me-2"></i>Location History
            </button>
          </li>
        </ul>
      </div>
      <div class="card-body">
        <div class="tab-content">
          <!-- Overview Tab -->
          <div class="tab-pane fade show active" id="overview-tab">
            <div class="row">
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Basic Information</h6>
                <table class="table table-borderless">
                  <tr>
                    <td class="text-muted">Asset Number:</td>
                    <td class="fw-bold">{{ asset.asset_number }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Vehicle Type:</td>
                    <td>{{ formatAssetType(asset.vehicle_type) }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Make/Model/Year:</td>
                    <td>{{ asset.make }} {{ asset.model }} {{ asset.year }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">VIN:</td>
                    <td>{{ asset.vin_number || 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">License Plate:</td>
                    <td>{{ asset.license_plate || 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Color:</td>
                    <td>{{ asset.color || 'N/A' }}</td>
                  </tr>
                </table>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Operational Details</h6>
                <table class="table table-borderless">
                  <tr>
                    <td class="text-muted">Department:</td>
                    <td>{{ asset.department?.name || 'Unassigned' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Current Mileage:</td>
                    <td>{{ asset.current_odometer_reading ? asset.current_odometer_reading.toLocaleString() : 'N/A' }} miles</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Engine Hours:</td>
                    <td>{{ asset.engine_hours ? asset.engine_hours.toLocaleString() : 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Fuel Type:</td>
                    <td>{{ asset.fuel_type || 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Purchase Date:</td>
                    <td>{{ asset.purchase_date ? formatDate(asset.purchase_date) : 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Purchase Cost:</td>
                    <td>{{ asset.purchase_cost ? '$' + asset.purchase_cost.toLocaleString() : 'N/A' }}</td>
                  </tr>
                </table>
              </div>
            </div>
            
            <div v-if="asset.notes" class="mt-4">
              <h6 class="fw-bold mb-3">Notes</h6>
              <div class="p-3 bg-light rounded">
                {{ asset.notes }}
              </div>
            </div>
          </div>

          <!-- Maintenance Tab -->
          <div class="tab-pane fade" id="maintenance-tab">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="mb-0">Maintenance History</h6>
              <button @click="scheduleMaintenance" class="btn btn-sm btn-primary">
                <i class="bi bi-plus-circle me-2"></i>Schedule Maintenance
              </button>
            </div>
            
            <div v-if="maintenanceRecords.length === 0" class="text-center py-4">
              <i class="bi bi-tools fs-1 text-muted opacity-50"></i>
              <p class="text-muted mt-2">No maintenance records found</p>
            </div>
            
            <div v-else class="timeline">
              <div v-for="record in maintenanceRecords" :key="record.record_id" class="timeline-item">
                <div class="timeline-marker" :class="getMaintenanceTypeClass(record.maintenance_type)"></div>
                <div class="timeline-content">
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 class="mb-1">{{ record.maintenance_type_name }}</h6>
                      <p class="text-muted small mb-1">{{ formatDate(record.completed_date) }}</p>
                      <p class="mb-1">{{ record.description }}</p>
                      <div class="small">
                        <span class="text-muted me-3">
                          <i class="bi bi-speedometer2 me-1"></i>
                          {{ record.mileage_at_service?.toLocaleString() }} miles
                        </span>
                        <span class="text-muted">
                          <i class="bi bi-currency-dollar me-1"></i>
                          ${{ record.cost?.toLocaleString() || '0' }}
                        </span>
                      </div>
                    </div>
                    <span class="badge" :class="getMaintenanceStatusClass(record.status === 'completed')">
                      {{ record.status }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Work Orders Tab -->
          <div class="tab-pane fade" id="workorders-tab">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="mb-0">Work Orders</h6>
              <button @click="createWorkOrder" class="btn btn-sm btn-primary">
                <i class="bi bi-plus-circle me-2"></i>Create Work Order
              </button>
            </div>
            
            <div v-if="workOrders.length === 0" class="text-center py-4">
              <i class="bi bi-clipboard-x fs-1 text-muted opacity-50"></i>
              <p class="text-muted mt-2">No work orders found</p>
            </div>
            
            <div v-else class="list-group list-group-flush">
              <div v-for="wo in workOrders" :key="wo.work_order_id" class="list-group-item px-0">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <div class="d-flex align-items-center mb-2">
                      <span class="badge me-2" :class="getWorkOrderStatusClass(wo.status)">
                        {{ wo.status }}
                      </span>
                      <h6 class="mb-0">{{ wo.work_order_number }}</h6>
                    </div>
                    <p class="mb-1">{{ wo.title }}</p>
                    <div class="small text-muted">
                      <span class="me-3">
                        <i class="bi bi-calendar3 me-1"></i>
                        Created: {{ formatDate(wo.created_at) }}
                      </span>
                      <span v-if="wo.due_date" class="me-3">
                        <i class="bi bi-clock me-1"></i>
                        Due: {{ formatDate(wo.due_date) }}
                      </span>
                      <span v-if="wo.assigned_to">
                        <i class="bi bi-person me-1"></i>
                        {{ wo.assigned_to.first_name }} {{ wo.assigned_to.last_name }}
                      </span>
                    </div>
                  </div>
                  <router-link :to="`/work-orders/${wo.work_order_id}`" class="btn btn-sm btn-outline-primary">
                    View
                  </router-link>
                </div>
              </div>
            </div>
          </div>

          <!-- Documents Tab -->
          <div class="tab-pane fade" id="documents-tab">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="mb-0">Documents & Images</h6>
              <button @click="uploadDocument" class="btn btn-sm btn-primary">
                <i class="bi bi-upload me-2"></i>Upload Document
              </button>
            </div>
            
            <div class="row">
              <div class="col-md-6">
                <h6>Documents</h6>
                <div v-if="documents.length === 0" class="text-center py-3 border rounded">
                  <i class="bi bi-file-text fs-3 text-muted opacity-50"></i>
                  <p class="text-muted mt-2 small">No documents uploaded</p>
                </div>
                <div v-else class="list-group">
                  <div v-for="doc in documents" :key="doc.document_id" class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <div class="fw-bold">{{ doc.document_name }}</div>
                        <small class="text-muted">{{ doc.document_type }}</small>
                      </div>
                      <div>
                        <a :href="doc.document_file" target="_blank" class="btn btn-sm btn-outline-primary me-2">
                          <i class="bi bi-download"></i>
                        </a>
                        <button @click="deleteDocument(doc)" class="btn btn-sm btn-outline-danger">
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <h6>Images</h6>
                <div v-if="images.length === 0" class="text-center py-3 border rounded">
                  <i class="bi bi-image fs-3 text-muted opacity-50"></i>
                  <p class="text-muted mt-2 small">No images uploaded</p>
                </div>
                <div v-else class="row g-2">
                  <div v-for="img in images" :key="img.image_id" class="col-6">
                    <div class="card">
                      <img :src="img.image_file" class="card-img-top" style="height: 150px; object-fit: cover;">
                      <div class="card-body p-2">
                        <p class="card-text small mb-1">{{ img.image_name }}</p>
                        <button @click="deleteImage(img)" class="btn btn-sm btn-outline-danger">
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Location History Tab -->
          <div class="tab-pane fade" id="location-tab">
            <h6 class="mb-3">Recent Locations</h6>
            
            <div v-if="locationHistory.length === 0" class="text-center py-4">
              <i class="bi bi-geo-alt fs-1 text-muted opacity-50"></i>
              <p class="text-muted mt-2">No location data available</p>
            </div>
            
            <div v-else class="list-group">
              <div v-for="location in locationHistory" :key="location.point_id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <h6 class="mb-1">{{ location.address || 'Unknown Address' }}</h6>
                    <p class="mb-1 text-muted small">
                      Lat: {{ location.latitude.toFixed(6) }}, Lng: {{ location.longitude.toFixed(6) }}
                    </p>
                    <small class="text-muted">{{ formatDateTime(location.timestamp) }}</small>
                  </div>
                  <div class="text-end">
                    <div v-if="location.speed" class="small">
                      <i class="bi bi-speedometer2 me-1"></i>
                      {{ Math.round(location.speed) }} mph
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Loading State -->
  <div v-else class="text-center py-5">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { assetsAPI, maintenanceAPI, workOrdersAPI, trackingAPI } from '@/services/api'
import { toast } from '@/utils/toast'

export default {
  name: 'AssetDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const assetId = route.params.id
    
    const loading = ref(true)
    const asset = ref({})
    const nextMaintenance = ref(null)
    const maintenanceRecords = ref([])
    const workOrders = ref([])
    const documents = ref([])
    const images = ref([])
    const locationHistory = ref([])

    const loadAssetDetail = async () => {
      try {
        const response = await assetsAPI.getAsset(assetId)
        asset.value = response.data
      } catch (error) {
        console.error('Error loading asset:', error)
        toast.error('Failed to load asset details')
        router.push('/assets')
      }
    }

    const loadMaintenanceData = async () => {
      try {
        const [recordsRes, schedulesRes] = await Promise.allSettled([
          maintenanceAPI.getMaintenanceRecords({ asset_id: assetId }),
          maintenanceAPI.getMaintenanceSchedules({ asset_id: assetId })
        ])
        
        if (recordsRes.status === 'fulfilled') {
          maintenanceRecords.value = recordsRes.value.data.results || []
        }
        
        if (schedulesRes.status === 'fulfilled') {
          const schedules = schedulesRes.value.data.results || []
          nextMaintenance.value = schedules.find(s => s.next_due_date) || null
        }
      } catch (error) {
        console.error('Error loading maintenance data:', error)
      }
    }

    const loadWorkOrders = async () => {
      try {
        const response = await workOrdersAPI.getWorkOrders({ asset_id: assetId })
        workOrders.value = response.data.results || []
      } catch (error) {
        console.error('Error loading work orders:', error)
      }
    }

    const loadDocuments = async () => {
      try {
        const [docsRes, imagesRes] = await Promise.allSettled([
          assetsAPI.getAssetDocuments(assetId),
          assetsAPI.getAssetImages(assetId)
        ])
        
        if (docsRes.status === 'fulfilled') {
          documents.value = docsRes.value.data.results || []
        }
        
        if (imagesRes.status === 'fulfilled') {
          images.value = imagesRes.value.data.results || []
        }
      } catch (error) {
        console.error('Error loading documents:', error)
      }
    }

    const loadLocationHistory = async () => {
      try {
        const response = await trackingAPI.getLocationHistory({ asset_id: assetId, limit: 10 })
        locationHistory.value = response.data.results || []
      } catch (error) {
        console.error('Error loading location history:', error)
      }
    }

    const createWorkOrder = () => {
      router.push({
        path: '/work-orders/create',
        query: { asset_id: assetId }
      })
    }

    const scheduleMaintenance = () => {
      router.push({
        path: '/maintenance/schedule',
        query: { asset_id: assetId }
      })
    }

    const uploadDocument = () => {
      // TODO: Implement document upload modal
      toast.info('Document upload feature coming soon')
    }

    const deleteDocument = async (doc) => {
      if (confirm('Are you sure you want to delete this document?')) {
        try {
          await assetsAPI.deleteAssetDocument(assetId, doc.document_id)
          documents.value = documents.value.filter(d => d.document_id !== doc.document_id)
          toast.success('Document deleted successfully')
        } catch (error) {
          toast.error('Failed to delete document')
        }
      }
    }

    const deleteImage = async (img) => {
      if (confirm('Are you sure you want to delete this image?')) {
        try {
          await assetsAPI.deleteAssetImage(assetId, img.image_id)
          images.value = images.value.filter(i => i.image_id !== img.image_id)
          toast.success('Image deleted successfully')
        } catch (error) {
          toast.error('Failed to delete image')
        }
      }
    }

    const getStatusClass = (status) => {
      const statusClasses = {
        'active': 'bg-success',
        'inactive': 'bg-secondary',
        'maintenance': 'bg-warning',
        'retired': 'bg-dark'
      }
      return statusClasses[status] || 'bg-secondary'
    }

    const formatStatus = (status) => {
      return status.charAt(0).toUpperCase() + status.slice(1)
    }

    const formatAssetType = (type) => {
      return type.charAt(0).toUpperCase() + type.slice(1)
    }

    const getMaintenanceStatusClass = (isOverdue) => {
      return isOverdue ? 'bg-danger' : 'bg-success'
    }

    const getMaintenanceTypeClass = (type) => {
      const typeClasses = {
        'preventive': 'bg-primary',
        'corrective': 'bg-warning',
        'emergency': 'bg-danger'
      }
      return typeClasses[type] || 'bg-primary'
    }

    const getWorkOrderStatusClass = (status) => {
      const statusClasses = {
        'open': 'bg-secondary',
        'assigned': 'bg-info',
        'in_progress': 'bg-primary',
        'on_hold': 'bg-warning',
        'completed': 'bg-success',
        'cancelled': 'bg-dark',
        'closed': 'bg-dark'
      }
      return statusClasses[status] || 'bg-secondary'
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(async () => {
      loading.value = true
      try {
        await Promise.all([
          loadAssetDetail(),
          loadMaintenanceData(),
          loadWorkOrders(),
          loadDocuments(),
          loadLocationHistory()
        ])
      } finally {
        loading.value = false
      }
    })

    return {
      loading,
      asset,
      nextMaintenance,
      maintenanceRecords,
      workOrders,
      documents,
      images,
      locationHistory,
      createWorkOrder,
      scheduleMaintenance,
      uploadDocument,
      deleteDocument,
      deleteImage,
      getStatusClass,
      formatStatus,
      formatAssetType,
      getMaintenanceStatusClass,
      getMaintenanceTypeClass,
      getWorkOrderStatusClass,
      formatDate,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 1rem;
  top: 0;
  height: 100%;
  width: 2px;
  background-color: #dee2e6;
}

.timeline-item {
  position: relative;
  margin-bottom: 2rem;
}

.timeline-marker {
  position: absolute;
  left: -2rem;
  top: 0.25rem;
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #dee2e6;
}

.timeline-content {
  background: #f8f9fa;
  border-radius: 0.375rem;
  padding: 1rem;
  border-left: 3px solid #007bff;
}

.nav-tabs .nav-link {
  color: #6c757d;
  border: none;
  border-bottom: 2px solid transparent;
}

.nav-tabs .nav-link.active {
  color: #007bff;
  border-bottom-color: #007bff;
  background: none;
}

.card-img-top {
  cursor: pointer;
  transition: transform 0.2s;
}

.card-img-top:hover {
  transform: scale(1.05);
}
</style>