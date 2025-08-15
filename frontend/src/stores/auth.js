import { defineStore } from 'pinia'
import { authAPI } from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isLoading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user,
  },

  actions: {
    async login(credentials) {
      this.isLoading = true
      this.error = null
      try {
        const response = await authAPI.login(credentials)
        this.token = response.data.token
        this.user = response.data.user
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
        localStorage.removeItem('token')
      }
    },

    async fetchUser() {
      if (!this.token) return
      try {
        const response = await authAPI.getUser()
        this.user = response.data
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