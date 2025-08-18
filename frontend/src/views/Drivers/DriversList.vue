<template>
  <div class="drivers-list-container">
    <!-- Header with controls -->
    <div class="page-header">
      <div class="d-flex align-center justify-space-between">
        <div>
          <h1 class="text-h4 mb-1">Drivers</h1>
          <p class="text-body-2 text-medium-emphasis">
            Manage driver profiles, certifications, and vehicle assignments
          </p>
        </div>
        
        <div class="d-flex align-center gap-3">
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="showAddDriverDialog"
          >
            Add Driver
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="d-flex gap-4 mb-6" v-if="driversStore.hasStats">
      <div class="stats-card clickable" @click="clearAllFilters">
        <div class="stats-value">{{ driversStore.driverStats.total_drivers }}</div>
        <div class="stats-label">Total Drivers</div>
      </div>
      
      <div class="stats-card clickable" @click="filterByStatus('active')">
        <div class="stats-value">{{ driversStore.driverStats.active_drivers }}</div>
        <div class="stats-label">Active</div>
      </div>
      
      <div class="stats-card clickable" @click="filterByStatus('inactive')">
        <div class="stats-value">{{ driversStore.driverStats.inactive_drivers }}</div>
        <div class="stats-label">Inactive</div>
      </div>
      
      <div class="stats-card clickable" @click="filterByStatus('suspended')">
        <div class="stats-value">{{ driversStore.driverStats.suspended_drivers }}</div>
        <div class="stats-label">Suspended</div>
      </div>
      
      <div class="stats-card alert" v-if="driversStore.driverStats.expired_licenses > 0" @click="filterByLicenseStatus('expired')">
        <div class="stats-value">{{ driversStore.driverStats.expired_licenses }}</div>
        <div class="stats-label">Expired Licenses</div>
      </div>
      
      <div class="stats-card warning" v-if="driversStore.driverStats.expiring_licenses > 0" @click="filterByLicenseStatus('expiring_soon')">
        <div class="stats-value">{{ driversStore.driverStats.expiring_licenses }}</div>
        <div class="stats-label">Expiring Soon</div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="filters-section">
      <v-row no-gutters class="gap-3">
        <v-col cols="12" md="4">
          <v-text-field
            v-model="searchQuery"
            label="Search drivers..."
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="compact"
            hide-details
            clearable
            @input="debouncedSearch"
          />
        </v-col>
        
        <v-col cols="12" md="2">
          <v-select
            v-model="filters.employment_status"
            :items="employmentStatusOptions"
            label="Employment Status"
            variant="outlined"
            density="compact"
            hide-details
            clearable
            @update:model-value="handleFilterChange"
          />
        </v-col>
        
        <v-col cols="12" md="2">
          <v-select
            v-model="filters.license_type"
            :items="licenseTypeOptions"
            label="License Type"
            variant="outlined"
            density="compact"
            hide-details
            clearable
            @update:model-value="handleFilterChange"
          />
        </v-col>
        
        <v-col cols="12" md="2">
          <v-select
            v-model="filters.department"
            :items="departmentOptions"
            label="Department"
            variant="outlined"
            density="compact"
            hide-details
            clearable
            @update:model-value="handleFilterChange"
          />
        </v-col>
        
        <v-col cols="12" md="2">
          <v-btn
            variant="outlined"
            prepend-icon="mdi-filter"
            @click="showAdvancedFilters = !showAdvancedFilters"
            :class="{ 'active-filter': driversStore.hasActiveFilters }"
          >
            Filters
          </v-btn>
        </v-col>
      </v-row>
      
      <!-- Advanced Filters -->
      <v-expand-transition>
        <v-card v-if="showAdvancedFilters" class="mt-4 pa-4" variant="outlined">
          <v-row no-gutters class="gap-3">
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.license_status"
                :items="licenseStatusOptions"
                label="License Status"
                variant="outlined"
                density="compact"
                hide-details
                clearable
                @update:model-value="handleFilterChange"
              />
            </v-col>
            
            <v-col cols="12" md="2">
              <v-text-field
                v-model="filters.min_age"
                label="Min Age"
                type="number"
                variant="outlined"
                density="compact"
                hide-details
                @input="handleFilterChange"
              />
            </v-col>
            
            <v-col cols="12" md="2">
              <v-text-field
                v-model="filters.max_age"
                label="Max Age"
                type="number"
                variant="outlined"
                density="compact"
                hide-details
                @input="handleFilterChange"
              />
            </v-col>
            
            <v-col cols="12" md="3">
              <v-text-field
                v-model="filters.position"
                label="Position"
                variant="outlined"
                density="compact"
                hide-details
                @input="handleFilterChange"
              />
            </v-col>
            
            <v-col cols="12" md="2">
              <v-btn
                variant="outlined"
                color="secondary"
                block
                @click="clearAllFilters"
              >
                Clear All
              </v-btn>
            </v-col>
          </v-row>
        </v-card>
      </v-expand-transition>
    </div>

    <!-- Drivers Table -->
    <v-card>
      <v-data-table-server
        v-model:items-per-page="pageSize"
        v-model:page="currentPage"
        v-model:sort-by="sortBy"
        :headers="headers"
        :items="driversStore.drivers"
        :items-length="driversStore.totalDrivers"
        :loading="driversStore.isLoading"
        item-value="id"
        @update:options="handleTableUpdate"
        @click:row="handleRowClick"
        class="clickable-rows"
      >
        <template v-slot:item.profile_photo="{ item }">
          <v-avatar size="40" class="ma-2">
            <v-img
              v-if="item.profile_photo"
              :src="item.profile_photo"
              :alt="item.full_name"
            />
            <v-icon v-else color="grey-lighten-1">mdi-account</v-icon>
          </v-avatar>
        </template>
        
        <template v-slot:item.full_name="{ item }">
          <div class="d-flex align-center">
            <div>
              <div class="font-weight-medium">{{ item.full_name }}</div>
              <div class="text-caption text-medium-emphasis">{{ item.driver_id }}</div>
            </div>
          </div>
        </template>
        
        <template v-slot:item.employment_status="{ item }">
          <v-chip
            :color="getEmploymentStatusColor(item.employment_status)"
            size="small"
            variant="flat"
          >
            {{ item.employment_status_display }}
          </v-chip>
        </template>
        
        <template v-slot:item.license_expiration="{ item }">
          <div>
            <div>{{ formatDate(item.license_expiration) }}</div>
            <v-chip
              v-if="item.license_is_expired"
              color="error"
              size="x-small"
              variant="flat"
              class="mt-1"
            >
              Expired
            </v-chip>
            <v-chip
              v-else-if="item.license_expires_soon"
              color="warning"
              size="x-small"
              variant="flat"
              class="mt-1"
            >
              Expires Soon
            </v-chip>
          </div>
        </template>
        
        <template v-slot:item.certifications_count="{ item }">
          <v-chip size="small" variant="outlined">
            {{ item.certifications_count }}
          </v-chip>
        </template>
        
        <template v-slot:item.active_assignments_count="{ item }">
          <v-tooltip bottom>
            <template v-slot:activator="{ props }">
              <v-chip 
                size="small" 
                variant="outlined" 
                color="primary"
                v-bind="props"
                class="cursor-pointer"
              >
                {{ item.active_assignments_count }}
              </v-chip>
            </template>
            <span v-if="item.active_assignments_count > 0">
              Click to view asset assignments
            </span>
            <span v-else>No active assignments</span>
          </v-tooltip>
        </template>
        
        <template v-slot:item.expiring_items_count="{ item }">
          <v-chip
            v-if="item.expiring_items_count > 0"
            color="warning"
            size="small"
            variant="flat"
          >
            {{ item.expiring_items_count }}
          </v-chip>
          <span v-else class="text-medium-emphasis">—</span>
        </template>
        
        <template v-slot:item.actions="{ item }">
          <div class="d-flex align-center gap-1">
            <v-btn
              icon="mdi-pencil"
              variant="text"
              size="small"
              @click.stop="editDriver(item)"
              title="Edit Driver"
            />
            <v-btn
              icon="mdi-delete"
              variant="text"
              size="small"
              color="error"
              @click.stop="confirmDeleteDriver(item)"
              title="Delete Driver"
            />
          </div>
        </template>
        
        <template v-slot:no-data>
          <div class="text-center pa-8">
            <v-icon size="64" color="grey-lighten-2" class="mb-4">mdi-account-group</v-icon>
            <h3 class="text-h6 text-medium-emphasis mb-2">No drivers found</h3>
            <p class="text-body-2 text-medium-emphasis mb-4">
              {{ driversStore.hasActiveFilters ? 'Try adjusting your search filters' : 'Get started by adding your first driver' }}
            </p>
            <v-btn
              v-if="!driversStore.hasActiveFilters"
              color="primary"
              prepend-icon="mdi-plus"
              @click="showAddDriverDialog"
            >
              Add Driver
            </v-btn>
            <v-btn
              v-else
              variant="outlined"
              @click="clearAllFilters"
            >
              Clear Filters
            </v-btn>
          </div>
        </template>
      </v-data-table-server>
    </v-card>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">Confirm Delete</v-card-title>
        <v-card-text>
          Are you sure you want to delete driver {{ driverToDelete?.full_name }}? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn color="error" variant="flat" @click="deleteDriver" :loading="driversStore.isDeleting">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDriversStore } from '../../stores/drivers'

