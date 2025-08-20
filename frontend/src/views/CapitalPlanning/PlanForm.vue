<template>
  <v-container fluid>
    <!-- Error/Success Notifications -->
    <v-snackbar
      v-model="errorSnackbar"
      :timeout="5000"
      color="error"
      top
    >
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="errorSnackbar = false">Close</v-btn>
      </template>
    </v-snackbar>

    <v-snackbar
      v-model="successSnackbar"
      :timeout="3000"
      color="success"
      top
    >
      {{ successMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="successSnackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h5 font-weight-medium">
            {{ isEditMode ? 'Edit Capital Plan' : 'New Capital Plan' }}
          </h1>
          <v-btn variant="text" size="small" @click="$router.push('/capital-planning')">
            <v-icon left>mdi-close</v-icon>
            Cancel
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8">
        <div class="form-section pa-4">
          <v-form ref="form" v-model="valid" @submit.prevent="savePlan">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.name"
                  label="Plan Name"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="compact"
                ></v-text-field>
              </v-col>

              <v-col cols="12" md="6">
                <v-select
                  v-model="formData.fiscal_year"
                  :items="yearOptions"
                  label="Fiscal Year"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="compact"
                ></v-select>
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.total_budget"
                  label="Total Budget"
                  type="number"
                  prefix="$"
                  :rules="[rules.required, rules.positive]"
                  variant="outlined"
                  density="compact"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="formData.description"
                  label="Description"
                  rows="3"
                  variant="outlined"
                  density="compact"
                ></v-textarea>
              </v-col>

              <v-col cols="12">
                <v-btn
                  type="submit"
                  color="primary"
                  :loading="loading"
                  :disabled="!valid"
                >
                  {{ isEditMode ? 'Update Plan' : 'Create Plan' }}
                </v-btn>
                <v-btn
                  variant="text"
                  class="ml-2"
                  @click="$router.push('/capital-planning')"
                >
                  Cancel
                </v-btn>
              </v-col>
            </v-row>
          </v-form>
        </div>
      </v-col>

      <v-col cols="12" md="4">
        <div class="info-section pa-4">
          <h3 class="text-h6 mb-3">Tips</h3>
          <ul class="text-body-2">
            <li>Choose the appropriate fiscal year for budget planning</li>
            <li>Set a realistic total budget based on available funds</li>
            <li>Provide a clear description of the plan's objectives</li>
            <li>Plans start in 'draft' status and can be edited</li>
            <li>Submit for review when ready for approval</li>
          </ul>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCapitalPlanningStore } from '@/stores/capitalPlanning'

const props = defineProps({
  id: String
})

const route = useRoute()
const router = useRouter()
const store = useCapitalPlanningStore()

const form = ref(null)
const valid = ref(false)
const loading = ref(false)
const errorSnackbar = ref(false)
const errorMessage = ref('')
const successSnackbar = ref(false)
const successMessage = ref('')

const isEditMode = computed(() => !!props.id || !!route.params.id)
const planId = computed(() => props.id || route.params.id)

const formData = ref({
  name: '',
  fiscal_year: new Date().getFullYear(),
  total_budget: 0,
  description: '',
  status: 'draft'
})

const yearOptions = [
  2024,
  2025,
  2026,
  2027,
  2028
]

const rules = {
  required: v => !!v || 'Required',
  positive: v => v > 0 || 'Must be greater than 0'
}

const loadPlan = async () => {
  if (!isEditMode.value) return
  
  loading.value = true
  try {
    const plan = await store.fetchPlan(planId.value)
    formData.value = {
      name: plan.name,
      fiscal_year: plan.fiscal_year,
      total_budget: plan.total_budget,
      description: plan.description || '',
      status: plan.status
    }
  } catch (error) {
    console.error('Failed to load plan:', error)
  } finally {
    loading.value = false
  }
}

const savePlan = async () => {
  console.log('savePlan called with formData:', formData.value)
  
  // Validate form if it exists
  if (form.value) {
    const validationResult = await form.value.validate()
    console.log('Form validation result:', validationResult)
    if (!validationResult.valid) {
      console.log('Form validation failed')
      return
    }
  }
  
  loading.value = true
  try {
    console.log('Attempting to save plan...')
    console.log('Token in localStorage:', localStorage.getItem('token'))
    
    if (isEditMode.value) {
      await store.updatePlan(planId.value, formData.value)
      showSuccess('Plan updated successfully')
    } else {
      const newPlan = await store.createPlan(formData.value)
      console.log('Plan created successfully:', newPlan)
      showSuccess('Plan created successfully')
    }
    setTimeout(() => {
      router.push('/capital-planning')
    }, 1000)
  } catch (error) {
    console.error('Failed to save plan - Full error:', error)
    console.error('Error response:', error.response)
    
    // Provide more detailed error messages
    let errorMsg = 'Failed to save plan. Please try again.'
    if (error.response?.data?.error) {
      errorMsg = error.response.data.error
    } else if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail
    } else if (error.response?.status === 401) {
      errorMsg = 'Authentication required. Please login.'
    } else if (error.response?.status === 403) {
      errorMsg = 'You do not have permission to create plans.'
    } else if (error.message) {
      errorMsg = error.message
    }
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const showError = (message) => {
  errorMessage.value = message
  errorSnackbar.value = true
}

const showSuccess = (message) => {
  successMessage.value = message
  successSnackbar.value = true
}

onMounted(() => {
  loadPlan()
})
</script>

<style scoped>
.form-section {
  background: var(--v-theme-surface);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.info-section {
  background: var(--v-theme-surface);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.info-section ul {
  padding-left: 20px;
}

.info-section li {
  margin-bottom: 8px;
}
</style>