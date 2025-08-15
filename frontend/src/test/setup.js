import { expect, afterEach, beforeEach, vi } from 'vitest'
import { cleanup } from '@testing-library/vue'
import '@testing-library/jest-dom'
import { config } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import { createPinia } from 'pinia'
import { server } from './mocks'

// Setup MSW server
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' })
})

afterEach(() => {
  server.resetHandlers()
  cleanup()
})

afterAll(() => {
  server.close()
})

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }))
})

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn(() => ({
  disconnect: vi.fn(),
  observe: vi.fn(),
  unobserve: vi.fn(),
}))

// Mock ResizeObserver
global.ResizeObserver = vi.fn(() => ({
  disconnect: vi.fn(),
  observe: vi.fn(),
  unobserve: vi.fn(),
}))

// Note: We don't set global plugins here to avoid duplication warnings
// Instead, we use the renderWithProviders and mountWithProviders helpers

// Mock router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  resolve: vi.fn(),
  currentRoute: {
    value: {
      path: '/',
      query: {},
      params: {}
    }
  }
}

config.global.mocks = {
  $router: mockRouter,
  $route: mockRouter.currentRoute.value
}

// Extend expect with custom matchers
expect.extend({
  toHaveAccessibleName(received, expected) {
    const pass = received.getAttribute('aria-label') === expected ||
                 received.getAttribute('aria-labelledby') ||
                 received.textContent.trim() === expected
    
    return {
      pass,
      message: () => pass 
        ? `expected element not to have accessible name "${expected}"`
        : `expected element to have accessible name "${expected}"`
    }
  }
})