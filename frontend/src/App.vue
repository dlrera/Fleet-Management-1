<template>
  <div id="app">
    <!-- Loading Screen -->
    <div v-if="authStore.isLoading" class="d-flex justify-content-center align-items-center" style="min-height: 100vh;">
      <div class="text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading...</p>
      </div>
    </div>
    
    <!-- Authenticated Layout -->
    <AppLayout v-else-if="authStore.isAuthenticated" />
    
    <!-- Public Layout (Login/Register) -->
    <router-view v-else />
  </div>
</template>

<script>
import { useAuthStore } from '@/store/auth'
import { onMounted } from 'vue'
import AppLayout from '@/components/Layout/AppLayout.vue'

export default {
  name: 'App',
  components: {
    AppLayout
  },
  setup() {
    const authStore = useAuthStore()

    onMounted(async () => {
      // Check authentication on app start
      if (authStore.token && !authStore.isChecked) {
        await authStore.checkAuth()
      }
    })

    return {
      authStore
    }
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>