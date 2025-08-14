<template>
  <div class="driver-form">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/drivers">Drivers</router-link>
            </li>
            <li class="breadcrumb-item active">{{ isEditing ? 'Edit Driver' : 'Create Driver' }}</li>
          </ol>
        </nav>
        <h1 class="mb-1">{{ isEditing ? 'Edit Driver' : 'Create New Driver' }}</h1>
        <p class="text-muted mb-0">{{ isEditing ? 'Update driver information' : 'Add a new driver to your fleet' }}</p>
      </div>
    </div>

    <!-- Form -->
    <div class="row">
      <div class="col-lg-8">
        <form @submit.prevent="saveDriver">
          <!-- User Account Information -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-person me-2"></i>User Account Information
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">First Name <span class="text-danger">*</span></label>
                  <input 
                    v-model="form.user.first_name" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.user?.first_name }"
                    required
                  >
                  <div v-if="errors.user?.first_name" class="invalid-feedback">
                    {{ errors.user.first_name[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Last Name <span class="text-danger">*</span></label>
                  <input 
                    v-model="form.user.last_name" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.user?.last_name }"
                    required
                  >
                  <div v-if="errors.user?.last_name" class="invalid-feedback">
                    {{ errors.user.last_name[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Username <span class="text-danger">*</span></label>
                  <input 
                    v-model="form.user.username" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.user?.username }"
                    :disabled="isEditing"
                    required
                  >
                  <div v-if="errors.user?.username" class="invalid-feedback">
                    {{ errors.user.username[0] }}
                  </div>
                  <div v-if="isEditing" class="form-text">Username cannot be changed after creation</div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Email <span class="text-danger">*</span></label>
                  <input 
                    v-model="form.user.email" 
                    type="email" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.user?.email }"
                    required
                  >
                  <div v-if="errors.user?.email" class="invalid-feedback">
                    {{ errors.user.email[0] }}
                  </div>
                </div>
                <div v-if="!isEditing" class="col-md-6">
                  <label class="form-label">Password <span class="text-danger">*</span></label>
                  <input 
                    v-model="form.user.password" 
                    type="password" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.user?.password }"
                    required
                  >
                  <div v-if="errors.user?.password" class="invalid-feedback">
                    {{ errors.user.password[0] }}
                  </div>
                  <div class="form-text">Minimum 8 characters</div>
                </div>
                <div v-if="!isEditing" class="col-md-6">
                  <label class="form-label">Confirm Password <span class="text-danger">*</span></label>
                  <input 
                    v-model="form.user.password_confirm" 
                    type="password" 
                    class="form-control"
                    :class="{ 'is-invalid': passwordMismatch }"
                    required
                  >
                  <div v-if="passwordMismatch" class="invalid-feedback">
                    Passwords do not match
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Driver Information -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-id-card me-2"></i>Driver Information
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Employee ID</label>
                  <input 
                    v-model="form.employee_id" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.employee_id }"
                  >
                  <div v-if="errors.employee_id" class="invalid-feedback">
                    {{ errors.employee_id[0] }}
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
                    <option value="suspended">Suspended</option>
                  </select>
                  <div v-if="errors.status" class="invalid-feedback">
                    {{ errors.status[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Phone Number</label>
                  <input 
                    v-model="form.phone_number" 
                    type="tel" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.phone_number }"
                  >
                  <div v-if="errors.phone_number" class="invalid-feedback">
                    {{ errors.phone_number[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Date of Birth</label>
                  <input 
                    v-model="form.date_of_birth" 
                    type="date" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.date_of_birth }"
                  >
                  <div v-if="errors.date_of_birth" class="invalid-feedback">
                    {{ errors.date_of_birth[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Hire Date</label>
                  <input 
                    v-model="form.hire_date" 
                    type="date" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.hire_date }"
                  >
                  <div v-if="errors.hire_date" class="invalid-feedback">
                    {{ errors.hire_date[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Safety Rating</label>
                  <div class="input-group">
                    <input 
                      v-model.number="form.safety_rating" 
                      type="number" 
                      class="form-control"
                      :class="{ 'is-invalid': errors.safety_rating }"
                      min="0"
                      max="100"
                      step="0.1"
                    >
                    <span class="input-group-text">%</span>
                  </div>
                  <div v-if="errors.safety_rating" class="invalid-feedback">
                    {{ errors.safety_rating[0] }}
                  </div>
                </div>
                <div class="col-12">
                  <label class="form-label">Address</label>
                  <textarea 
                    v-model="form.address" 
                    class="form-control" 
                    rows="3"
                    :class="{ 'is-invalid': errors.address }"
                    placeholder="Street address, city, state, zip code"
                  ></textarea>
                  <div v-if="errors.address" class="invalid-feedback">
                    {{ errors.address[0] }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- License Information -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-card-text me-2"></i>License Information
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">License Number</label>
                  <input 
                    v-model="form.license_number" 
                    type="text" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.license_number }"
                  >
                  <div v-if="errors.license_number" class="invalid-feedback">
                    {{ errors.license_number[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">License Type</label>
                  <select 
                    v-model="form.license_type" 
                    class="form-select"
                    :class="{ 'is-invalid': errors.license_type }"
                  >
                    <option value="">Select License Type</option>
                    <option value="cdl_a">CDL Class A</option>
                    <option value="cdl_b">CDL Class B</option>
                    <option value="cdl_c">CDL Class C</option>
                    <option value="regular">Regular License</option>
                  </select>
                  <div v-if="errors.license_type" class="invalid-feedback">
                    {{ errors.license_type[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Issue Date</label>
                  <input 
                    v-model="form.license_issue_date" 
                    type="date" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.license_issue_date }"
                  >
                  <div v-if="errors.license_issue_date" class="invalid-feedback">
                    {{ errors.license_issue_date[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Expiry Date</label>
                  <input 
                    v-model="form.license_expiry_date" 
                    type="date" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.license_expiry_date }"
                  >
                  <div v-if="errors.license_expiry_date" class="invalid-feedback">
                    {{ errors.license_expiry_date[0] }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Issuing State</label>
                  <select 
                    v-model="form.license_state" 
                    class="form-select"
                  >
                    <option value="">Select State</option>
                    <option v-for="state in states" :key="state.value" :value="state.value">
                      {{ state.label }}
                    </option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Medical Certificate Expiry</label>
                  <input 
                    v-model="form.medical_cert_expiry" 
                    type="date" 
                    class="form-control"
                    :class="{ 'is-invalid': errors.medical_cert_expiry }"
                  >
                  <div v-if="errors.medical_cert_expiry" class="invalid-feedback">
                    {{ errors.medical_cert_expiry[0] }}
                  </div>
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
                  placeholder="Any additional notes or comments about this driver..."
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
                    {{ isEditing ? 'Update Driver' : 'Create Driver' }}
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
                <strong>Username:</strong>
                <p class="text-muted mb-0">Must be unique. Cannot be changed after creation. Use employee ID or email prefix.</p>
              </div>
              <div class="mb-3">
                <strong>License Types:</strong>
                <ul class="text-muted mb-0 ps-3">
                  <li><strong>CDL Class A:</strong> Heavy trucks, tractor-trailers</li>
                  <li><strong>CDL Class B:</strong> Large trucks, buses</li>
                  <li><strong>CDL Class C:</strong> Hazmat, passenger vehicles</li>
                  <li><strong>Regular:</strong> Standard vehicles</li>
                </ul>
              </div>
              <div class="mb-3">
                <strong>Safety Rating:</strong>
                <p class="text-muted mb-0">Enter percentage (0-100). Based on driving record, incidents, and training.</p>
              </div>
              <div class="mb-3">
                <strong>Medical Certificate:</strong>
                <p class="text-muted mb-0">Required for CDL drivers. Must be renewed regularly.</p>
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
import { driversAPI } from '@/services/api'
import { toast } from '@/utils/toast'

export default {
  name: 'DriverForm',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const driverId = route.params.id
    const isEditing = computed(() => !!driverId)
    
    const loading = ref(false)
    const saving = ref(false)
    const errors = ref({})
    
    const form = reactive({
      user: {
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        password: '',
        password_confirm: ''
      },
      employee_id: '',
      status: 'active',
      phone_number: '',
      date_of_birth: '',
      hire_date: '',
      safety_rating: 100,
      address: '',
      license_number: '',
      license_type: '',
      license_issue_date: '',
      license_expiry_date: '',
      license_state: '',
      medical_cert_expiry: '',
      notes: ''
    })

    const passwordMismatch = computed(() => {
      return !isEditing.value && 
             form.user.password && 
             form.user.password_confirm && 
             form.user.password !== form.user.password_confirm
    })

    const states = ref([
      { value: 'AL', label: 'Alabama' },
      { value: 'AK', label: 'Alaska' },
      { value: 'AZ', label: 'Arizona' },
      { value: 'AR', label: 'Arkansas' },
      { value: 'CA', label: 'California' },
      { value: 'CO', label: 'Colorado' },
      { value: 'CT', label: 'Connecticut' },
      { value: 'DE', label: 'Delaware' },
      { value: 'FL', label: 'Florida' },
      { value: 'GA', label: 'Georgia' },
      { value: 'HI', label: 'Hawaii' },
      { value: 'ID', label: 'Idaho' },
      { value: 'IL', label: 'Illinois' },
      { value: 'IN', label: 'Indiana' },
      { value: 'IA', label: 'Iowa' },
      { value: 'KS', label: 'Kansas' },
      { value: 'KY', label: 'Kentucky' },
      { value: 'LA', label: 'Louisiana' },
      { value: 'ME', label: 'Maine' },
      { value: 'MD', label: 'Maryland' },
      { value: 'MA', label: 'Massachusetts' },
      { value: 'MI', label: 'Michigan' },
      { value: 'MN', label: 'Minnesota' },
      { value: 'MS', label: 'Mississippi' },
      { value: 'MO', label: 'Missouri' },
      { value: 'MT', label: 'Montana' },
      { value: 'NE', label: 'Nebraska' },
      { value: 'NV', label: 'Nevada' },
      { value: 'NH', label: 'New Hampshire' },
      { value: 'NJ', label: 'New Jersey' },
      { value: 'NM', label: 'New Mexico' },
      { value: 'NY', label: 'New York' },
      { value: 'NC', label: 'North Carolina' },
      { value: 'ND', label: 'North Dakota' },
      { value: 'OH', label: 'Ohio' },
      { value: 'OK', label: 'Oklahoma' },
      { value: 'OR', label: 'Oregon' },
      { value: 'PA', label: 'Pennsylvania' },
      { value: 'RI', label: 'Rhode Island' },
      { value: 'SC', label: 'South Carolina' },
      { value: 'SD', label: 'South Dakota' },
      { value: 'TN', label: 'Tennessee' },
      { value: 'TX', label: 'Texas' },
      { value: 'UT', label: 'Utah' },
      { value: 'VT', label: 'Vermont' },
      { value: 'VA', label: 'Virginia' },
      { value: 'WA', label: 'Washington' },
      { value: 'WV', label: 'West Virginia' },
      { value: 'WI', label: 'Wisconsin' },
      { value: 'WY', label: 'Wyoming' }
    ])

    const loadDriver = async () => {
      if (!isEditing.value) return
      
      loading.value = true
      try {
        const response = await driversAPI.getDriver(driverId)
        const driver = response.data
        
        // Populate user form
        if (driver.user) {
          Object.keys(form.user).forEach(key => {
            if (key !== 'password' && key !== 'password_confirm' && driver.user[key] !== undefined) {
              form.user[key] = driver.user[key]
            }
          })
        }
        
        // Populate driver form
        Object.keys(form).forEach(key => {
          if (key !== 'user' && driver[key] !== undefined) {
            form[key] = driver[key]
          }
        })
      } catch (error) {
        console.error('Error loading driver:', error)
        toast.error('Failed to load driver details')
        router.push('/drivers')
      } finally {
        loading.value = false
      }
    }

    const saveDriver = async (continueAdding = false) => {
      if (passwordMismatch.value) {
        toast.error('Passwords do not match')
        return
      }

      saving.value = true
      errors.value = {}
      
      try {
        // Prepare form data
        const formData = { ...form }
        
        // Remove password confirmation
        if (formData.user.password_confirm) {
          delete formData.user.password_confirm
        }
        
        // Remove empty strings and convert to null
        Object.keys(formData).forEach(key => {
          if (key !== 'user') {
            if (formData[key] === '' || formData[key] === undefined) {
              formData[key] = null
            }
          }
        })

        Object.keys(formData.user).forEach(key => {
          if (formData.user[key] === '' || formData.user[key] === undefined) {
            if (key !== 'password' || !isEditing.value) {
              formData.user[key] = null
            }
          }
        })
        
        let response
        if (isEditing.value) {
          response = await driversAPI.updateDriver(driverId, formData)
          toast.success('Driver updated successfully')
        } else {
          response = await driversAPI.createDriver(formData)
          toast.success('Driver created successfully')
        }
        
        if (continueAdding) {
          // Reset form for new driver
          Object.keys(form.user).forEach(key => {
            form.user[key] = ''
          })
          Object.keys(form).forEach(key => {
            if (key !== 'user' && key !== 'status' && key !== 'safety_rating') {
              form[key] = typeof form[key] === 'number' ? null : ''
            }
          })
          form.status = 'active'
          form.safety_rating = 100
        } else {
          // Navigate to driver detail or list
          if (isEditing.value) {
            router.push(`/drivers/${driverId}`)
          } else {
            router.push(`/drivers/${response.data.driver_id}`)
          }
        }
      } catch (error) {
        console.error('Error saving driver:', error)
        
        if (error.response?.status === 400 && error.response?.data) {
          errors.value = error.response.data
          toast.error('Please check the form for errors')
        } else {
          toast.error('Failed to save driver')
        }
      } finally {
        saving.value = false
      }
    }

    const saveAndContinue = () => {
      saveDriver(true)
    }

    const goBack = () => {
      if (isEditing.value) {
        router.push(`/drivers/${driverId}`)
      } else {
        router.push('/drivers')
      }
    }

    onMounted(async () => {
      if (isEditing.value) {
        await loadDriver()
      }
    })

    return {
      isEditing,
      loading,
      saving,
      errors,
      form,
      passwordMismatch,
      states,
      saveDriver,
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