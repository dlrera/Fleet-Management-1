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
        >
          Add Asset
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
          <div class="d-flex ga-1">
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

// Table headers configuration
const headers = [
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
    width: '100px'
  },
  {
    title: 'License',
    key: 'license_plate',
    sortable: true,
    width: '100px'
  },
  {
    title: 'Department',
    key: 'department',
    sortable: true,
    width: '120px'
  },
  {
    title: 'Status',
    key: 'status',
    sortable: true,
    width: '100px'
  },
  {
    title: 'Odometer',
    key: 'current_odometer',
    sortable: true,
    width: '100px'
  },
  {
    title: 'Docs',
    key: 'documents_count',
    sortable: true,
    width: '70px'
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
  font-weight: 500;
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
</style>