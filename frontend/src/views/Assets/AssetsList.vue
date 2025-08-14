<template>
  <div class="assets-list">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="mb-1">Fleet Assets</h1>
        <p class="text-muted mb-0">Manage your fleet vehicles and equipment</p>
      </div>
      <router-link to="/assets/create" class="btn btn-primary">
        <i class="bi bi-plus-circle me-2"></i>Add Asset
      </router-link>
    </div>

    <!-- Filters and Search -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Search</label>
            <div class="input-group">
              <span class="input-group-text">
                <i class="bi bi-search"></i>
              </span>
              <input 
                v-model="filters.search" 
                type="text" 
                class="form-control" 
                placeholder="Asset number, VIN, license plate..."
                @input="debounceSearch"
              >
            </div>
          </div>
          <div class="col-md-2">
            <label class="form-label">Department</label>
            <select v-model="filters.department" class="form-select" @change="loadAssets">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept.department_id" :value="dept.department_id">
                {{ dept.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Asset Type</label>
            <select v-model="filters.asset_type" class="form-select" @change="loadAssets">
              <option value="">All Types</option>
              <option value="vehicle">Vehicle</option>
              <option value="equipment">Equipment</option>
              <option value="trailer">Trailer</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Status</label>
            <select v-model="filters.status" class="form-select" @change="loadAssets">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="maintenance">In Maintenance</option>
              <option value="retired">Retired</option>
            </select>
          </div>
          <div class="col-md-2">
            <button @click="clearFilters" class="btn btn-outline-secondary mt-4">
              <i class="bi bi-x-circle me-2"></i>Clear
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ statistics.total_assets || 0 }}</h3>
            <small>Total Assets</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ statistics.active_assets || 0 }}</h3>
            <small>Active Assets</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ statistics.maintenance_assets || 0 }}</h3>
            <small>In Maintenance</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ Math.round(statistics.avg_utilization || 0) }}%</h3>
            <small>Avg Utilization</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Assets Table -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Assets</h5>
        <div class="d-flex align-items-center gap-3">
          <span class="text-muted">{{ pagination.count || 0 }} assets</span>
          <div class="btn-group btn-group-sm" role="group">
            <button 
              type="button" 
              class="btn" 
              :class="viewMode === 'table' ? 'btn-primary' : 'btn-outline-primary'"
              @click="viewMode = 'table'"
            >
              <i class="bi bi-list"></i>
            </button>
            <button 
              type="button" 
              class="btn" 
              :class="viewMode === 'grid' ? 'btn-primary' : 'btn-outline-primary'"
              @click="viewMode = 'grid'"
            >
              <i class="bi bi-grid"></i>
            </button>
          </div>
        </div>
      </div>
      <div class="card-body p-0">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="assets.length === 0" class="text-center py-5">
          <i class="bi bi-truck fs-1 text-muted opacity-50"></i>
          <h5 class="mt-3 text-muted">No assets found</h5>
          <p class="text-muted">
            {{ hasFilters ? 'Try adjusting your filters or search terms' : 'Get started by adding your first asset' }}
          </p>
          <router-link v-if="!hasFilters" to="/assets/create" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>Add First Asset
          </router-link>
        </div>

        <!-- Table View -->
        <div v-else-if="viewMode === 'table'" class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th @click="setSortBy('asset_number')" class="sortable">
                  Asset Number 
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th>Details</th>
                <th @click="setSortBy('department__name')" class="sortable">
                  Department
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th @click="setSortBy('status')" class="sortable">
                  Status
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th @click="setSortBy('current_mileage')" class="sortable">
                  Mileage
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th>Last Maintenance</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="asset in assets" :key="asset.asset_id" @click="viewAsset(asset.asset_id)">
                <td>
                  <div class="fw-bold">{{ asset.asset_number }}</div>
                  <small class="text-muted">{{ asset.vin || 'No VIN' }}</small>
                </td>
                <td>
                  <div>{{ asset.make }} {{ asset.model }}</div>
                  <small class="text-muted">{{ asset.year }} • {{ asset.asset_type }}</small>
                </td>
                <td>
                  <span class="badge bg-light text-dark">{{ asset.department?.name || 'Unassigned' }}</span>
                </td>
                <td>
                  <span class="badge" :class="getStatusClass(asset.status)">
                    {{ formatStatus(asset.status) }}
                  </span>
                </td>
                <td>
                  <div v-if="asset.current_mileage">
                    {{ asset.current_mileage.toLocaleString() }} {{ asset.mileage_unit }}
                  </div>
                  <span v-else class="text-muted">N/A</span>
                </td>
                <td>
                  <div v-if="asset.last_maintenance_date">
                    {{ formatDate(asset.last_maintenance_date) }}
                  </div>
                  <span v-else class="text-muted">Never</span>
                </td>
                <td @click.stop>
                  <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                            data-bs-toggle="dropdown">
                      Actions
                    </button>
                    <ul class="dropdown-menu">
                      <li>
                        <router-link :to="`/assets/${asset.asset_id}`" class="dropdown-item">
                          <i class="bi bi-eye me-2"></i>View Details
                        </router-link>
                      </li>
                      <li>
                        <router-link :to="`/assets/${asset.asset_id}/edit`" class="dropdown-item">
                          <i class="bi bi-pencil me-2"></i>Edit
                        </router-link>
                      </li>
                      <li><hr class="dropdown-divider"></li>
                      <li>
                        <button @click="createWorkOrder(asset)" class="dropdown-item">
                          <i class="bi bi-wrench me-2"></i>Create Work Order
                        </button>
                      </li>
                      <li>
                        <button @click="schedulemaintenance(asset)" class="dropdown-item">
                          <i class="bi bi-calendar-plus me-2"></i>Schedule Maintenance
                        </button>
                      </li>
                    </ul>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Grid View -->
        <div v-else class="row g-3 p-3">
          <div v-for="asset in assets" :key="asset.asset_id" class="col-md-6 col-xl-4">
            <div class="card asset-card h-100" @click="viewAsset(asset.asset_id)">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="card-title mb-0">{{ asset.asset_number }}</h6>
                  <span class="badge" :class="getStatusClass(asset.status)">
                    {{ formatStatus(asset.status) }}
                  </span>
                </div>
                <p class="card-text text-muted mb-2">
                  {{ asset.make }} {{ asset.model }} {{ asset.year }}
                </p>
                <div class="row text-center mb-2">
                  <div class="col-6">
                    <small class="text-muted">Mileage</small>
                    <div class="fw-bold">
                      {{ asset.current_odometer_reading ? asset.current_odometer_reading.toLocaleString() : 'N/A' }}
                    </div>
                  </div>
                  <div class="col-6">
                    <small class="text-muted">Department</small>
                    <div class="fw-bold">{{ asset.department?.name || 'Unassigned' }}</div>
                  </div>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                  <small class="text-muted">
                    <i class="bi bi-calendar3 me-1"></i>
                    Last Maintenance: {{ asset.last_maintenance_date ? formatDate(asset.last_maintenance_date) : 'Never' }}
                  </small>
                  <div class="dropdown" @click.stop>
                    <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
                      <i class="bi bi-three-dots-vertical"></i>
                    </button>
                    <ul class="dropdown-menu">
                      <li>
                        <router-link :to="`/assets/${asset.asset_id}/edit`" class="dropdown-item">
                          <i class="bi bi-pencil me-2"></i>Edit
                        </router-link>
                      </li>
                      <li>
                        <button @click="createWorkOrder(asset)" class="dropdown-item">
                          <i class="bi bi-wrench me-2"></i>Work Order
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.count > pagination.page_size" class="card-footer">
          <nav>
            <ul class="pagination pagination-sm justify-content-center mb-0">
              <li class="page-item" :class="{ disabled: !pagination.previous }">
                <button @click="changePage(currentPage - 1)" class="page-link" :disabled="!pagination.previous">
                  Previous
                </button>
              </li>
              
              <li v-for="page in visiblePages" :key="page" class="page-item" :class="{ active: page === currentPage }">
                <button @click="changePage(page)" class="page-link">{{ page }}</button>
              </li>
              
              <li class="page-item" :class="{ disabled: !pagination.next }">
                <button @click="changePage(currentPage + 1)" class="page-link" :disabled="!pagination.next">
                  Next
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { assetsAPI } from '@/services/api'
import { useAssetsStore } from '@/store/assets'
import { toast } from '@/utils/toast'

