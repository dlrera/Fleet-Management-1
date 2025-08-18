import { defineStore } from 'pinia'
import { authAPI } from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    roles: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user,
    
    // Role-based getters
    isAdmin: (state) => state.roles.includes('Admin'),
    isFleetManager: (state) => state.roles.includes('Fleet Manager') || state.roles.includes('Admin'),
    isTechnician: (state) => state.roles.includes('Technician') || state.roles.includes('Fleet Manager') || state.roles.includes('Admin'),
    isReadOnly: (state) => state.roles.includes('Read-only') && state.roles.length === 1,
    
    // Permission helpers
    canCreateAsset: (state) => state.roles.some(r => ['Admin', 'Fleet Manager'].includes(r)),
    canEditAsset: (state) => state.roles.some(r => ['Admin', 'Fleet Manager'].includes(r)),
    canDeleteAsset: (state) => state.roles.some(r => ['Admin', 'Fleet Manager'].includes(r)),
    
    canCreateDriver: (state) => state.roles.some(r => ['Admin', 'Fleet Manager'].includes(r)),
    canEditDriver: (state) => state.roles.some(r => ['Admin', 'Fleet Manager'].includes(r)),
    canDeleteDriver: (state) => state.roles.some(r => ['Admin', 'Fleet Manager'].includes(r)),
    
    canCreateFuel: (state) => state.roles.some(r => ['Admin', 'Fleet Manager', 'Technician'].includes(r)),
    canEditFuel: (state) => state.roles.some(r => ['Admin', 'Fleet Manager', 'Technician'].includes(r)),
    canDeleteFuel: (state) => state.roles.some(r => ['Admin', 'Fleet Manager'].includes(r)),
  },

  actions: {
    async login(credentials) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authAPI.login(credentials)
        this.token = response.data.token
        this.user = response.data.user
        this.roles = response.data.roles || []
        localStorage.setItem('token', this.token)
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Login failed'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async register(userData) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authAPI.register(userData)
        this.token = response.data.token
        this.user = response.data.user
        this.roles = response.data.roles || ['Read-only']
        localStorage.setItem('token', this.token)
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Registration failed'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      try {
        await authAPI.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.token = null
        this.user = null
        this.roles = []
        localStorage.removeItem('token')
      }
    },

    async fetchUser() {
      if (!this.token) return
      try {
        const response = await authAPI.getUser()
        this.user = response.data
        this.roles = response.data.roles || []
        return response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch user'
        if (error.response?.status === 401) {
          this.logout()
        }
        throw error
      }
    },

    async checkAuth() {
      if (!this.token) {
        return false
      }
      try {
        const response = await authAPI.checkAuth()
        if (response.data.authenticated) {
          this.user = response.data.user
          this.roles = response.data.user.roles || []
          return true
        }
        this.logout()
        return false
      } catch (error) {
        this.logout()
        return false
      }
    },
  },
})