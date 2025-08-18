<template>
  <v-container fluid>
    <!-- Page Header -->
    <v-row class="mb-3">
      <v-col cols="12" md="8">
        <h1 class="text-h5 font-weight-medium mb-1" data-testid="assets-page-title">
          Asset Management
        </h1>
        <p class="text-body-2 text-medium-emphasis">
          Manage your fleet assets, vehicles, and equipment
        </p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-btn
          variant="outlined"
          size="small"
          prepend-icon="mdi-plus"
          :to="{ name: 'AssetCreate' }"
          data-testid="add-asset-btn"
          aria-label="Add new asset"
          class="mr-2"
        >
          Add Asset
        </v-btn>
        <v-btn
          variant="outlined"
          size="small"
          prepend-icon="mdi-file-upload"
          @click="showImportDialog = true"
          data-testid="import-csv-btn"
          aria-label="Import CSV"
        >
          Import CSV
        </v-btn>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row v-if="assetsStore.hasStats" class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 cursor-pointer"
          @click="clearAllFilters"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ assetsStore.assetStats.total_assets }}
              </div>
              <div class="text-caption text-medium-emphasis">Total Assets</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-truck</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 cursor-pointer"
          :class="{ 'stat-card--active': filters.status === 'active' }"
          @click="setStatusFilter('active')"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ assetsStore.assetStats.active_assets }}
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
          :class="{ 'stat-card--active': filters.status === 'maintenance' }"
          @click="setStatusFilter('maintenance')"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ assetsStore.assetStats.maintenance_assets }}
              </div>
              <div class="text-caption text-medium-emphasis">Maintenance</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-wrench</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 cursor-pointer"
          :class="{ 'stat-card--active': filters.status === 'retired' }"
          @click="setStatusFilter('retired')"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ assetsStore.assetStats.retired_assets }}
              </div>
              <div class="text-caption text-medium-emphasis">Retired</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-archive</v-icon>
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
              placeholder="Asset ID, make, model..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              data-testid="search-input"
              @input="handleSearchChange"
            />
          </v-col>

          <!-- Vehicle Type Filter -->
          <v-col cols="6" sm="3" md="2">
            <v-select
              v-model="filters.vehicle_type"
              :items="vehicleTypeOptions"
              label="Type"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              data-testid="vehicle-type-filter"
              @update:model-value="updateFilter('vehicle_type', $event)"
            />
          </v-col>

          <!-- Status Filter -->
          <v-col cols="6" sm="3" md="2">
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              label="Status"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              data-testid="status-filter"
              @update:model-value="updateFilter('status', $event)"
            />
          </v-col>

          <!-- Department Filter -->
          <v-col cols="6" sm="3" md="2">
            <v-text-field
              v-model="filters.department"
              label="Department"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              data-testid="department-filter"
              @input="handleDepartmentChange"
            />
          </v-col>

          <!-- Year Filter -->
          <v-col cols="6" sm="3" md="2">
            <v-text-field
              v-model="filters.year"
              label="Year"
              type="number"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              data-testid="year-filter"
              @input="handleYearChange"
            />
          </v-col>
        </v-row>

        <!-- Filter Actions -->
        <div v-if="assetsStore.hasActiveFilters" class="mt-3">
          <v-btn
            variant="text"
            size="x-small"
            prepend-icon="mdi-filter-remove"
            data-testid="clear-filters-btn"
            @click="clearAllFilters"
          >
            Clear All
          </v-btn>
          <v-chip
            v-if="searchQuery"
            size="x-small"
            variant="outlined"
            closable
            class="ml-2"
            @click:close="searchQuery = ''"
          >
            {{ searchQuery }}
          </v-chip>
          <v-chip
            v-for="(value, key) in activeFilters"
            :key="key"
            size="x-small"
            variant="outlined"
            closable
            class="ml-1"
            @click:close="clearFilter(key)"
          >
            {{ value }}
          </v-chip>
        </div>
      </div>
    </div>

    <!-- Assets Data Table -->
    <div class="table-section">
      <v-data-table-server
        v-model:items-per-page="itemsPerPage"
        v-model:page="currentPage"
        v-model:sort-by="sortBy"
        :headers="headers"
        :items="assetsStore.assets"
        :items-length="assetsStore.totalAssets"
        :loading="assetsStore.isLoading"
        :search="searchQuery"
        class="elevation-0"
        item-value="id"
        data-testid="assets-table"
        density="compact"
        @update:options="loadAssets"
      >
        <!-- Thumbnail Column -->
        <template #item.thumbnail="{ item }">
          <div class="thumbnail-container">
            <v-img
              v-if="item.thumbnail"
              :src="item.thumbnail"
              :alt="`${item.asset_id} thumbnail`"
              class="asset-thumbnail"
              cover
            />
            <div v-else class="no-image-placeholder">
              <v-icon size="24" color="grey-lighten-2">
                {{ getVehicleTypeIcon(item.vehicle_type) }}
              </v-icon>
            </div>
          </div>
        </template>

        <!-- Asset ID Column -->
        <template #item.asset_id="{ item }">
          <router-link
            :to="{ name: 'AssetDetail', params: { id: item.id } }"
            class="text-decoration-none font-weight-medium"
            :data-testid="`asset-link-${item.asset_id}`"
          >
            {{ item.asset_id }}
          </router-link>
        </template>

        <!-- Vehicle Info Column -->
        <template #item.vehicle_info="{ item }">
          <div>
            <div class="font-weight-medium">
              {{ item.year }} {{ item.make }} {{ item.model }}
            </div>
            <div class="text-caption text-medium-emphasis">
              VIN: {{ item.vin || 'N/A' }}
            </div>
          </div>
        </template>

        <!-- Vehicle Type Column -->
        <template #item.vehicle_type="{ item }">
          <span class="text-body-2" :data-vehicle-type="item.vehicle_type">
            {{ formatVehicleType(item.vehicle_type) }}
          </span>
        </template>

        <!-- Status Column -->
        <template #item.status="{ item }">
          <span 
            class="text-body-2"
            :class="getStatusTextClass(item.status)"
            :data-status="item.status"
          >
            {{ formatStatus(item.status) }}
          </span>
        </template>

        <!-- Odometer Column -->
        <template #item.current_odometer="{ item }">
          <div class="text-no-wrap">
            {{ formatOdometer(item.current_odometer) }}
          </div>
        </template>

        <!-- Documents Column -->
        <template #item.documents_count="{ item }">
          <span class="text-body-2">
            {{ item.documents_count || 0 }}
          </span>
        </template>

        <!-- Actions Column -->
        <template #item.actions="{ item }">
          <div class="d-flex ga-1 justify-center">
            <v-btn
              :to="{ name: 'AssetDetail', params: { id: item.id } }"
              icon="mdi-eye"
              size="x-small"
              variant="text"
              density="compact"
              :data-testid="`view-asset-${item.asset_id}`"
              :aria-label="`View details for asset ${item.asset_id}`"
            />

            <v-btn
              :to="{ name: 'AssetEdit', params: { id: item.id } }"
              icon="mdi-pencil"
              size="x-small"
              variant="text"
              density="compact"
              :data-testid="`edit-asset-${item.asset_id}`"
              :aria-label="`Edit asset ${item.asset_id}`"
            />

            <v-btn
              icon="mdi-delete"
              size="x-small"
              variant="text"
              density="compact"
              :data-testid="`delete-asset-${item.asset_id}`"
              :aria-label="`Delete asset ${item.asset_id}`"
              @click="confirmDelete(item)"
            />
          </div>
        </template>

        <!-- Loading Slot -->
        <template #loading>
          <v-skeleton-loader type="table-row@10" />
        </template>

        <!-- No Data Slot -->
        <template #no-data>
          <div class="text-center pa-8">
            <v-icon size="64" color="grey-lighten-1">mdi-truck-off</v-icon>
            <h3 class="text-h6 mt-4 mb-2">No Assets Found</h3>
            <p class="text-body-2 text-medium-emphasis mb-4">
              {{ assetsStore.hasActiveFilters 
                ? 'No assets match your current filters.' 
                : 'Get started by adding your first asset.' 
              }}
            </p>
            <v-btn
              v-if="!assetsStore.hasActiveFilters"
              color="primary"
              :to="{ name: 'AssetCreate' }"
            >
              Add First Asset
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
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
          Confirm Deletion
        </v-card-title>
        
        <v-card-text>
          <p>Are you sure you want to delete asset <strong>{{ assetToDelete?.asset_id }}</strong>?</p>
          <p class="text-caption text-error">This action cannot be undone.</p>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            :disabled="assetsStore.isDeleting"
            @click="deleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="assetsStore.isDeleting"
            data-testid="confirm-delete-btn"
            @click="deleteAsset"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- CSV Import Dialog -->
    <v-dialog v-model="showImportDialog" max-width="600">
      <v-card>
        <v-card-title>Import Assets from CSV</v-card-title>
        <v-card-text>
          <v-form ref="importForm" @submit.prevent="importCSV">
            <!-- Instructions -->
            <v-alert
              type="info"
              variant="tonal"
              class="mb-4"
            >
              <div class="text-body-2">
                Upload a CSV file with asset data. Required columns:
                <strong>asset_id, vehicle_type, make, model, year</strong>
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
              <v-icon size="48" class="mb-2" color="grey">
                {{ selectedCSVFile ? 'mdi-file-check' : 'mdi-file-delimited' }}
              </v-icon>
              
              <p v-if="!selectedCSVFile" class="text-body-2 mb-2">
                Drag and drop CSV file here or click to browse
              </p>
              
              <p v-else class="text-body-2 mb-2 font-weight-medium">
                {{ selectedCSVFile.name }}
                <v-chip size="small" class="ml-2">
                  {{ formatFileSize(selectedCSVFile.size) }}
                </v-chip>
              </p>
              
              <input
                ref="csvFileInput"
                type="file"
                hidden
                accept=".csv"
                @change="handleCSVFileSelect"
              />
              
              <v-btn
                v-if="!selectedCSVFile"
                size="small"
                variant="outlined"
                @click="$refs.csvFileInput.click()"
              >
                Choose File
              </v-btn>
              
              <v-btn
                v-else
                size="small"
                variant="text"
                color="error"
                @click="clearCSVFile"
              >
                Remove File
              </v-btn>
            </div>
            
            <p class="text-caption text-medium-emphasis mt-2">
              CSV format only (Max 5MB)
            </p>
            
            <!-- Import Results -->
            <v-alert
              v-if="importResults"
              :type="importResults.error_count > 0 ? 'warning' : 'success'"
              class="mt-4"
              closable
              @click:close="importResults = null"
            >
              <div class="text-body-2">
                <strong>Import Complete!</strong><br>
                Successfully imported: {{ importResults.success_count }} assets<br>
                <span v-if="importResults.error_count > 0">
                  Failed: {{ importResults.error_count }} rows
                </span>
              </div>
              
              <div v-if="importResults.errors && importResults.errors.length > 0" class="mt-2">
                <strong>Errors:</strong>
                <ul class="mt-1">
                  <li v-for="error in importResults.errors.slice(0, 5)" :key="error.row">
                    Row {{ error.row }} ({{ error.asset_id }}): {{ error.error }}
                  </li>
                  <li v-if="importResults.errors.length > 5">
                    ... and {{ importResults.errors.length - 5 }} more errors
                  </li>
                </ul>
              </div>
            </v-alert>
            
            <!-- Import Error -->
            <v-alert
              v-if="importError"
              type="error"
              class="mt-4"
              closable
              @click:close="importError = ''"
            >
              {{ importError }}
            </v-alert>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeImportDialog">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isImporting"
            :disabled="!selectedCSVFile"
            @click="importCSV"
          >
            Import
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Error Snackbar -->
    <v-snackbar
      v-model="showError"
      color="error"
      multi-line
      :timeout="5000"
    >
      {{ assetsStore.error }}
      <template #actions>
        <v-btn
          variant="text"
          @click="showError = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'
