<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4">
            Dashboard
          </v-card-title>
          <v-card-text>
            <p class="text-h6">Welcome, {{ user?.username || 'User' }}!</p>
            <p>You are successfully logged in.</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Dashboard',
  setup() {
    const authStore = useAuthStore()
    const user = computed(() => authStore.currentUser)
    
    return {
      user
    }
  }
}
</script>