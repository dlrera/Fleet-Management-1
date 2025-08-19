<template>
  <v-container fluid>
    <!-- Page Header -->
    <v-row class="mb-3">
      <v-col cols="12" md="8">
        <h1 class="text-h5 font-weight-medium mb-1">
          Driver Management
        </h1>
        <p class="text-body-2 text-medium-emphasis">
          Manage driver profiles, certifications, and vehicle assignments
        </p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-btn
          color="primary"
          size="small"
          prepend-icon="mdi-plus"
          @click="showAddDriverDialog"
          class="mr-2"
        >
          Add Driver
        </v-btn>
        <v-btn
          variant="outlined"
          size="small"
          prepend-icon="mdi-file-upload"
          @click="showImportDialog = true"
        >
          Import CSV
        </v-btn>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row v-if="driversStore.hasStats" class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 cursor-pointer"
          @click="clearAllFilters"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ driversStore.driverStats.total_drivers }}
              </div>
              <div class="text-caption text-medium-emphasis">Total Drivers</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-account-group</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 cursor-pointer"
          :class="{ 'stat-card--active': filters.employment_status === 'active' }"
          @click="filterByStatus('active')"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ driversStore.driverStats.active_drivers }}
              </div>
              <div class="text-caption text-medium-emphasis">Active</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-check-circle</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 cursor-pointer"
          :class="{ 'stat-card--active': filters.employment_status === 'inactive' }"
          @click="filterByStatus('inactive')"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ driversStore.driverStats.inactive_drivers }}
              </div>
              <div class="text-caption text-medium-emphasis">Inactive</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-account-off</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 cursor-pointer"
          :class="{ 'stat-card--active': filters.employment_status === 'suspended' }"
          @click="filterByStatus('suspended')"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ driversStore.driverStats.suspended_drivers }}
              </div>
              <div class="text-caption text-medium-emphasis">Suspended</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-account-cancel</v-icon>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Search and Filter Section -->
    <div class="filter-section pa-3 mb-3">
      <div class="py-1">
        <v-row class="align-center">
          <!-- Global Search -->
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchQuery"
              label="Search"
              placeholder="Name, ID, license..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @input="debouncedSearch"
            />
          </v-col>
        
          <!-- Employment Status Filter -->
          <v-col cols="6" sm="3" md="2">
            <v-select
              v-model="filters.employment_status"
              :items="employmentStatusOptions"
              label="Status"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              @update:model-value="handleFilterChange"
            />
          </v-col>
        
          <!-- License Type Filter -->
          <v-col cols="6" sm="3" md="2">
            <v-select
              v-model="filters.license_type"
              :items="licenseTypeOptions"
              label="License"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              @update:model-value="handleFilterChange"
            />
          </v-col>
        
          <!-- Department Filter -->
          <v-col cols="6" sm="3" md="2">
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
        
          <!-- Advanced Filters Toggle -->
          <v-col cols="6" sm="3" md="2">
            <v-btn
              variant="outlined"
              prepend-icon="mdi-filter"
              density="comfortable"
              @click="showAdvancedFilters = !showAdvancedFilters"
              :class="{ 'active-filter': driversStore.hasActiveFilters }"
            >
              More Filters
            </v-btn>
          </v-col>
        </v-row>
        
        <!-- Advanced Filters -->
        <v-expand-transition>
          <div v-if="showAdvancedFilters" class="mt-3">
            <v-row class="align-center">
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
          </div>
        </v-expand-transition>
      </div>
    </div>

    <!-- Bulk Actions Bar -->
    <v-expand-transition>
      <v-card v-if="selectedDrivers.length > 0" class="mb-4" variant="outlined">
        <v-card-text class="d-flex align-center justify-space-between">
          <div class="d-flex align-center gap-3">
            <span class="text-body-1">{{ selectedDrivers.length }} drivers selected</span>
            <v-btn
              variant="tonal"
              size="small"
              @click="clearSelection"
            >
              Clear Selection
            </v-btn>
          </div>
          <div class="d-flex align-center gap-3">
            <v-select
              v-model="bulkEmploymentStatus"
              :items="employmentStatusOptions"
              label="Change Status"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              style="width: 180px"
            />
            <v-text-field
              v-model="bulkDepartment"
              label="Change Department"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              style="width: 180px"
            />
            <v-btn
              color="primary"
              variant="flat"
              :disabled="!bulkEmploymentStatus && !bulkDepartment"
              @click="applyBulkUpdate"
            >
              Apply Changes
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-expand-transition>

    <!-- Drivers Table -->
    <div class="table-section">
      <v-data-table-server
        v-model="selectedDrivers"
        v-model:items-per-page="pageSize"
        v-model:page="currentPage"
        v-model:sort-by="sortBy"
        :headers="headers"
        :items="driversStore.drivers"
        :items-length="driversStore.totalDrivers"
        :loading="driversStore.isLoading"
        item-value="id"
        show-select
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
          <div v-if="item.has_critical_alert">
            <v-tooltip location="top">
              <template v-slot:activator="{ props }">
                <v-chip
                  v-bind="props"
                  color="error"
                  size="small"
                  variant="flat"
                  @click.stop="showAlertDetails(item)"
                  style="cursor: pointer;"
                >
                  <v-icon size="small" start>mdi-alert</v-icon>
                  {{ item.alert_details.length }}
                </v-chip>
              </template>
              <div v-if="item.alert_details.length === 1">
                {{ item.alert_details[0].message }}
              </div>
              <div v-else>
                Please click for list of alerts.
              </div>
            </v-tooltip>
          </div>
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
    </div>

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

    <!-- Import CSV Dialog -->
    <v-dialog v-model="showImportDialog" max-width="600">
      <v-card>
        <v-card-title>Import Drivers from CSV</v-card-title>
        <v-card-text>
          <v-form ref="importForm" @submit.prevent="handleImport">
            <!-- Instructions -->
            <v-alert
              type="info"
              variant="tonal"
              class="mb-4"
            >
              <div class="text-body-2">
                Upload a CSV file with driver data. Required columns:
                <strong>driver_id, first_name, last_name, email</strong>
              </div>
              <v-btn
                size="small"
                variant="text"
                class="mt-2"
                @click="downloadTemplate"
              >
                <v-icon left>mdi-download</v-icon>
                Download Template
              </v-btn>
            </v-alert>
            
            <!-- File Upload Area -->
            <div
              class="import-zone pa-6 text-center rounded"
              :class="{ 'import-zone--active': isCSVDragging }"
              @drop.prevent="handleCSVDrop"
              @dragover.prevent="isCSVDragging = true"
              @dragleave.prevent="isCSVDragging = false"
            >
              <v-icon size="48" color="grey-darken-1" class="mb-3">
                mdi-file-upload-outline
              </v-icon>
              <p class="text-body-1 mb-2">
                Drag and drop your CSV file here or
              </p>
              <v-file-input
                v-model="importFile"
                label="Choose File"
                accept=".csv"
                variant="outlined"
                density="compact"
                hide-details
                class="mx-auto"
                style="max-width: 250px;"
              />
            </div>
            
            <!-- Selected File Display -->
            <div v-if="importFile && importFile.length > 0" class="mt-4">
              <v-alert type="success" variant="tonal" density="compact">
                <strong>Selected:</strong> {{ importFile[0].name }}
                <span class="text-caption ml-2">
                  ({{ formatFileSize(importFile[0].size) }})
                </span>
              </v-alert>
            </div>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="cancelImport">Cancel</v-btn>
          <v-btn 
            color="primary"
            :loading="driversStore.isImporting"
            :disabled="!importFile || importFile.length === 0"
            @click="handleImport"
          >
            Import
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Alert Details Modal -->
    <v-dialog v-model="showAlertModal" max-width="600">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Driver Alerts - {{ alertDriver?.full_name }}</span>
          <v-btn
            icon="mdi-close"
            variant="text"
            size="small"
            @click="showAlertModal = false"
          />
        </v-card-title>
        <v-card-text>
          <v-alert
            type="error"
            variant="tonal"
            class="mb-3"
          >
            <strong>Critical Issue:</strong> This driver has active vehicle assignments but is not eligible to drive.
          </v-alert>
          
          <div v-for="(alert, index) in alertDriver?.alert_details" :key="index" class="mb-4">
            <div class="d-flex align-center mb-2">
              <v-icon color="error" size="small" class="mr-2">mdi-alert-circle</v-icon>
              <strong>{{ alert.type === 'employment_status' ? 'Employment Status Issue' : 'License Issue' }}</strong>
            </div>
            
            <div class="ml-7">
              <p class="mb-2">{{ alert.message }}</p>
              
              <div v-if="alert.affected_vehicles && alert.affected_vehicles.length > 0">
                <strong class="text-caption">Affected Vehicles:</strong>
                <v-chip-group class="mt-1">
                  <v-chip
                    v-for="vehicle in alert.affected_vehicles"
                    :key="vehicle"
                    size="small"
                    variant="outlined"
                  >
                    {{ vehicle }}
                  </v-chip>
                </v-chip-group>
              </div>
            </div>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="primary"
            variant="outlined"
            @click="() => { showAlertModal = false; editDriver(alertDriver); }"
          >
            Edit Driver
          </v-btn>
          <v-btn
            color="primary"
            @click="showAlertModal = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
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
const showImportDialog = ref(false)
const showAlertModal = ref(false)
const driverToDelete = ref(null)
const alertDriver = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const sortBy = ref([{ key: 'driver_id', order: 'asc' }])
const importFile = ref(null)
const selectedDrivers = ref([])
const bulkEmploymentStatus = ref('')
const bulkDepartment = ref('')
const isCSVDragging = ref(false)

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

