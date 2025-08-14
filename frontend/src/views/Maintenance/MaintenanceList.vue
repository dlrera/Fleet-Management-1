<template>
  <div class="maintenance-list">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="mb-1">Maintenance Scheduler</h1>
        <p class="text-muted mb-0">Manage preventive maintenance schedules and records</p>
      </div>
      <div class="d-flex gap-2">
        <router-link to="/maintenance/schedule" class="btn btn-success">
          <i class="bi bi-calendar-plus me-2"></i>Schedule Maintenance
        </router-link>
        <router-link to="/maintenance/create" class="btn btn-primary">
          <i class="bi bi-plus-circle me-2"></i>Record Maintenance
        </router-link>
      </div>
    </div>

    <!-- Filters and View Toggle -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="form-label">Search</label>
            <div class="input-group">
              <span class="input-group-text">
                <i class="bi bi-search"></i>
              </span>
              <input 
                v-model="filters.search" 
                type="text" 
                class="form-control" 
                placeholder="Asset number, maintenance type..."
                @input="debounceSearch"
              >
            </div>
          </div>
          <div class="col-md-2">
            <label class="form-label">Asset</label>
            <select v-model="filters.asset" class="form-select" @change="loadData">
              <option value="">All Assets</option>
              <option v-for="asset in assets" :key="asset.asset_id" :value="asset.asset_id">
                {{ asset.asset_number }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Status</label>
            <select v-model="filters.status" class="form-select" @change="loadData">
              <option value="">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="due">Due</option>
              <option value="overdue">Overdue</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Period</label>
            <select v-model="filters.period" class="form-select" @change="loadData">
              <option value="">All Time</option>
              <option value="7">Next 7 days</option>
              <option value="30">Next 30 days</option>
              <option value="90">Next 90 days</option>
            </select>
          </div>
          <div class="col-md-3">
            <div class="d-flex gap-2">
              <button @click="clearFilters" class="btn btn-outline-secondary">
                <i class="bi bi-x-circle me-2"></i>Clear
              </button>
              <div class="btn-group" role="group">
                <button 
                  type="button" 
                  class="btn" 
                  :class="viewMode === 'calendar' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="viewMode = 'calendar'"
                >
                  <i class="bi bi-calendar3"></i>
                </button>
                <button 
                  type="button" 
                  class="btn" 
                  :class="viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="viewMode = 'list'"
                >
                  <i class="bi bi-list-task"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ statistics.total_schedules || 0 }}</h3>
            <small>Total Schedules</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ statistics.due_today || 0 }}</h3>
            <small>Due Today</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-danger text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ statistics.overdue || 0 }}</h3>
            <small>Overdue</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ statistics.completed_month || 0 }}</h3>
            <small>Completed This Month</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar View -->
    <div v-if="viewMode === 'calendar'" class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="bi bi-calendar3 me-2"></i>Maintenance Calendar
        </h5>
        <div class="d-flex align-items-center gap-3">
          <div class="btn-group" role="group">
            <button @click="previousMonth" class="btn btn-sm btn-outline-secondary">
              <i class="bi bi-chevron-left"></i>
            </button>
            <button class="btn btn-sm btn-outline-secondary" disabled>
              {{ formatMonthYear(currentMonth) }}
            </button>
            <button @click="nextMonth" class="btn btn-sm btn-outline-secondary">
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
          <button @click="goToToday" class="btn btn-sm btn-primary">Today</button>
        </div>
      </div>
      <div class="card-body p-0">
        <div class="calendar-grid">
          <div class="calendar-header">
            <div v-for="day in weekDays" :key="day" class="calendar-day-header">
              {{ day }}
            </div>
          </div>
          <div class="calendar-body">
            <div 
              v-for="week in calendarWeeks" 
              :key="week[0]?.date || 'empty'" 
              class="calendar-week"
            >
              <div 
                v-for="day in week" 
                :key="day?.date || Math.random()"
                class="calendar-day"
                :class="{
                  'other-month': day?.otherMonth,
                  'today': day?.isToday,
                  'has-maintenance': day?.maintenanceItems?.length > 0
                }"
              >
                <div v-if="day" class="day-content">
                  <div class="day-number">{{ day.dayNumber }}</div>
                  <div v-if="day.maintenanceItems?.length" class="maintenance-items">
                    <div 
                      v-for="item in day.maintenanceItems.slice(0, 3)" 
                      :key="item.schedule_id"
                      class="maintenance-item"
                      :class="getMaintenanceClass(item)"
                      @click="viewMaintenanceDetail(item)"
                    >
                      <small class="text-truncate">{{ item.asset_number }} - {{ item.maintenance_type_name }}</small>
                    </div>
                    <div v-if="day.maintenanceItems.length > 3" class="more-items">
                      <small class="text-muted">+{{ day.maintenanceItems.length - 3 }} more</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Maintenance Schedule</h5>
        <span class="text-muted">{{ pagination.count || 0 }} schedules</span>
      </div>
      <div class="card-body p-0">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="schedules.length === 0" class="text-center py-5">
          <i class="bi bi-calendar-x fs-1 text-muted opacity-50"></i>
          <h5 class="mt-3 text-muted">No maintenance scheduled</h5>
          <p class="text-muted">
            {{ hasFilters ? 'Try adjusting your filters' : 'Get started by scheduling maintenance for your assets' }}
          </p>
          <router-link v-if="!hasFilters" to="/maintenance/schedule" class="btn btn-primary">
            <i class="bi bi-calendar-plus me-2"></i>Schedule Maintenance
          </router-link>
        </div>

        <!-- Schedules Table -->
        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th @click="setSortBy('asset__asset_number')" class="sortable">
                  Asset
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th @click="setSortBy('maintenance_type__name')" class="sortable">
                  Maintenance Type
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th @click="setSortBy('next_due_date')" class="sortable">
                  Next Due Date
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th>Status</th>
                <th>Last Service</th>
                <th>Frequency</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="schedule in schedules" :key="schedule.schedule_id" @click="viewMaintenanceDetail(schedule)">
                <td>
                  <div class="fw-bold">{{ schedule.asset_number }}</div>
                  <small class="text-muted">{{ schedule.asset_make }} {{ schedule.asset_model }}</small>
                </td>
                <td>
                  <div>{{ schedule.maintenance_type_name }}</div>
                  <small class="text-muted">{{ schedule.description || 'No description' }}</small>
                </td>
                <td>
                  <div v-if="schedule.next_due_date">
                    {{ formatDate(schedule.next_due_date) }}
                    <div class="small text-muted">
                      {{ getDaysUntilDue(schedule.next_due_date) }}
                    </div>
                  </div>
                  <span v-else class="text-muted">Not scheduled</span>
                </td>
                <td>
                  <span class="badge" :class="getStatusClass(schedule)">
                    {{ getStatusText(schedule) }}
                  </span>
                </td>
                <td>
                  <div v-if="schedule.last_service_date">
                    {{ formatDate(schedule.last_service_date) }}
                    <div class="small text-muted">
                      {{ schedule.last_service_mileage?.toLocaleString() }} {{ schedule.mileage_unit }}
                    </div>
                  </div>
                  <span v-else class="text-muted">Never</span>
                </td>
                <td>
                  <div class="small">
                    <div v-if="schedule.frequency_days">Every {{ schedule.frequency_days }} days</div>
                    <div v-if="schedule.frequency_mileage">Every {{ schedule.frequency_mileage.toLocaleString() }} {{ schedule.mileage_unit }}</div>
                    <div v-if="schedule.frequency_hours">Every {{ schedule.frequency_hours }} hours</div>
                  </div>
                </td>
                <td @click.stop>
                  <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                            data-bs-toggle="dropdown">
                      Actions
                    </button>
                    <ul class="dropdown-menu">
                      <li>
                        <router-link :to="`/maintenance/${schedule.schedule_id}`" class="dropdown-item">
                          <i class="bi bi-eye me-2"></i>View Details
                        </router-link>
                      </li>
                      <li>
                        <button @click="completeService(schedule)" class="dropdown-item">
                          <i class="bi bi-check-circle me-2"></i>Mark Complete
                        </button>
                      </li>
                      <li>
                        <router-link :to="`/maintenance/${schedule.schedule_id}/edit`" class="dropdown-item">
                          <i class="bi bi-pencil me-2"></i>Edit Schedule
                        </router-link>
                      </li>
                      <li><hr class="dropdown-divider"></li>
                      <li>
                        <router-link 
                          :to="`/work-orders/create?maintenance_schedule_id=${schedule.schedule_id}`" 
                          class="dropdown-item"
                        >
                          <i class="bi bi-wrench me-2"></i>Create Work Order
                        </router-link>
                      </li>
                    </ul>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.count > pagination.page_size" class="card-footer">
          <nav>
            <ul class="pagination pagination-sm justify-content-center mb-0">
              <li class="page-item" :class="{ disabled: !pagination.previous }">
                <button @click="changePage(currentPage - 1)" class="page-link" :disabled="!pagination.previous">
                  Previous
                </button>
              </li>
              
              <li v-for="page in visiblePages" :key="page" class="page-item" :class="{ active: page === currentPage }">
                <button @click="changePage(page)" class="page-link">{{ page }}</button>
              </li>
              
              <li class="page-item" :class="{ disabled: !pagination.next }">
                <button @click="changePage(currentPage + 1)" class="page-link" :disabled="!pagination.next">
                  Next
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { maintenanceAPI, assetsAPI } from '@/services/api'
import { toast } from '@/utils/toast'

