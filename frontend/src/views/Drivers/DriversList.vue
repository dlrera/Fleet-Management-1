<template>
  <div class="drivers-list">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="mb-1">Fleet Drivers</h1>
        <p class="text-muted mb-0">Manage driver profiles, licenses, and certifications</p>
      </div>
      <router-link to="/drivers/create" class="btn btn-primary">
        <i class="bi bi-person-plus me-2"></i>Add Driver
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
                placeholder="Name, employee ID, license number..."
                @input="debounceSearch"
              >
            </div>
          </div>
          <div class="col-md-2">
            <label class="form-label">Status</label>
            <select v-model="filters.status" class="form-select" @change="loadDrivers">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="suspended">Suspended</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">License Type</label>
            <select v-model="filters.license_type" class="form-select" @change="loadDrivers">
              <option value="">All Licenses</option>
              <option value="cdl_a">CDL Class A</option>
              <option value="cdl_b">CDL Class B</option>
              <option value="cdl_c">CDL Class C</option>
              <option value="regular">Regular</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Expires Soon</label>
            <select v-model="filters.expiring" class="form-select" @change="loadDrivers">
              <option value="">All</option>
              <option value="30">Next 30 days</option>
              <option value="60">Next 60 days</option>
              <option value="90">Next 90 days</option>
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
            <h3 class="mb-0">{{ statistics.total_drivers || 0 }}</h3>
            <small>Total Drivers</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ statistics.active_drivers || 0 }}</h3>
            <small>Active Drivers</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ statistics.licenses_expiring_30_days || 0 }}</h3>
            <small>Licenses Expiring Soon</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ Math.round(statistics.avg_safety_rating || 0) }}%</h3>
            <small>Avg Safety Rating</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Drivers Table -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Drivers</h5>
        <div class="d-flex align-items-center gap-3">
          <span class="text-muted">{{ pagination.count || 0 }} drivers</span>
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
              :class="viewMode === 'cards' ? 'btn-primary' : 'btn-outline-primary'"
              @click="viewMode = 'cards'"
            >
              <i class="bi bi-person-vcard"></i>
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
        <div v-else-if="drivers.length === 0" class="text-center py-5">
          <i class="bi bi-person-x fs-1 text-muted opacity-50"></i>
          <h5 class="mt-3 text-muted">No drivers found</h5>
          <p class="text-muted">
            {{ hasFilters ? 'Try adjusting your filters or search terms' : 'Get started by adding your first driver' }}
          </p>
          <router-link v-if="!hasFilters" to="/drivers/create" class="btn btn-primary">
            <i class="bi bi-person-plus me-2"></i>Add First Driver
          </router-link>
        </div>

        <!-- Table View -->
        <div v-else-if="viewMode === 'table'" class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th @click="setSortBy('user__first_name')" class="sortable">
                  Name
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th @click="setSortBy('employee_id')" class="sortable">
                  Employee ID
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th @click="setSortBy('license_number')" class="sortable">
                  License
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th @click="setSortBy('status')" class="sortable">
                  Status
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th @click="setSortBy('license_expiry_date')" class="sortable">
                  License Expires
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th>Safety Rating</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="driver in drivers" :key="driver.driver_id" @click="viewDriver(driver.driver_id)">
                <td>
                  <div class="d-flex align-items-center">
                    <div class="me-3">
                      <div class="rounded-circle bg-light d-flex align-items-center justify-content-center" 
                           style="width: 40px; height: 40px;">
                        <i class="bi bi-person-circle text-muted"></i>
                      </div>
                    </div>
                    <div>
                      <div class="fw-bold">{{ driver.user?.first_name }} {{ driver.user?.last_name }}</div>
                      <small class="text-muted">{{ driver.user?.email || 'No email' }}</small>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="fw-bold">{{ driver.employee_id || 'N/A' }}</span>
                </td>
                <td>
                  <div>{{ driver.license_number || 'N/A' }}</div>
                  <small class="text-muted">{{ formatLicenseType(driver.license_type) }}</small>
                </td>
                <td>
                  <span class="badge" :class="getStatusClass(driver.status)">
                    {{ formatStatus(driver.status) }}
                  </span>
                </td>
                <td>
                  <div v-if="driver.license_expiry_date">
                    {{ formatDate(driver.license_expiry_date) }}
                    <span v-if="isExpiringSoon(driver.license_expiry_date)" class="badge bg-warning ms-2">
                      <i class="bi bi-exclamation-triangle me-1"></i>Soon
                    </span>
                  </div>
                  <span v-else class="text-muted">N/A</span>
                </td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="progress me-2" style="width: 60px; height: 8px;">
                      <div 
                        class="progress-bar" 
                        :class="getSafetyRatingClass(driver.safety_rating)"
                        :style="`width: ${driver.safety_rating || 0}%`"
                      ></div>
                    </div>
                    <small class="text-muted">{{ Math.round(driver.safety_rating || 0) }}%</small>
                  </div>
                </td>
                <td @click.stop>
                  <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                            data-bs-toggle="dropdown">
                      Actions
                    </button>
                    <ul class="dropdown-menu">
                      <li>
                        <router-link :to="`/drivers/${driver.driver_id}`" class="dropdown-item">
                          <i class="bi bi-eye me-2"></i>View Details
                        </router-link>
                      </li>
                      <li>
                        <router-link :to="`/drivers/${driver.driver_id}/edit`" class="dropdown-item">
                          <i class="bi bi-pencil me-2"></i>Edit
                        </router-link>
                      </li>
                      <li><hr class="dropdown-divider"></li>
                      <li>
                        <button @click="addTraining(driver)" class="dropdown-item">
                          <i class="bi bi-mortarboard me-2"></i>Add Training
                        </button>
                      </li>
                      <li>
                        <button @click="reportIncident(driver)" class="dropdown-item">
                          <i class="bi bi-exclamation-triangle me-2"></i>Report Incident
                        </button>
                      </li>
                    </ul>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Cards View -->
        <div v-else class="row g-3 p-3">
          <div v-for="driver in drivers" :key="driver.driver_id" class="col-md-6 col-xl-4">
            <div class="card driver-card h-100" @click="viewDriver(driver.driver_id)">
              <div class="card-body">
                <div class="d-flex align-items-start mb-3">
                  <div class="me-3">
                    <div class="rounded-circle bg-light d-flex align-items-center justify-content-center" 
                         style="width: 50px; height: 50px;">
                      <i class="bi bi-person-circle text-muted fs-4"></i>
                    </div>
                  </div>
                  <div class="flex-grow-1">
                    <h6 class="card-title mb-1">{{ driver.user?.first_name }} {{ driver.user?.last_name }}</h6>
                    <p class="text-muted small mb-0">{{ driver.employee_id || 'No Employee ID' }}</p>
                    <span class="badge" :class="getStatusClass(driver.status)">
                      {{ formatStatus(driver.status) }}
                    </span>
                  </div>
                </div>
                
                <div class="row g-2 text-center mb-3">
                  <div class="col-6">
                    <small class="text-muted">License</small>
                    <div class="fw-bold small">{{ formatLicenseType(driver.license_type) }}</div>
                  </div>
                  <div class="col-6">
                    <small class="text-muted">Safety Rating</small>
                    <div class="fw-bold small">{{ Math.round(driver.safety_rating || 0) }}%</div>
                  </div>
                </div>

                <div class="d-flex justify-content-between align-items-center">
                  <small class="text-muted">
                    <i class="bi bi-calendar3 me-1"></i>
                    License: {{ driver.license_expiry_date ? formatDate(driver.license_expiry_date) : 'N/A' }}
                    <span v-if="isExpiringSoon(driver.license_expiry_date)" class="text-warning ms-1">
                      <i class="bi bi-exclamation-triangle"></i>
                    </span>
                  </small>
                  <div class="dropdown" @click.stop>
                    <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
                      <i class="bi bi-three-dots-vertical"></i>
                    </button>
                    <ul class="dropdown-menu">
                      <li>
                        <router-link :to="`/drivers/${driver.driver_id}/edit`" class="dropdown-item">
                          <i class="bi bi-pencil me-2"></i>Edit
                        </router-link>
                      </li>
                      <li>
                        <button @click="addTraining(driver)" class="dropdown-item">
                          <i class="bi bi-mortarboard me-2"></i>Add Training
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { driversAPI } from '@/services/api'
import { toast } from '@/utils/toast'