const showAlertDetails = (driver) => {
  alertDriver.value = driver
  showAlertModal.value = true
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

const downloadTemplate = async () => {
  try {
    const response = await driversStore.downloadTemplate()
    // Create a blob from the response
    const blob = new Blob([response], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'drivers_import_template.csv'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to download template:', error)
  }
}

const handleCSVDrop = (event) => {
  isCSVDragging.value = false
  const files = event.dataTransfer.files
  if (files.length > 0 && files[0].type === 'text/csv') {
    importFile.value = [files[0]]
  }
}

const cancelImport = () => {
  showImportDialog.value = false
  importFile.value = null
  isCSVDragging.value = false
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleImport = async () => {
  if (!importFile.value || importFile.value.length === 0) return
  
  try {
    await driversStore.importDrivers(importFile.value[0])
    showImportDialog.value = false
    importFile.value = null
    // Reload data
    await loadDrivers()
    await loadStats()
  } catch (error) {
    console.error('Import failed:', error)
  }
}

const clearSelection = () => {
  selectedDrivers.value = []
  bulkEmploymentStatus.value = ''
  bulkDepartment.value = ''
}

const applyBulkUpdate = async () => {
  if (selectedDrivers.value.length === 0) return
  
  const updates = {}
  if (bulkEmploymentStatus.value) {
    updates.employment_status = bulkEmploymentStatus.value
  }
  if (bulkDepartment.value) {
    updates.department = bulkDepartment.value
  }
  
  if (Object.keys(updates).length === 0) return
  
  try {
    await driversStore.bulkUpdateDrivers(selectedDrivers.value, updates)
    clearSelection()
    // Reload data
    await loadDrivers()
    await loadStats()
  } catch (error) {
    console.error('Bulk update failed:', error)
  }
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
/* Import zone styling */
.import-zone {
  border: 2px dashed #e0e0e0;
  background-color: #fafafa;
  transition: all 0.3s ease;
}

.import-zone--active {
  border-color: #1976d2;
  background-color: #e3f2fd;
}

/* Statistics cards styling - matching Assets */
.stat-card {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  background-color: rgb(var(--v-theme-surface));
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: rgba(var(--v-theme-primary), 0.3);
  background-color: rgba(var(--v-theme-primary), 0.02);
}

.stat-card--active {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.08);
}

/* Filter section styling - matching Assets */
.filter-section {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  background-color: rgb(var(--v-theme-surface));
}

/* Table section styling - matching Assets */
.table-section {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  background-color: rgb(var(--v-theme-surface));
  overflow: hidden;
}

.active-filter {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.08);
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

/* Table styling - matching Assets */
.v-data-table :deep(.v-data-table__td) {
  padding: 6px 12px;
  font-size: 0.875rem;
}

.v-data-table :deep(.v-data-table__th) {
  font-weight: 600;
  font-size: 0.875rem;
  padding: 8px 12px;
}
</style>