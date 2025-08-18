<template>
  <div class="driver-form-container">
    <!-- Header -->
    <div class="page-header">
      <div class="d-flex align-center justify-space-between">
        <div>
          <h1 class="text-h4 mb-1">{{ isEditing ? 'Edit Driver' : 'Add New Driver' }}</h1>
          <p class="text-body-2 text-medium-emphasis">
            {{ isEditing ? 'Update driver information and assignments' : 'Create a new driver profile' }}
          </p>
        </div>
        
        <div class="d-flex align-center gap-3">
          <v-btn
            variant="outlined"
            prepend-icon="mdi-arrow-left"
            @click="goBack"
          >
            Back to Drivers
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Form Card -->
    <v-card>
      <v-card-text class="pa-6">
        <v-form ref="form" v-model="isFormValid" @submit.prevent="handleSubmit">
          <v-row>
            <!-- Personal Information Section -->
            <v-col cols="12">
              <h3 class="text-h6 mb-4 text-primary">Personal Information</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.first_name"
                label="First Name *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.last_name"
                label="Last Name *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.email"
                label="Email Address *"
                type="email"
                variant="outlined"
                :rules="[rules.required, rules.email]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.phone"
                label="Phone Number *"
                variant="outlined"
                :rules="[rules.required, rules.phone]"
                required
                placeholder="+1234567890"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.date_of_birth"
                label="Date of Birth *"
                type="date"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <!-- Employment Information Section -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">Employment Information</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.hire_date"
                label="Hire Date *"
                type="date"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.employment_status"
                :items="employmentStatusOptions"
                label="Employment Status *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.department"
                label="Department"
                variant="outlined"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.position"
                label="Position"
                variant="outlined"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.employee_number"
                label="Employee Number"
                variant="outlined"
              />
            </v-col>
            
            <!-- License Information Section -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">License Information</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.license_number"
                label="License Number *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.license_type"
                :items="licenseTypeOptions"
                label="License Type *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.license_expiration"
                label="License Expiration *"
                type="date"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.license_state"
                label="License State *"
                variant="outlined"
                :rules="[rules.required, rules.stateCode]"
                required
                placeholder="NY"
                maxlength="2"
              />
            </v-col>
            
            <!-- Address Information Section -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">Address Information</h3>
            </v-col>
            
            <v-col cols="12">
              <v-text-field
                v-model="formData.address_line1"
                label="Address Line 1 *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12">
              <v-text-field
                v-model="formData.address_line2"
                label="Address Line 2"
                variant="outlined"
              />
            </v-col>
            
            <v-col cols="12" md="4">
              <v-text-field
                v-model="formData.city"
                label="City *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="4">
              <v-text-field
                v-model="formData.state"
                label="State *"
                variant="outlined"
                :rules="[rules.required, rules.stateCode]"
                required
                placeholder="NY"
                maxlength="2"
              />
            </v-col>
            
            <v-col cols="12" md="4">
              <v-text-field
                v-model="formData.zip_code"
                label="ZIP Code *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <!-- Emergency Contact Section -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">Emergency Contact</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.emergency_contact_name"
                label="Emergency Contact Name *"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.emergency_contact_phone"
                label="Emergency Contact Phone *"
                variant="outlined"
                :rules="[rules.required, rules.phone]"
                required
                placeholder="+1234567890"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.emergency_contact_relationship"
                label="Relationship *"
                variant="outlined"
                :rules="[rules.required]"
                required
                placeholder="Spouse, Parent, Sibling, etc."
              />
            </v-col>
            
            <!-- Profile Photo Section -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">Profile Photo</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <div class="photo-upload-section">
                <div class="d-flex align-center gap-4">
                  <v-avatar size="80" class="profile-preview">
                    <v-img
                      v-if="photoPreview || (isEditing && formData.profile_photo)"
                      :src="photoPreview || formData.profile_photo"
                      :alt="formData.first_name + ' ' + formData.last_name"
                    />
                    <v-icon v-else size="40" color="grey-lighten-1">mdi-account</v-icon>
                  </v-avatar>
                  
                  <div>
                    <v-file-input
                      ref="photoInput"
                      v-model="selectedPhoto"
                      label="Upload Photo"
                      accept="image/jpeg,image/jpg,image/png,image/webp"
                      variant="outlined"
                      density="compact"
                      prepend-icon="mdi-camera"
                      show-size
                      @change="handlePhotoSelect"
                      @click:clear="clearPhoto"
                    />
                    <p class="text-caption text-medium-emphasis mt-1">
                      JPEG, PNG, or WebP. Max 2MB. Recommended: 300x300px
                    </p>
                  </div>
                </div>
              </div>
            </v-col>

            <!-- Additional Information Section -->
            <v-col cols="12" class="mt-6">
              <h3 class="text-h6 mb-4 text-primary">Additional Information</h3>
            </v-col>
            
            <v-col cols="12">
              <v-textarea
                v-model="formData.notes"
                label="Notes"
                variant="outlined"
                rows="3"
                placeholder="Additional notes or comments about the driver..."
              />
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      
      <v-card-actions class="pa-6 pt-0">
        <v-spacer />
        <v-btn
          variant="outlined"
          @click="goBack"
          :disabled="driversStore.isLoading"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          @click="handleSubmit"
          :loading="driversStore.isLoading"
          :disabled="!isFormValid"
        >
          {{ isEditing ? 'Update Driver' : 'Create Driver' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDriversStore } from '../../stores/drivers'

// Router and store
const router = useRouter()
const route = useRoute()
const driversStore = useDriversStore()

// Component state
const form = ref(null)
const isFormValid = ref(false)
const selectedPhoto = ref(null)
const photoPreview = ref(null)
const photoInput = ref(null)
const isUploadingPhoto = ref(false)

// Check if we're editing
const isEditing = computed(() => !!route.params.id)

// Form data
const formData = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  date_of_birth: '',
  hire_date: '',
  employment_status: 'active',
  department: '',
  position: '',
  employee_number: '',
  license_number: '',
  license_type: '',
  license_expiration: '',
  license_state: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  zip_code: '',
  emergency_contact_name: '',
  emergency_contact_phone: '',
  emergency_contact_relationship: '',
  profile_photo: '',
  notes: ''
})

