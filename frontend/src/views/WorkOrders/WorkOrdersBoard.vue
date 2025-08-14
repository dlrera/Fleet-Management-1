<template>
  <div class="work-orders-board">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="mb-1">Work Orders</h1>
        <p class="text-muted mb-0">Manage work orders with Kanban-style workflow</p>
      </div>
      <div class="d-flex gap-2">
        <div class="btn-group" role="group">
          <button 
            type="button" 
            class="btn" 
            :class="viewMode === 'board' ? 'btn-primary' : 'btn-outline-primary'"
            @click="viewMode = 'board'"
          >
            <i class="bi bi-kanban me-2"></i>Board
          </button>
          <button 
            type="button" 
            class="btn" 
            :class="viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary'"
            @click="viewMode = 'list'"
          >
            <i class="bi bi-list-task me-2"></i>List
          </button>
        </div>
        <router-link to="/work-orders/create" class="btn btn-primary">
          <i class="bi bi-plus-circle me-2"></i>Create Work Order
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
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
                placeholder="Work order number, title..."
                @input="debounceSearch"
              >
            </div>
          </div>
          <div class="col-md-2">
            <label class="form-label">Asset</label>
            <select v-model="filters.asset" class="form-select" @change="loadWorkOrders">
              <option value="">All Assets</option>
              <option v-for="asset in assets" :key="asset.asset_id" :value="asset.asset_id">
                {{ asset.asset_number }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Assigned To</label>
            <select v-model="filters.assigned_to" class="form-select" @change="loadWorkOrders">
              <option value="">All Technicians</option>
              <option v-for="tech in technicians" :key="tech.id" :value="tech.id">
                {{ tech.first_name }} {{ tech.last_name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Priority</label>
            <select v-model="filters.priority" class="form-select" @change="loadWorkOrders">
              <option value="">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="emergency">Emergency</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Date Range</label>
            <select v-model="filters.date_range" class="form-select" @change="loadWorkOrders">
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="overdue">Overdue</option>
            </select>
          </div>
          <div class="col-md-1">
            <button @click="clearFilters" class="btn btn-outline-secondary mt-4">
              <i class="bi bi-x-circle me-2"></i>Clear
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card bg-secondary text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ getStatusCount('open') }}</h3>
            <small>Open</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ getStatusCount('in_progress') }}</h3>
            <small>In Progress</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ getStatusCount('on_hold') }}</h3>
            <small>On Hold</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body text-center">
            <h3 class="mb-0">{{ getStatusCount('completed') }}</h3>
            <small>Completed</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Kanban Board View -->
    <div v-else-if="viewMode === 'board'" class="kanban-board">
      <div class="row g-3">
        <div v-for="status in workOrderStatuses" :key="status.value" class="col-md-3">
          <div class="kanban-column">
            <div class="kanban-header" :class="`bg-${status.color}`">
              <h6 class="mb-0 text-white">
                {{ status.label }}
                <span class="badge bg-light text-dark ms-2">
                  {{ getStatusWorkOrders(status.value).length }}
                </span>
              </h6>
            </div>
            <div class="kanban-body" @drop="drop($event, status.value)" @dragover="allowDrop($event)">
              <div
                v-for="workOrder in getStatusWorkOrders(status.value)"
                :key="workOrder.work_order_id"
                class="work-order-card"
                draggable="true"
                @dragstart="drag($event, workOrder)"
                @click="viewWorkOrder(workOrder.work_order_id)"
              >
                <div class="card-header d-flex justify-content-between align-items-start p-2">
                  <small class="text-muted">#{{ workOrder.work_order_number }}</small>
                  <span class="badge" :class="getPriorityClass(workOrder.priority)">
                    {{ workOrder.priority }}
                  </span>
                </div>
                <div class="card-body p-2">
                  <h6 class="card-title mb-2">{{ workOrder.title }}</h6>
                  <p class="card-text small text-muted mb-2">{{ workOrder.description }}</p>
                  
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-truck me-1"></i>
                    <small class="text-muted">{{ workOrder.asset_details?.asset_number }}</small>
                  </div>
                  
                  <div v-if="workOrder.assigned_to" class="d-flex align-items-center mb-2">
                    <i class="bi bi-person me-1"></i>
                    <small class="text-muted">{{ workOrder.assigned_to.first_name }} {{ workOrder.assigned_to.last_name }}</small>
                  </div>
                  
                  <div v-if="workOrder.due_date" class="d-flex align-items-center mb-2">
                    <i class="bi bi-calendar3 me-1"></i>
                    <small :class="isOverdue(workOrder.due_date) ? 'text-danger' : 'text-muted'">
                      Due: {{ formatDate(workOrder.due_date) }}
                    </small>
                  </div>
                  
                  <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">{{ formatDate(workOrder.created_at) }}</small>
                    <div class="dropdown" @click.stop>
                      <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                              data-bs-toggle="dropdown">
                        <i class="bi bi-three-dots"></i>
                      </button>
                      <ul class="dropdown-menu">
                        <li>
                          <router-link :to="`/work-orders/${workOrder.work_order_id}`" class="dropdown-item">
                            <i class="bi bi-eye me-2"></i>View
                          </router-link>
                        </li>
                        <li>
                          <router-link :to="`/work-orders/${workOrder.work_order_id}/edit`" class="dropdown-item">
                            <i class="bi bi-pencil me-2"></i>Edit
                          </router-link>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                          <button @click="changeStatus(workOrder, 'completed')" class="dropdown-item">
                            <i class="bi bi-check-circle me-2"></i>Mark Complete
                          </button>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Empty Column Message -->
              <div v-if="getStatusWorkOrders(status.value).length === 0" class="empty-column">
                <i class="bi bi-clipboard-x text-muted opacity-50"></i>
                <p class="text-muted mt-2 mb-0">No {{ status.label.toLowerCase() }} work orders</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Work Orders List</h5>
        <span class="text-muted">{{ workOrders.length }} work orders</span>
      </div>
      <div class="card-body p-0">
        <!-- Empty State -->
        <div v-if="workOrders.length === 0" class="text-center py-5">
          <i class="bi bi-clipboard-x fs-1 text-muted opacity-50"></i>
          <h5 class="mt-3 text-muted">No work orders found</h5>
          <p class="text-muted">
            {{ hasFilters ? 'Try adjusting your filters' : 'Get started by creating your first work order' }}
          </p>
          <router-link v-if="!hasFilters" to="/work-orders/create" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>Create Work Order
          </router-link>
        </div>

        <!-- Work Orders Table -->
        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th @click="setSortBy('work_order_number')" class="sortable">
                  Work Order #
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th>Title & Description</th>
                <th>Asset</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Assigned To</th>
                <th @click="setSortBy('due_date')" class="sortable">
                  Due Date
                  <i class="bi bi-arrow-up-down ms-1"></i>
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="workOrder in workOrders" :key="workOrder.work_order_id" @click="viewWorkOrder(workOrder.work_order_id)">
                <td class="fw-bold">#{{ workOrder.work_order_number }}</td>
                <td>
                  <div>{{ workOrder.title }}</div>
                  <small class="text-muted">{{ workOrder.description || 'No description' }}</small>
                </td>
                <td>
                  <div class="fw-bold">{{ workOrder.asset_details?.asset_number }}</div>
                  <small class="text-muted">{{ workOrder.asset_details?.make }} {{ workOrder.asset_details?.model }}</small>
                </td>
                <td>
                  <span class="badge" :class="getStatusClass(workOrder.status)">
                    {{ formatStatus(workOrder.status) }}
                  </span>
                </td>
                <td>
                  <span class="badge" :class="getPriorityClass(workOrder.priority)">
                    {{ workOrder.priority }}
                  </span>
                </td>
                <td>
                  <div v-if="workOrder.assigned_to">
                    {{ workOrder.assigned_to.first_name }} {{ workOrder.assigned_to.last_name }}
                  </div>
                  <span v-else class="text-muted">Unassigned</span>
                </td>
                <td>
                  <div v-if="workOrder.due_date" :class="isOverdue(workOrder.due_date) ? 'text-danger' : ''">
                    {{ formatDate(workOrder.due_date) }}
                    <div v-if="isOverdue(workOrder.due_date)" class="small">
                      <i class="bi bi-exclamation-triangle"></i> Overdue
                    </div>
                  </div>
                  <span v-else class="text-muted">No due date</span>
                </td>
                <td @click.stop>
                  <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                            data-bs-toggle="dropdown">
                      Actions
                    </button>
                    <ul class="dropdown-menu">
                      <li>
                        <router-link :to="`/work-orders/${workOrder.work_order_id}`" class="dropdown-item">
                          <i class="bi bi-eye me-2"></i>View Details
                        </router-link>
                      </li>
                      <li>
                        <router-link :to="`/work-orders/${workOrder.work_order_id}/edit`" class="dropdown-item">
                          <i class="bi bi-pencil me-2"></i>Edit
                        </router-link>
                      </li>
                      <li><hr class="dropdown-divider"></li>
                      <li>
                        <button @click="changeStatus(workOrder, 'in_progress')" class="dropdown-item">
                          <i class="bi bi-play-circle me-2"></i>Start Work
                        </button>
                      </li>
                      <li>
                        <button @click="changeStatus(workOrder, 'completed')" class="dropdown-item">
                          <i class="bi bi-check-circle me-2"></i>Mark Complete
                        </button>
                      </li>
                    </ul>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { workOrdersAPI, assetsAPI } from '@/services/api'
