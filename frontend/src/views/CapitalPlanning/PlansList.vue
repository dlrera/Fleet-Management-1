<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h5 font-weight-medium">Capital Planning</h1>
          <div>
            <v-btn variant="outlined" size="small" @click="$router.push('/capital-planning/asset-lifecycle')" class="mr-2">
              <v-icon left>mdi-wrench</v-icon>
              Asset Lifecycle
            </v-btn>
            <v-btn variant="outlined" size="small" @click="$router.push('/capital-planning/projects')" class="mr-2">
              <v-icon left>mdi-briefcase</v-icon>
              Projects
            </v-btn>
            <v-btn color="primary" size="small" @click="createNewPlan">
              <v-icon left>mdi-plus</v-icon>
              New Plan
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row>
      <v-col cols="12" sm="6" md="3">
        <div class="stat-card pa-3">
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">Active Plans</span>
            <span class="text-h6 font-weight-medium">{{ stats.active }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <div class="stat-card pa-3">
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">Total Budget</span>
            <span class="text-h6 font-weight-medium">${{ formatCurrency(stats.totalBudget) }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <div class="stat-card pa-3">
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">Pending Approval</span>
            <span class="text-h6 font-weight-medium">{{ stats.pendingApproval }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <div class="stat-card pa-3">
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">Scenarios</span>
            <span class="text-h6 font-weight-medium">{{ stats.scenarios }}</span>
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
                v-model="filters.status"
                :items="statusOptions"
                label="Status"
                clearable
                density="compact"
                variant="outlined"
              ></v-select>
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                v-model="filters.year"
                :items="yearOptions"
                label="Fiscal Year"
                clearable
                density="compact"
                variant="outlined"
              ></v-select>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="searchQuery"
                label="Search plans..."
                prepend-inner-icon="mdi-magnify"
                clearable
                density="compact"
                variant="outlined"
              ></v-text-field>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>

    <!-- Plans Table -->
    <v-row>
      <v-col cols="12">
        <div class="table-section">
          <v-data-table-server
            :headers="headers"
            :items="plans"
            :loading="loading"
            :items-length="totalItems"
            :items-per-page="itemsPerPage"
            @update:page="loadPlans"
            @update:items-per-page="loadPlans"
          >
            <template v-slot:item.status="{ item }">
              <v-chip size="small" :color="getStatusColor(item.status)">
                {{ item.status }}
              </v-chip>
            </template>
            <template v-slot:item.total_budget="{ item }">
              ${{ formatCurrency(item.total_budget) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn icon="mdi-eye" size="small" variant="text" @click="viewPlan(item)"></v-btn>
              <v-btn icon="mdi-pencil" size="small" variant="text" @click="editPlan(item)"></v-btn>
            </template>
          </v-data-table-server>
        </div>
      </v-col>
    </v-row>
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

const filters = ref({
  status: null,
  year: null
})

const plans = computed(() => store.plans)

const stats = ref({
  active: 0,
  totalBudget: 0,
  pendingApproval: 0,
  scenarios: 0
})

const headers = [
  { title: 'Name', key: 'name' },
  { title: 'Fiscal Year', key: 'fiscal_year' },
  { title: 'Status', key: 'status' },
  { title: 'Total Budget', key: 'total_budget' },
  { title: 'Created', key: 'created_at' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const statusOptions = [
  'draft',
  'submitted',
  'approved',
  'rejected',
  'completed'
]

const yearOptions = [
  2024,
  2025,
  2026,
  2027,
  2028
]

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US').format(value || 0)
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    submitted: 'blue',
    approved: 'green',
    rejected: 'red',
    completed: 'success'
  }
  return colors[status] || 'grey'
}

const loadPlans = async () => {
  loading.value = true
  try {
    await store.fetchPlans({
      search: searchQuery.value,
      status: filters.value.status,
      fiscal_year: filters.value.year,
      page_size: itemsPerPage.value
    })
    totalItems.value = store.totalCount
    await loadStats()
  } catch (error) {
    console.error('Failed to load plans:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const data = await store.fetchStats()
    stats.value = data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const createNewPlan = () => {
  router.push('/capital-planning/new')
}

const viewPlan = (plan) => {
  router.push(`/capital-planning/${plan.id}`)
}

const editPlan = (plan) => {
  router.push(`/capital-planning/${plan.id}/edit`)
}

onMounted(() => {
  loadPlans()
})
</script>

<style scoped>
.stat-card {
  background: var(--v-theme-surface);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 4px;
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