// Store and router
const router = useRouter()
const driversStore = useDriversStore()

// Component state
const searchQuery = ref('')
const showAdvancedFilters = ref(false)
const showDeleteDialog = ref(false)
const driverToDelete = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const sortBy = ref([{ key: 'driver_id', order: 'asc' }])

// Filters
const filters = ref({
  employment_status: '',
  license_type: '',
  department: '',
  position: '',
  license_status: '',
  min_age: null,
  max_age: null
})

// Options for dropdowns
const employmentStatusOptions = [
  { title: 'Active', value: 'active' },
  { title: 'Inactive', value: 'inactive' },
  { title: 'Suspended', value: 'suspended' },
  { title: 'Terminated', value: 'terminated' },
  { title: 'On Leave', value: 'on_leave' }
]

const licenseTypeOptions = [
  { title: 'Class A CDL', value: 'class_a' },
  { title: 'Class B CDL', value: 'class_b' },
  { title: 'Class C CDL', value: 'class_c' },
  { title: 'Chauffeur License', value: 'chauffeur' },
  { title: 'Regular License', value: 'regular' },
  { title: 'Motorcycle License', value: 'motorcycle' }
]

const licenseStatusOptions = [
  { title: 'Expired', value: 'expired' },
  { title: 'Expiring Soon', value: 'expiring_soon' }
]

