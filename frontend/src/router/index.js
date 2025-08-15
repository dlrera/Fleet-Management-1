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