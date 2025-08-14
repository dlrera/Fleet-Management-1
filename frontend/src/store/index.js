import { defineStore } from 'pinia'

export const useMainStore = defineStore('main', {
  state: () => ({
    user: null,
    vehicles: [],
    drivers: [],
    maintenance: [],
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.user,
    activeVehicles: (state) => state.vehicles.filter(v => v.status === 'active'),
    activeDrivers: (state) => state.drivers.filter(d => d.status === 'active'),
  },
  
  actions: {
    setUser(user) {
      this.user = user
    },
    
    logout() {
      this.user = null
      localStorage.removeItem('token')
    },
    
    async fetchVehicles() {
      // TODO: Implement API call
      this.vehicles = []
    },
    
    async fetchDrivers() {
      // TODO: Implement API call
      this.drivers = []
    },
    
    async fetchMaintenance() {
      // TODO: Implement API call
      this.maintenance = []
    },
  },
})