<template>
  <div class="audit-logs">
    <div class="d-flex justify-space-between align-center mb-4">
      <h1 class="text-h4">Audit Logs</h1>
      <div class="d-flex gap-2">
        <v-btn
          color="primary"
          variant="outlined"
          @click="exportLogs"
          :loading="exporting"
        >
          <v-icon left>mdi-download</v-icon>
          Export CSV
        </v-btn>
        <v-btn
          color="primary"
          variant="outlined"
          @click="refreshLogs"
        >
          <v-icon left>mdi-refresh</v-icon>
          Refresh
        </v-btn>
      </div>
    </div>

    <!-- Stats Cards -->
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_events || 0 }}</div>
          <div class="stat-label">Total Events (30d)</div>
        </div>
      </v-col>
      <v-col cols="12" md="3">
        <div class="stat-card">
          <div class="stat-value text-error">{{ stats.high_risk_events || 0 }}</div>
          <div class="stat-label">High Risk Events</div>
        </div>
      </v-col>
      <v-col cols="12" md="3">
        <div class="stat-card">
          <div class="stat-value text-warning">{{ stats.failed_permissions || 0 }}</div>
          <div class="stat-label">Permission Denied</div>
        </div>
      </v-col>
      <v-col cols="12" md="3">
        <div class="stat-card">
          <div class="stat-value">{{ activeFilters }}</div>
          <div class="stat-label">Active Filters</div>
        </div>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-expansion-panels v-model="filterPanel" class="mb-4">
      <v-expansion-panel>
        <v-expansion-panel-title>
          <v-icon left>mdi-filter</v-icon>
          Filters
          <v-chip v-if="activeFilters > 0" size="small" class="ml-2">
            {{ activeFilters }}
          </v-chip>
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-row>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="filters.search"
                label="Search"
                density="compact"
                clearable
                @input="debouncedSearch"
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.action"
                :items="actionTypes"
                item-title="label"
                item-value="value"
                label="Action"
                density="compact"
                clearable
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="filters.actor"
                label="Actor Email"
                density="compact"
                clearable
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.resource_type"
                :items="resourceTypes"
                label="Resource Type"
                density="compact"
                clearable
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="filters.start_date"
                label="Start Date"
                type="date"
                density="compact"
                clearable
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="filters.end_date"
                label="End Date"
                type="date"
                density="compact"
                clearable
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                v-model.number="filters.min_risk"
                label="Min Risk Score"
                type="number"
                min="0"
                max="100"
                density="compact"
                clearable
              />
            </v-col>
            <v-col cols="12" md="3" class="d-flex align-center">
              <v-btn
                color="primary"
                @click="applyFilters"
                size="small"
                class="mr-2"
              >
                Apply Filters
              </v-btn>
              <v-btn
                variant="outlined"
                @click="clearFilters"
                size="small"
              >
                Clear
              </v-btn>
            </v-col>
          </v-row>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>

    <!-- Audit Log Table -->
    <v-data-table-server
      :headers="headers"
      :items="logs"
      :items-length="totalItems"
      :loading="loading"
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      @update:options="loadLogs"
      density="compact"
      hover
    >
      <template v-slot:item.timestamp="{ item }">
        <div>{{ formatDate(item.timestamp) }}</div>
        <div class="text-caption text-grey">{{ formatTime(item.timestamp) }}</div>
      </template>

      <template v-slot:item.action="{ item }">
        <v-chip
          :color="getActionColor(item.action)"
          size="small"
          label
        >
          {{ item.action_display }}
        </v-chip>
      </template>

      <template v-slot:item.actor_email="{ item }">
        <div>{{ item.actor_email }}</div>
        <div class="text-caption text-grey">{{ item.actor_role }}</div>
      </template>

      <template v-slot:item.resource="{ item }">
        <div>{{ item.resource_type }}/{{ item.resource_id }}</div>
        <div class="text-caption text-grey">{{ item.resource_name }}</div>
      </template>

      <template v-slot:item.risk_score="{ item }">
        <v-chip
          :color="getRiskColor(item.risk_score)"
          size="small"
          label
        >
          {{ item.risk_score }}
        </v-chip>
      </template>

      <template v-slot:item.details="{ item }">
        <v-btn
          icon="mdi-eye"
          size="small"
          variant="text"
          @click="showDetails(item)"
        />
      </template>
    </v-data-table-server>

    <!-- Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="800">
      <v-card v-if="selectedLog">
        <v-card-title>
          Audit Log Details
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="detailsDialog = false"
          />
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <div class="mb-2">
                <strong>Timestamp:</strong><br>
                {{ formatDate(selectedLog.timestamp) }} {{ formatTime(selectedLog.timestamp) }}
              </div>
              <div class="mb-2">
                <strong>Actor:</strong><br>
                {{ selectedLog.actor_email }} ({{ selectedLog.actor_role }})
              </div>
              <div class="mb-2">
                <strong>Action:</strong><br>
                {{ selectedLog.action_display }}
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="mb-2">
                <strong>Resource:</strong><br>
                {{ selectedLog.resource_type }}/{{ selectedLog.resource_id }}<br>
                {{ selectedLog.resource_name }}
              </div>
              <div class="mb-2">
                <strong>IP Address:</strong><br>
                {{ selectedLog.ip_address || 'N/A' }}
              </div>
              <div class="mb-2">
                <strong>Risk Score:</strong><br>
                <v-chip
                  :color="getRiskColor(selectedLog.risk_score)"
                  size="small"
                  label
                >
                  {{ selectedLog.risk_score }}
                </v-chip>
              </div>
            </v-col>
          </v-row>

          <div v-if="selectedLog.before_state || selectedLog.after_state" class="mt-4">
            <h3 class="mb-2">Changes</h3>
            <v-row>
              <v-col cols="12" md="6" v-if="selectedLog.before_state">
                <div class="text-subtitle-2 mb-1">Before:</div>
                <pre class="json-display">{{ JSON.stringify(selectedLog.before_state, null, 2) }}</pre>
              </v-col>
              <v-col cols="12" md="6" v-if="selectedLog.after_state">
                <div class="text-subtitle-2 mb-1">After:</div>
                <pre class="json-display">{{ JSON.stringify(selectedLog.after_state, null, 2) }}</pre>
              </v-col>
            </v-row>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()