import { debounce } from 'lodash-es'

// Store and router
const assetsStore = useAssetsStore()
const router = useRouter()

// Reactive data
const searchQuery = ref('')
const filters = ref({
  vehicle_type: '',
  status: '',
  department: '',
  year: null
})

const currentPage = ref(1)
const itemsPerPage = ref(20)
const sortBy = ref([{ key: 'asset_id', order: 'asc' }])

const deleteDialog = ref(false)
const assetToDelete = ref(null)
const showError = ref(false)

// CSV Import state
const showImportDialog = ref(false)
const csvFileInput = ref(null)
const importForm = ref(null)
const selectedCSVFile = ref(null)
const isCSVDragging = ref(false)
const isImporting = ref(false)
const importError = ref('')
const importResults = ref(null)

// Table headers configuration
const headers = [
  {
    title: '',
    key: 'thumbnail',
    sortable: false,
    width: '60px'
  },
  {
    title: 'Asset ID',
    key: 'asset_id',
    sortable: true,
    width: '110px'
  },
  {
    title: 'Vehicle',
    key: 'vehicle_info',
    sortable: false,
    width: '200px'
  },
  {
    title: 'Type',
    key: 'vehicle_type',
    sortable: true,
    width: '100px',
    align: 'center'
  },
  {
    title: 'License',
    key: 'license_plate',
    sortable: true,
    width: '100px',
    align: 'center'
  },
  {
    title: 'Department',
    key: 'department',
    sortable: true,
    width: '120px',
    align: 'center'
  },
  {
    title: 'Status',
    key: 'status',
    sortable: true,
    width: '100px',
    align: 'center'
  },
  {
    title: 'Odometer',
    key: 'current_odometer',
    sortable: true,
    width: '100px',
    align: 'end'
  },
  {
    title: 'Docs',
    key: 'documents_count',
    sortable: true,
    width: '70px',
    align: 'center'
  },
  {
    title: 'Actions',
    key: 'actions',
    sortable: false,
    width: '120px',
    align: 'center'
  }
]

