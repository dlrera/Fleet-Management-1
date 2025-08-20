<template>
  <v-container fluid>
    <!-- Error Notification -->
    <v-snackbar
      v-model="errorSnackbar"
      :timeout="5000"
      color="error"
      top
    >
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="errorSnackbar = false">Close</v-btn>
      </template>
    </v-snackbar>

    <!-- Success Notification -->
    <v-snackbar
      v-model="successSnackbar"
      :timeout="3000"
      color="success"
      top
    >
      {{ successMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="successSnackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h5 font-weight-medium">Asset Lifecycle Management</h1>
          <div>
            <v-btn color="primary" size="small" @click="createNewAsset" class="mr-2">
              <v-icon left>mdi-plus</v-icon>
              Add Asset
            </v-btn>
            <v-btn variant="outlined" size="small" @click="showReplacementSchedule">
              <v-icon left>mdi-calendar-clock</v-icon>
              Replacement Schedule
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row>
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3" 
          @click="filterByCondition(null)" 
          @keydown.enter="filterByCondition(null)"
          :class="{ active: !filters.condition }"
          tabindex="0"
          role="button"
          :aria-label="`Filter by all assets. Currently showing ${stats.total} assets`"
          :aria-pressed="!filters.condition"
        >
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">Total Assets</span>
            <span class="text-h6 font-weight-medium">{{ stats.total }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3" 
          @click="filterByCondition('critical')" 
          @keydown.enter="filterByCondition('critical')"
          :class="{ active: filters.condition === 'critical' }"
          tabindex="0"
          role="button"
          :aria-label="`Filter by critical condition assets. ${stats.critical} assets in critical condition`"
          :aria-pressed="filters.condition === 'critical'"
        >
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">Critical Condition</span>
            <span class="text-h6 font-weight-medium text-red">{{ stats.critical }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 non-clickable"
          role="status"
          :aria-label="`Total replacement value: $${formatCurrency(stats.totalReplacementCost)}`"
        >
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">Replacement Value</span>
            <span class="text-h6 font-weight-medium">${{ formatCurrency(stats.totalReplacementCost) }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3" 
          @click="showMaintenanceAnalysis" 
          @keydown.enter="showMaintenanceAnalysis"
          tabindex="0"
          role="button"
          :aria-label="`View maintenance analysis. ${stats.highMaintenance} assets with high maintenance costs`"
        >
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">High Maintenance</span>
            <span class="text-h6 font-weight-medium text-orange">{{ stats.highMaintenance }}</span>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Filter Section -->
    <v-row>
      <v-col cols="12">
        <div class="filter-section pa-3 mb-3">
          <v-row>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.category"
                :items="categoryOptions"
                label="Asset Category"
                clearable
                density="compact"
                variant="outlined"
              ></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.condition"
                :items="conditionOptions"
                label="Condition"
                clearable
                density="compact"
                variant="outlined"
              ></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.department"
                :items="departmentOptions"
                label="Department"
                clearable
                density="compact"
                variant="outlined"
              ></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="searchQuery"
                label="Search assets..."
                prepend-inner-icon="mdi-magnify"
                clearable
                density="compact"
                variant="outlined"
                @input="debouncedSearch"
              ></v-text-field>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>

    <!-- Assets Table -->
    <v-row>
      <v-col cols="12">
        <div class="table-section" role="region" aria-label="Assets data table">
          <!-- Empty State -->
          <div v-if="!loading && assets.length === 0" class="text-center pa-8">
            <v-icon size="64" color="grey">mdi-package-variant</v-icon>
            <h3 class="text-h6 mt-4">No assets found</h3>
            <p class="text-body-2 text-medium-emphasis mt-2">
              {{ filters.condition || filters.category || filters.department || searchQuery 
                ? 'Try adjusting your filters or search criteria' 
                : 'Get started by adding your first asset' }}
            </p>
            <v-btn 
              v-if="!filters.condition && !filters.category && !filters.department && !searchQuery"
              color="primary" 
              class="mt-4"
              @click="createNewAsset"
            >
              Add First Asset
            </v-btn>
            <v-btn
              v-else
              variant="outlined"
              class="mt-4"
              @click="clearFilters"
            >
              Clear Filters
            </v-btn>
          </div>
          <!-- Loading Skeleton -->
          <div v-if="loading && assets.length === 0" class="pa-4">
            <v-skeleton-loader type="table-heading"></v-skeleton-loader>
            <v-skeleton-loader type="table-row" v-for="i in 5" :key="i"></v-skeleton-loader>
          </div>

          <v-data-table-server
            v-else
            :headers="headers"
            :items="assets"
            :loading="loading"
            :items-length="totalItems"
            :items-per-page="itemsPerPage"
            @update:page="loadAssets"
            @update:items-per-page="loadAssets"
          >
            <template v-slot:item.asset_name="{ item }">
              <a @click="viewAsset(item)" class="text-primary" style="cursor: pointer;">
                {{ item.asset_name }}
              </a>
            </template>
            <template v-slot:item.current_condition="{ item }">
              <v-chip size="small" :color="getConditionColor(item.current_condition)">
                {{ item.condition_display }}
              </v-chip>
            </template>
            <template v-slot:item.lifecycle_percentage="{ item }">
              <v-progress-linear
                :model-value="item.lifecycle_percentage"
                :color="getLifecycleColor(item.lifecycle_percentage)"
                height="20"
                rounded
              >
                <template v-slot:default>
                  <span class="text-caption">{{ Math.round(item.lifecycle_percentage) }}%</span>
                </template>
              </v-progress-linear>
            </template>
            <template v-slot:item.replacement_cost="{ item }">
              ${{ formatCurrency(item.replacement_cost) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn icon="mdi-eye" size="small" variant="text" @click="viewAsset(item)"></v-btn>
              <v-btn icon="mdi-pencil" size="small" variant="text" @click="editAsset(item)"></v-btn>
              <v-btn 
                icon="mdi-clipboard-check" 
                size="small" 
                variant="text" 
                @click="updateCondition(item)"
                title="Update Condition"
              ></v-btn>
            </template>
          </v-data-table-server>
        </div>
      </v-col>
    </v-row>

    <!-- Replacement Schedule Dialog -->
    <v-dialog v-model="scheduleDialog" max-width="800">
      <v-card>
        <v-card-title>Asset Replacement Schedule</v-card-title>
        <v-card-text>
          <v-timeline v-if="replacementSchedule.length">
            <v-timeline-item
              v-for="year in replacementSchedule"
              :key="year.year"
              :dot-color="year.year <= new Date().getFullYear() + 1 ? 'red' : 'primary'"
            >
              <template v-slot:opposite>
                <span class="text-h6">{{ year.year }}</span>
              </template>
              <v-card>
                <v-card-subtitle>
                  {{ year.asset_count }} assets - ${{ formatCurrency(year.total_cost) }}
                </v-card-subtitle>
                <v-card-text>
                  <v-list dense>
                    <v-list-item v-for="asset in year.assets.slice(0, 3)" :key="asset.id">
                      <v-list-item-title>{{ asset.asset_name }}</v-list-item-title>
                      <v-list-item-subtitle>
                        ${{ formatCurrency(asset.replacement_cost) }} - {{ asset.condition }}
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item v-if="year.assets.length > 3">
                      <v-list-item-title class="text-caption">
                        ... and {{ year.assets.length - 3 }} more
                      </v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-timeline-item>
          </v-timeline>
          <v-alert v-else type="info">
            No assets scheduled for replacement
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="scheduleDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Condition Update Dialog -->
    <v-dialog v-model="conditionDialog" max-width="500">
      <v-card>
        <v-card-title>Update Asset Condition</v-card-title>
        <v-card-text>
          <v-form ref="conditionForm">
            <v-select
              v-model="conditionUpdate.condition"
              :items="conditionOptions"
              label="New Condition"
              required
              variant="outlined"
              density="compact"
            ></v-select>
            <v-text-field
              v-model="conditionUpdate.assessment_date"
              label="Assessment Date"
              type="date"
              required
              variant="outlined"
              density="compact"
            ></v-text-field>
            <v-textarea
              v-model="conditionUpdate.notes"
              label="Notes"
              rows="3"
              variant="outlined"
              density="compact"
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="conditionDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveConditionUpdate">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCapitalPlanningStore } from '@/stores/capitalPlanning'

const router = useRouter()
const store = useCapitalPlanningStore()

const loading = ref(false)
const searchQuery = ref('')
const itemsPerPage = ref(10)
const totalItems = ref(0)
const scheduleDialog = ref(false)
const conditionDialog = ref(false)
const selectedAsset = ref(null)
const replacementSchedule = ref([])
const errorSnackbar = ref(false)
const errorMessage = ref('')
const successSnackbar = ref(false)
const successMessage = ref('')

const filters = ref({
  category: null,
  condition: null,
  department: null
})

const conditionUpdate = ref({
  condition: '',
  assessment_date: new Date().toISOString().split('T')[0],
  notes: ''
})

const assets = computed(() => store.assetLifecycles)

const stats = ref({
  total: 0,
  critical: 0,
  totalReplacementCost: 0,
  highMaintenance: 0
})

const headers = [
  { title: 'Asset Name', key: 'asset_name', sortable: true },
  { title: 'Code', key: 'asset_code', sortable: true },
  { title: 'Category', key: 'category_display', sortable: true },
  { title: 'Location', key: 'location', sortable: true },
  { title: 'Condition', key: 'current_condition', sortable: true },
  { title: 'Lifecycle', key: 'lifecycle_percentage', sortable: false },
  { title: 'Replacement Cost', key: 'replacement_cost', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

const categoryOptions = [
  { title: 'Building', value: 'building' },
  { title: 'Vehicle', value: 'vehicle' },
  { title: 'Equipment', value: 'equipment' },
  { title: 'Infrastructure', value: 'infrastructure' },
  { title: 'Technology', value: 'technology' },
  { title: 'Other', value: 'other' }
]

const conditionOptions = [
  { title: 'Excellent', value: 'excellent' },
  { title: 'Good', value: 'good' },
  { title: 'Fair', value: 'fair' },
  { title: 'Poor', value: 'poor' },
  { title: 'Critical', value: 'critical' }
]

const departmentOptions = ref([])

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US').format(value || 0)
}

const getConditionColor = (condition) => {
  const colors = {
    excellent: 'green',
    good: 'light-green',
    fair: 'yellow',
    poor: 'orange',
    critical: 'red'
  }
  return colors[condition] || 'grey'
}

const getLifecycleColor = (percentage) => {
  if (percentage >= 90) return 'red'
  if (percentage >= 75) return 'orange'
  if (percentage >= 50) return 'yellow'
  return 'green'
}

const loadAssets = async () => {
  loading.value = true
  try {
    await store.fetchAssetLifecycles({
      search: searchQuery.value,
      asset_category: filters.value.category,
      current_condition: filters.value.condition,
      department: filters.value.department,
      page_size: itemsPerPage.value
    })
    totalItems.value = store.assetLifecycleCount
    await loadStats()
  } catch (error) {
    console.error('Failed to load assets:', error)
    showError('Failed to load assets. Please try again.')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  // In a real app, this would be an API call
  stats.value = {
    total: totalItems.value,
    critical: assets.value.filter(a => a.current_condition === 'critical').length,
    totalReplacementCost: assets.value.reduce((sum, a) => sum + (a.replacement_cost || 0), 0),
    highMaintenance: assets.value.filter(a => a.maintenance_cost_ratio > 50).length
  }
}

const filterByCondition = (condition) => {
  filters.value.condition = condition
  loadAssets()
}

const createNewAsset = () => {
  router.push('/capital-planning/asset-lifecycle/new')
}

const viewAsset = (asset) => {
  router.push(`/capital-planning/asset-lifecycle/${asset.id}`)
}

const editAsset = (asset) => {
  router.push(`/capital-planning/asset-lifecycle/${asset.id}/edit`)
}

const updateCondition = (asset) => {
  selectedAsset.value = asset
  conditionUpdate.value.condition = asset.current_condition
  conditionDialog.value = true
}

const saveConditionUpdate = async () => {
  if (!selectedAsset.value) return
  
  try {
    await store.updateAssetCondition(selectedAsset.value.id, conditionUpdate.value)
    conditionDialog.value = false
    showSuccess('Asset condition updated successfully')
    await loadAssets()
  } catch (error) {
    console.error('Failed to update condition:', error)
    showError('Failed to update asset condition. Please try again.')
  }
}

const showReplacementSchedule = async () => {
  try {
    replacementSchedule.value = await store.fetchReplacementSchedule()
    scheduleDialog.value = true
  } catch (error) {
    console.error('Failed to load replacement schedule:', error)
    showError('Failed to load replacement schedule. Please try again.')
  }
}

const showMaintenanceAnalysis = () => {
  router.push('/capital-planning/asset-lifecycle/maintenance-analysis')
}

const clearFilters = () => {
  filters.value = {
    category: null,
    condition: null,
    department: null
  }
  searchQuery.value = ''
  loadAssets()
}

const showError = (message) => {
  errorMessage.value = message
  errorSnackbar.value = true
}

const showSuccess = (message) => {
  successMessage.value = message
  successSnackbar.value = true
}

const debouncedSearch = () => {
  clearTimeout(window.searchTimeout)
  window.searchTimeout = setTimeout(() => {
    loadAssets()
  }, 500)
}

onMounted(() => {
  loadAssets()
})
</script>

<style scoped>
.stat-card {
  background: var(--v-theme-surface);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.stat-card:focus {
  outline: 2px solid var(--v-theme-primary);
  outline-offset: 2px;
}

.stat-card.non-clickable {
  cursor: default;
}

.stat-card:hover {
  border-color: var(--v-theme-primary);
}

.stat-card.active {
  border-color: var(--v-theme-primary);
  background: rgba(var(--v-theme-primary-rgb), 0.05);
}

.filter-section {
  background: var(--v-theme-surface);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.table-section {
  background: var(--v-theme-surface);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}
</style>