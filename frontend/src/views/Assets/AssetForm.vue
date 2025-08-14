<template>
  <div class="asset-form">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/assets">Assets</router-link>
            </li>
            <li class="breadcrumb-item active">{{ isEditing ? 'Edit Asset' : 'Create Asset' }}</li>
          </ol>
        </nav>
        <h1 class="mb-1">{{ isEditing ? 'Edit Asset' : 'Create New Asset' }}</h1>
        <p class="text-muted mb-0">{{ isEditing ? 'Update asset information' : 'Add a new asset to your fleet' }}</p>
      </div>
    </div>

    <!-- Form -->
    <div class="row">
      <div class="col-lg-8">
        <form @submit.prevent="saveAsset">
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
                  <label class="form-label">Asset Number <span class="text-danger">*</span></label>
                  <input 
                    v-model="form.asset_number" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.asset_number }"
                    required
                  >
                  <div v-if="errors.asset_number" class="invalid-feedback">
                    {{ errors.asset_number[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Vehicle Type <span class="text-danger">*</span></label>
                  <select 
                    v-model="form.vehicle_type" 
                    class="form-select"
                    :class="{ 'is-invalid': errors.vehicle_type }"
                    required
                  >
                    <option value="">Select Vehicle Type</option>
                    <option value="bus">Bus</option>
                    <option value="truck">Truck</option>
                    <option value="tractor">Tractor</option>
                    <option value="trailer">Trailer</option>
                    <option value="van">Van</option>
                    <option value="sedan">Sedan</option>
                    <option value="suv">SUV</option>
                    <option value="pickup">Pickup Truck</option>
                    <option value="motorcycle">Motorcycle</option>
                    <option value="equipment">Equipment</option>
                    <option value="other">Other</option>
                  </select>
                  <div v-if="errors.vehicle_type" class="invalid-feedback">
                    {{ errors.vehicle_type[0] }}
                  </div>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Make <span class="text-danger">*</span></label>
                  <input 
                    v-model="form.make" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.make }"
                    required
                  >
                  <div v-if="errors.make" class="invalid-feedback">
                    {{ errors.make[0] }}
                  </div>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Model <span class="text-danger">*</span></label>
                  <input 
                    v-model="form.model" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.model }"
                    required
                  >
                  <div v-if="errors.model" class="invalid-feedback">
                    {{ errors.model[0] }}
                  </div>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Year <span class="text-danger">*</span></label>
                  <input 
                    v-model.number="form.year" 
                    type="number" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.year }"
                    min="1900"
                    :max="new Date().getFullYear() + 1"
                    required
                  >
                  <div v-if="errors.year" class="invalid-feedback">
                    {{ errors.year[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">VIN</label>
                  <input 
                    v-model="form.vin_number" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.vin_number }"
                    maxlength="17"
                  >
                  <div v-if="errors.vin_number" class="invalid-feedback">
                    {{ errors.vin_number[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">License Plate</label>
                  <input 
                    v-model="form.license_plate" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.license_plate }"
                  >
                  <div v-if="errors.license_plate" class="invalid-feedback">
                    {{ errors.license_plate[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Fuel Type</label>
                  <select v-model="form.fuel_type" class="form-select">
                    <option value="">Select Fuel Type</option>
                    <option value="Gasoline">Gasoline</option>
                    <option value="Diesel">Diesel</option>
                    <option value="Hybrid">Hybrid</option>
                    <option value="Electric">Electric</option>
                    <option value="CNG">CNG</option>
                    <option value="LPG">LPG</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Assignment & Status -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-building me-2"></i>Assignment & Status
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Department <span class="text-danger">*</span></label>
                  <select 
                    v-model="form.department" 
                    class="form-select"
                    :class="{ 'is-invalid': errors.department }"
                    required
                  >
                    <option value="">Select Department</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                      {{ dept.name }}
                    </option>
                  </select>
                  <div v-if="errors.department" class="invalid-feedback">
                    {{ errors.department[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Status <span class="text-danger">*</span></label>
                  <select 
                    v-model="form.status" 
                    class="form-select"
                    :class="{ 'is-invalid': errors.status }"
                    required
                  >
                    <option value="">Select Status</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="maintenance">In Maintenance</option>
                    <option value="retired">Retired</option>
                  </select>
                  <div v-if="errors.status" class="invalid-feedback">
                    {{ errors.status[0] }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Operational Details -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-speedometer2 me-2"></i>Operational Details
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label">Current Odometer Reading</label>
                  <input 
                    v-model.number="form.current_odometer_reading" 
                    type="number" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.current_odometer_reading }"
                    min="0"
                    step="1"
                  >
                  <div v-if="errors.current_odometer_reading" class="invalid-feedback">
                    {{ errors.current_odometer_reading[0] }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Purchase Information -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-receipt me-2"></i>Purchase Information
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Purchase Date</label>
                  <input 
                    v-model="form.purchase_date" 
                    type="date" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.purchase_date }"
                  >
                  <div v-if="errors.purchase_date" class="invalid-feedback">
                    {{ errors.purchase_date[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Purchase Cost</label>
                  <div class="input-group">
                    <span class="input-group-text">$</span>
                    <input 
                      v-model.number="form.purchase_cost" 
                      type="number" 
                      class="form-control"
                      :class="{ 'is-invalid': errors.purchase_cost }"
                      min="0"
                      step="0.01"
                    >
                  </div>
                  <div v-if="errors.purchase_cost" class="invalid-feedback">
                    {{ errors.purchase_cost[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Warranty Expiry Date</label>
                  <input 
                    v-model="form.warranty_expiry" 
                    type="date" 
                    class="form-control"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Insurance Expiry Date</label>
                  <input 
                    v-model="form.insurance_expiry" 
                    type="date" 
                    class="form-control"
                  >
                </div>
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-journal-text me-2"></i>Additional Information
              </h5>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea 
                  v-model="form.notes" 
                  class="form-control" 
                  rows="4"
                  :class="{ 'is-invalid': errors.notes }"
                  placeholder="Any additional notes or comments about this asset..."
                ></textarea>
                <div v-if="errors.notes" class="invalid-feedback">
                  {{ errors.notes[0] }}
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
                  <button type="button" @click="saveAndContinue" class="btn btn-outline-primary me-2" :disabled="saving">
                    <i class="bi bi-check-circle me-2"></i>Save & Add Another
                  </button>
                  <button type="submit" class="btn btn-primary" :disabled="saving">
                    <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-check-circle me-2"></i>
                    {{ isEditing ? 'Update Asset' : 'Create Asset' }}
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
              <i class="bi bi-lightbulb me-2"></i>Quick Tips
            </h6>
          </div>
          <div class="card-body">
            <div class="small">
              <div class="mb-3">
                <strong>Asset Number:</strong>
                <p class="text-muted mb-0">Use a consistent numbering system. Example: VEH-001, EQP-001</p>
              </div>
              <div class="mb-3">
                <strong>VIN:</strong>
                <p class="text-muted mb-0">Vehicle Identification Number should be exactly 17 characters</p>
              </div>
              <div class="mb-3">
                <strong>Status:</strong>
                <ul class="text-muted mb-0 ps-3">
                  <li><strong>Active:</strong> Currently in use</li>
                  <li><strong>Inactive:</strong> Not in use but available</li>
                  <li><strong>Maintenance:</strong> Under repair</li>
                  <li><strong>Retired:</strong> No longer in service</li>
                </ul>
              </div>
              <div class="mb-3">
                <strong>Departments:</strong>
                <p class="text-muted mb-0">Assign assets to departments for better organization and cost tracking</p>
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
import { assetsAPI } from '@/services/api'
import { toast } from '@/utils/toast'

export default {
  name: 'AssetForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const assetId = route.params.id
    const isEditing = computed(() => !!assetId)
    
    const loading = ref(false)
    const saving = ref(false)
    const departments = ref([])
    const errors = ref({})
    
    const form = reactive({
      asset_number: '',
      vehicle_type: '',
      make: '',
      model: '',
      year: new Date().getFullYear(),
      vin_number: '',
      license_plate: '',
      fuel_type: '',
      department: '',
      status: 'active',
      current_odometer_reading: 0,
      purchase_date: '',
      purchase_cost: null,
      warranty_expiry: '',
      insurance_expiry: '',
      notes: ''
    })

    const loadDepartments = async () => {
      try {
        const response = await assetsAPI.getDepartments()
        departments.value = response.data.results || []
      } catch (error) {
        console.error('Error loading departments:', error)
      }
    }

    const loadAsset = async () => {
      if (!isEditing.value) return
      
      loading.value = true
      try {
        const response = await assetsAPI.getAsset(assetId)
        const asset = response.data
        
        // Populate form with asset data
        Object.keys(form).forEach(key => {
          if (asset[key] !== undefined) {
            form[key] = asset[key]
          }
        })
        
        // Handle department specially
        if (asset.department) {
          form.department = asset.department
        }
      } catch (error) {
        console.error('Error loading asset:', error)
        toast.error('Failed to load asset details')
        router.push('/assets')
      } finally {
        loading.value = false
      }
    }

    const saveAsset = async (continueAdding = false) => {
      saving.value = true
      errors.value = {}
      
      try {
        // Prepare form data
        const formData = { ...form }
        
        // Remove empty strings and convert to null
        Object.keys(formData).forEach(key => {
          if (formData[key] === '' || formData[key] === undefined) {
            formData[key] = null
          }
        })
        
        let response
        if (isEditing.value) {
          response = await assetsAPI.updateAsset(assetId, formData)
          toast.success('Asset updated successfully')
        } else {
          response = await assetsAPI.createAsset(formData)
          toast.success('Asset created successfully')
        }
        
        if (continueAdding) {
          // Reset form for new asset
          Object.keys(form).forEach(key => {
            if (key !== 'status' && key !== 'mileage_unit' && key !== 'year') {
              form[key] = key === 'year' ? new Date().getFullYear() : (typeof form[key] === 'number' ? null : '')
            }
          })
          form.status = 'active'
          form.mileage_unit = 'miles'
        } else {
          // Navigate to asset detail or list
          if (isEditing.value) {
            router.push(`/assets/${assetId}`)
          } else {
            router.push(`/assets/${response.data.asset_id}`)
          }
        }
      } catch (error) {
        console.error('Error saving asset:', error)
        
        if (error.response?.status === 400 && error.response?.data) {
          errors.value = error.response.data
          toast.error('Please check the form for errors')
        } else {
          toast.error('Failed to save asset')
        }
      } finally {
        saving.value = false
      }
    }

    const saveAndContinue = () => {
      saveAsset(true)
    }

    const goBack = () => {
      if (isEditing.value) {
        router.push(`/assets/${assetId}`)
      } else {
        router.push('/assets')
      }
    }

    onMounted(async () => {
      await loadDepartments()
      if (isEditing.value) {
        await loadAsset()
      }
    })

    return {
      isEditing,
      loading,
      saving,
      departments,
      errors,
      form,
      saveAsset,
      saveAndContinue,
      goBack
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
</style>