import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import AssetLifecycleList from '../AssetLifecycleList.vue'
import { useCapitalPlanningStore } from '@/stores/capitalPlanning'

// Mock Vue Router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

describe('AssetLifecycleList UX Improvements', () => {
  let wrapper
  let vuetify
  let store

  beforeEach(() => {
    vuetify = createVuetify()
    setActivePinia(createPinia())
    store = useCapitalPlanningStore()
    
    // Mock store methods
    store.fetchAssetLifecycles = vi.fn().mockResolvedValue([])
    store.updateAssetCondition = vi.fn().mockResolvedValue({})
    store.fetchReplacementSchedule = vi.fn().mockResolvedValue([])
    store.assetLifecycles = []
    store.assetLifecycleCount = 0
  })

  describe('Error Handling', () => {
    it('should display error notification when loading fails', async () => {
      store.fetchAssetLifecycles = vi.fn().mockRejectedValue(new Error('Network error'))
      
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.errorSnackbar).toBe(true)
      expect(wrapper.vm.errorMessage).toBe('Failed to load assets. Please try again.')
    })

    it('should display success notification after condition update', async () => {
      store.updateAssetCondition = vi.fn().mockResolvedValue({})
      
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      wrapper.vm.selectedAsset = { id: 1, name: 'Test Asset' }
      await wrapper.vm.saveConditionUpdate()

      expect(wrapper.vm.successSnackbar).toBe(true)
      expect(wrapper.vm.successMessage).toBe('Asset condition updated successfully')
    })
  })

  describe('Accessibility Features', () => {
    it('should have proper ARIA labels on stat cards', () => {
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      const statCards = wrapper.findAll('[role="button"]')
      expect(statCards.length).toBeGreaterThan(0)
      
      statCards.forEach(card => {
        expect(card.attributes('aria-label')).toBeTruthy()
        expect(card.attributes('tabindex')).toBe('0')
      })
    })

    it('should support keyboard navigation on clickable cards', async () => {
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      const card = wrapper.find('[role="button"]')
      await card.trigger('keydown.enter')
      
      // Verify the filter was triggered
      expect(store.fetchAssetLifecycles).toHaveBeenCalled()
    })

    it('should have focus indicators on interactive elements', () => {
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      const styles = wrapper.find('style').text()
      expect(styles).toContain('.stat-card:focus')
      expect(styles).toContain('outline')
    })
  })

  describe('Empty States', () => {
    it('should display empty state when no assets found', async () => {
      store.assetLifecycles = []
      
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      await wrapper.vm.$nextTick()
      wrapper.vm.loading = false
      await wrapper.vm.$nextTick()

      const emptyState = wrapper.find('.text-center.pa-8')
      expect(emptyState.exists()).toBe(true)
      expect(emptyState.text()).toContain('No assets found')
    })

    it('should show different message when filters are active', async () => {
      store.assetLifecycles = []
      
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      wrapper.vm.filters.condition = 'critical'
      wrapper.vm.loading = false
      await wrapper.vm.$nextTick()

      const emptyState = wrapper.find('.text-center.pa-8')
      expect(emptyState.text()).toContain('Try adjusting your filters')
    })

    it('should provide clear filters button in empty state', async () => {
      store.assetLifecycles = []
      
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      wrapper.vm.filters.condition = 'critical'
      wrapper.vm.loading = false
      await wrapper.vm.$nextTick()

      const clearButton = wrapper.find('.text-center.pa-8 .v-btn')
      expect(clearButton.text()).toContain('Clear Filters')
      
      await clearButton.trigger('click')
      expect(wrapper.vm.filters.condition).toBeNull()
    })
  })

  describe('Loading States', () => {
    it('should display skeleton loader when loading initial data', async () => {
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      wrapper.vm.loading = true
      wrapper.vm.assets = []
      await wrapper.vm.$nextTick()

      const skeletons = wrapper.findAll('v-skeleton-loader')
      expect(skeletons.length).toBeGreaterThan(0)
    })
  })

  describe('Card Behavior Consistency', () => {
    it('should only make clickable cards interactive', () => {
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      const nonClickableCard = wrapper.find('.stat-card.non-clickable')
      expect(nonClickableCard.exists()).toBe(true)
      expect(nonClickableCard.attributes('role')).toBe('status')
      expect(nonClickableCard.attributes('tabindex')).toBeUndefined()
    })

    it('should provide visual feedback for active filters', async () => {
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      wrapper.vm.filters.condition = 'critical'
      await wrapper.vm.$nextTick()

      const criticalCard = wrapper.find('[aria-label*="critical condition"]')
      expect(criticalCard.classes()).toContain('active')
      expect(criticalCard.attributes('aria-pressed')).toBe('true')
    })
  })

  describe('User Feedback', () => {
    it('should show clear filter function', () => {
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      wrapper.vm.filters = {
        category: 'vehicle',
        condition: 'good',
        department: 'ops'
      }
      wrapper.vm.searchQuery = 'test'

      wrapper.vm.clearFilters()

      expect(wrapper.vm.filters.category).toBeNull()
      expect(wrapper.vm.filters.condition).toBeNull()
      expect(wrapper.vm.filters.department).toBeNull()
      expect(wrapper.vm.searchQuery).toBe('')
    })

    it('should debounce search input', async () => {
      wrapper = mount(AssetLifecycleList, {
        global: {
          plugins: [vuetify]
        }
      })

      const fetchSpy = vi.spyOn(store, 'fetchAssetLifecycles')
      
      wrapper.vm.debouncedSearch()
      wrapper.vm.debouncedSearch()
      wrapper.vm.debouncedSearch()

      // Should not be called immediately
      expect(fetchSpy).not.toHaveBeenCalled()

      // Wait for debounce
      await new Promise(resolve => setTimeout(resolve, 600))
      
      // Should only be called once after debounce
      expect(fetchSpy).toHaveBeenCalledTimes(1)
    })
  })
})