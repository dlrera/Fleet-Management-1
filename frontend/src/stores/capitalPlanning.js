import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/services/api'

export const useCapitalPlanningStore = defineStore('capitalPlanning', () => {
  // State
  const plans = ref([])
  const currentPlan = ref(null)
  const planItems = ref([])
  const scenarios = ref([])
  const approvals = ref([])
  const loading = ref(false)
  const error = ref(null)
  const totalCount = ref(0)
  const featureEnabled = ref(false)
  
  // Asset Lifecycle state
  const assetLifecycles = ref([])
  const currentAssetLifecycle = ref(null)
  const assetLifecycleCount = ref(0)
  
  // Capital Projects state
  const capitalProjects = ref([])
  const currentCapitalProject = ref(null)
  const capitalProjectCount = ref(0)

  // Check if feature is enabled
  const checkFeatureFlag = async () => {
    try {
      const response = await apiClient.get('/cap-planning/v1/plans/')
      featureEnabled.value = true
      return true
    } catch (error) {
      if (error.response && error.response.status === 403) {
        featureEnabled.value = false
        return false
      }
      throw error
    }
  }

  // Fetch plans with filters
  const fetchPlans = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/cap-planning/v1/plans/', { params })
      plans.value = response.data.results || response.data
      totalCount.value = response.data.count || plans.value.length
      return plans.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch single plan
  const fetchPlan = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get(`/cap-planning/v1/plans/${id}/`)
      currentPlan.value = response.data
      return currentPlan.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create new plan
  const createPlan = async (planData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/cap-planning/v1/plans/', planData)
      plans.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Update plan
  const updatePlan = async (id, planData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.patch(`/cap-planning/v1/plans/${id}/`, planData)
      const index = plans.value.findIndex(p => p.id === id)
      if (index !== -1) {
        plans.value[index] = response.data
      }
      if (currentPlan.value?.id === id) {
        currentPlan.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Delete plan
  const deletePlan = async (id) => {
    loading.value = true
    error.value = null
    try {
      await apiClient.delete(`/cap-planning/v1/plans/${id}/`)
      plans.value = plans.value.filter(p => p.id !== id)
      if (currentPlan.value?.id === id) {
        currentPlan.value = null
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch plan items
  const fetchPlanItems = async (planId, params = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/cap-planning/v1/items/', {
        params: { plan: planId, ...params }
      })
      planItems.value = response.data.results || response.data
      return planItems.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create plan item
  const createPlanItem = async (itemData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/cap-planning/v1/items/', itemData)
      planItems.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Update plan item
  const updatePlanItem = async (id, itemData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.patch(`/cap-planning/v1/items/${id}/`, itemData)
      const index = planItems.value.findIndex(i => i.id === id)
      if (index !== -1) {
        planItems.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Delete plan item
  const deletePlanItem = async (id) => {
    loading.value = true
    error.value = null
    try {
      await apiClient.delete(`/cap-planning/v1/items/${id}/`)
      planItems.value = planItems.value.filter(i => i.id !== id)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch scenarios
  const fetchScenarios = async (planId) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/cap-planning/v1/scenarios/', {
        params: { plan: planId }
      })
      scenarios.value = response.data.results || response.data
      return scenarios.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Create scenario
  const createScenario = async (scenarioData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/cap-planning/v1/scenarios/', scenarioData)
      scenarios.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch approvals
  const fetchApprovals = async (planId) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/cap-planning/v1/approvals/', {
        params: { plan: planId }
      })
      approvals.value = response.data.results || response.data
      return approvals.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Submit plan for review
  const submitForReview = async (planId) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post(`/cap-planning/v1/plans/${planId}/submit_for_review/`)
      const index = plans.value.findIndex(p => p.id === planId)
      if (index !== -1) {
        plans.value[index] = response.data
      }
      if (currentPlan.value?.id === planId) {
        currentPlan.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Approve plan
  const approvePlan = async (planId, comments = '') => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post(`/cap-planning/v1/plans/${planId}/approve/`, {
        comments
      })
      const index = plans.value.findIndex(p => p.id === planId)
      if (index !== -1) {
        plans.value[index] = response.data
      }
      if (currentPlan.value?.id === planId) {
        currentPlan.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Reject plan
  const rejectPlan = async (planId, comments = '') => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post(`/cap-planning/v1/plans/${planId}/reject/`, {
        comments
      })
      const index = plans.value.findIndex(p => p.id === planId)
      if (index !== -1) {
        plans.value[index] = response.data
      }
      if (currentPlan.value?.id === planId) {
        currentPlan.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Fetch stats
  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/cap-planning/v1/plans/stats/')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  // Asset Lifecycle Management Functions
  const fetchAssetLifecycles = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/cap-planning/v1/asset-lifecycle/', { params })
      assetLifecycles.value = response.data.results || response.data
      assetLifecycleCount.value = response.data.count || assetLifecycles.value.length
      return assetLifecycles.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchAssetLifecycle = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get(`/cap-planning/v1/asset-lifecycle/${id}/`)
      currentAssetLifecycle.value = response.data
      return currentAssetLifecycle.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createAssetLifecycle = async (assetData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/cap-planning/v1/asset-lifecycle/', assetData)
      assetLifecycles.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateAssetLifecycle = async (id, assetData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.patch(`/cap-planning/v1/asset-lifecycle/${id}/`, assetData)
      const index = assetLifecycles.value.findIndex(a => a.id === id)
      if (index !== -1) {
        assetLifecycles.value[index] = response.data
      }
      if (currentAssetLifecycle.value?.id === id) {
        currentAssetLifecycle.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateAssetCondition = async (id, conditionData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post(`/cap-planning/v1/asset-lifecycle/${id}/update_condition/`, conditionData)
      const index = assetLifecycles.value.findIndex(a => a.id === id)
      if (index !== -1) {
        assetLifecycles.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchReplacementSchedule = async () => {
    try {
      const response = await apiClient.get('/cap-planning/v1/asset-lifecycle/replacement_schedule/')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const fetchMaintenanceAnalysis = async () => {
    try {
      const response = await apiClient.get('/cap-planning/v1/asset-lifecycle/maintenance_analysis/')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  // Capital Projects Functions
  const fetchCapitalProjects = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/cap-planning/v1/projects/', { params })
      capitalProjects.value = response.data.results || response.data
      capitalProjectCount.value = response.data.count || capitalProjects.value.length
      return capitalProjects.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCapitalProject = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get(`/cap-planning/v1/projects/${id}/`)
      currentCapitalProject.value = response.data
      return currentCapitalProject.value
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createCapitalProject = async (projectData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/cap-planning/v1/projects/', projectData)
      capitalProjects.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateCapitalProject = async (id, projectData) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.patch(`/cap-planning/v1/projects/${id}/`, projectData)
      const index = capitalProjects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        capitalProjects.value[index] = response.data
      }
      if (currentCapitalProject.value?.id === id) {
        currentCapitalProject.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const linkAssetsToProject = async (projectId, assets) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post(`/cap-planning/v1/projects/${projectId}/link_assets/`, { assets })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const approveCapitalProject = async (projectId, approvalData = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post(`/cap-planning/v1/projects/${projectId}/approve/`, approvalData)
      const index = capitalProjects.value.findIndex(p => p.id === projectId)
      if (index !== -1) {
        capitalProjects.value[index] = response.data
      }
      if (currentCapitalProject.value?.id === projectId) {
        currentCapitalProject.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchProjectYearlySummary = async () => {
    try {
      const response = await apiClient.get('/cap-planning/v1/projects/yearly_summary/')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const fetchProjectPriorityMatrix = async () => {
    try {
      const response = await apiClient.get('/cap-planning/v1/projects/priority_matrix/')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  // Reset store
  const reset = () => {
    plans.value = []
    currentPlan.value = null
    planItems.value = []
    scenarios.value = []
    approvals.value = []
    loading.value = false
    error.value = null
    totalCount.value = 0
    assetLifecycles.value = []
    currentAssetLifecycle.value = null
    assetLifecycleCount.value = 0
    capitalProjects.value = []
    currentCapitalProject.value = null
    capitalProjectCount.value = 0
  }

  return {
    // State
    plans,
    currentPlan,
    planItems,
    scenarios,
    approvals,
    loading,
    error,
    totalCount,
    featureEnabled,
    assetLifecycles,
    currentAssetLifecycle,
    assetLifecycleCount,
    capitalProjects,
    currentCapitalProject,
    capitalProjectCount,

    // Actions
    checkFeatureFlag,
    fetchPlans,
    fetchPlan,
    createPlan,
    updatePlan,
    deletePlan,
    fetchPlanItems,
    createPlanItem,
    updatePlanItem,
    deletePlanItem,
    fetchScenarios,
    createScenario,
    fetchApprovals,
    submitForReview,
    approvePlan,
    rejectPlan,
    fetchStats,
    
    // Asset Lifecycle Actions
    fetchAssetLifecycles,
    fetchAssetLifecycle,
    createAssetLifecycle,
    updateAssetLifecycle,
    updateAssetCondition,
    fetchReplacementSchedule,
    fetchMaintenanceAnalysis,
    
    // Capital Projects Actions
    fetchCapitalProjects,
    fetchCapitalProject,
    createCapitalProject,
    updateCapitalProject,
    linkAssetsToProject,
    approveCapitalProject,
    fetchProjectYearlySummary,
    fetchProjectPriorityMatrix,
    
    reset
  }
})