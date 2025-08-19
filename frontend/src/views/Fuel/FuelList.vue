<template>
  <v-container fluid>
    <!-- Page Header -->
    <v-row class="mb-3">
      <v-col cols="12" md="8">
        <h1 class="text-h5 font-weight-medium mb-1">
          Fuel Management
        </h1>
        <p class="text-body-2 text-medium-emphasis">
          Track fuel consumption, costs, and efficiency across your fleet
        </p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-btn
          v-if="authStore.canCreateFuel"
          color="primary"
          size="small"
          prepend-icon="mdi-plus"
          @click="$router.push('/fuel/new')"
          class="mr-2"
        >
          Add Fuel Transaction
        </v-btn>
        <v-btn
          v-if="authStore.canCreateFuel"
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
    <v-row v-if="fuelStore.hasStats" class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 cursor-pointer"
          @click="clearFilters"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ formatNumber(fuelStore.totalFuelVolume) }}
              </div>
              <div class="text-caption text-medium-emphasis">Total Gallons</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-gas-station</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div class="stat-card pa-3">
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                ${{ formatNumber(fuelStore.totalFuelCost) }}
              </div>
              <div class="text-caption text-medium-emphasis">Total Cost</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-currency-usd</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div class="stat-card pa-3">
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ formatNumber(fuelStore.averageMPG, 1) }}
              </div>
              <div class="text-caption text-medium-emphasis">Average MPG</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-speedometer</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3"
          :class="{ 'cursor-pointer': fuelStore.openAlertsCount > 0 }"
          @click="fuelStore.openAlertsCount > 0 ? setFilter('anomalies_only', 'true') : null"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ fuelStore.openAlertsCount }}
              </div>
              <div class="text-caption text-medium-emphasis">Open Alerts</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-alert</v-icon>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Search and Filter Section -->
    <div class="filter-section pa-3 mb-3">
      <div class="py-1">
        <v-row class="align-center">
          <!-- Vehicle Filter -->
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchQuery"
              label="Search"
              placeholder="Vehicle, vendor, transaction..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @update:model-value="applySearch"
            />
          </v-col>
          
          <v-col cols="6" sm="3" md="2">
            <v-select
              v-model="filters.asset_id"
              :items="assetOptions"
              item-title="display_name"
              item-value="id"
              label="Vehicle"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <!-- Fuel Type Filter -->
          <v-col cols="6" sm="3" md="2">
            <v-select
              v-model="filters.product_type"
              :items="productTypeOptions"
              label="Fuel Type"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <!-- Date Range -->
          <v-col cols="6" sm="3" md="2">
            <v-text-field
              v-model="filters.start_date"
              label="From"
              type="date"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="6" sm="3" md="2">
            <v-text-field
              v-model="filters.end_date"
              label="To"
              type="date"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="applyFilters"
            />
          </v-col>
        </v-row>
      </div>
    </div>

    <!-- Fuel Transactions Table -->
    <div class="table-section">
      <v-data-table-server
        v-model:items-per-page="pageSize"
        v-model:page="currentPage"
        :headers="tableHeaders"
        :items="fuelStore.transactions"
        :items-length="fuelStore.totalTransactions"
        :loading="fuelStore.isLoading"
        item-value="id"
        @update:options="loadTransactions"
      >
        <template #header.mpg="{ column }">
          <div class="d-flex align-center justify-center">
            <span>{{ column.title }}</span>
            <v-tooltip location="top">
              <template v-slot:activator="{ props }">
                <v-icon 
                  v-bind="props"
                  size="small"
                  class="ml-1"
                  style="cursor: help;"
                >
                  mdi-information-outline
                </v-icon>
              </template>
              <div style="max-width: 300px;">
                <strong>Miles Per Gallon (MPG)</strong><br>
                Calculated as: (Current Odometer - Previous Odometer) ÷ Fuel Volume<br><br>
                Shows "N/A" when:
                <ul style="margin: 0; padding-left: 20px;">
                  <li>No previous fuel transaction exists</li>
                  <li>Previous odometer reading is missing</li>
                  <li>Current odometer reading is missing</li>
                </ul>
              </div>
            </v-tooltip>
          </div>
        </template>
        <template #item.asset_details="{ item }">
          <div>
            <div class="font-weight-medium">{{ item.asset_details?.asset_id }}</div>
            <div class="text-caption text-medium-emphasis">
              {{ item.asset_details?.make }} {{ item.asset_details?.model }}
            </div>
          </div>
        </template>
        
        <template #item.timestamp="{ item }">
          <div>
            <div>{{ formatDate(item.timestamp) }}</div>
            <div class="text-caption text-medium-emphasis">{{ item.days_ago }} days ago</div>
          </div>
        </template>
        
        <template #item.volume="{ item }">
          <div class="font-weight-medium">
            {{ formatNumber(item.volume, 1) }} {{ item.unit_display }}
          </div>
        </template>
        
        <template #item.total_cost="{ item }">
          <div class="font-weight-medium">
            ${{ formatNumber(item.total_cost) }}
          </div>
          <div class="text-caption text-medium-emphasis" v-if="item.unit_price">
            ${{ formatNumber(item.unit_price, 3) }}/{{ item.unit_display }}
          </div>
        </template>
        
        <template #item.mpg="{ item }">
          <div v-if="item.mpg" class="font-weight-medium">
            {{ formatNumber(item.mpg, 1) }} MPG
          </div>
          <div v-else class="text-medium-emphasis">
            <v-tooltip location="top">
              <template v-slot:activator="{ props }">
                <span v-bind="props" style="cursor: help;">N/A</span>
              </template>
              <span>MPG cannot be calculated without previous odometer reading</span>
            </v-tooltip>
          </div>
        </template>
        
        <template #item.vendor="{ item }">
          <div v-if="item.vendor">{{ item.vendor }}</div>
          <div v-else class="text-medium-emphasis">Unknown</div>
        </template>
        
        <template #item.entry_source="{ item }">
          <v-chip 
            :color="getSourceColor(item.entry_source)"
            size="small"
            variant="tonal"
          >
            {{ item.entry_source_display }}
          </v-chip>
        </template>
        
        <template #item.is_anomaly="{ item }">
          <v-tooltip v-if="item.is_anomaly" location="top">
            <template v-slot:activator="{ props }">
              <v-icon 
                v-bind="props"
                color="warning"
                size="small"
                style="cursor: help;"
              >
                mdi-alert
              </v-icon>
            </template>
            <div>
              <strong>Alert Details:</strong>
              <div v-if="item.mpg && item.mpg < 5">• Low MPG ({{ formatNumber(item.mpg, 1) }}) - Possible data error or vehicle issue</div>
              <div v-if="item.unit_price && item.unit_price > 10">• High price (${{ formatNumber(item.unit_price, 2) }}/{{ item.unit_display }}) - Unusual pricing</div>
              <div v-if="item.distance_delta && item.distance_delta < 0">• Odometer rollback detected - Data entry error</div>
              <div v-if="!item.mpg && !item.unit_price && !item.distance_delta">• Anomaly detected - Review transaction details</div>
            </div>
          </v-tooltip>
        </template>
        
        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-eye"
            size="small"
            variant="text"
            @click="viewTransaction(item)"
            title="View Details"
          />
          <v-btn
            v-if="canEditTransaction(item)"
            icon="mdi-pencil"
            size="small"
            variant="text"
            @click="$router.push(`/fuel/${item.id}/edit`)"
            title="Edit"
          />
          <v-btn
            v-if="authStore.canDeleteFuel"
            icon="mdi-delete"
            size="small"
            variant="text"
            color="error"
            @click="confirmDelete(item)"
            title="Delete"
          />
        </template>
      </v-data-table-server>
    </div>

    <!-- Import CSV Dialog -->
    <v-dialog v-model="showImportDialog" max-width="600">
      <v-card>
        <v-card-title>Import Fuel Transactions from CSV</v-card-title>
        <v-card-text>
          <v-form ref="importForm" @submit.prevent="handleImport">
            <!-- Instructions -->
            <v-alert
              type="info"
              variant="tonal"
              class="mb-4"
            >
              <div class="text-body-2">
                Upload a CSV file with fuel transaction data. Required columns:
                <strong>Asset ID, Date, Product Type, Volume, Total Cost</strong>
              </div>
              <v-btn
                size="small"
                variant="text"
                class="mt-2"
                @click="downloadFuelTemplate"
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
            :loading="fuelStore.isImporting"
            :disabled="!importFile || importFile.length === 0"
            @click="handleImport"
          >
            Import
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete Transaction</v-card-title>
        <v-card-text>
          Are you sure you want to delete this fuel transaction? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn 
            color="error"
            :loading="fuelStore.isDeleting"
            @click="handleDelete"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- View Transaction Dialog -->
    <v-dialog v-model="showViewDialog" max-width="600">
      <v-card v-if="viewingTransaction">
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Fuel Transaction Details</span>
          <v-btn
            icon="mdi-close"
            variant="text"
            size="small"
            @click="showViewDialog = false"
          />
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <div class="text-caption text-medium-emphasis">Vehicle</div>
              <div class="font-weight-medium">{{ viewingTransaction.asset_details?.asset_id }}</div>
              <div class="text-body-2">{{ viewingTransaction.asset_details?.make }} {{ viewingTransaction.asset_details?.model }}</div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-caption text-medium-emphasis">Date</div>
              <div class="font-weight-medium">{{ formatDate(viewingTransaction.timestamp) }}</div>
              <div class="text-body-2">{{ viewingTransaction.days_ago }} days ago</div>
            </v-col>
          </v-row>
          
          <v-row class="mt-2">
            <v-col cols="12" md="6">
              <div class="text-caption text-medium-emphasis">Fuel Type</div>
              <div class="font-weight-medium">{{ viewingTransaction.product_type_display }}</div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-caption text-medium-emphasis">Volume</div>
              <div class="font-weight-medium">{{ formatNumber(viewingTransaction.volume, 1) }} {{ viewingTransaction.unit_display }}</div>
            </v-col>
          </v-row>
          
          <v-row class="mt-2">
            <v-col cols="12" md="6">
              <div class="text-caption text-medium-emphasis">Total Cost</div>
              <div class="font-weight-medium">${{ formatNumber(viewingTransaction.total_cost) }}</div>
              <div class="text-body-2" v-if="viewingTransaction.unit_price">
                ${{ formatNumber(viewingTransaction.unit_price, 3) }}/{{ viewingTransaction.unit_display }}
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-caption text-medium-emphasis">MPG</div>
              <div v-if="viewingTransaction.mpg" class="font-weight-medium">
                {{ formatNumber(viewingTransaction.mpg, 1) }} MPG
              </div>
              <div v-else class="text-medium-emphasis">N/A</div>
            </v-col>
          </v-row>
          
          <v-row class="mt-2" v-if="viewingTransaction.odometer">
            <v-col cols="12" md="6">
              <div class="text-caption text-medium-emphasis">Odometer</div>
              <div class="font-weight-medium">{{ formatNumber(viewingTransaction.odometer) }} miles</div>
            </v-col>
            <v-col cols="12" md="6" v-if="viewingTransaction.distance_delta">
              <div class="text-caption text-medium-emphasis">Distance Since Last Fill</div>
              <div class="font-weight-medium">{{ formatNumber(viewingTransaction.distance_delta) }} miles</div>
            </v-col>
          </v-row>
          
          <v-row class="mt-2">
            <v-col cols="12" md="6">
              <div class="text-caption text-medium-emphasis">Vendor</div>
              <div class="font-weight-medium">{{ viewingTransaction.vendor || 'Unknown' }}</div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-caption text-medium-emphasis">Entry Source</div>
              <v-chip 
                :color="getSourceColor(viewingTransaction.entry_source)"
                size="small"
                variant="tonal"
              >
                {{ viewingTransaction.entry_source_display }}
              </v-chip>
            </v-col>
          </v-row>
          
          <v-row class="mt-2" v-if="viewingTransaction.notes">
            <v-col cols="12">
              <div class="text-caption text-medium-emphasis">Notes</div>
              <div class="font-weight-medium">{{ viewingTransaction.notes }}</div>
            </v-col>
          </v-row>
          
          <v-alert 
            v-if="viewingTransaction.is_anomaly"
            type="warning"
            variant="tonal"
            class="mt-3"
          >
            <strong>Alert:</strong> This transaction has been flagged for review
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            v-if="canEditTransaction(viewingTransaction)"
            color="primary"
            variant="outlined"
            prepend-icon="mdi-pencil"
            @click="editFromView"
          >
            Edit Transaction
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFuelStore } from '../../stores/fuel'
import { useAssetsStore } from '../../stores/assets'
import { useAuthStore } from '../../stores/auth'

