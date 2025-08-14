<template>
  <header class="app-header">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <!-- Brand and Mobile Toggle -->
        <button 
          class="navbar-toggler border-0 me-2" 
          type="button" 
          @click="toggleSidebar"
          aria-label="Toggle navigation"
        >
          <i class="bi bi-list"></i>
        </button>
        
        <router-link class="navbar-brand fw-bold" to="/dashboard">
          <i class="bi bi-truck me-2"></i>
          Fleet Manager
        </router-link>

        <!-- Right Side Items -->
        <div class="navbar-nav flex-row ms-auto">
          <!-- Notifications -->
          <div class="nav-item dropdown me-3">
            <button
              class="btn btn-outline-light position-relative"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i class="bi bi-bell"></i>
              <span 
                v-if="notificationCount > 0"
                class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
              >
                {{ notificationCount > 99 ? '99+' : notificationCount }}
              </span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end notification-dropdown">
              <li class="dropdown-header d-flex justify-content-between align-items-center">
                <span>Notifications</span>
                <button class="btn btn-sm btn-outline-primary" @click="markAllAsRead">
                  Mark all read
                </button>
              </li>
              <li><hr class="dropdown-divider"></li>
              
              <!-- Notification Items -->
              <li v-if="notifications.length === 0" class="dropdown-item-text text-muted text-center py-3">
                No new notifications
              </li>
              <li v-else v-for="notification in notifications" :key="notification.id" class="dropdown-item p-3">
                <div class="d-flex">
                  <div class="flex-shrink-0 me-2">
                    <i :class="getNotificationIcon(notification.type)" class="text-muted"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="fw-semibold small">{{ notification.title }}</div>
                    <div class="text-muted small">{{ notification.message }}</div>
                    <div class="text-muted small">{{ formatTime(notification.created_at) }}</div>
                  </div>
                </div>
              </li>
              
              <li><hr class="dropdown-divider"></li>
              <li>
                <router-link class="dropdown-item text-center" to="/notifications">
                  View all notifications
                </router-link>
              </li>
            </ul>
          </div>

          <!-- User Menu -->
          <div class="nav-item dropdown">
            <button
              class="btn btn-outline-light d-flex align-items-center"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <div class="user-avatar me-2">
                <i class="bi bi-person-circle"></i>
              </div>
              <span class="d-none d-md-inline">{{ userName }}</span>
              <i class="bi bi-chevron-down ms-1"></i>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li class="dropdown-header">
                {{ userName }}
                <div class="small text-muted">{{ userEmail }}</div>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <router-link class="dropdown-item" to="/profile">
                  <i class="bi bi-person me-2"></i>
                  Profile
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item" to="/settings">
                  <i class="bi bi-gear me-2"></i>
                  Settings
                </router-link>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <button class="dropdown-item text-danger" @click="logout">
                  <i class="bi bi-box-arrow-right me-2"></i>
                  Logout
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>
  </header>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'AppHeader',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    const userName = computed(() => {
      const user = authStore.currentUser
      return user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username : 'User'
    })

    const userEmail = computed(() => {
      return authStore.currentUser?.email || ''
    })

    const logout = async () => {
      try {
        await authStore.logout()
        router.push('/login')
      } catch (error) {
        console.error('Logout failed:', error)
      }
    }

    return {
      userName,
      userEmail,
      logout
    }
  },
  data() {
    return {
      notifications: [
        {
          id: 1,
          type: 'maintenance',
          title: 'Maintenance Due',
          message: 'Vehicle FL001 is due for maintenance',
          created_at: new Date(Date.now() - 30 * 60 * 1000) // 30 minutes ago
        },
        {
          id: 2,
          type: 'license',
          title: 'License Expiring',
          message: 'Driver John Doe license expires in 7 days',
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
        }
      ]
    }
  },
  computed: {
    notificationCount() {
      return this.notifications.length
    }
  },
  methods: {
    toggleSidebar() {
      this.$emit('toggle-sidebar')
    },
    
    getNotificationIcon(type) {
      const icons = {
        maintenance: 'bi bi-tools',
        license: 'bi bi-card-text',
        workorder: 'bi bi-clipboard-check',
        alert: 'bi bi-exclamation-triangle',
        default: 'bi bi-info-circle'
      }
      return icons[type] || icons.default
    },
    
    formatTime(date) {
      const now = new Date()
      const diff = now - new Date(date)
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(minutes / 60)
      const days = Math.floor(hours / 24)
      
      if (minutes < 60) {
        return `${minutes}m ago`
      } else if (hours < 24) {
        return `${hours}h ago`
      } else {
        return `${days}d ago`
      }
    },
    
    markAllAsRead() {
      this.notifications = []
    }
  }
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 1030;
  box-shadow: 0 2px 4px rgba(0,0,0,.1);
}

.user-avatar {
  font-size: 1.5rem;
}

.notification-dropdown {
  min-width: 320px;
  max-width: 400px;
}

.notification-dropdown .dropdown-item {
  white-space: normal;
  border-bottom: 1px solid #dee2e6;
}

.notification-dropdown .dropdown-item:last-child {
  border-bottom: none;
}

@media (max-width: 576px) {
  .notification-dropdown {
    min-width: 280px;
  }
}
</style>