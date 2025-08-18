<template>
  <v-app>
    <template v-if="!authStore.isAuthenticated">
      <router-view />
    </template>
    
    <template v-else>
      <!-- Navigation Drawer -->
      <v-navigation-drawer
        v-model="drawer"
        app
        color="secondary"
        dark
      >
        <v-list-item
          class="px-2 py-4"
          title="Fleet Management"
          subtitle="System"
        >
          <template v-slot:prepend>
            <v-icon size="40">mdi-truck</v-icon>
          </template>
        </v-list-item>

        <v-divider></v-divider>

        <v-list density="compact" nav>
          <v-list-item
            prepend-icon="mdi-view-dashboard"
            title="Dashboard"
            to="/"
            color="primary"
            style="color: white !important;"
          ></v-list-item>
          
          <v-list-item
            prepend-icon="mdi-truck"
            title="Assets"
            to="/assets"
            color="primary"
            style="color: white !important;"
          ></v-list-item>
          
          <v-list-item
            prepend-icon="mdi-account-group"
            title="Drivers"
            to="/drivers"
            color="primary"
            style="color: white !important;"
          ></v-list-item>
          
          <v-list-item
            prepend-icon="mdi-gas-station"
            title="Fuel"
            to="/fuel"
            color="primary"
            style="color: white !important;"
          ></v-list-item>
          
          <v-list-item
            prepend-icon="mdi-map"
            title="Locations"
            to="/locations"
            color="primary"
            style="color: white !important;"
          ></v-list-item>
        </v-list>
      </v-navigation-drawer>

      <!-- App Bar -->
      <v-app-bar app color="primary" dark>
        <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
        <v-toolbar-title>Fleet Management System</v-toolbar-title>
        <v-spacer></v-spacer>
        
        <v-menu>
          <template v-slot:activator="{ props }">
            <v-btn icon v-bind="props">
              <v-icon>mdi-account-circle</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item class="px-4">
              <v-list-item-title>{{ authStore.currentUser?.username }}</v-list-item-title>
              <v-list-item-subtitle>{{ authStore.currentUser?.email }}</v-list-item-subtitle>
              <v-list-item-subtitle v-if="authStore.roles.length > 0" class="mt-1">
                <v-chip
                  v-for="role in authStore.roles"
                  :key="role"
                  size="x-small"
                  class="mr-1"
                  :color="getRoleColor(role)"
                >
                  {{ role }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>
            <v-divider></v-divider>
            <v-list-item v-if="authStore.isAdmin" @click="router.push('/admin/users')">
              <template v-slot:prepend>
                <v-icon>mdi-account-group</v-icon>
              </template>
              <v-list-item-title>Manage Users</v-list-item-title>
            </v-list-item>
            <v-list-item v-if="authStore.isAdmin" @click="router.push('/admin/audit')">
              <template v-slot:prepend>
                <v-icon>mdi-file-document-outline</v-icon>
              </template>
              <v-list-item-title>Audit Logs</v-list-item-title>
            </v-list-item>
            <v-list-item @click="handleLogout">
              <template v-slot:prepend>
                <v-icon>mdi-logout</v-icon>
              </template>
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-app-bar>

      <!-- Main Content -->
      <v-main>
        <router-view />
      </v-main>
    </template>
  </v-app>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    const drawer = ref(true)

    const handleLogout = async () => {
      await authStore.logout()
      router.push('/login')
    }
    
    const getRoleColor = (role) => {
      const colors = {
        'Admin': 'red',
        'Fleet Manager': 'blue',
        'Technician': 'green',
        'Read-only': 'grey'
      }
      return colors[role] || 'default'
    }

    onMounted(async () => {
      // Check authentication on app start
      if (authStore.token) {
        try {
          await authStore.fetchUser()
        } catch (error) {
          console.error('Failed to fetch user:', error)
        }
      }
    })

    return {
      authStore,
      drawer,
      router,
      handleLogout,
      getRoleColor
    }
  }
}
</script>