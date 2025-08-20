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
          <h1 class="text-h5 font-weight-medium">Capital Projects</h1>
          <div>
            <v-btn color="primary" size="small" @click="createNewProject" class="mr-2">
              <v-icon left>mdi-plus</v-icon>
              New Project
            </v-btn>
            <v-btn variant="outlined" size="small" @click="showPriorityMatrix">
              <v-icon left>mdi-view-grid</v-icon>
              Priority Matrix
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
          @click="filterByStatus(null)" 
          @keydown.enter="filterByStatus(null)"
          :class="{ active: !filters.status }"
          tabindex="0"
          role="button"
          :aria-label="`Show all projects. Total: ${stats.total} projects`"
          :aria-pressed="!filters.status"
        >
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">Total Projects</span>
            <span class="text-h6 font-weight-medium">{{ stats.total }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3" 
          @click="filterByStatus('approved')" 
          @keydown.enter="filterByStatus('approved')"
          :class="{ active: filters.status === 'approved' }"
          tabindex="0"
          role="button"
          :aria-label="`Filter by approved projects. ${stats.approved} approved`"
          :aria-pressed="filters.status === 'approved'"
        >
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">Approved</span>
            <span class="text-h6 font-weight-medium text-green">{{ stats.approved }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3" 
          @click="filterByStatus('in_progress')" 
          @keydown.enter="filterByStatus('in_progress')"
          :class="{ active: filters.status === 'in_progress' }"
          tabindex="0"
          role="button"
          :aria-label="`Filter by in progress projects. ${stats.inProgress} in progress`"
          :aria-pressed="filters.status === 'in_progress'"
        >
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">In Progress</span>
            <span class="text-h6 font-weight-medium text-blue">{{ stats.inProgress }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 non-clickable"
          role="status"
          :aria-label="`Total budget: $${formatCurrency(stats.totalBudget)}`"
        >
          <div class="d-flex flex-column">
            <span class="text-caption text-medium-emphasis">Total Budget</span>
            <span class="text-h6 font-weight-medium">${{ formatCurrency(stats.totalBudget) }}</span>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Filter Section -->
    <v-row>
      <v-col cols="12">
        <div class="filter-section pa-3 mb-3">
          <v-row>
            <v-col cols="12" md="2">
              <v-select
                v-model="filters.status"
                :items="statusOptions"
                label="Status"
                clearable
                density="compact"
                variant="outlined"
              ></v-select>
            </v-col>
            <v-col cols="12" md="2">
              <v-select
                v-model="filters.priority"
                :items="priorityOptions"
                label="Priority"
                clearable
                density="compact"
                variant="outlined"
              ></v-select>
            </v-col>
            <v-col cols="12" md="2">
              <v-select
                v-model="filters.category"
                :items="categoryOptions"
                label="Category"
                clearable
                density="compact"
                variant="outlined"
              ></v-select>
            </v-col>
            <v-col cols="12" md="2">
              <v-select
                v-model="filters.year"
                :items="yearOptions"
                label="Year"
                clearable
                density="compact"
                variant="outlined"
              ></v-select>
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="searchQuery"
                label="Search projects..."
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

    <!-- Projects Table -->
    <v-row>
      <v-col cols="12">
        <div class="table-section" role="region" aria-label="Projects data table">
          <!-- Empty State -->
          <div v-if="!loading && projects.length === 0" class="text-center pa-8">
            <v-icon size="64" color="grey">mdi-folder-outline</v-icon>
            <h3 class="text-h6 mt-4">No projects found</h3>
            <p class="text-body-2 text-medium-emphasis mt-2">
              {{ filters.status || filters.priority || filters.category || filters.year || searchQuery 
                ? 'Try adjusting your filters or search criteria' 
                : 'Get started by creating your first capital project' }}
            </p>
            <v-btn 
              v-if="!filters.status && !filters.priority && !filters.category && !filters.year && !searchQuery"
              color="primary" 
              class="mt-4"
              @click="createNewProject"
            >
              Create First Project
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
          <div v-if="loading && projects.length === 0" class="pa-4">
            <v-skeleton-loader type="table-heading"></v-skeleton-loader>
            <v-skeleton-loader type="table-row" v-for="i in 5" :key="i"></v-skeleton-loader>
          </div>

          <v-data-table-server
            v-else
            :headers="headers"
            :items="projects"
            :loading="loading"
            :items-length="totalItems"
            :items-per-page="itemsPerPage"
            @update:page="loadProjects"
            @update:items-per-page="loadProjects"
          >
            <template v-slot:item.title="{ item }">
              <div>
                <a @click="viewProject(item)" class="text-primary" style="cursor: pointer;">
                  {{ item.title }}
                </a>
                <div class="text-caption text-medium-emphasis">{{ item.project_code }}</div>
              </div>
            </template>
            <template v-slot:item.priority="{ item }">
              <v-chip size="small" :color="getPriorityColor(item.priority)">
                {{ item.priority_display }}
              </v-chip>
            </template>
            <template v-slot:item.status="{ item }">
              <v-chip size="small" :color="getStatusColor(item.status)">
                {{ item.status_display }}
              </v-chip>
            </template>
            <template v-slot:item.estimated_cost="{ item }">
              ${{ formatCurrency(item.estimated_cost) }}
            </template>
            <template v-slot:item.scheduled_year="{ item }">
              {{ item.scheduled_year }}
              <span v-if="item.scheduled_quarter" class="text-caption">
                Q{{ item.scheduled_quarter }}
              </span>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn icon="mdi-eye" size="small" variant="text" @click="viewProject(item)"></v-btn>
              <v-btn icon="mdi-pencil" size="small" variant="text" @click="editProject(item)"></v-btn>
              <v-btn 
                v-if="item.status === 'proposed'"
                icon="mdi-check" 
                size="small" 
                variant="text" 
                color="green"
                @click="approveProject(item)"
                title="Approve Project"
              ></v-btn>
            </template>
          </v-data-table-server>
        </div>
      </v-col>
    </v-row>

    <!-- Priority Matrix Dialog -->
    <v-dialog v-model="matrixDialog" max-width="1200">
      <v-card>
        <v-card-title>Project Priority Matrix</v-card-title>
        <v-card-text>
          <v-row>
            <v-col v-for="priority in ['critical', 'high', 'medium', 'low']" :key="priority" cols="12" md="3">
              <div class="priority-column">
                <h3 class="text-h6 mb-2" :class="`text-${getPriorityColor(priority)}`">
                  {{ getPriorityLabel(priority) }}
                </h3>
                <v-row>
                  <v-col v-for="status in ['proposed', 'approved', 'in_progress', 'completed']" :key="status" cols="12">
                    <div class="status-section pa-2">
                      <div class="text-caption font-weight-bold mb-1">{{ getStatusLabel(status) }}</div>
                      <div v-if="priorityMatrix[priority] && priorityMatrix[priority][status]">
                        <v-chip 
                          v-for="project in priorityMatrix[priority][status].slice(0, 3)" 
                          :key="project.id"
                          size="small"
                          class="ma-1"
                          @click="viewProject(project)"
                        >
                          {{ project.project_code }}
                        </v-chip>
                        <div v-if="priorityMatrix[priority][status].length > 3" class="text-caption">
                          +{{ priorityMatrix[priority][status].length - 3 }} more
                        </div>
                      </div>
                      <div v-else class="text-caption text-medium-emphasis">None</div>
                    </div>
                  </v-col>
                </v-row>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="matrixDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Yearly Summary Dialog -->
    <v-dialog v-model="summaryDialog" max-width="800">
      <v-card>
        <v-card-title>Yearly Project Summary</v-card-title>
        <v-card-text>
          <v-simple-table>
            <thead>
              <tr>
                <th>Year</th>
                <th>Projects</th>
                <th>Estimated Cost</th>
                <th>Approved Budget</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="year in yearlySummary" :key="year.scheduled_year">
                <td>{{ year.scheduled_year }}</td>
                <td>{{ year.total_projects }}</td>
                <td>${{ formatCurrency(year.total_estimated_cost) }}</td>
                <td>${{ formatCurrency(year.total_approved_budget) }}</td>
                <td>
                  <v-chip size="x-small" color="green" class="mr-1">
                    {{ year.approved_count }} approved
                  </v-chip>
                  <v-chip size="x-small" color="blue" class="mr-1">
                    {{ year.in_progress_count }} in progress
                  </v-chip>
                  <v-chip size="x-small" color="success">
                    {{ year.completed_count }} completed
                  </v-chip>
                </td>
              </tr>
            </tbody>
          </v-simple-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="summaryDialog = false">Close</v-btn>
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
const matrixDialog = ref(false)
const summaryDialog = ref(false)
const priorityMatrix = ref({})
const yearlySummary = ref([])
const errorSnackbar = ref(false)
const errorMessage = ref('')
const successSnackbar = ref(false)
const successMessage = ref('')

const filters = ref({
  status: null,
  priority: null,
  category: null,
  year: null
})

const projects = computed(() => store.capitalProjects)

const stats = ref({
  total: 0,
  approved: 0,
  inProgress: 0,
  totalBudget: 0
})

const headers = [
  { title: 'Project', key: 'title', sortable: true },
  { title: 'Category', key: 'category_display', sortable: true },
  { title: 'Priority', key: 'priority', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Year', key: 'scheduled_year', sortable: true },
  { title: 'Est. Cost', key: 'estimated_cost', sortable: true },
  { title: 'Department', key: 'department', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

const statusOptions = [
  { title: 'Proposed', value: 'proposed' },
  { title: 'Approved', value: 'approved' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Completed', value: 'completed' },
  { title: 'Deferred', value: 'deferred' },
  { title: 'Cancelled', value: 'cancelled' }
]

const priorityOptions = [
  { title: 'Critical - Immediate', value: 'critical' },
  { title: 'High - Within 1 Year', value: 'high' },
  { title: 'Medium - 1-3 Years', value: 'medium' },
  { title: 'Low - 3+ Years', value: 'low' }
]

const categoryOptions = [
  { title: 'Asset Replacement', value: 'replacement' },
  { title: 'Renovation/Upgrade', value: 'renovation' },
  { title: 'New Construction', value: 'new_construction' },
  { title: 'Infrastructure', value: 'infrastructure' },
  { title: 'Technology', value: 'technology' },
  { title: 'Fleet', value: 'fleet' },
  { title: 'Equipment', value: 'equipment' },
  { title: 'Other', value: 'other' }
]

const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 10 }, (_, i) => currentYear + i)
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US').format(value || 0)
}

const getPriorityColor = (priority) => {
  const colors = {
    critical: 'red',
    high: 'orange',
    medium: 'yellow',
    low: 'green'
  }
  return colors[priority] || 'grey'
}

const getPriorityLabel = (priority) => {
  const labels = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  }
  return labels[priority] || priority
}

const getStatusColor = (status) => {
  const colors = {
    proposed: 'grey',
    approved: 'green',
    in_progress: 'blue',
    completed: 'success',
    deferred: 'warning',
    cancelled: 'error'
  }
  return colors[status] || 'grey'
}

const getStatusLabel = (status) => {
  const labels = {
    proposed: 'Proposed',
    approved: 'Approved',
    in_progress: 'In Progress',
    completed: 'Completed'
  }
  return labels[status] || status
}

const loadProjects = async () => {
  loading.value = true
  try {
    await store.fetchCapitalProjects({
      search: searchQuery.value,
      status: filters.value.status,
      priority: filters.value.priority,
      category: filters.value.category,
      scheduled_year: filters.value.year,
      page_size: itemsPerPage.value
    })
    totalItems.value = store.capitalProjectCount
    await loadStats()
  } catch (error) {
    console.error('Failed to load projects:', error)
    showError('Failed to load projects. Please try again.')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  stats.value = {
    total: totalItems.value,
    approved: projects.value.filter(p => p.status === 'approved').length,
    inProgress: projects.value.filter(p => p.status === 'in_progress').length,
    totalBudget: projects.value.reduce((sum, p) => sum + (p.estimated_cost || 0), 0)
  }
}

const filterByStatus = (status) => {
  filters.value.status = status
  loadProjects()
}

const createNewProject = () => {
  router.push('/capital-planning/projects/new')
}

const viewProject = (project) => {
  router.push(`/capital-planning/projects/${project.id}`)
}

const editProject = (project) => {
  router.push(`/capital-planning/projects/${project.id}/edit`)
}

const approveProject = async (project) => {
  try {
    await store.approveCapitalProject(project.id, { budget: project.estimated_cost })
    showSuccess(`Project ${project.project_code} approved successfully`)
    await loadProjects()
  } catch (error) {
    console.error('Failed to approve project:', error)
    showError('Failed to approve project. Please check your permissions.')
  }
}

const showPriorityMatrix = async () => {
  try {
    priorityMatrix.value = await store.fetchProjectPriorityMatrix()
    matrixDialog.value = true
  } catch (error) {
    console.error('Failed to load priority matrix:', error)
    showError('Failed to load priority matrix. Please try again.')
  }
}

const showYearlySummary = async () => {
  try {
    yearlySummary.value = await store.fetchProjectYearlySummary()
    summaryDialog.value = true
  } catch (error) {
    console.error('Failed to load yearly summary:', error)
    showError('Failed to load yearly summary. Please try again.')
  }
}

const clearFilters = () => {
  filters.value = {
    status: null,
    priority: null,
    category: null,
    year: null
  }
  searchQuery.value = ''
  loadProjects()
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
    loadProjects()
  }, 500)
}

onMounted(() => {
  loadProjects()
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

.priority-column {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 12px;
}

.status-section {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
  min-height: 60px;
}
</style>