// Filter options
const vehicleTypeOptions = [
  { title: 'Bus', value: 'bus' },
  { title: 'Truck', value: 'truck' },
  { title: 'Tractor', value: 'tractor' },
  { title: 'Trailer', value: 'trailer' },
  { title: 'Van', value: 'van' },
  { title: 'Car', value: 'car' },
  { title: 'Equipment', value: 'equipment' },
  { title: 'Other', value: 'other' }
]

const statusOptions = [
  { title: 'Active', value: 'active' },
  { title: 'Maintenance', value: 'maintenance' },
  { title: 'Retired', value: 'retired' },
  { title: 'Out of Service', value: 'out_of_service' }
]

// Computed properties
const activeFilters = computed(() => {
  const active = {}
  Object.entries(filters.value).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) {
      active[key] = value
    }
  })
  return active
})

// Debounced search handler
const handleSearchChange = debounce((value) => {
  assetsStore.setSearchQuery(value)
  currentPage.value = 1
  loadAssets()
}, 300)

// Filter change handlers
const handleDepartmentChange = debounce((value) => {
  updateFilter('department', value)
}, 300)

const handleYearChange = debounce((value) => {
  updateFilter('year', value ? parseInt(value) : null)
}, 300)

const updateFilter = (key, value) => {
  filters.value[key] = value
  assetsStore.setFilter(key, value)
  currentPage.value = 1
  loadAssets()
}

