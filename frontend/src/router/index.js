import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import Dashboard from '@/views/Dashboard.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'

// Asset Management
import AssetsList from '@/views/Assets/AssetsList.vue'
import AssetDetail from '@/views/Assets/AssetDetail.vue'
import AssetForm from '@/views/Assets/AssetForm.vue'

// Driver Management
import DriversList from '@/views/Drivers/DriversList.vue'
import DriverDetail from '@/views/Drivers/DriverDetail.vue'
import DriverForm from '@/views/Drivers/DriverForm.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  // Asset Management Routes
  {
    path: '/assets',
    name: 'AssetsList',
    component: AssetsList,
    meta: { requiresAuth: true }
  },
  {
    path: '/assets/create',
    name: 'AssetCreate',
    component: AssetForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/assets/:id',
    name: 'AssetDetail',
    component: AssetDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/assets/:id/edit',
    name: 'AssetEdit',
    component: AssetForm,
    meta: { requiresAuth: true }
  },
  // Driver Management Routes
  {
    path: '/drivers',
    name: 'DriversList',
    component: DriversList,
    meta: { requiresAuth: true }
  },
  {
    path: '/drivers/create',
    name: 'DriverCreate',
    component: DriverForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/drivers/:id',
    name: 'DriverDetail',
    component: DriverDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/drivers/:id/edit',
    name: 'DriverEdit',
    component: DriverForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/maintenance',
    name: 'MaintenanceList',
    component: () => import('@/views/Maintenance/MaintenanceList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/maintenance/schedule',
    name: 'MaintenanceSchedule',
    component: () => import('@/views/Maintenance/MaintenanceForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/maintenance/create',
    name: 'MaintenanceCreate',
    component: () => import('@/views/Maintenance/MaintenanceForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/work-orders',
    name: 'WorkOrdersList',
    component: () => import('@/views/WorkOrders/WorkOrdersBoard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tracking',
    name: 'Tracking',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check authentication status
  if (!authStore.isChecked) {
    await authStore.checkAuth()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router