// Validation rules
const rules = {
  required: value => !!value || 'This field is required',
  email: value => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(value) || 'Please enter a valid email address'
  },
  phone: value => {
    const pattern = /^\+?1?\d{9,15}$/
    return pattern.test(value.replace(/[-\s]/g, '')) || 'Please enter a valid phone number'
  },
  stateCode: value => {
    return !value || (value.length === 2 && /^[A-Z]{2}$/.test(value.toUpperCase())) || 'Please enter a valid 2-letter state code'
  }
}

// Options for dropdowns
const employmentStatusOptions = [
  { title: 'Active', value: 'active' },
  { title: 'Inactive', value: 'inactive' },
  { title: 'Suspended', value: 'suspended' },
  { title: 'Terminated', value: 'terminated' },
  { title: 'On Leave', value: 'on_leave' }
]

const licenseTypeOptions = [
  { title: 'Class A CDL', value: 'class_a' },
  { title: 'Class B CDL', value: 'class_b' },
  { title: 'Class C CDL', value: 'class_c' },
  { title: 'Chauffeur License', value: 'chauffeur' },
  { title: 'Regular License', value: 'regular' },
  { title: 'Motorcycle License', value: 'motorcycle' }
]

// Methods
const loadDriverData = async () => {
  if (isEditing.value) {
    try {
      await driversStore.fetchDriver(route.params.id)
      const driver = driversStore.currentDriver
      if (driver) {
        console.log('Loading driver data:', driver)
        // Populate form with existing driver data, excluding profile_photo since it's handled separately
        Object.keys(formData.value).forEach(key => {
          if (key !== 'profile_photo' && driver[key] !== undefined) {
            formData.value[key] = driver[key]
          }
        })
        console.log('Form data after loading:', formData.value)
      }
    } catch (error) {
      console.error('Failed to load driver:', error)
      router.push('/drivers')
    }
  }
}

const handlePhotoSelect = (files) => {
  if (files && files.length > 0) {
    const file = files[0]
    
    // Validate file size (2MB)
    if (file.size > 2097152) {
      console.error('File size too large')
      return
    }
    
    // Create preview URL
    photoPreview.value = URL.createObjectURL(file)
  }
}

const clearPhoto = () => {
  selectedPhoto.value = null
  photoPreview.value = null
  if (photoPreview.value) {
    URL.revokeObjectURL(photoPreview.value)
  }
}

const uploadPhoto = async (driverId) => {
  if (!selectedPhoto.value || selectedPhoto.value.length === 0) return

  isUploadingPhoto.value = true
  try {
    const formData = new FormData()
    formData.append('photo', selectedPhoto.value[0])
    
    await driversStore.uploadDriverPhoto(driverId, formData)
  } catch (error) {
    console.error('Failed to upload photo:', error)
  } finally {
    isUploadingPhoto.value = false
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  try {
    // Convert state codes to uppercase
    formData.value.license_state = formData.value.license_state.toUpperCase()
    formData.value.state = formData.value.state.toUpperCase()
    
    // Create submission data without profile_photo field (handled separately)
    const submissionData = { ...formData.value }
    delete submissionData.profile_photo
    
    // Debug logging
    console.log('Form data before submission:', submissionData)
    console.log('Is editing:', isEditing.value)
    console.log('Route params ID:', route.params.id)
    
    let driver
    if (isEditing.value) {
      driver = await driversStore.updateDriver(route.params.id, submissionData)
    } else {
      driver = await driversStore.createDriver(submissionData)
    }
    
    // Upload photo if one was selected
    if (selectedPhoto.value && selectedPhoto.value.length > 0) {
      const driverId = isEditing.value ? route.params.id : driver.id
      await uploadPhoto(driverId)
    }
    
    router.push('/drivers')
  } catch (error) {
    console.error('Failed to save driver:', error)
    console.error('Error details:', error.response?.data || error.message)
  }
}

const goBack = () => {
  router.push('/drivers')
}

// Lifecycle hooks
onMounted(() => {
  loadDriverData()
})
</script>

<style scoped>
.driver-form-container {
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

.photo-upload-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafafa;
}

.profile-preview {
  border: 2px solid #216093;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.gap-4 {
  gap: 16px;
}
</style>