// Stores and router
const router = useRouter()
const fuelStore = useFuelStore()
const assetsStore = useAssetsStore()
const authStore = useAuthStore()

// Component state
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const showImportDialog = ref(false)
const showDeleteDialog = ref(false)
const showViewDialog = ref(false)
const importFile = ref(null)
const transactionToDelete = ref(null)
const viewingTransaction = ref(null)
const isCSVDragging = ref(false)

// Filters
const filters = ref({
  asset_id: '',
  product_type: '',
  start_date: '',
  end_date: ''
})

// Table configuration
const tableHeaders = [
  { title: 'Vehicle', key: 'asset_details', sortable: false },
  { title: 'Date', key: 'timestamp', sortable: true },
  { title: 'Fuel Type', key: 'product_type_display', sortable: true },
  { title: 'Volume', key: 'volume', sortable: true },
  { title: 'Cost', key: 'total_cost', sortable: true },
  { 
    title: 'MPG', 
    key: 'mpg', 
    sortable: true,
    align: 'center',
    headerProps: {
      class: 'mpg-header'
    }
  },
  { title: 'Vendor', key: 'vendor', sortable: false },
  { title: 'Source', key: 'entry_source', sortable: false },
  { title: 'Alert', key: 'is_anomaly', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false }
]

// Options for dropdowns
const productTypeOptions = [
  { title: 'Gasoline', value: 'gasoline' },
  { title: 'Diesel', value: 'diesel' },
  { title: 'DEF', value: 'def' },
  { title: 'CNG', value: 'cng' },
  { title: 'LNG', value: 'lng' },
  { title: 'Propane', value: 'propane' },
  { title: 'Electricity', value: 'electricity' },
  { title: 'Other', value: 'other' }
]

