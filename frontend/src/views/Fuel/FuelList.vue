<template>
  <div class="fuel-list-container">
    <!-- Header -->
    <div class="page-header">
      <div class="d-flex align-center justify-space-between">
        <div>
          <h1 class="text-h4 mb-1">Fuel Management</h1>
          <p class="text-body-2 text-medium-emphasis">
            Track fuel consumption, costs, and efficiency across your fleet
          </p>
        </div>
        
        <div class="d-flex align-center gap-3">
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="$router.push('/fuel/new')"
          >
            Add Fuel Transaction
          </v-btn>
          <v-btn
            variant="outlined"
            prepend-icon="mdi-upload"
            @click="showImportDialog = true"
          >
            Import CSV
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <div class="stat-card" @click="clearFilters">
          <div class="stat-icon">
            <v-icon size="24" color="primary">mdi-gas-station</v-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(fuelStore.totalFuelVolume) }}</div>
            <div class="stat-label">Total Gallons</div>
            <div class="stat-sublabel">{{ fuelStore.fuelStats.total_transactions || 0 }} transactions</div>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" md="3">
        <div class="stat-card">
          <div class="stat-icon">
            <v-icon size="24" color="success">mdi-currency-usd</v-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">${{ formatNumber(fuelStore.totalFuelCost) }}</div>
            <div class="stat-label">Total Cost</div>
            <div class="stat-sublabel">30 days</div>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" md="3">
        <div class="stat-card">
          <div class="stat-icon">
            <v-icon size="24" color="info">mdi-speedometer</v-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(fuelStore.averageMPG, 1) }}</div>
            <div class="stat-label">Average MPG</div>
            <div class="stat-sublabel">Fleet average</div>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" md="3">
        <div class="stat-card" @click="setFilter('anomalies_only', 'true')" :class="{ 'clickable': fuelStore.openAlertsCount > 0 }">
          <div class="stat-icon">
            <v-icon size="24" :color="fuelStore.criticalAlertsCount > 0 ? 'error' : 'warning'">mdi-alert</v-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ fuelStore.openAlertsCount }}</div>
            <div class="stat-label">Open Alerts</div>
            <div class="stat-sublabel">{{ fuelStore.criticalAlertsCount }} critical</div>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.asset_id"
              :items="assetOptions"
              item-title="display_name"
              item-value="id"
              label="Filter by Vehicle"
              variant="outlined"
              density="compact"
              clearable
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.product_type"
              :items="productTypeOptions"
              label="Filter by Fuel Type"
              variant="outlined"
              density="compact"
              clearable
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filters.start_date"
              label="Start Date"
              type="date"
              variant="outlined"
              density="compact"
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filters.end_date"
              label="End Date"
              type="date"
              variant="outlined"
              density="compact"
              @update:model-value="applyFilters"
            />
          </v-col>
        </v-row>
        
        <v-row v-if="fuelStore.hasActiveFilters">
          <v-col cols="12">
            <v-btn
              variant="outlined"
              size="small"
              prepend-icon="mdi-filter-off"
              @click="clearFilters"
            >
              Clear Filters
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Fuel Transactions Table -->
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <span>Fuel Transactions</span>
        <v-text-field
          v-model="searchQuery"
          placeholder="Search transactions..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          style="max-width: 300px;"
          @update:model-value="applySearch"
        />
      </v-card-title>
      
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
            N/A
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
          <v-icon 
            v-if="item.is_anomaly"
            color="warning"
            size="small"
          >
            mdi-alert
          </v-icon>
        </template>
        
        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-pencil"
            size="small"
            variant="text"
            @click="$router.push(`/fuel/${item.id}/edit`)"
          />
          <v-btn
            icon="mdi-delete"
            size="small"
            variant="text"
            color="error"
            @click="confirmDelete(item)"
          />
        </template>
      </v-data-table-server>
    </v-card>

    <!-- Import CSV Dialog -->
    <v-dialog v-model="showImportDialog" max-width="500">
      <v-card>
        <v-card-title>Import Fuel Transactions</v-card-title>
        <v-card-text>
          <v-file-input
            v-model="importFile"
            label="Select CSV file"
            accept=".csv"
            prepend-icon="mdi-file-excel"
            variant="outlined"
          />
          <div class="text-caption text-medium-emphasis mt-2">
            CSV should include columns: Asset ID, Date, Product Type, Volume, Total Cost
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showImportDialog = false">Cancel</v-btn>
          <v-btn 
            color="primary"
            :loading="fuelStore.isImporting"
            :disabled="!importFile"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFuelStore } from '../../stores/fuel'
import { useAssetsStore } from '../../stores/assets'

// Stores
const fuelStore = useFuelStore()
const assetsStore = useAssetsStore()

// Component state
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const showImportDialog = ref(false)
const showDeleteDialog = ref(false)
const importFile = ref(null)
const transactionToDelete = ref(null)

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
  { title: 'MPG', key: 'mpg', sortable: true },
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
      '-timestamp'
  }
  
  await fuelStore.fetchTransactions({ params })
}

const applyFilters = () => {
  // Apply filters to store
  Object.keys(filters.value).forEach(key => {
    fuelStore.setFilter(key, filters.value[key])
  })
  
  // Reload transactions
  currentPage.value = 1
  loadTransactions({ page: 1, itemsPerPage: pageSize.value })
}

const applySearch = () => {
  fuelStore.searchQuery = searchQuery.value
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
  fuelStore.clearFilters()
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
.fuel-list-container {
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

.gap-3 {
  gap: 12px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.2s ease;
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  transform: translateY(-1px);
}

.stat-icon {
  background: #f5f5f5;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1976d2;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 2px;
}

.stat-sublabel {
  font-size: 0.75rem;
  color: #999;
}
</style>