export default {
  name: 'AssetsList',
  setup() {
    const router = useRouter()
    const assetsStore = useAssetsStore()
    
    const loading = ref(true)
    const viewMode = ref('table')
    const searchTimeout = ref(null)
    
    const assets = ref([])
    const departments = ref([])
    const statistics = ref({})
    const pagination = ref({})
    const currentPage = ref(1)
    
    const filters = reactive({
      search: '',
      department: '',
      asset_type: '',
      status: '',
      ordering: '-created_at'
    })

    const hasFilters = computed(() => {
      return filters.search || filters.department || filters.asset_type || filters.status
    })

    const visiblePages = computed(() => {
      const totalPages = Math.ceil(pagination.value.count / pagination.value.page_size)
      const current = currentPage.value
      const pages = []
      
      const start = Math.max(1, current - 2)
      const end = Math.min(totalPages, current + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })

    const loadAssets = async (page = 1) => {
      loading.value = true
      currentPage.value = page
      
      try {
        const params = {
          page,
          page_size: 20,
          ...filters
        }
        
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key]
          }
        })
        
        console.log('Loading assets with params:', params)
        const response = await assetsAPI.getAssets(params)
        console.log('Assets API response:', response.data)
        
        assets.value = response.data.results || []
        pagination.value = {
          count: response.data.count || 0,
          next: response.data.next,
          previous: response.data.previous,
          page_size: params.page_size || 20
        }
        
        console.log('Loaded assets:', assets.value.length)
      } catch (error) {
        console.error('Error loading assets:', error)
        console.error('Error details:', error.response?.data)
        toast.error(`Failed to load assets: ${error.response?.status || 'Network error'}`)
        assets.value = []
        pagination.value = { count: 0, page_size: 20 }
      } finally {
        loading.value = false
      }
    }

    const loadStatistics = async () => {
      try {
        const response = await assetsAPI.getAssetStatistics()
        statistics.value = response.data
      } catch (error) {
        console.error('Error loading statistics:', error)
      }
    }

    const loadDepartments = async () => {
      try {
        const response = await assetsAPI.getDepartments()
        departments.value = response.data.results || []
      } catch (error) {
        console.error('Error loading departments:', error)
      }
    }

    const debounceSearch = () => {
      clearTimeout(searchTimeout.value)
      searchTimeout.value = setTimeout(() => {
        loadAssets(1)
      }, 500)
    }

    const clearFilters = () => {
      Object.assign(filters, {
        search: '',
        department: '',
        asset_type: '',
        status: '',
        ordering: '-created_at'
      })
      loadAssets(1)
    }

    const setSortBy = (field) => {
      if (filters.ordering === field) {
        filters.ordering = `-${field}`
      } else if (filters.ordering === `-${field}`) {
        filters.ordering = field
      } else {
        filters.ordering = field
      }
      loadAssets(1)
    }

    const changePage = (page) => {
      if (page >= 1 && page <= Math.ceil(pagination.value.count / pagination.value.page_size)) {
        loadAssets(page)
      }
    }

    const viewAsset = (assetId) => {
      router.push(`/assets/${assetId}`)
    }

    const createWorkOrder = (asset) => {
      router.push({
        path: '/work-orders/create',
        query: { asset_id: asset.asset_id }
      })
    }

    const scheduleMainten = (asset) => {
      router.push({
        path: '/maintenance/schedule',
        query: { asset_id: asset.asset_id }
      })
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

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(async () => {
      await Promise.all([
        loadAssets(),
        loadStatistics(),
        loadDepartments()
      ])
    })

    return {
      loading,
      viewMode,
      assets,
      departments,
      statistics,
      pagination,
      currentPage,
      filters,
      hasFilters,
      visiblePages,
      loadAssets,
      debounceSearch,
      clearFilters,
      setSortBy,
      changePage,
      viewAsset,
      createWorkOrder,
      scheduleMainten,
      getStatusClass,
      formatStatus,
      formatDate
    }
  }
}
</script>

<style scoped>
.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: #f8f9fa;
}

.asset-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.asset-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

tbody tr {
  cursor: pointer;
}

tbody tr:hover {
  background-color: #f8f9fa;
}

.dropdown-toggle::after {
  display: none;
}
</style>