<template>
  <div class="maintenance-form">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/maintenance">Maintenance</router-link>
            </li>
            <li class="breadcrumb-item active">{{ formTitle }}</li>
          </ol>
        </nav>
        <h1 class="mb-1">{{ formTitle }}</h1>
        <p class="text-muted mb-0">{{ formSubtitle }}</p>
      </div>
    </div>

    <!-- Form -->
    <div class="row">
      <div class="col-lg-8">
        <form @submit.prevent="saveRecord">
          <!-- Basic Information -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-info-circle me-2"></i>Basic Information
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Asset <span class="text-danger">*</span></label>
                  <select 
                    v-model="form.asset_id" 
                    class="form-select"
                    :class="{ 'is-invalid': errors.asset_id }"
                    @change="onAssetChange"
                    required
                  >
                    <option value="">Select Asset</option>
                    <option v-for="asset in assets" :key="asset.asset_id" :value="asset.asset_id">
                      {{ asset.asset_number }} - {{ asset.make }} {{ asset.model }}
                    </option>
                  </select>
                  <div v-if="errors.asset_id" class="invalid-feedback">
                    {{ errors.asset_id[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Maintenance Type <span class="text-danger">*</span></label>
                  <select 
                    v-model="form.maintenance_type_id" 
                    class="form-select"
                    :class="{ 'is-invalid': errors.maintenance_type_id }"
                    required
                  >
                    <option value="">Select Maintenance Type</option>
                    <option v-for="type in maintenanceTypes" :key="type.type_id" :value="type.type_id">
                      {{ type.name }} - {{ type.category }}
                    </option>
                  </select>
                  <div v-if="errors.maintenance_type_id" class="invalid-feedback">
                    {{ errors.maintenance_type_id[0] }}
                  </div>
                </div>
                
                <div v-if="isScheduling" class="col-12">
                  <div class="alert alert-info">
                    <i class="bi bi-info-circle me-2"></i>
                    <strong>Scheduling Mode:</strong> You are creating a maintenance schedule. This will set up recurring maintenance for the selected asset.
                  </div>
                </div>
                
                <div v-if="isCompleting && scheduleInfo" class="col-12">
                  <div class="alert alert-success">
                    <i class="bi bi-check-circle me-2"></i>
                    <strong>Completing Scheduled Maintenance:</strong> {{ scheduleInfo.maintenance_type_name }} for {{ scheduleInfo.asset_number }}
                    <br><small>Originally due: {{ formatDate(scheduleInfo.next_due_date) }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Schedule Information (for scheduling) -->
          <div v-if="isScheduling" class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-calendar-plus me-2"></i>Schedule Information
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label">Frequency (Days)</label>
                  <input 
                    v-model.number="form.frequency_days" 
                    type="number" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.frequency_days }"
                    min="1"
                    placeholder="e.g., 30"
                  >
                  <div v-if="errors.frequency_days" class="invalid-feedback">
                    {{ errors.frequency_days[0] }}
                  </div>
                  <div class="form-text">Days between maintenance</div>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Frequency (Miles/KM)</label>
                  <input 
                    v-model.number="form.frequency_mileage" 
                    type="number" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.frequency_mileage }"
                    min="1"
                    placeholder="e.g., 5000"
                  >
                  <div v-if="errors.frequency_mileage" class="invalid-feedback">
                    {{ errors.frequency_mileage[0] }}
                  </div>
                  <div class="form-text">Distance between maintenance</div>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Frequency (Hours)</label>
                  <input 
                    v-model.number="form.frequency_hours" 
                    type="number" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.frequency_hours }"
                    min="1"
                    placeholder="e.g., 100"
                  >
                  <div v-if="errors.frequency_hours" class="invalid-feedback">
                    {{ errors.frequency_hours[0] }}
                  </div>
                  <div class="form-text">Engine hours between maintenance</div>
                </div>
                <div class="col-12">
                  <div class="form-text text-info">
                    <i class="bi bi-info-circle me-1"></i>
                    Maintenance will be due based on whichever condition is met first (time, mileage, or hours).
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Service Details (for recording) -->
          <div v-if="!isScheduling" class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-wrench me-2"></i>Service Details
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Service Date <span class="text-danger">*</span></label>
                  <input 
                    v-model="form.completed_date" 
                    type="date" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.completed_date }"
                    required
                  >
                  <div v-if="errors.completed_date" class="invalid-feedback">
                    {{ errors.completed_date[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Technician/Performed By</label>
                  <input 
                    v-model="form.technician" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.technician }"
                  >
                  <div v-if="errors.technician" class="invalid-feedback">
                    {{ errors.technician[0] }}
                  </div>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Mileage at Service</label>
                  <input 
                    v-model.number="form.mileage_at_service" 
                    type="number" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.mileage_at_service }"
                    min="0"
                  >
                  <div v-if="errors.mileage_at_service" class="invalid-feedback">
                    {{ errors.mileage_at_service[0] }}
                  </div>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Engine Hours at Service</label>
                  <input 
                    v-model.number="form.hours_at_service" 
                    type="number" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.hours_at_service }"
                    min="0"
                    step="0.1"
                  >
                  <div v-if="errors.hours_at_service" class="invalid-feedback">
                    {{ errors.hours_at_service[0] }}
                  </div>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Service Cost</label>
                  <div class="input-group">
                    <span class="input-group-text">$</span>
                    <input 
                      v-model.number="form.cost" 
                      type="number" 
                      class="form-control"
                      :class="{ 'is-invalid': errors.cost }"
                      min="0"
                      step="0.01"
                    >
                  </div>
                  <div v-if="errors.cost" class="invalid-feedback">
                    {{ errors.cost[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Service Provider</label>
                  <input 
                    v-model="form.service_provider" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.service_provider }"
                    placeholder="Shop name, internal maintenance, etc."
                  >
                  <div v-if="errors.service_provider" class="invalid-feedback">
                    {{ errors.service_provider[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Status</label>
                  <select 
                    v-model="form.status" 
                    class="form-select"
                    :class="{ 'is-invalid': errors.status }"
                  >
                    <option value="completed">Completed</option>
                    <option value="in_progress">In Progress</option>
                    <option value="scheduled">Scheduled</option>
                  </select>
                  <div v-if="errors.status" class="invalid-feedback">
                    {{ errors.status[0] }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Parts Used (for recording) -->
          <div v-if="!isScheduling" class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-tools me-2"></i>Parts Used
              </h5>
              <button type="button" @click="addPart" class="btn btn-sm btn-outline-primary">
                <i class="bi bi-plus-circle me-2"></i>Add Part
              </button>
            </div>
            <div class="card-body">
              <div v-if="form.parts.length === 0" class="text-center text-muted py-3">
                <i class="bi bi-tools fs-3 opacity-50"></i>
                <p class="mt-2 mb-0">No parts added yet</p>
                <small>Click "Add Part" to record parts used in this maintenance</small>
              </div>
              <div v-else class="table-responsive">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Part Name</th>
                      <th>Part Number</th>
                      <th>Quantity</th>
                      <th>Unit Cost</th>
                      <th>Total</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(part, index) in form.parts" :key="index">
                      <td>
                        <input 
                          v-model="part.part_name" 
                          type="text" 
                          class="form-control form-control-sm"
                          placeholder="e.g., Oil Filter"
                        >
                      </td>
                      <td>
                        <input 
                          v-model="part.part_number" 
                          type="text" 
                          class="form-control form-control-sm"
                          placeholder="e.g., OF-123"
                        >
                      </td>
                      <td>
                        <input 
                          v-model.number="part.quantity" 
                          type="number" 
                          class="form-control form-control-sm"
                          min="1"
                          style="width: 80px;"
                        >
                      </td>
                      <td>
                        <div class="input-group input-group-sm">
                          <span class="input-group-text">$</span>
                          <input 
                            v-model.number="part.unit_cost" 
                            type="number" 
                            class="form-control"
                            min="0"
                            step="0.01"
                            style="width: 90px;"
                          >
                        </div>
                      </td>
                      <td>
                        <strong>${{ ((part.quantity || 0) * (part.unit_cost || 0)).toFixed(2) }}</strong>
                      </td>
                      <td>
                        <button type="button" @click="removePart(index)" class="btn btn-sm btn-outline-danger">
                          <i class="bi bi-trash"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                  <tfoot>
                    <tr>
                      <th colspan="4" class="text-end">Total Parts Cost:</th>
                      <th>${{ totalPartsCost.toFixed(2) }}</th>
                      <th></th>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          </div>

          <!-- Description and Notes -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-journal-text me-2"></i>{{ isScheduling ? 'Schedule' : 'Service' }} Details
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-12">
                  <label class="form-label">{{ isScheduling ? 'Schedule Description' : 'Work Performed' }}</label>
                  <textarea 
                    v-model="form.description" 
                    class="form-control" 
                    rows="4"
                    :class="{ 'is-invalid': errors.description }"
                    :placeholder="isScheduling ? 'Describe what this maintenance schedule covers...' : 'Describe the work that was performed...'"
                  ></textarea>
                  <div v-if="errors.description" class="invalid-feedback">
                    {{ errors.description[0] }}
                  </div>
                </div>
                <div class="col-12">
                  <label class="form-label">Notes</label>
                  <textarea 
                    v-model="form.notes" 
                    class="form-control" 
                    rows="3"
                    :class="{ 'is-invalid': errors.notes }"
                    placeholder="Any additional notes or observations..."
                  ></textarea>
                  <div v-if="errors.notes" class="invalid-feedback">
                    {{ errors.notes[0] }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="card">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <button type="button" @click="goBack" class="btn btn-outline-secondary">
                  <i class="bi bi-arrow-left me-2"></i>Cancel
                </button>
                <div>
                  <button v-if="!isScheduling" type="button" @click="saveAndCreateWorkOrder" class="btn btn-outline-primary me-2" :disabled="saving">
                    <i class="bi bi-wrench me-2"></i>Save & Create Work Order
                  </button>
                  <button type="submit" class="btn btn-primary" :disabled="saving">
                    <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-check-circle me-2"></i>
                    {{ isScheduling ? 'Create Schedule' : 'Record Maintenance' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>

      <!-- Sidebar -->
      <div class="col-lg-4">
        <div class="card sticky-top" style="top: 1rem;">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="bi bi-lightbulb me-2"></i>{{ isScheduling ? 'Scheduling' : 'Recording' }} Tips
            </h6>
          </div>
          <div class="card-body">
            <div class="small">
              <div v-if="isScheduling" class="mb-3">
                <strong>Frequency Setup:</strong>
                <p class="text-muted mb-0">Set at least one frequency type. The system will automatically calculate next due dates based on whichever condition is met first.</p>
              </div>
              <div v-else class="mb-3">
                <strong>Service Recording:</strong>
                <p class="text-muted mb-0">Record completed maintenance to track service history and update schedules.</p>
              </div>
              <div class="mb-3">
                <strong>Asset Selection:</strong>
                <p class="text-muted mb-0">Selecting an asset will pre-populate current mileage and engine hours if available.</p>
              </div>
              <div v-if="!isScheduling" class="mb-3">
                <strong>Parts Tracking:</strong>
                <p class="text-muted mb-0">Record parts used for inventory management and cost tracking.</p>
              </div>
              <div class="mb-3">
                <strong>Cost Tracking:</strong>
                <p class="text-muted mb-0">Include all costs (labor, parts, shop fees) for accurate maintenance expense reporting.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { maintenanceAPI, assetsAPI } from '@/services/api'
import { toast } from '@/utils/toast'

export default {
  name: 'MaintenanceForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const isScheduling = computed(() => route.path.includes('/schedule') || route.query.mode === 'schedule')
    const isCompleting = computed(() => !!route.query.schedule_id)
    const scheduleId = route.query.schedule_id
    
    const loading = ref(false)
    const saving = ref(false)
    const assets = ref([])
    const maintenanceTypes = ref([])
    const scheduleInfo = ref(null)
    const errors = ref({})
    
    const form = reactive({
      asset_id: route.query.asset_id || '',
      maintenance_type_id: '',
      // Schedule fields
      frequency_days: null,
      frequency_mileage: null,
      frequency_hours: null,
      // Record fields
      completed_date: new Date().toISOString().split('T')[0],
      technician: '',
      mileage_at_service: null,
      hours_at_service: null,
      cost: null,
      service_provider: '',
      status: 'completed',
      parts: [],
      // Common fields
      description: '',
      notes: ''
    })

    const formTitle = computed(() => {
      if (isScheduling.value) return 'Schedule Maintenance'
      if (isCompleting.value) return 'Complete Scheduled Maintenance'
      return 'Record Maintenance'
    })

    const formSubtitle = computed(() => {
      if (isScheduling.value) return 'Set up recurring maintenance schedule for an asset'
      if (isCompleting.value) return 'Record completion of scheduled maintenance'
      return 'Record completed maintenance work'
    })

    const totalPartsCost = computed(() => {
      return form.parts.reduce((total, part) => {
        return total + ((part.quantity || 0) * (part.unit_cost || 0))
      }, 0)
    })

    const loadAssets = async () => {
      try {
        const response = await assetsAPI.getAssets({ page_size: 100 })
        assets.value = response.data.results || []
      } catch (error) {
        console.error('Error loading assets:', error)
      }
    }

    const loadMaintenanceTypes = async () => {
      try {
        const response = await maintenanceAPI.getMaintenanceTypes()
        maintenanceTypes.value = response.data.results || []
      } catch (error) {
        console.error('Error loading maintenance types:', error)
      }
    }

    const loadScheduleInfo = async () => {
      if (!scheduleId) return
      
      try {
        const response = await maintenanceAPI.getMaintenanceSchedule(scheduleId)
        scheduleInfo.value = response.data
        
        // Pre-fill form with schedule data
        form.asset_id = response.data.asset_id
        form.maintenance_type_id = response.data.maintenance_type_id
      } catch (error) {
        console.error('Error loading schedule info:', error)
        toast.error('Failed to load schedule information')
      }
    }

    const onAssetChange = () => {
      if (form.asset_id) {
        const asset = assets.value.find(a => a.asset_id === form.asset_id)
        if (asset) {
          form.mileage_at_service = asset.current_mileage
          form.hours_at_service = asset.engine_hours
        }
      }
    }

    const addPart = () => {
      form.parts.push({
        part_name: '',
        part_number: '',
        quantity: 1,
        unit_cost: 0
      })
    }

    const removePart = (index) => {
      form.parts.splice(index, 1)
    }

    const saveRecord = async (createWorkOrder = false) => {
      saving.value = true
      errors.value = {}
      
      try {
        const formData = { ...form }
        
        // Remove empty strings and convert to null
        Object.keys(formData).forEach(key => {
          if (key !== 'parts' && (formData[key] === '' || formData[key] === undefined)) {
            formData[key] = null
          }
        })

        // Clean up parts data
        formData.parts = formData.parts.filter(part => part.part_name).map(part => ({
          ...part,
          quantity: part.quantity || 1,
          unit_cost: part.unit_cost || 0
        }))

        let response
        if (isScheduling.value) {
          // Create maintenance schedule
          response = await maintenanceAPI.createMaintenanceSchedule(formData)
          toast.success('Maintenance schedule created successfully')
        } else {
          // Add schedule_id if completing scheduled maintenance
          if (scheduleId) {
            formData.maintenance_schedule_id = scheduleId
          }
          
          // Create maintenance record
          response = await maintenanceAPI.createMaintenanceRecord(formData)
          toast.success('Maintenance record created successfully')
        }
        
        if (createWorkOrder) {
          // Redirect to work order creation
          router.push({
            path: '/work-orders/create',
            query: { 
              asset_id: formData.asset_id,
              maintenance_record_id: response.data.record_id
            }
          })
        } else {
          // Navigate back to maintenance list
          router.push('/maintenance')
        }
      } catch (error) {
        console.error('Error saving maintenance:', error)
        
        if (error.response?.status === 400 && error.response?.data) {
          errors.value = error.response.data
          toast.error('Please check the form for errors')
        } else {
          toast.error('Failed to save maintenance record')
        }
      } finally {
        saving.value = false
      }
    }

    const saveAndCreateWorkOrder = () => {
      saveRecord(true)
    }

    const goBack = () => {
      router.push('/maintenance')
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(async () => {
      await Promise.all([
        loadAssets(),
        loadMaintenanceTypes(),
        loadScheduleInfo()
      ])
    })

    return {
      isScheduling,
      isCompleting,
      loading,
      saving,
      assets,
      maintenanceTypes,
      scheduleInfo,
      errors,
      form,
      formTitle,
      formSubtitle,
      totalPartsCost,
      onAssetChange,
      addPart,
      removePart,
      saveRecord,
      saveAndCreateWorkOrder,
      goBack,
      formatDate
    }
  }
}
</script>

<style scoped>
.form-label {
  font-weight: 500;
  color: #495057;
}

.card-header h5 {
  color: #495057;
}

.text-danger {
  font-weight: 500;
}

.sticky-top {
  z-index: 1020;
}

@media (max-width: 991.98px) {
  .sticky-top {
    position: static !important;
  }
}

.invalid-feedback {
  display: block;
}

.table th {
  border-top: none;
}

.input-group-sm .input-group-text {
  font-size: 0.875rem;
}
</style>