const clearFilter = (key) => {
  filters.value[key] = key === 'year' ? null : ''
  updateFilter(key, filters.value[key])
}

const setStatusFilter = (status) => {
  filters.value.status = status
  updateFilter('status', status)
}

const clearAllFilters = () => {
  searchQuery.value = ''
  filters.value = {
    vehicle_type: '',
    status: '',
    department: '',
    year: null
  }
  assetsStore.clearFilters()
  currentPage.value = 1
  loadAssets()
}

// Data loading
const loadAssets = async (options = {}) => {
  try {
    // Update sort from options
    if (options.sortBy) {
      sortBy.value = options.sortBy
      const sortItem = options.sortBy[0]
      if (sortItem) {
        assetsStore.setSorting(sortItem.key, sortItem.order === 'desc')
      }
    }
    
    // Update page from options
    if (options.page) {
      currentPage.value = options.page
      assetsStore.setPage(options.page)
    }
    
    await assetsStore.fetchAssets({
      page: currentPage.value,
      params: {
        page_size: itemsPerPage.value
      }
    })
  } catch (error) {
    console.error('Failed to load assets:', error)
    showError.value = true
  }
}

// Asset actions
const confirmDelete = (asset) => {
  assetToDelete.value = asset
  deleteDialog.value = true
}

