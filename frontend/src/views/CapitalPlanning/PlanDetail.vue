<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <div>
            <h1 class="text-h5 font-weight-medium">{{ plan?.name || 'Capital Plan' }}</h1>
            <p class="text-body-2 text-medium-emphasis">Fiscal Year {{ plan?.fiscal_year }}</p>
          </div>
          <div>
            <v-btn variant="text" size="small" @click="$router.push('/capital-planning')">
              <v-icon left>mdi-arrow-left</v-icon>
              Back
            </v-btn>
            <v-btn color="primary" size="small" @click="editPlan">
              <v-icon left>mdi-pencil</v-icon>
              Edit
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12">
        <v-progress-linear indeterminate color="primary"></v-progress-linear>
      </v-col>
    </v-row>

    <v-row v-else-if="plan">
      <v-col cols="12" md="8">
        <div class="detail-section pa-4 mb-3">
          <h3 class="text-h6 mb-3">Plan Details</h3>
          <v-row>
            <v-col cols="6">
              <p class="text-caption text-medium-emphasis">Status</p>
              <v-chip size="small" :color="getStatusColor(plan.status)">
                {{ plan.status }}
              </v-chip>
            </v-col>
            <v-col cols="6">
              <p class="text-caption text-medium-emphasis">Total Budget</p>
              <p class="text-body-1 font-weight-medium">${{ formatCurrency(plan.total_budget) }}</p>
            </v-col>
            <v-col cols="12">
              <p class="text-caption text-medium-emphasis">Description</p>
              <p class="text-body-2">{{ plan.description || 'No description provided' }}</p>
            </v-col>
          </v-row>
        </div>
      </v-col>

      <v-col cols="12" md="4">
        <div class="detail-section pa-4">
          <h3 class="text-h6 mb-3">Actions</h3>
          <v-btn 
            v-if="plan.status === 'draft'" 
            color="primary" 
            block 
            size="small"
            @click="submitForReview"
          >
            Submit for Review
          </v-btn>
          <v-btn 
            v-if="canApprove" 
            color="success" 
            block 
            size="small"
            class="mt-2"
            @click="approvePlan"
          >
            Approve Plan
          </v-btn>
          <v-btn 
            v-if="canApprove" 
            color="error" 
            block 
            size="small"
            class="mt-2"
            @click="rejectPlan"
          >
            Reject Plan
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCapitalPlanningStore } from '@/stores/capitalPlanning'

const route = useRoute()
const router = useRouter()
const store = useCapitalPlanningStore()

const loading = ref(false)
const plan = computed(() => store.currentPlan)

const canApprove = computed(() => {
  return plan.value?.status === 'submitted'
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US').format(value || 0)
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    submitted: 'blue',
    approved: 'green',
    rejected: 'red',
    completed: 'success'
  }
  return colors[status] || 'grey'
}

const loadPlan = async () => {
  loading.value = true
  try {
    await store.fetchPlan(route.params.id)
  } catch (error) {
    console.error('Failed to load plan:', error)
  } finally {
    loading.value = false
  }
}

const editPlan = () => {
  router.push(`/capital-planning/${route.params.id}/edit`)
}

const submitForReview = async () => {
  try {
    await store.submitForReview(route.params.id)
    await loadPlan()
  } catch (error) {
    console.error('Failed to submit plan:', error)
  }
}

const approvePlan = async () => {
  try {
    await store.approvePlan(route.params.id)
    await loadPlan()
  } catch (error) {
    console.error('Failed to approve plan:', error)
  }
}

const rejectPlan = async () => {
  try {
    await store.rejectPlan(route.params.id)
    await loadPlan()
  } catch (error) {
    console.error('Failed to reject plan:', error)
  }
}

onMounted(() => {
  loadPlan()
})
</script>

<style scoped>
.detail-section {
  background: var(--v-theme-surface);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}
</style>