// Computed properties
const departmentOptions = computed(() => {
  const departments = [...new Set(driversStore.drivers.map(d => d.department).filter(Boolean))]
  return departments.map(dept => ({ title: dept, value: dept }))
})

// Table headers
const headers = [
  { title: '', key: 'profile_photo', sortable: false, width: '60px' },
  { title: 'Driver', key: 'full_name', sortable: true },
  { title: 'Status', key: 'employment_status', sortable: true },
  { title: 'License Type', key: 'license_type_display', sortable: true },
  { title: 'License Exp.', key: 'license_expiration', sortable: true },
  { title: 'Department', key: 'department', sortable: true },
  { title: 'Certs', key: 'certifications_count', sortable: false },
  { title: 'Assets', key: 'active_assignments_count', sortable: false },
  { title: 'Alerts', key: 'expiring_items_count', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, width: '80px' }
]

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    driversStore.setSearchQuery(searchQuery.value)
    loadDrivers()
  }, 300)
}

// Methods
const loadDrivers = async () => {
  try {
    await driversStore.fetchDrivers({
      page: currentPage.value
    })
  } catch (error) {
    console.error('Failed to load drivers:', error)
  }
}

const loadStats = async () => {
  try {
    await driversStore.fetchDriverStats()
  } catch (error) {
    console.error('Failed to load driver stats:', error)
  }
}