const deleteAsset = async () => {
  if (!assetToDelete.value) return
  
  try {
    await assetsStore.deleteAsset(assetToDelete.value.id)
    deleteDialog.value = false
    assetToDelete.value = null
    
    // Reload current page or go to previous if current is empty
    if (assetsStore.assets.length === 0 && currentPage.value > 1) {
      currentPage.value--
    }
    await loadAssets()
  } catch (error) {
    console.error('Failed to delete asset:', error)
    showError.value = true
  }
}

// Utility functions
const getVehicleTypeColor = (type) => {
  const colors = {
    bus: 'blue',
    truck: 'green',
    tractor: 'orange',
    trailer: 'purple',
    van: 'cyan',
    car: 'indigo',
    equipment: 'brown',
    other: 'grey'
  }
  return colors[type] || 'grey'
}

const getVehicleTypeIcon = (type) => {
  const icons = {
    bus: 'mdi-bus',
    truck: 'mdi-truck',
    tractor: 'mdi-tractor',
    trailer: 'mdi-truck-trailer',
    van: 'mdi-van-passenger',
    car: 'mdi-car',
    equipment: 'mdi-excavator',
    other: 'mdi-help-circle'
  }
  return icons[type] || 'mdi-help-circle'
}

const getStatusColor = (status) => {
  const colors = {
    active: 'success',
    maintenance: 'warning',
    retired: 'error',
    out_of_service: 'grey'
  }
  return colors[status] || 'grey'
}

// CSV Import functions
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleCSVFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndSetCSVFile(file)
  }
}

const handleCSVDrop = (event) => {
  isCSVDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndSetCSVFile(file)
  }
}

const validateAndSetCSVFile = (file) => {
  // Check file type
  if (!file.name.endsWith('.csv')) {
    importError.value = 'File must be in CSV format'
    return
  }
  
  // Check file size (5MB max)
  if (file.size > 5242880) {
    importError.value = 'File size must be less than 5MB'
    return
  }
  
  selectedCSVFile.value = file
  importError.value = ''
  importResults.value = null
}

const clearCSVFile = () => {
  selectedCSVFile.value = null
  if (csvFileInput.value) {
    csvFileInput.value.value = ''
  }
  importResults.value = null
}

const closeImportDialog = () => {
  showImportDialog.value = false
  selectedCSVFile.value = null
  importError.value = ''
  importResults.value = null
  isCSVDragging.value = false
}

const downloadTemplate = async () => {
  try {
    const response = await assetsStore.downloadCSVTemplate()
    
    // Create a blob from the response
    const blob = new Blob([response.data], { type: 'text/csv' })
    
    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'assets_import_template.csv'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to download template:', error)
    importError.value = 'Failed to download template. Please try again.'
  }
}

const importCSV = async () => {
  if (!selectedCSVFile.value) return
  
  isImporting.value = true
  importError.value = ''
  importResults.value = null
  
  try {
    const formData = new FormData()
    formData.append('file', selectedCSVFile.value)
    
    const result = await assetsStore.bulkImportAssets(formData)
    
    importResults.value = result
    
    // If successful import, refresh the assets list
    if (result.success_count > 0) {
      await loadAssets()
      await assetsStore.fetchAssetStats()
    }
    
    // Clear file if all successful
    if (result.error_count === 0) {
      clearCSVFile()
    }
  } catch (error) {
    console.error('Import failed:', error)
    if (error.response?.data?.error) {
      importError.value = error.response.data.error
    } else if (error.response?.data?.errors) {
      importResults.value = error.response.data
    } else {
      importError.value = 'Failed to import CSV file. Please check the file format and try again.'
    }
  } finally {
    isImporting.value = false
  }
}

