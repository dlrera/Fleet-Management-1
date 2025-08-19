import { ref } from 'vue'

// Global snackbar state
const snackbar = ref({
  show: false,
  message: '',
  color: 'success',
  timeout: 3000
})

export function useSnackbar() {
  const showSuccess = (message) => {
    snackbar.value = {
      show: true,
      message,
      color: 'success',
      timeout: 3000
    }
  }

  const showError = (message) => {
    snackbar.value = {
      show: true,
      message,
      color: 'error',
      timeout: 5000
    }
  }

  const showWarning = (message) => {
    snackbar.value = {
      show: true,
      message,
      color: 'warning',
      timeout: 4000
    }
  }

  const showInfo = (message) => {
    snackbar.value = {
      show: true,
      message,
      color: 'info',
      timeout: 3000
    }
  }

  const hideSnackbar = () => {
    snackbar.value.show = false
  }

  return {
    snackbar,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    hideSnackbar
  }
}