import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/assets',
    name: 'AssetsList',
    component: () => import('../views/Assets/AssetsList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/assets/create',
    name: 'AssetCreate',
    component: () => import('../views/Assets/AssetForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/assets/:id',
    name: 'AssetDetail',
    component: () => import('../views/Assets/AssetDetail.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/assets/:id/edit',
    name: 'AssetEdit',
    component: () => import('../views/Assets/AssetForm.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/locations',
    name: 'LocationMap',
    component: () => import('../views/Locations/LocationMap.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/locations/zones',
    name: 'ZoneManagement',
    component: () => import('../views/Locations/ZoneManagement.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/drivers',
    name: 'DriversList',
    component: () => import('../views/Drivers/DriversList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/drivers/create',
    name: 'DriverCreate',
    component: () => import('../views/Drivers/DriverForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/drivers/:id',
    name: 'DriverDetail',
    component: () => import('../views/Drivers/DriverDetail.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/drivers/:id/edit',
    name: 'DriverEdit',
    component: () => import('../views/Drivers/DriverForm.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/fuel',
    name: 'FuelList',
    component: () => import('../views/Fuel/FuelList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/fuel/new',
    name: 'FuelCreate',
    component: () => import('../views/Fuel/FuelForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/fuel/:id/edit',
    name: 'FuelEdit',
    component: () => import('../views/Fuel/FuelForm.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: () => import('../views/Admin/UserManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/audit',
    name: 'AuditLogs',
    component: () => import('../views/Admin/AuditLogs.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/capital-planning',
    name: 'CapitalPlansList',
    component: () => import('../views/CapitalPlanning/PlansList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/capital-planning/new',
    name: 'CapitalPlanCreate',
    component: () => import('../views/CapitalPlanning/PlanForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/capital-planning/:id',
    name: 'CapitalPlanDetail',
    component: () => import('../views/CapitalPlanning/PlanDetail.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/capital-planning/:id/edit',
    name: 'CapitalPlanEdit',
    component: () => import('../views/CapitalPlanning/PlanForm.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/capital-planning/asset-lifecycle',
    name: 'AssetLifecycleList',
    component: () => import('../views/CapitalPlanning/AssetLifecycleList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/capital-planning/asset-lifecycle/new',
    name: 'AssetLifecycleCreate',
    component: () => import('../views/CapitalPlanning/AssetLifecycleForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/capital-planning/asset-lifecycle/:id',
    name: 'AssetLifecycleDetail',
    component: () => import('../views/CapitalPlanning/AssetLifecycleDetail.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/capital-planning/asset-lifecycle/:id/edit',
    name: 'AssetLifecycleEdit',
    component: () => import('../views/CapitalPlanning/AssetLifecycleForm.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/capital-planning/projects',
    name: 'CapitalProjectsList',
    component: () => import('../views/CapitalPlanning/ProjectsList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/capital-planning/projects/new',
    name: 'CapitalProjectCreate',
    component: () => import('../views/CapitalPlanning/ProjectForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/capital-planning/projects/:id',
    name: 'CapitalProjectDetail',
    component: () => import('../views/CapitalPlanning/ProjectDetail.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/capital-planning/projects/:id/edit',
    name: 'CapitalProjectEdit',
    component: () => import('../views/CapitalPlanning/ProjectForm.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/capital-planning/new',
    name: 'CapitalPlanCreate',
    component: () => import('../views/CapitalPlanning/PlanForm.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/capital-planning/:id',
    name: 'CapitalPlanDetail',
    component: () => import('../views/CapitalPlanning/PlanDetail.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/capital-planning/:id/edit',
    name: 'CapitalPlanEdit',
    component: () => import('../views/CapitalPlanning/PlanForm.vue'),
    meta: { requiresAuth: true },
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } 
  // Check if route requires admin role
  else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/')
  }
  // Check if route requires guest (not authenticated)
  else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
  } 
  else {
    next()
  }
})

export default router