const handleTableUpdate = ({ page, itemsPerPage, sortBy: newSortBy }) => {
  currentPage.value = page
  pageSize.value = itemsPerPage
  
  if (newSortBy && newSortBy.length > 0) {
    const sort = newSortBy[0]
    driversStore.setSorting(sort.key, sort.order === 'desc')
    sortBy.value = newSortBy
  }
  
  loadDrivers()
}

const handleFilterChange = () => {
  driversStore.setFilters(filters.value)
  currentPage.value = 1
  loadDrivers()
}

const filterByStatus = (status) => {
  filters.value.employment_status = status
  handleFilterChange()
}

const filterByLicenseStatus = (status) => {
  filters.value.license_status = status
  handleFilterChange()
}

const clearAllFilters = () => {
  searchQuery.value = ''
  filters.value = {
    employment_status: '',
    license_type: '',
    department: '',
    position: '',
    license_status: '',
    min_age: null,
    max_age: null
  }
  driversStore.clearFilters()
  currentPage.value = 1
  loadDrivers()
}

const handleRowClick = (event, { item }) => {
  // Navigate to driver detail page when row is clicked
  router.push(`/drivers/${item.id}`)
}

const editDriver = (driver) => {
  router.push(`/drivers/${driver.id}/edit`)
}

const showAddDriverDialog = () => {
  router.push('/drivers/create')
}

const confirmDeleteDriver = (driver) => {
  driverToDelete.value = driver
  showDeleteDialog.value = true
}

const deleteDriver = async () => {
  try {
    await driversStore.deleteDriver(driverToDelete.value.id)
    showDeleteDialog.value = false
    driverToDelete.value = null
    // Reload data
    await loadDrivers()
    await loadStats()
  } catch (error) {
    console.error('Failed to delete driver:', error)
  }
}

const getEmploymentStatusColor = (status) => {
  const colors = {
    active: 'success',
    inactive: 'warning',
    suspended: 'error',
    terminated: 'error',
    on_leave: 'info'
  }
  return colors[status] || 'default'
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

// Lifecycle hooks
onMounted(async () => {
  await Promise.all([
    loadDrivers(),
    loadStats()
  ])
})

// Watchers
watch(() => driversStore.searchQuery, (newQuery) => {
  searchQuery.value = newQuery
})

watch(() => driversStore.filters, (newFilters) => {
  filters.value = { ...newFilters }
}, { deep: true })
</script>

<style scoped>
.drivers-list-container {
  padding: 24px;
  background-color: #F9FAFA;
  min-height: 100vh;
}

.page-header {
  background: white;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stats-card {
  background: white;
  padding: 16px 20px;
  border-radius: 8px;
  text-align: center;
  min-width: 120px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
}

.stats-card.clickable {
  cursor: pointer;
}

.stats-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.stats-card.alert {
  border-left: 4px solid #DB162F;
  cursor: pointer;
}

.stats-card.warning {
  border-left: 4px solid #E18331;
  cursor: pointer;
}

.stats-value {
  font-size: 24px;
  font-weight: 600;
  color: #216093;
  line-height: 1;
}

.stats-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filters-section {
  background: white;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.active-filter {
  background-color: #216093 !important;
  color: white !important;
}

.gap-3 {
  gap: 12px;
}

.cursor-pointer {
  cursor: pointer;
}

.clickable-rows :deep(.v-data-table__tr) {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.clickable-rows :deep(.v-data-table__tr:hover) {
  background-color: #f5f5f5;
}

/* Bold table headers */
:deep(.v-data-table-header th) {
  font-weight: 600 !important;
}
</style>