/**
 * Global Toast Notification System
 * Provides easy-to-use functions for showing toast notifications
 */

export const toast = {
  /**
   * Show a success toast
   * @param {string} message - The message to display
   * @param {string} title - Optional title (defaults to 'Success')
   * @param {number} duration - Duration in milliseconds (defaults to 5000)
   */
  success(message, title = 'Success', duration = 5000) {
    this.show({
      type: 'success',
      title,
      message,
      duration
    })
  },

  /**
   * Show an error toast
   * @param {string} message - The message to display
   * @param {string} title - Optional title (defaults to 'Error')
   * @param {number} duration - Duration in milliseconds (defaults to 7000)
   */
  error(message, title = 'Error', duration = 7000) {
    this.show({
      type: 'danger',
      title,
      message,
      duration
    })
  },

  /**
   * Show a warning toast
   * @param {string} message - The message to display
   * @param {string} title - Optional title (defaults to 'Warning')
   * @param {number} duration - Duration in milliseconds (defaults to 6000)
   */
  warning(message, title = 'Warning', duration = 6000) {
    this.show({
      type: 'warning',
      title,
      message,
      duration
    })
  },

  /**
   * Show an info toast
   * @param {string} message - The message to display
   * @param {string} title - Optional title (defaults to 'Info')
   * @param {number} duration - Duration in milliseconds (defaults to 5000)
   */
  info(message, title = 'Info', duration = 5000) {
    this.show({
      type: 'info',
      title,
      message,
      duration
    })
  },

  /**
   * Show a custom toast
   * @param {Object} options - Toast options
   * @param {string} options.type - Toast type (success, danger, warning, info, primary, secondary, light, dark)
   * @param {string} options.title - Toast title
   * @param {string} options.message - Toast message
   * @param {number} options.duration - Duration in milliseconds
   */
  show(options) {
    const event = new CustomEvent('show-toast', {
      detail: options
    })
    window.dispatchEvent(event)
  }
}

/**
 * Vue 3 plugin for global toast notifications
 */
export const ToastPlugin = {
  install(app) {
    app.config.globalProperties.$toast = toast
    app.provide('toast', toast)
  }
}

export default toast