<template>
  <div class="toast-container position-fixed top-0 end-0 p-3">
    <div 
      v-for="toast in toasts" 
      :key="toast.id"
      class="toast show"
      :class="`bg-${toast.type}`"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="toast-header">
        <i 
          :class="[getToastIcon(toast.type), 'me-2', `text-${toast.type}`]"
        ></i>
        <strong class="me-auto">{{ toast.title }}</strong>
        <small class="text-muted">{{ formatTime(toast.timestamp) }}</small>
        <button 
          type="button" 
          class="btn-close" 
          @click="removeToast(toast.id)"
          aria-label="Close"
        ></button>
      </div>
      <div class="toast-body text-white" v-if="toast.type !== 'light'">
        {{ toast.message }}
      </div>
      <div class="toast-body" v-else>
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'AppToasts',
  setup() {
    const toasts = ref([])
    
    const addToast = (toast) => {
      const id = Date.now() + Math.random()
      const newToast = {
        id,
        timestamp: new Date(),
        ...toast
      }
      
      toasts.value.push(newToast)
      
      // Auto remove after delay
      setTimeout(() => {
        removeToast(id)
      }, toast.duration || 5000)
    }
    
    const removeToast = (id) => {
      const index = toasts.value.findIndex(toast => toast.id === id)
      if (index > -1) {
        toasts.value.splice(index, 1)
      }
    }
    
    const getToastIcon = (type) => {
      const icons = {
        success: 'bi bi-check-circle-fill',
        error: 'bi bi-exclamation-triangle-fill',
        warning: 'bi bi-exclamation-triangle-fill',
        info: 'bi bi-info-circle-fill',
        primary: 'bi bi-info-circle-fill',
        secondary: 'bi bi-info-circle-fill',
        light: 'bi bi-info-circle',
        dark: 'bi bi-info-circle-fill'
      }
      return icons[type] || icons.info
    }
    
    const formatTime = (timestamp) => {
      const now = new Date()
      const diff = now - timestamp
      const seconds = Math.floor(diff / 1000)
      
      if (seconds < 60) {
        return 'just now'
      } else if (seconds < 3600) {
        return `${Math.floor(seconds / 60)}m ago`
      } else {
        return `${Math.floor(seconds / 3600)}h ago`
      }
    }
    
    onMounted(() => {
      // Listen for global toast events
      window.addEventListener('show-toast', (event) => {
        addToast(event.detail)
      })
    })
    
    return {
      toasts,
      addToast,
      removeToast,
      getToastIcon,
      formatTime
    }
  }
}
</script>

<style scoped>
.toast-container {
  z-index: 1060;
  max-width: 400px;
}

.toast {
  margin-bottom: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.toast-header {
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
}

.toast.bg-success .toast-header {
  background-color: rgba(25, 135, 84, 0.1);
}

.toast.bg-error .toast-header,
.toast.bg-danger .toast-header {
  background-color: rgba(220, 53, 69, 0.1);
}

.toast.bg-warning .toast-header {
  background-color: rgba(255, 193, 7, 0.1);
}

.toast.bg-info .toast-header {
  background-color: rgba(13, 202, 240, 0.1);
}
</style>