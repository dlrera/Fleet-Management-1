<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card>
          <v-card-title class="text-h5">
            {{ isEdit ? 'Edit Asset' : 'Create New Asset' }}
          </v-card-title>
          
          <v-card-text>
            <p class="text-body-2 text-medium-emphasis mb-4">
              {{ isEdit ? 'Update asset information below.' : 'Enter asset information to add it to your fleet.' }}
            </p>
            
            <!-- Placeholder form -->
            <v-form v-model="valid" @submit.prevent="handleSubmit">
              <v-text-field
                v-model="form.make"
                label="Make"
                variant="outlined"
                :rules="[rules.required]"
                class="mb-4"
              />
              
              <v-text-field
                v-model="form.model"
                label="Model"
                variant="outlined"
                :rules="[rules.required]"
                class="mb-4"
              />
              
              <v-text-field
                v-model="form.year"
                label="Year"
                type="number"
                variant="outlined"
                :rules="[rules.required, rules.year]"
                class="mb-4"
              />
              
              <v-select
                v-model="form.vehicle_type"
                :items="vehicleTypes"
                label="Vehicle Type"
                variant="outlined"
                :rules="[rules.required]"
                class="mb-4"
              />
              
              <div class="d-flex ga-4">
                <v-btn
                  variant="outlined"
                  :to="{ name: 'AssetsList' }"
                >
                  Cancel
                </v-btn>
                
                <v-btn
                  type="submit"
                  color="primary"
                  :disabled="!valid"
                  :loading="loading"
                >
                  {{ isEdit ? 'Update Asset' : 'Create Asset' }}
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'

const route = useRoute()
const router = useRouter()
const assetsStore = useAssetsStore()

const valid = ref(false)
const loading = ref(false)

const form = ref({
  make: '',
  model: '',
  year: new Date().getFullYear(),
  vehicle_type: ''
})

const vehicleTypes = [
  { title: 'Bus', value: 'bus' },
  { title: 'Truck', value: 'truck' },
  { title: 'Van', value: 'van' },
  { title: 'Car', value: 'car' },
  { title: 'Equipment', value: 'equipment' },
  { title: 'Other', value: 'other' }
]

const rules = {
  required: value => !!value || 'Required.',
  year: value => {
    const currentYear = new Date().getFullYear()
    return (value >= 1900 && value <= currentYear + 1) || 'Invalid year'
  }
}

const isEdit = computed(() => !!route.params.id)

const handleSubmit = async () => {
  if (!valid.value) return
  
  loading.value = true
  try {
    if (isEdit.value) {
      await assetsStore.updateAsset(route.params.id, form.value)
    } else {
      await assetsStore.createAsset(form.value)
    }
    router.push({ name: 'AssetsList' })
  } catch (error) {
    console.error('Failed to save asset:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (isEdit.value) {
    try {
      const asset = await assetsStore.fetchAsset(route.params.id)
      Object.assign(form.value, {
        make: asset.make,
        model: asset.model,
        year: asset.year,
        vehicle_type: asset.vehicle_type
      })
    } catch (error) {
      console.error('Failed to load asset:', error)
      router.push({ name: 'AssetsList' })
    }
  }
})
</script>