// Data
const logs = ref([])
const loading = ref(false)
const exporting = ref(false)
const totalItems = ref(0)
const page = ref(1)
const itemsPerPage = ref(50)
const filterPanel = ref(0)
const detailsDialog = ref(false)
const selectedLog = ref(null)
const stats = ref({})
const actionTypes = ref([])

// Filters
const filters = ref({
  search: '',
  action: null,
  actor: '',
  resource_type: null,
  start_date: null,
  end_date: null,
  min_risk: null
})

// Resource types
const resourceTypes = [
  'assets',
  'drivers',
  'fuel',
  'locations',
  'users',
  'roles',
  'auth',
  'system'
]

// Table headers
const headers = [
  { title: 'Timestamp', key: 'timestamp', width: '180px' },
  { title: 'Actor', key: 'actor_email', width: '200px' },
  { title: 'Action', key: 'action', width: '150px' },
  { title: 'Resource', key: 'resource', width: '200px' },
  { title: 'Risk', key: 'risk_score', width: '80px' },
  { title: 'IP Address', key: 'ip_address', width: '120px' },
  { title: '', key: 'details', width: '50px', sortable: false }
]

// Computed
const activeFilters = computed(() => {
  let count = 0
  if (filters.value.search) count++
  if (filters.value.action) count++
  if (filters.value.actor) count++
  if (filters.value.resource_type) count++
  if (filters.value.start_date) count++
  if (filters.value.end_date) count++
  if (filters.value.min_risk) count++
  return count
})

// Methods
const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: itemsPerPage.value,
      ...filters.value
    }

    const response = await api.get('/auth/manage/audit/', { params })
    logs.value = response.data.results
    totalItems.value = response.data.count
  } catch (error) {
    console.error('Error loading audit logs:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await api.get('/auth/manage/audit/stats/')
    stats.value = response.data
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const loadActionTypes = async () => {
  try {
    const response = await api.get('/auth/manage/audit/action_types/')
    actionTypes.value = response.data.actions
  } catch (error) {
    console.error('Error loading action types:', error)
  }
}

const applyFilters = () => {
  page.value = 1
  loadLogs()
}

const clearFilters = () => {
  filters.value = {
    search: '',
    action: null,
    actor: '',
    resource_type: null,
    start_date: null,
    end_date: null,
    min_risk: null
  }
  applyFilters()
}

const refreshLogs = () => {
  loadLogs()
  loadStats()
}

const exportLogs = async () => {
  exporting.value = true
  try {
    const params = { ...filters.value }
    const response = await api.get('/auth/manage/audit/export/', {
      params,
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `audit_logs_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('Error exporting logs:', error)
  } finally {
    exporting.value = false
  }
}

const showDetails = (log) => {
  selectedLog.value = log
  detailsDialog.value = true
}

const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleDateString()
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const getActionColor = (action) => {
  const colorMap = {
    create: 'success',
    update: 'info',
    delete: 'error',
    login: 'primary',
    logout: 'grey',
    permission_denied: 'error',
    role_assigned: 'warning',
    user_suspended: 'error',
    export_data: 'info'
  }
  return colorMap[action] || 'grey'
}

const getRiskColor = (score) => {
  if (score >= 80) return 'error'
  if (score >= 60) return 'warning'
  if (score >= 30) return 'info'
  return 'success'
}

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 500)
}

// Lifecycle
onMounted(() => {
  loadLogs()
  loadStats()
  loadActionTypes()
})
</script>

<style scoped>
.audit-logs {
  padding: 20px;
}

.stat-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
}

.json-display {
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 300px;
}
</style>