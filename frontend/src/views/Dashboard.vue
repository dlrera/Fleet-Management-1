<template>
  <div class="dashboard">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="mb-1">Fleet Dashboard</h1>
        <p class="text-muted mb-0">Welcome back, {{ userName }}! Here's what's happening with your fleet today.</p>
      </div>
      <div class="text-end">
        <div class="small text-muted">Last updated</div>
        <div class="small">{{ formatDateTime(lastUpdated) }}</div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Key Metrics Cards -->
      <div class="row g-4 mb-4">
        <!-- Total Assets -->
        <div class="col-md-3 col-sm-6">
          <div class="card text-white bg-primary dashboard-card">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="card-subtitle mb-2 text-white-50">Total Assets</h6>
                  <h2 class="card-title mb-0">{{ statistics.assets?.total_assets || 0 }}</h2>
                  <div class="small">
                    <i class="bi bi-arrow-up"></i>
                    {{ statistics.assets?.active_assets || 0 }} active
                  </div>
                </div>
                <i class="bi bi-truck fs-1 opacity-50"></i>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Active Drivers -->
        <div class="col-md-3 col-sm-6">
          <div class="card text-white bg-success dashboard-card">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="card-subtitle mb-2 text-white-50">Active Drivers</h6>
                  <h2 class="card-title mb-0">{{ statistics.drivers?.active_drivers || 0 }}</h2>
                  <div class="small">
                    <i class="bi bi-exclamation-triangle" v-if="statistics.drivers?.licenses_expiring_30_days > 0"></i>
                    {{ statistics.drivers?.licenses_expiring_30_days || 0 }} expiring soon
                  </div>
                </div>
                <i class="bi bi-person-badge fs-1 opacity-50"></i>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Maintenance Due -->
        <div class="col-md-3 col-sm-6">
          <div class="card text-white bg-warning dashboard-card">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="card-subtitle mb-2 text-white-50">Maintenance Due</h6>
                  <h2 class="card-title mb-0">{{ statistics.maintenance?.due_today || 0 }}</h2>
                  <div class="small">
                    <i class="bi bi-exclamation-triangle" v-if="statistics.maintenance?.overdue > 0"></i>
                    {{ statistics.maintenance?.overdue || 0 }} overdue
                  </div>
                </div>
                <i class="bi bi-tools fs-1 opacity-50"></i>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Work Orders -->
        <div class="col-md-3 col-sm-6">
          <div class="card text-white bg-info dashboard-card">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="card-subtitle mb-2 text-white-50">Open Work Orders</h6>
                  <h2 class="card-title mb-0">{{ statistics.workOrders?.total_open || 0 }}</h2>
                  <div class="small">
                    <i class="bi bi-clock" v-if="statistics.workOrders?.overdue > 0"></i>
                    {{ statistics.workOrders?.overdue || 0 }} overdue
                  </div>
                </div>
                <i class="bi bi-clipboard-check fs-1 opacity-50"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Alerts Section -->
      <div v-if="hasAlerts" class="row mb-4">
        <div class="col-12">
          <div class="card border-warning">
            <div class="card-header bg-warning text-dark">
              <h5 class="mb-0">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Attention Required
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <!-- License Expiring -->
                <div v-if="alerts.licensesExpiring.length > 0" class="col-md-4 mb-3">
                  <h6 class="text-warning">
                    <i class="bi bi-card-text me-1"></i>
                    Licenses Expiring ({{ alerts.licensesExpiring.length }})
                  </h6>
                  <div class="small">
                    <div v-for="driver in alerts.licensesExpiring.slice(0, 3)" :key="driver.driver_id" class="mb-1">
                      {{ driver.user?.first_name }} {{ driver.user?.last_name }} - {{ formatDate(driver.license_expiry_date) }}
                    </div>
                    <router-link v-if="alerts.licensesExpiring.length > 3" to="/drivers" class="text-decoration-none">
                      View {{ alerts.licensesExpiring.length - 3 }} more...
                    </router-link>
                  </div>
                </div>

                <!-- Assets Expiring -->
                <div v-if="alerts.assetsExpiring.length > 0" class="col-md-4 mb-3">
                  <h6 class="text-warning">
                    <i class="bi bi-truck me-1"></i>
                    Documents Expiring ({{ alerts.assetsExpiring.length }})
                  </h6>
                  <div class="small">
                    <div v-for="asset in alerts.assetsExpiring.slice(0, 3)" :key="asset.asset_id" class="mb-1">
                      {{ asset.asset_number }} - Insurance/Registration
                    </div>
                    <router-link v-if="alerts.assetsExpiring.length > 3" to="/assets" class="text-decoration-none">
                      View {{ alerts.assetsExpiring.length - 3 }} more...
                    </router-link>
                  </div>
                </div>

                <!-- Maintenance Overdue -->
                <div v-if="alerts.maintenanceOverdue.length > 0" class="col-md-4 mb-3">
                  <h6 class="text-danger">
                    <i class="bi bi-tools me-1"></i>
                    Maintenance Overdue ({{ alerts.maintenanceOverdue.length }})
                  </h6>
                  <div class="small">
                    <div v-for="schedule in alerts.maintenanceOverdue.slice(0, 3)" :key="schedule.schedule_id" class="mb-1">
                      {{ schedule.asset_number }} - {{ schedule.maintenance_type_name }}
                    </div>
                    <router-link v-if="alerts.maintenanceOverdue.length > 3" to="/maintenance/due" class="text-decoration-none">
                      View {{ alerts.maintenanceOverdue.length - 3 }} more...
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Row -->
      <div class="row">
        <!-- Recent Activities & Work Orders -->
        <div class="col-lg-8">
          <!-- Recent Work Orders -->
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-clipboard-check me-2"></i>
                Recent Work Orders
              </h5>
              <router-link to="/work-orders" class="btn btn-sm btn-outline-primary">
                View All
              </router-link>
            </div>
            <div class="card-body">
              <div v-if="recentWorkOrders.length === 0" class="text-center text-muted py-3">
                <i class="bi bi-clipboard-x fs-1 opacity-50"></i>
                <p class="mb-0 mt-2">No recent work orders</p>
              </div>
              <div v-else class="list-group list-group-flush">
                <div 
                  v-for="wo in recentWorkOrders" 
                  :key="wo.work_order_id" 
                  class="list-group-item d-flex justify-content-between align-items-start border-0 px-0"
                >
                  <div class="ms-2 me-auto">
                    <div class="d-flex align-items-center">
                      <span class="badge me-2" :class="getWorkOrderStatusClass(wo.status)">
                        {{ wo.status }}
                      </span>
                      <strong>{{ wo.work_order_number }}</strong>
                    </div>
                    <div class="text-muted small">
                      {{ wo.asset_details?.asset_number }} - {{ wo.title }}
                    </div>
                  </div>
                  <small class="text-muted">{{ formatDate(wo.created_at) }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions & Summary -->
        <div class="col-lg-4">
          <!-- Quick Actions -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-lightning-charge me-2"></i>
                Quick Actions
              </h5>
            </div>
            <div class="card-body">
              <div class="d-grid gap-2">
                <router-link to="/assets/create" class="btn btn-primary">
                  <i class="bi bi-plus-circle me-2"></i>Add Asset
                </router-link>
                <router-link to="/drivers/create" class="btn btn-success">
                  <i class="bi bi-person-plus me-2"></i>Add Driver
                </router-link>
                <router-link to="/work-orders/create" class="btn btn-warning">
                  <i class="bi bi-wrench me-2"></i>Create Work Order
                </router-link>
                <router-link to="/tracking/live" class="btn btn-info">
                  <i class="bi bi-geo-alt me-2"></i>Live Tracking
                </router-link>
              </div>
            </div>
          </div>

          <!-- Fleet Summary -->
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-pie-chart me-2"></i>
                Fleet Summary
              </h5>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-6 border-end">
                  <h6 class="text-primary">{{ statistics.assets?.total_distance_km || 0 }}K</h6>
                  <small class="text-muted">Total KM</small>
                </div>
                <div class="col-6">
                  <h6 class="text-success">{{ statistics.trips?.active_trips || 0 }}</h6>
                  <small class="text-muted">Active Trips</small>
                </div>
              </div>
              <hr>
              <div class="row text-center">
                <div class="col-6 border-end">
                  <h6 class="text-info">${{ (statistics.maintenance?.total_cost_month || 0).toLocaleString() }}</h6>
                  <small class="text-muted">Monthly Costs</small>
                </div>
                <div class="col-6">
                  <h6 class="text-warning">{{ statistics.parts?.low_stock_parts || 0 }}</h6>
                  <small class="text-muted">Low Stock</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { assetsAPI, driversAPI, maintenanceAPI, workOrdersAPI } from '@/services/api'
import { toast } from '@/utils/toast'

export default {
  name: 'Dashboard',
  setup() {
    const authStore = useAuthStore()
    const loading = ref(true)
    const lastUpdated = ref(new Date())
    
    const statistics = reactive({
      assets: {},
      drivers: {},
      maintenance: {},
      workOrders: {},
      trips: {},
      parts: {}
    })
    
    const alerts = reactive({
      licensesExpiring: [],
      assetsExpiring: [],
      maintenanceOverdue: []
    })
    
    const recentWorkOrders = ref([])

    const userName = computed(() => {
      const user = authStore.currentUser
      if (!user) return 'User'
      return `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username
    })

    const hasAlerts = computed(() => {
      return alerts.licensesExpiring.length > 0 || 
             alerts.assetsExpiring.length > 0 || 
             alerts.maintenanceOverdue.length > 0
    })

    const loadDashboardData = async () => {
      loading.value = true
      try {
        // Load all statistics in parallel
        const [
          assetsStats,
          driversStats,
          maintenanceStats,
          workOrdersStats,
          recentWOs
        ] = await Promise.allSettled([
          assetsAPI.getAssetStatistics(),
          driversAPI.getDriverStatistics(),
          maintenanceAPI.getScheduleStatistics(),
          workOrdersAPI.getDashboard(),
          workOrdersAPI.getWorkOrders({ page_size: 10, ordering: '-created_at' })
        ])

        // Process results
        if (assetsStats.status === 'fulfilled') {
          Object.assign(statistics.assets, assetsStats.value.data)
        }
        
        if (driversStats.status === 'fulfilled') {
          Object.assign(statistics.drivers, driversStats.value.data)
        }
        
        if (maintenanceStats.status === 'fulfilled') {
          Object.assign(statistics.maintenance, maintenanceStats.value.data)
        }
        
        if (workOrdersStats.status === 'fulfilled') {
          Object.assign(statistics.workOrders, workOrdersStats.value.data.quick_stats)
          recentWorkOrders.value = workOrdersStats.value.data.recent_orders
        } else if (recentWOs.status === 'fulfilled') {
          recentWorkOrders.value = recentWOs.value.data.results || []
        }

        // Load alerts
        await loadAlerts()

        lastUpdated.value = new Date()
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        toast.error('Failed to load dashboard data')
      } finally {
        loading.value = false
      }
    }

    const loadAlerts = async () => {
      try {
        const [licenseAlertsRes, assetAlertsRes, maintenanceAlertsRes] = await Promise.allSettled([
          driversAPI.getLicenseAlerts({ days_ahead: 30 }),
          assetsAPI.getExpiringAssets({ days_ahead: 30 }),
          maintenanceAPI.getDueMaintenance({ days_ahead: 0 })
        ])

        if (licenseAlertsRes.status === 'fulfilled') {
          alerts.licensesExpiring = licenseAlertsRes.value.data.expiring_licenses || []
        }

        if (assetAlertsRes.status === 'fulfilled') {
          alerts.assetsExpiring = assetAlertsRes.value.data || []
        }

        if (maintenanceAlertsRes.status === 'fulfilled') {
          alerts.maintenanceOverdue = maintenanceAlertsRes.value.data.overdue_schedules || []
        }
      } catch (error) {
        console.error('Error loading alerts:', error)
      }
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

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getWorkOrderStatusClass = (status) => {
      const statusClasses = {
        'open': 'bg-secondary',
        'assigned': 'bg-info',
        'in_progress': 'bg-primary', 
        'on_hold': 'bg-warning',
        'completed': 'bg-success',
        'cancelled': 'bg-dark',
        'closed': 'bg-dark'
      }
      return statusClasses[status] || 'bg-secondary'
    }

    onMounted(() => {
      loadDashboardData()
      
      // Set up auto-refresh every 5 minutes
      const refreshInterval = setInterval(loadDashboardData, 5 * 60 * 1000)
      
      // Cleanup interval on unmount
      return () => {
        clearInterval(refreshInterval)
      }
    })

    return {
      loading,
      lastUpdated,
      statistics,
      alerts,
      recentWorkOrders,
      userName,
      hasAlerts,
      formatDate,
      formatDateTime,
      getWorkOrderStatusClass,
      loadDashboardData
    }
  }
}
</script>

<style scoped>
.dashboard-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.dashboard-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.12);
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dashboard > * {
  animation: fadeIn 0.5s ease-out;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .dashboard-card .card-body {
    padding: 1rem 0.75rem;
  }
  
  .dashboard-card h2 {
    font-size: 1.5rem;
  }
}
</style>