import { toast } from '@/utils/toast'

export default {
  name: 'WorkOrdersBoard',
  setup() {
    const router = useRouter()
    
    const loading = ref(true)
    const viewMode = ref('board')
    const searchTimeout = ref(null)
    
    const workOrders = ref([])
    const assets = ref([])
    const technicians = ref([])
    
    const filters = reactive({
      search: '',
      asset: '',
      assigned_to: '',
      priority: '',
      date_range: '',
      ordering: '-created_at'
    })

    const workOrderStatuses = [
      { value: 'open', label: 'Open', color: 'secondary' },
      { value: 'assigned', label: 'Assigned', color: 'info' },
      { value: 'in_progress', label: 'In Progress', color: 'primary' },
      { value: 'on_hold', label: 'On Hold', color: 'warning' },
      { value: 'completed', label: 'Completed', color: 'success' },
      { value: 'closed', label: 'Closed', color: 'dark' }
    ]

    const hasFilters = computed(() => {
      return filters.search || filters.asset || filters.assigned_to || filters.priority || filters.date_range
    })

    const loadWorkOrders = async () => {
      loading.value = true
      
      try {
        const params = {
          page_size: 100,
          ...filters
        }
        
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key]
          }
        })
        
        const response = await workOrdersAPI.getWorkOrders(params)
        workOrders.value = response.data.results || []
      } catch (error) {
        console.error('Error loading work orders:', error)
        toast.error('Failed to load work orders')
        workOrders.value = []
      } finally {
        loading.value = false
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

    const loadTechnicians = async () => {
      try {
        // This would load users with technician role
        // For now, we'll use drivers as potential assignees
        const response = await workOrdersAPI.getTechnicians()
        technicians.value = response.data.results || []
      } catch (error) {
        console.error('Error loading technicians:', error)
      }
    }

    const getStatusWorkOrders = (status) => {
      return workOrders.value.filter(wo => wo.status === status)
    }

    const getStatusCount = (status) => {
      return getStatusWorkOrders(status).length
    }

    const debounceSearch = () => {
      clearTimeout(searchTimeout.value)
      searchTimeout.value = setTimeout(() => {
        loadWorkOrders()
      }, 500)
    }

    const clearFilters = () => {
      Object.assign(filters, {
        search: '',
        asset: '',
        assigned_to: '',
        priority: '',
        date_range: '',
        ordering: '-created_at'
      })
      loadWorkOrders()
    }

    const setSortBy = (field) => {
      if (filters.ordering === field) {
        filters.ordering = `-${field}`
      } else if (filters.ordering === `-${field}`) {
        filters.ordering = field
      } else {
        filters.ordering = field
      }
      loadWorkOrders()
    }

    const viewWorkOrder = (workOrderId) => {
      router.push(`/work-orders/${workOrderId}`)
    }

    const drag = (event, workOrder) => {
      event.dataTransfer.setData('workOrder', JSON.stringify(workOrder))
    }

    const drop = async (event, newStatus) => {
      event.preventDefault()
      const workOrder = JSON.parse(event.dataTransfer.getData('workOrder'))
      
      if (workOrder.status !== newStatus) {
        await changeStatus(workOrder, newStatus)
      }
    }

    const allowDrop = (event) => {
      event.preventDefault()
    }

    const changeStatus = async (workOrder, newStatus) => {
      try {
        await workOrdersAPI.updateWorkOrder(workOrder.work_order_id, { status: newStatus })
        
        // Update local state
        const index = workOrders.value.findIndex(wo => wo.work_order_id === workOrder.work_order_id)
        if (index !== -1) {
          workOrders.value[index].status = newStatus
        }
        
        toast.success(`Work order status updated to ${newStatus.replace('_', ' ')}`)
      } catch (error) {
        console.error('Error updating work order status:', error)
        toast.error('Failed to update work order status')
      }
    }

    const getStatusClass = (status) => {
      const statusClasses = {
        'open': 'bg-secondary',
        'assigned': 'bg-info',
        'in_progress': 'bg-primary',
        'on_hold': 'bg-warning',
        'completed': 'bg-success',
        'cancelled': 'bg-danger',
        'closed': 'bg-dark'
      }
      return statusClasses[status] || 'bg-secondary'
    }

    const getPriorityClass = (priority) => {
      const priorityClasses = {
        'low': 'bg-light text-dark',
        'medium': 'bg-warning text-dark',
        'high': 'bg-danger',
        'emergency': 'bg-danger'
      }
      return priorityClasses[priority] || 'bg-secondary'
    }

    const formatStatus = (status) => {
      return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const isOverdue = (dueDateString) => {
      if (!dueDateString) return false
      const dueDate = new Date(dueDateString)
      return dueDate < new Date()
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

    onMounted(async () => {
      await Promise.all([
        loadWorkOrders(),
        loadAssets(),
        loadTechnicians()
      ])
    })

    return {
      loading,
      viewMode,
      workOrders,
      assets,
      technicians,
      filters,
      workOrderStatuses,
      hasFilters,
      loadWorkOrders,
      getStatusWorkOrders,
      getStatusCount,
      debounceSearch,
      clearFilters,
      setSortBy,
      viewWorkOrder,
      drag,
      drop,
      allowDrop,
      changeStatus,
      getStatusClass,
      getPriorityClass,
      formatStatus,
      isOverdue,
      formatDate
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

.kanban-board {
  min-height: 600px;
}

.kanban-column {
  background: #f8f9fa;
  border-radius: 0.375rem;
  overflow: hidden;
  height: fit-content;
  min-height: 500px;
}

.kanban-header {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.kanban-body {
  padding: 1rem;
  min-height: 450px;
  max-height: 70vh;
  overflow-y: auto;
}

.work-order-card {
  background: white;
  border-radius: 0.375rem;
  border: 1px solid #dee2e6;
  margin-bottom: 0.75rem;
  cursor: move;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.work-order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
}

.work-order-card:last-child {
  margin-bottom: 0;
}

.work-order-card .card-header {
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.empty-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #6c757d;
}

.empty-column i {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.dropdown-toggle::after {
  display: none;
}

.badge {
  font-size: 0.65rem;
  text-transform: capitalize;
}

/* Drag and drop styling */
.kanban-body.drag-over {
  background-color: #e3f2fd;
  border: 2px dashed #2196f3;
}
</style>