import { defineStore } from 'pinia'
import { authAPI } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isChecked: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    currentUser: (state) => state.user,
    isStaff: (state) => state.user?.is_staff || false,
    isLoading: (state) => !!state.token && !state.user && !state.isChecked
  },

  actions: {
    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },

    setUser(user) {
      this.user = user
    },

    async login(credentials) {
      try {
        const response = await authAPI.login(credentials)
        this.setUser(response.data.user || { username: credentials.username })
        this.setToken(response.data.token)
        return response.data
      } catch (error) {
        this.user = null
        this.setToken(null)
        throw error
      }
    },

    async register(userData) {
      try {
        const response = await authAPI.register(userData)
        this.setUser(response.data.user)
        this.setToken(response.data.token)
        return response.data
      } catch (error) {
        this.user = null
        this.setToken(null)
        throw error
      }
    },

    async logout() {
      try {
        await authAPI.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.user = null
        this.setToken(null)
        this.isChecked = false
      }
    },

    clearSession() {
      this.user = null
      this.setToken(null)
      this.isChecked = false
    },

    async checkAuth() {
      this.isChecked = true
      if (!this.token) {
        this.user = null
        return false
      }

      try {
        const response = await authAPI.checkAuth()
        this.setUser(response.data.user)
        return true
      } catch (error) {
        this.user = null
        this.setToken(null)
        return false
      }
    }
  }
})