export default {
  name: 'DriversList',
  setup() {
    const router = useRouter()
    
    const loading = ref(true)
    const viewMode = ref('table')
    const searchTimeout = ref(null)
    
    const drivers = ref([])
    const statistics = ref({})
    const pagination = ref({})
    const currentPage = ref(1)
    
    const filters = reactive({
      search: '',
      status: '',
      license_type: '',
      expiring: '',
      ordering: '-created_at'
    })

    const hasFilters = computed(() => {
      return filters.search || filters.status || filters.license_type || filters.expiring
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

    const loadDrivers = async (page = 1) => {
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
        
        const response = await driversAPI.getDrivers(params)
        drivers.value = response.data.results || []
        pagination.value = {
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
          page_size: params.page_size
        }
      } catch (error) {
        console.error('Error loading drivers:', error)
        toast.error('Failed to load drivers')
        drivers.value = []
      } finally {
        loading.value = false
      }
    }

    const loadStatistics = async () => {
      try {
        const response = await driversAPI.getDriverStatistics()
        statistics.value = response.data
      } catch (error) {
        console.error('Error loading statistics:', error)
      }
    }

    const debounceSearch = () => {
      clearTimeout(searchTimeout.value)
      searchTimeout.value = setTimeout(() => {
        loadDrivers(1)
      }, 500)
    }

    const clearFilters = () => {
      Object.assign(filters, {
        search: '',
        status: '',
        license_type: '',
        expiring: '',
        ordering: '-created_at'
      })
      loadDrivers(1)
    }

    const setSortBy = (field) => {
      if (filters.ordering === field) {
        filters.ordering = `-${field}`
      } else if (filters.ordering === `-${field}`) {
        filters.ordering = field
      } else {
        filters.ordering = field
      }
      loadDrivers(1)
    }

    const changePage = (page) => {
      if (page >= 1 && page <= Math.ceil(pagination.value.count / pagination.value.page_size)) {
        loadDrivers(page)
      }
    }

    const viewDriver = (driverId) => {
      router.push(`/drivers/${driverId}`)
    }

    const addTraining = (driver) => {
      router.push({
        path: '/drivers/training/create',
        query: { driver_id: driver.driver_id }
      })
    }

    const reportIncident = (driver) => {
      router.push({
        path: '/drivers/incidents/create',
        query: { driver_id: driver.driver_id }
      })
    }

    const getStatusClass = (status) => {
      const statusClasses = {
        'active': 'bg-success',
        'inactive': 'bg-secondary',
        'suspended': 'bg-danger'
      }
      return statusClasses[status] || 'bg-secondary'
    }

    const getSafetyRatingClass = (rating) => {
      if (rating >= 90) return 'bg-success'
      if (rating >= 70) return 'bg-warning'
      return 'bg-danger'
    }

    const formatStatus = (status) => {
      return status.charAt(0).toUpperCase() + status.slice(1)
    }

    const formatLicenseType = (type) => {
      const types = {
        'cdl_a': 'CDL-A',
        'cdl_b': 'CDL-B',
        'cdl_c': 'CDL-C',
        'regular': 'Regular'
      }
      return types[type] || 'Unknown'
    }

    const isExpiringSoon = (expiryDate) => {
      if (!expiryDate) return false
      const expiry = new Date(expiryDate)
      const thirtyDaysFromNow = new Date()
      thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30)
      return expiry <= thirtyDaysFromNow
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
        loadDrivers(),
        loadStatistics()
      ])
    })

    return {
      loading,
      viewMode,
      drivers,
      statistics,
      pagination,
      currentPage,
      filters,
      hasFilters,
      visiblePages,
      loadDrivers,
      debounceSearch,
      clearFilters,
      setSortBy,
      changePage,
      viewDriver,
      addTraining,
      reportIncident,
      getStatusClass,
      getSafetyRatingClass,
      formatStatus,
      formatLicenseType,
      isExpiringSoon,
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

.driver-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.driver-card:hover {
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

.progress {
  border-radius: 4px;
}
</style>