// Computed properties
const assetOptions = computed(() => {
  return assetsStore.assets.map(asset => ({
    ...asset,
    display_name: `${asset.asset_id} - ${asset.make} ${asset.model}`
  }))
})

// Methods
const canEditTransaction = (transaction) => {
  // Admin and Fleet Manager can edit all
  if (authStore.isAdmin || authStore.isFleetManager) return true
  
  // Technicians can edit their own entries
  if (authStore.isTechnician && transaction.created_by === authStore.currentUser?.id) {
    return true
  }
  
  return false
}

const formatNumber = (value, decimals = 0) => {
  if (!value) return '0'
  return parseFloat(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const getSourceColor = (source) => {
  const colors = {
    manual: 'primary',
    csv_import: 'info',
    fuel_card: 'success',
    tank_controller: 'warning',
    ev_charger_api: 'purple'
  }
  return colors[source] || 'default'
}

const loadTransactions = async (options) => {
  currentPage.value = options.page
  pageSize.value = options.itemsPerPage
  
  const params = {
    page: options.page,
    page_size: options.itemsPerPage,
    ordering: options.sortBy?.length ? 
      (options.sortDesc?.[0] ? `-${options.sortBy[0]}` : options.sortBy[0]) : 
      '-timestamp',
    // Include all active filters
    ...(filters.value.asset_id && { asset: filters.value.asset_id }),
    ...(filters.value.product_type && { product_type: filters.value.product_type }),
    ...(filters.value.start_date && { start_date: filters.value.start_date }),
    ...(filters.value.end_date && { end_date: filters.value.end_date }),
    ...(searchQuery.value && { search: searchQuery.value })
  }
  
  await fuelStore.fetchTransactions({ params })
}

const applyFilters = () => {
  // Reload transactions with new filters
  currentPage.value = 1
  loadTransactions({ page: 1, itemsPerPage: pageSize.value })
}

const applySearch = () => {
  currentPage.value = 1
  loadTransactions({ page: 1, itemsPerPage: pageSize.value })
}

const setFilter = (key, value) => {
  filters.value[key] = value
  applyFilters()
}

const clearFilters = () => {
  filters.value = {
    asset_id: '',
    product_type: '',
    start_date: '',
    end_date: ''
  }
  searchQuery.value = ''
  loadTransactions({ page: 1, itemsPerPage: pageSize.value })
}

const handleImport = async () => {
  if (!importFile.value) return
  
  try {
    await fuelStore.importCSV(importFile.value[0])
    showImportDialog.value = false
    importFile.value = null
    
    // Reload data
    loadTransactions({ page: currentPage.value, itemsPerPage: pageSize.value })
  } catch (error) {
    console.error('Import failed:', error)
  }
}

const confirmDelete = (transaction) => {
  transactionToDelete.value = transaction
  showDeleteDialog.value = true
}

const handleDelete = async () => {
  if (!transactionToDelete.value) return
  
  try {
    await fuelStore.deleteTransaction(transactionToDelete.value.id)
    showDeleteDialog.value = false
    transactionToDelete.value = null
    
    // Reload current page
    loadTransactions({ page: currentPage.value, itemsPerPage: pageSize.value })
  } catch (error) {
    console.error('Delete failed:', error)
  }
}

const viewTransaction = (transaction) => {
  viewingTransaction.value = transaction
  showViewDialog.value = true
}

const editFromView = () => {
  showViewDialog.value = false
  router.push(`/fuel/${viewingTransaction.value.id}/edit`)
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

const downloadFuelTemplate = () => {
  // Create a CSV template for fuel import
  const csvContent = `Asset ID,Date,Product Type,Volume,Unit,Total Cost,Odometer,Vendor,Notes
VEH001,2024-01-15,gasoline,15.5,gal,65.25,45000,Shell Station,Regular fill-up
VEH002,2024-01-16,diesel,25.0,gal,95.00,112000,BP,Highway travel`
  
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'fuel_import_template.csv'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// Lifecycle hooks
onMounted(async () => {
  // Load assets for filter dropdown
  if (!assetsStore.hasAssets) {
    await assetsStore.fetchAssets()
  }
  
  // Load fuel statistics
  await fuelStore.fetchStats()
  
  // Load initial transactions
  await loadTransactions({ page: 1, itemsPerPage: 10 })
})
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

.cursor-pointer {
  cursor: pointer;
}
</style>