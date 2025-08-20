import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCapitalPlanningStore } from '../capitalPlanning'
import apiClient from '@/services/api'

// Mock the API client
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

describe('Capital Planning Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useCapitalPlanningStore()
    vi.clearAllMocks()
  })

  describe('Feature Flag', () => {
    it('should check if capital planning is enabled', async () => {
      apiClient.get.mockResolvedValueOnce({ data: { success: true } })
      
      const result = await store.checkFeatureFlag()
      
      expect(result).toBe(true)
      expect(store.featureEnabled).toBe(true)
      expect(apiClient.get).toHaveBeenCalledWith('/cap-planning/v1/plans/')
    })

    it('should handle feature disabled (403 error)', async () => {
      apiClient.get.mockRejectedValueOnce({ 
        response: { status: 403 } 
      })
      
      const result = await store.checkFeatureFlag()
      
      expect(result).toBe(false)
      expect(store.featureEnabled).toBe(false)
    })
  })

  describe('Capital Plans', () => {
    it('should fetch capital plans', async () => {
      const mockPlans = [
        { id: 1, name: 'Plan 1', fiscal_year: 2025 },
        { id: 2, name: 'Plan 2', fiscal_year: 2026 }
      ]
      apiClient.get.mockResolvedValueOnce({ 
        data: { results: mockPlans, count: 2 } 
      })
      
      await store.fetchPlans({ status: 'draft' })
      
      expect(store.plans).toEqual(mockPlans)
      expect(store.totalCount).toBe(2)
      expect(apiClient.get).toHaveBeenCalledWith('/cap-planning/v1/plans/', {
        params: { status: 'draft' }
      })
    })

    it('should create a new capital plan', async () => {
      const newPlan = { 
        name: 'New Plan', 
        fiscal_year: 2027,
        total_budget: 1000000
      }
      const createdPlan = { id: 3, ...newPlan }
      apiClient.post.mockResolvedValueOnce({ data: createdPlan })
      
      const result = await store.createPlan(newPlan)
      
      expect(result).toEqual(createdPlan)
      expect(store.plans).toContainEqual(createdPlan)
      expect(apiClient.post).toHaveBeenCalledWith('/cap-planning/v1/plans/', newPlan)
    })

    it('should update a capital plan', async () => {
      const planId = 1
      const updates = { name: 'Updated Plan' }
      const updatedPlan = { id: planId, ...updates }
      store.plans = [{ id: planId, name: 'Old Plan' }]
      apiClient.patch.mockResolvedValueOnce({ data: updatedPlan })
      
      const result = await store.updatePlan(planId, updates)
      
      expect(result).toEqual(updatedPlan)
      expect(store.plans[0]).toEqual(updatedPlan)
      expect(apiClient.patch).toHaveBeenCalledWith(`/cap-planning/v1/plans/${planId}/`, updates)
    })

    it('should submit plan for review', async () => {
      const planId = 1
      const submittedPlan = { id: planId, status: 'review' }
      apiClient.post.mockResolvedValueOnce({ data: submittedPlan })
      
      const result = await store.submitForReview(planId)
      
      expect(result).toEqual(submittedPlan)
      expect(apiClient.post).toHaveBeenCalledWith(`/cap-planning/v1/plans/${planId}/submit_for_review/`)
    })
  })

  describe('Asset Lifecycle', () => {
    it('should fetch asset lifecycles', async () => {
      const mockAssets = [
        { id: 1, asset_name: 'Vehicle 1', current_condition: 'good' },
        { id: 2, asset_name: 'Equipment 1', current_condition: 'fair' }
      ]
      apiClient.get.mockResolvedValueOnce({ 
        data: { results: mockAssets, count: 2 } 
      })
      
      await store.fetchAssetLifecycles({ category: 'vehicle' })
      
      expect(store.assetLifecycles).toEqual(mockAssets)
      expect(store.assetLifecycleCount).toBe(2)
      expect(apiClient.get).toHaveBeenCalledWith('/cap-planning/v1/asset-lifecycle/', {
        params: { category: 'vehicle' }
      })
    })

    it('should update asset condition', async () => {
      const assetId = 1
      const conditionData = {
        condition: 'poor',
        assessment_date: '2025-01-01',
        notes: 'Wear and tear'
      }
      const updatedAsset = { id: assetId, current_condition: 'poor' }
      store.assetLifecycles = [{ id: assetId, current_condition: 'good' }]
      apiClient.post.mockResolvedValueOnce({ data: updatedAsset })
      
      const result = await store.updateAssetCondition(assetId, conditionData)
      
      expect(result).toEqual(updatedAsset)
      expect(store.assetLifecycles[0]).toEqual(updatedAsset)
      expect(apiClient.post).toHaveBeenCalledWith(
        `/cap-planning/v1/asset-lifecycle/${assetId}/update_condition/`,
        conditionData
      )
    })

    it('should fetch replacement schedule', async () => {
      const mockSchedule = [
        { year: 2025, asset_count: 3, total_cost: 500000 },
        { year: 2026, asset_count: 2, total_cost: 300000 }
      ]
      apiClient.get.mockResolvedValueOnce({ data: mockSchedule })
      
      const result = await store.fetchReplacementSchedule()
      
      expect(result).toEqual(mockSchedule)
      expect(apiClient.get).toHaveBeenCalledWith('/cap-planning/v1/asset-lifecycle/replacement_schedule/')
    })

    it('should fetch maintenance analysis', async () => {
      const mockAnalysis = {
        high_maintenance_assets: [
          { id: 1, maintenance_cost_ratio: 75 }
        ],
        total_assets: 10,
        assets_needing_review: 1
      }
      apiClient.get.mockResolvedValueOnce({ data: mockAnalysis })
      
      const result = await store.fetchMaintenanceAnalysis()
      
      expect(result).toEqual(mockAnalysis)
      expect(apiClient.get).toHaveBeenCalledWith('/cap-planning/v1/asset-lifecycle/maintenance_analysis/')
    })
  })

  describe('Capital Projects', () => {
    it('should fetch capital projects', async () => {
      const mockProjects = [
        { id: 1, title: 'Project 1', priority: 'high' },
        { id: 2, title: 'Project 2', priority: 'medium' }
      ]
      apiClient.get.mockResolvedValueOnce({ 
        data: { results: mockProjects, count: 2 } 
      })
      
      await store.fetchCapitalProjects({ status: 'proposed' })
      
      expect(store.capitalProjects).toEqual(mockProjects)
      expect(store.capitalProjectCount).toBe(2)
      expect(apiClient.get).toHaveBeenCalledWith('/cap-planning/v1/projects/', {
        params: { status: 'proposed' }
      })
    })

    it('should create a capital project', async () => {
      const newProject = {
        project_code: 'PROJ-001',
        title: 'New Project',
        estimated_cost: 100000
      }
      const createdProject = { id: 1, ...newProject }
      apiClient.post.mockResolvedValueOnce({ data: createdProject })
      
      const result = await store.createCapitalProject(newProject)
      
      expect(result).toEqual(createdProject)
      expect(store.capitalProjects).toContainEqual(createdProject)
      expect(apiClient.post).toHaveBeenCalledWith('/cap-planning/v1/projects/', newProject)
    })

    it('should approve a capital project', async () => {
      const projectId = 1
      const approvalData = { budget: 95000 }
      const approvedProject = { 
        id: projectId, 
        status: 'approved',
        approved_budget: 95000 
      }
      store.capitalProjects = [{ id: projectId, status: 'proposed' }]
      apiClient.post.mockResolvedValueOnce({ data: approvedProject })
      
      const result = await store.approveCapitalProject(projectId, approvalData)
      
      expect(result).toEqual(approvedProject)
      expect(store.capitalProjects[0]).toEqual(approvedProject)
      expect(apiClient.post).toHaveBeenCalledWith(
        `/cap-planning/v1/projects/${projectId}/approve/`,
        approvalData
      )
    })

    it('should link assets to a project', async () => {
      const projectId = 1
      const assets = [
        { asset_lifecycle_id: 1, relationship_type: 'replace' },
        { asset_lifecycle_id: 2, relationship_type: 'upgrade' }
      ]
      const mockLinks = assets.map((a, i) => ({ id: i + 1, ...a }))
      apiClient.post.mockResolvedValueOnce({ data: mockLinks })
      
      const result = await store.linkAssetsToProject(projectId, assets)
      
      expect(result).toEqual(mockLinks)
      expect(apiClient.post).toHaveBeenCalledWith(
        `/cap-planning/v1/projects/${projectId}/link_assets/`,
        { assets }
      )
    })

    it('should fetch project yearly summary', async () => {
      const mockSummary = [
        { 
          scheduled_year: 2025,
          total_projects: 5,
          total_estimated_cost: 1000000,
          approved_count: 3
        },
        {
          scheduled_year: 2026,
          total_projects: 3,
          total_estimated_cost: 750000,
          approved_count: 1
        }
      ]
      apiClient.get.mockResolvedValueOnce({ data: mockSummary })
      
      const result = await store.fetchProjectYearlySummary()
      
      expect(result).toEqual(mockSummary)
      expect(apiClient.get).toHaveBeenCalledWith('/cap-planning/v1/projects/yearly_summary/')
    })

    it('should fetch project priority matrix', async () => {
      const mockMatrix = {
        critical: {
          proposed: [{ id: 1, title: 'Critical Project' }],
          approved: [],
          in_progress: [],
          completed: []
        },
        high: {
          proposed: [],
          approved: [{ id: 2, title: 'High Priority' }],
          in_progress: [],
          completed: []
        },
        medium: { proposed: [], approved: [], in_progress: [], completed: [] },
        low: { proposed: [], approved: [], in_progress: [], completed: [] }
      }
      apiClient.get.mockResolvedValueOnce({ data: mockMatrix })
      
      const result = await store.fetchProjectPriorityMatrix()
      
      expect(result).toEqual(mockMatrix)
      expect(apiClient.get).toHaveBeenCalledWith('/cap-planning/v1/projects/priority_matrix/')
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const errorMessage = 'Network error'
      apiClient.get.mockRejectedValueOnce(new Error(errorMessage))
      
      await expect(store.fetchPlans()).rejects.toThrow(errorMessage)
      expect(store.error).toBe(errorMessage)
      expect(store.loading).toBe(false)
    })

    it('should set loading state correctly', async () => {
      apiClient.get.mockImplementationOnce(() => {
        expect(store.loading).toBe(true)
        return Promise.resolve({ data: { results: [], count: 0 } })
      })
      
      await store.fetchPlans()
      
      expect(store.loading).toBe(false)
    })
  })

  describe('State Management', () => {
    it('should reset store state', () => {
      // Set some state
      store.plans = [{ id: 1 }]
      store.currentPlan = { id: 1 }
      store.assetLifecycles = [{ id: 1 }]
      store.capitalProjects = [{ id: 1 }]
      store.loading = true
      store.error = 'Some error'
      
      store.reset()
      
      expect(store.plans).toEqual([])
      expect(store.currentPlan).toBeNull()
      expect(store.assetLifecycles).toEqual([])
      expect(store.capitalProjects).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })
  })
})