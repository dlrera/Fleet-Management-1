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
  // Check if route requires guest (not authenticated)
  else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
  } 
  else {
    next()
  }
})

export default router