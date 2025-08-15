import { render } from '@testing-library/vue'
import { createVuetify } from 'vuetify'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

// Test routes
const routes = [
  { path: '/', name: 'Dashboard', component: { template: '<div>Dashboard</div>' } },
  { path: '/assets', name: 'AssetsList', component: { template: '<div>Assets List</div>' } },
  { path: '/assets/:id', name: 'AssetDetail', component: { template: '<div>Asset Detail</div>' } },
  { path: '/assets/:id/edit', name: 'AssetEdit', component: { template: '<div>Asset Edit</div>' } },
  { path: '/assets/create', name: 'AssetCreate', component: { template: '<div>Asset Create</div>' } }
]

// Custom render function with Vuetify and Pinia
export function renderWithProviders(component, options = {}) {
  const vuetify = createVuetify({
    theme: {
      defaultTheme: 'light'
    }
  })
  
  const pinia = createPinia()
  
  const router = createRouter({
    history: createWebHistory(),
    routes
  })
  
  const mergedOptions = {
    global: {
      plugins: [vuetify, pinia, router],
      ...options.global
    },
    ...options
  }
  
  return render(component, mergedOptions)
}

// Helper to create a mounted component with all providers
export function mountWithProviders(component, options = {}) {
  const { mount } = require('@vue/test-utils')
  
  const vuetify = createVuetify({
    theme: {
      defaultTheme: 'light'
    }
  })
  
  const pinia = createPinia()
  
  const router = createRouter({
    history: createWebHistory(),
    routes
  })
  
  return mount(component, {
    global: {
      plugins: [vuetify, pinia, router],
      ...options.global
    },
    ...options
  })
}

// Helper to wait for async operations
export async function waitForAsync() {
  await new Promise(resolve => setTimeout(resolve, 0))
}

// Helper to trigger keyboard events
export function triggerKeyboardEvent(element, key, type = 'keydown') {
  const event = new KeyboardEvent(type, { key })
  element.dispatchEvent(event)
}

// Helper to assert accessibility
export function assertAccessibility(wrapper, testId) {
  const element = wrapper.find(`[data-testid="${testId}"]`)
  expect(element.exists()).toBe(true)
  
  // Check for ARIA label or accessible text
  const hasAriaLabel = element.attributes('aria-label')
  const hasAriaLabelledBy = element.attributes('aria-labelledby')
  const hasText = element.text().trim().length > 0
  
  expect(hasAriaLabel || hasAriaLabelledBy || hasText).toBeTruthy()
}

// Helper to simulate file upload
export function createMockFile(name = 'test.pdf', size = 1024, type = 'application/pdf') {
  return new File(['mock content'], name, { type, size })
}

// Helper to mock form validation
export function mockFormValidation(isValid = true) {
  return {
    validate: () => Promise.resolve(isValid),
    reset: () => {},
    resetValidation: () => {}
  }
}