const getStatusTextClass = (status) => {
  const classes = {
    active: 'text-success',
    maintenance: 'text-warning',
    retired: 'text-error',
    out_of_service: 'text-medium-emphasis'
  }
  return classes[status] || 'text-medium-emphasis'
}

const getStatusIcon = (status) => {
  const icons = {
    active: 'mdi-check-circle',
    maintenance: 'mdi-wrench',
    retired: 'mdi-archive',
    out_of_service: 'mdi-close-circle'
  }
  return icons[status] || 'mdi-help-circle'
}

const formatVehicleType = (type) => {
  return type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')
}

const formatStatus = (status) => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatOdometer = (odometer) => {
  if (!odometer) return '0'
  return new Intl.NumberFormat().format(odometer)
}

const getFilterLabel = (key) => {
  const labels = {
    vehicle_type: 'Type',
    status: 'Status',
    department: 'Department',
    year: 'Year'
  }
  return labels[key] || key
}

// Watch for errors
watch(() => assetsStore.error, (error) => {
  if (error) {
    showError.value = true
  }
})

// Lifecycle
onMounted(async () => {
  // Load statistics and assets
  await Promise.all([
    assetsStore.fetchAssetStats(),
    loadAssets()
  ])
})
</script>

<style scoped>
.v-data-table :deep(.v-data-table__td) {
  padding: 6px 12px;
  font-size: 0.875rem;
}

.v-data-table :deep(.v-data-table__th) {
  font-weight: 600;
  font-size: 0.875rem;
  padding: 8px 12px;
}

.text-no-wrap {
  white-space: nowrap;
}

/* Make the vehicle info column more compact */
.v-data-table :deep(.v-data-table__td:nth-child(2)) {
  line-height: 1.3;
}

/* Column alignments */
/* Type column (4th column) */
.v-data-table :deep(.v-data-table__td:nth-child(4)),
.v-data-table :deep(.v-data-table__th:nth-child(4)) {
  text-align: center !important;
}

/* License column (5th column) */
.v-data-table :deep(.v-data-table__td:nth-child(5)),
.v-data-table :deep(.v-data-table__th:nth-child(5)) {
  text-align: center !important;
}

/* Department column (6th column) */
.v-data-table :deep(.v-data-table__td:nth-child(6)),
.v-data-table :deep(.v-data-table__th:nth-child(6)) {
  text-align: center !important;
}

/* Status column (7th column) */
.v-data-table :deep(.v-data-table__td:nth-child(7)),
.v-data-table :deep(.v-data-table__th:nth-child(7)) {
  text-align: center !important;
}

/* Odometer column (8th column) - right aligned */
.v-data-table :deep(.v-data-table__td:nth-child(8)),
.v-data-table :deep(.v-data-table__th:nth-child(8)) {
  text-align: right !important;
}

/* Docs column (9th column) */
.v-data-table :deep(.v-data-table__td:nth-child(9)),
.v-data-table :deep(.v-data-table__th:nth-child(9)) {
  text-align: center !important;
}

/* Actions column (10th column) */
.v-data-table :deep(.v-data-table__td:nth-child(10)),
.v-data-table :deep(.v-data-table__th:nth-child(10)) {
  text-align: center !important;
}

/* Statistics cards styling */
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

/* Filter section styling */
.filter-section {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  background-color: rgb(var(--v-theme-surface));
}

/* Table section styling */
.table-section {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  background-color: rgb(var(--v-theme-surface));
}

.table-section :deep(.v-data-table) {
  background-color: transparent;
}

.import-zone {
  border: 2px dashed #e0e0e0;
  background-color: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.import-zone:hover {
  border-color: #1976d2;
  background-color: #f5f5f5;
}

.import-zone--active {
  border-color: #1976d2;
  background-color: #e3f2fd;
}

.thumbnail-container {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
}

.asset-thumbnail {
  width: 40px;
  height: 40px;
  border-radius: 4px;
}

.no-image-placeholder {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}
</style>