export default {
  name: 'MaintenanceList',
  setup() {
    const router = useRouter()
    
    const loading = ref(true)
    const viewMode = ref('list')
    const searchTimeout = ref(null)
    const currentMonth = ref(new Date())
    
    const schedules = ref([])
    const assets = ref([])
    const statistics = ref({})
    const pagination = ref({})
    const currentPage = ref(1)
    
    const filters = reactive({
      search: '',
      asset: '',
      status: '',
      period: '',
      ordering: 'next_due_date'
    })

    const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    const hasFilters = computed(() => {
      return filters.search || filters.asset || filters.status || filters.period
    })

    const visiblePages = computed(() => {
      const totalPages = Math.ceil(pagination.value.count / pagination.value.page_size)
      const current = currentPage.value
      const pages = []
      
      const start = Math.max(1, current - 2)
      const end = Math.min(totalPages, current + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })

    const calendarWeeks = computed(() => {
      const weeks = []
      const firstDay = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth(), 1)
      const lastDay = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 0)
      
      // Start from the beginning of the week containing the first day
      const startDate = new Date(firstDay)
      startDate.setDate(startDate.getDate() - startDate.getDay())
      
      // End at the end of the week containing the last day
      const endDate = new Date(lastDay)
      endDate.setDate(endDate.getDate() + (6 - endDate.getDay()))
      
      const currentDate = new Date(startDate)
      while (currentDate <= endDate) {
        const week = []
        for (let i = 0; i < 7; i++) {
          const dayDate = new Date(currentDate)
          const isOtherMonth = dayDate.getMonth() !== currentMonth.value.getMonth()
          const isToday = dayDate.toDateString() === new Date().toDateString()
          
          // Find maintenance items for this day
          const maintenanceItems = schedules.value.filter(schedule => {
            if (!schedule.next_due_date) return false
            const dueDate = new Date(schedule.next_due_date)
            return dueDate.toDateString() === dayDate.toDateString()
          })
          
          week.push({
            date: dayDate.toISOString().split('T')[0],
            dayNumber: dayDate.getDate(),
            otherMonth: isOtherMonth,
            isToday,
            maintenanceItems
          })
          
          currentDate.setDate(currentDate.getDate() + 1)
        }
        weeks.push(week)
      }
      
      return weeks
    })

    const loadSchedules = async (page = 1) => {
      loading.value = true
      currentPage.value = page
      
      try {
        const params = {
          page,
          page_size: 20,
          ...filters
        }
        
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key]
          }
        })
        
        const response = await maintenanceAPI.getMaintenanceSchedules(params)
        schedules.value = response.data.results || []
        pagination.value = {
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
          page_size: params.page_size
        }
      } catch (error) {
        console.error('Error loading schedules:', error)
        toast.error('Failed to load maintenance schedules')
        schedules.value = []
      } finally {
        loading.value = false
      }
    }

    const loadStatistics = async () => {
      try {
        const response = await maintenanceAPI.getScheduleStatistics()
        statistics.value = response.data
      } catch (error) {
        console.error('Error loading statistics:', error)
      }
    }

    const loadAssets = async () => {
      try {
        const response = await assetsAPI.getAssets({ page_size: 100 })
        assets.value = response.data.results || []
      } catch (error) {
        console.error('Error loading assets:', error)
      }
    }

    const loadData = async () => {
      await Promise.all([
        loadSchedules(),
        loadStatistics()
      ])
    }

    const debounceSearch = () => {
      clearTimeout(searchTimeout.value)
      searchTimeout.value = setTimeout(() => {
        loadData()
      }, 500)
    }

    const clearFilters = () => {
      Object.assign(filters, {
        search: '',
        asset: '',
        status: '',
        period: '',
        ordering: 'next_due_date'
      })
      loadData()
    }

    const setSortBy = (field) => {
      if (filters.ordering === field) {
        filters.ordering = `-${field}`
      } else if (filters.ordering === `-${field}`) {
        filters.ordering = field
      } else {
        filters.ordering = field
      }
      loadData()
    }

    const changePage = (page) => {
      if (page >= 1 && page <= Math.ceil(pagination.value.count / pagination.value.page_size)) {
        loadSchedules(page)
      }
    }

    const previousMonth = () => {
      currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() - 1, 1)
    }

    const nextMonth = () => {
      currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1)
    }

    const goToToday = () => {
      currentMonth.value = new Date()
    }

    const viewMaintenanceDetail = (schedule) => {
      router.push(`/maintenance/${schedule.schedule_id}`)
    }

    const completeService = (schedule) => {
      router.push({
        path: '/maintenance/create',
        query: { schedule_id: schedule.schedule_id }
      })
    }

    const getStatusClass = (schedule) => {
      if (!schedule.next_due_date) return 'bg-secondary'
      
      const dueDate = new Date(schedule.next_due_date)
      const today = new Date()
      const timeDiff = dueDate - today
      const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24))
      
      if (daysDiff < 0) return 'bg-danger'
      if (daysDiff === 0) return 'bg-warning'
      if (daysDiff <= 7) return 'bg-info'
      return 'bg-success'
    }

    const getStatusText = (schedule) => {
      if (!schedule.next_due_date) return 'Not Scheduled'
      
      const dueDate = new Date(schedule.next_due_date)
      const today = new Date()
      const timeDiff = dueDate - today
      const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24))
      
      if (daysDiff < 0) return 'Overdue'
      if (daysDiff === 0) return 'Due Today'
      if (daysDiff <= 7) return 'Due Soon'
      return 'Scheduled'
    }

    const getMaintenanceClass = (item) => {
      const statusClass = getStatusClass(item)
      return `maintenance-item-${statusClass.replace('bg-', '')}`
    }

    const getDaysUntilDue = (dueDate) => {
      if (!dueDate) return ''
      
      const due = new Date(dueDate)
      const today = new Date()
      const timeDiff = due - today
      const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24))
      
      if (daysDiff < 0) return `${Math.abs(daysDiff)} days overdue`
      if (daysDiff === 0) return 'Due today'
      if (daysDiff === 1) return 'Due tomorrow'
      return `Due in ${daysDiff} days`
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const formatMonthYear = (date) => {
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long'
      })
    }

    watch(() => viewMode.value, () => {
      if (viewMode.value === 'calendar' && schedules.value.length === 0) {
        loadData()
      }
    })

    onMounted(async () => {
      await Promise.all([
        loadData(),
        loadAssets()
      ])
    })

    return {
      loading,
      viewMode,
      currentMonth,
      schedules,
      assets,
      statistics,
      pagination,
      currentPage,
      filters,
      weekDays,
      hasFilters,
      visiblePages,
      calendarWeeks,
      loadData,
      debounceSearch,
      clearFilters,
      setSortBy,
      changePage,
      previousMonth,
      nextMonth,
      goToToday,
      viewMaintenanceDetail,
      completeService,
      getStatusClass,
      getStatusText,
      getMaintenanceClass,
      getDaysUntilDue,
      formatDate,
      formatMonthYear
    }
  }
}
</script>

