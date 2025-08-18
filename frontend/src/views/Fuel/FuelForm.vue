<template>
  <div class="fuel-form-container">
    <!-- Header -->
    <div class="page-header">
      <div class="d-flex align-center justify-space-between">
        <div>
          <h1 class="text-h4 mb-1">{{ isEditing ? 'Edit Fuel Transaction' : 'Add Fuel Transaction' }}</h1>
          <p class="text-body-2 text-medium-emphasis">
            {{ isEditing ? 'Update fuel transaction details' : 'Record a new fuel purchase or fill-up' }}
          </p>
        </div>
        
        <div class="d-flex align-center gap-3">
          <v-btn
            variant="outlined"
            prepend-icon="mdi-arrow-left"
            @click="goBack"
          >
            Back to Fuel Log
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Form Card -->
    <v-card>
      <v-card-text class="pa-6">
        <v-form ref="form" v-model="isFormValid" @submit.prevent="handleSubmit">
          <v-row>
            <!-- Asset Selection -->
            <v-col cols="12">
              <h3 class="text-h6 mb-4 text-primary">Vehicle Information</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.asset"
                :items="assetOptions"
                item-title="display_name"
                item-value="id"
                label="Vehicle *"
                variant="outlined"
                :rules="[rules.required]"
                :loading="assetsStore.isLoading"
                required
              >
                <template #item="{ item, props }">
                  <v-list-item v-bind="props">
                    <v-list-item-title>{{ item.raw.asset_id }}</v-list-item-title>
                    <v-list-item-subtitle>{{ item.raw.make }} {{ item.raw.model }} ({{ item.raw.year }})</v-list-item-subtitle>
                  </v-list-item>
                </template>
              </v-select>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.timestamp"
                label="Date & Time *"
                type="datetime-local"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>

            <!-- Fuel Details -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">Fuel Details</h3>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-select
                v-model="formData.product_type"
                :items="productTypeOptions"
                label="Fuel Type *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="4">
              <v-text-field
                v-model="formData.volume"
                label="Volume *"
                type="number"
                step="0.001"
                min="0"
                variant="outlined"
                :rules="[rules.required, rules.positiveNumber]"
                required
                :suffix="formData.unit"
              />
            </v-col>
            
            <v-col cols="12" md="4">
              <v-select
                v-model="formData.unit"
                :items="unitOptions"
                label="Unit *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>

            <!-- Pricing -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">Pricing</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.unit_price"
                label="Price per Unit"
                type="number"
                step="0.001"
                min="0"
                variant="outlined"
                :prefix="currencySymbol"
                @input="calculateTotalFromUnitPrice"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.total_cost"
                label="Total Cost"
                type="number"
                step="0.01"
                min="0"
                variant="outlined"
                :prefix="currencySymbol"
                @input="calculateUnitPriceFromTotal"
              />
            </v-col>

            <!-- Vehicle State -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">Vehicle State</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.odometer"
                label="Odometer Reading"
                type="number"
                step="0.1"
                min="0"
                variant="outlined"
                :suffix="distanceUnit"
                placeholder="Current mileage"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.engine_hours"
                label="Engine Hours"
                type="number"
                step="0.1"
                min="0"
                variant="outlined"
                suffix="hours"
                placeholder="Engine hour meter reading"
              />
            </v-col>

            <!-- Location Information -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">Location & Vendor</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.vendor"
                label="Gas Station / Vendor"
                variant="outlined"
                placeholder="e.g., Shell, Chevron, Fleet Depot"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.location_label"
                label="Location"
                variant="outlined"
                placeholder="e.g., 123 Main St, Downtown Station"
              />
            </v-col>

            <!-- Additional Information -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">Additional Information</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.payment_ref"
                label="Receipt / Transaction #"
                variant="outlined"
                placeholder="Receipt number or card transaction ID"
              />
            </v-col>
            
            <v-col cols="12">
              <v-textarea
                v-model="formData.notes"
                label="Notes"
                variant="outlined"
                rows="3"
                placeholder="Additional notes about this fuel transaction..."
              />
            </v-col>
          </v-row>

          <!-- Calculated Metrics Display -->
          <v-row v-if="calculatedMetrics.mpg || calculatedMetrics.costPerMile" class="mt-4">
            <v-col cols="12">
              <v-card color="blue-grey-lighten-5" variant="tonal">
                <v-card-title class="text-h6">Efficiency Metrics</v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="6" md="3" v-if="calculatedMetrics.mpg">
                      <div class="text-caption text-medium-emphasis">Miles per Gallon</div>
                      <div class="text-h6 text-primary">{{ calculatedMetrics.mpg }} MPG</div>
                    </v-col>
                    <v-col cols="6" md="3" v-if="calculatedMetrics.costPerMile">
                      <div class="text-caption text-medium-emphasis">Cost per Mile</div>
                      <div class="text-h6 text-primary">${{ calculatedMetrics.costPerMile }}</div>
                    </v-col>
                    <v-col cols="6" md="3" v-if="calculatedMetrics.distanceTraveled">
                      <div class="text-caption text-medium-emphasis">Distance Since Last Fill</div>
                      <div class="text-h6">{{ calculatedMetrics.distanceTraveled }} {{ distanceUnit }}</div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      
      <v-card-actions class="pa-6 pt-0">
        <v-spacer />
        <v-btn
          variant="outlined"
          @click="goBack"
          :disabled="fuelStore.isAnyLoading"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          @click="handleSubmit"
          :loading="fuelStore.isCreating || fuelStore.isUpdating"
          :disabled="!isFormValid"
        >
          {{ isEditing ? 'Update Transaction' : 'Save Transaction' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useFuelStore } from '../../stores/fuel'
import { useAssetsStore } from '../../stores/assets'

// Router and stores
const router = useRouter()
const route = useRoute()
const fuelStore = useFuelStore()
const assetsStore = useAssetsStore()

// Component state
const form = ref(null)
const isFormValid = ref(false)

// Check if we're editing
const isEditing = computed(() => !!route.params.id)

// Form data
const formData = ref({
  asset: '',
  timestamp: new Date().toISOString().slice(0, 16), // Current date/time
  product_type: 'gasoline',
  volume: '',
  unit: 'gal',
  unit_price: '',
  total_cost: '',
  odometer: '',
  engine_hours: '',
  vendor: '',
  location_label: '',
  payment_ref: '',
  notes: ''
})

// Calculated metrics
const calculatedMetrics = ref({
  mpg: null,
  costPerMile: null,
  distanceTraveled: null
})

// Validation rules
const rules = {
  required: value => !!value || 'This field is required',
  positiveNumber: value => !value || parseFloat(value) > 0 || 'Must be a positive number'
}

// Options for dropdowns
const productTypeOptions = [
  { title: 'Gasoline', value: 'gasoline' },
  { title: 'Diesel', value: 'diesel' },
  { title: 'Diesel Exhaust Fluid (DEF)', value: 'def' },
  { title: 'Compressed Natural Gas', value: 'cng' },
  { title: 'Liquefied Natural Gas', value: 'lng' },
  { title: 'Propane', value: 'propane' },
  { title: 'Electricity', value: 'electricity' },
  { title: 'Other', value: 'other' }
]

const unitOptions = [
  { title: 'Gallons', value: 'gal' },
  { title: 'Liters', value: 'L' },
  { title: 'Kilowatt Hours', value: 'kWh' }
]

// Computed properties
const assetOptions = computed(() => {
  return assetsStore.assets.map(asset => ({
    ...asset,
    display_name: `${asset.asset_id} - ${asset.make} ${asset.model}`
  }))
})

const currencySymbol = computed(() => '$') // Could be dynamic based on units policy
const distanceUnit = computed(() => 'mi') // Could be dynamic based on units policy

// Methods
const calculateTotalFromUnitPrice = () => {
  if (formData.value.unit_price && formData.value.volume) {
    const total = parseFloat(formData.value.unit_price) * parseFloat(formData.value.volume)
    formData.value.total_cost = total.toFixed(2)
  }
}

const calculateUnitPriceFromTotal = () => {
  if (formData.value.total_cost && formData.value.volume) {
    const unitPrice = parseFloat(formData.value.total_cost) / parseFloat(formData.value.volume)
    formData.value.unit_price = unitPrice.toFixed(3)
  }
}

const loadTransactionData = async () => {
  if (isEditing.value) {
    try {
      await fuelStore.fetchTransaction(route.params.id)
      const transaction = fuelStore.currentTransaction
      if (transaction) {
        // Convert datetime to local format for input
        const timestamp = new Date(transaction.timestamp)
        const localTimestamp = new Date(timestamp.getTime() - (timestamp.getTimezoneOffset() * 60000))
        
        // Populate form with existing transaction data
        Object.keys(formData.value).forEach(key => {
          if (key === 'timestamp') {
            formData.value[key] = localTimestamp.toISOString().slice(0, 16)
          } else if (transaction[key] !== undefined && transaction[key] !== null) {
            formData.value[key] = transaction[key].toString()
          }
        })
      }
    } catch (error) {
      console.error('Failed to load transaction:', error)
      router.push('/fuel')
    }
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  try {
    // Prepare submission data
    const submissionData = {
      ...formData.value,
      volume: parseFloat(formData.value.volume) || 0,
      unit_price: parseFloat(formData.value.unit_price) || null,
      total_cost: parseFloat(formData.value.total_cost) || null,
      odometer: parseFloat(formData.value.odometer) || null,
      engine_hours: parseFloat(formData.value.engine_hours) || null,
      timestamp: new Date(formData.value.timestamp).toISOString()
    }
    
    // Remove empty strings
    Object.keys(submissionData).forEach(key => {
      if (submissionData[key] === '') {
        submissionData[key] = null
      }
    })
    
    let transaction
    if (isEditing.value) {
      transaction = await fuelStore.updateTransaction(route.params.id, submissionData)
    } else {
      transaction = await fuelStore.createTransaction(submissionData)
    }
    
    router.push('/fuel')
  } catch (error) {
    console.error('Failed to save transaction:', error)
  }
}

const goBack = () => {
  router.push('/fuel')
}

// Lifecycle hooks
onMounted(async () => {
  // Load assets for dropdown
  if (!assetsStore.hasAssets) {
    await assetsStore.fetchAssets()
  }
  
  // Load transaction data if editing
  await loadTransactionData()
  
  // Load units policy
  await fuelStore.fetchUnitsPolicy()
})

// Watch for changes to calculate metrics
watch([() => formData.value.odometer, () => formData.value.volume, () => formData.value.total_cost], () => {
  // This is a simplified calculation - the backend will do the real calculation
  if (formData.value.volume && formData.value.total_cost) {
    const volume = parseFloat(formData.value.volume)
    const cost = parseFloat(formData.value.total_cost)
    
    // Simple cost per gallon
    if (volume > 0) {
      calculatedMetrics.value.costPerGallon = (cost / volume).toFixed(3)
    }
  }
})
</script>

<style scoped>
.fuel-form-container {
  padding: 24px;
  background-color: #F9FAFA;
  min-height: 100vh;
}

.page-header {
  background: white;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.gap-3 {
  gap: 12px;
}
</style>