<style scoped>
.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: #f8f9fa;
}

tbody tr {
  cursor: pointer;
}

tbody tr:hover {
  background-color: #f8f9fa;
}

.calendar-grid {
  min-height: 600px;
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.calendar-day-header {
  padding: 0.75rem;
  text-align: center;
  font-weight: 600;
  color: #495057;
  border-right: 1px solid #dee2e6;
}

.calendar-day-header:last-child {
  border-right: none;
}

.calendar-body {
  display: flex;
  flex-direction: column;
}

.calendar-week {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  min-height: 120px;
}

.calendar-day {
  border-right: 1px solid #dee2e6;
  border-bottom: 1px solid #dee2e6;
  position: relative;
}

.calendar-day:last-child {
  border-right: none;
}

.calendar-day.other-month {
  background-color: #f8f9fa;
  color: #6c757d;
}

.calendar-day.today {
  background-color: #e3f2fd;
}

.calendar-day.has-maintenance {
  background-color: #fff3cd;
}

.day-content {
  padding: 0.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.day-number {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.maintenance-items {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.maintenance-item {
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
}

.maintenance-item-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.maintenance-item-warning {
  background-color: #fff3cd;
  color: #856404;
}

.maintenance-item-info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.maintenance-item-success {
  background-color: #d4edda;
  color: #155724;
}

.more-items {
  margin-top: 0.25rem;
}

.dropdown-toggle::after {
  display: none;
}
</style>