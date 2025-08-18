<template>
  <v-card>
    <v-card-title class="d-flex align-center justify-space-between">
      <span>Add Manual Location Entry</span>
      <v-btn
        icon="mdi-close"
        variant="text"
        size="small"
        @click="$emit('close')"
      />
    </v-card-title>

    <v-card-text>
      <v-form ref="form" v-model="valid" @submit.prevent="submitLocation">
        <!-- Asset selection -->
        <v-autocomplete
          v-model="selectedAsset"
          :items="assets"
          :loading="assetsStore.isLoading"
          item-title="asset_id"
          item-value="asset_id"
          label="Select Asset"
          placeholder="Type to search assets..."
          variant="outlined"
          :rules="[rules.required]"
          clearable
          @update:search="searchAssets"
        >
          <template #item="{ props, item }">
            <v-list-item v-bind="props">
              <template #prepend>
                <v-avatar size="32">
                  <v-img
                    v-if="item.raw.thumbnail"
                    :src="item.raw.thumbnail"
                    :alt="item.raw.asset_id"
                  />
                  <v-icon v-else>mdi-car</v-icon>
                </v-avatar>
              </template>
              
              <v-list-item-title>{{ item.raw.asset_id }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ item.raw.make }} {{ item.raw.model }} ({{ item.raw.status }})
              </v-list-item-subtitle>
            </v-list-item>
          </template>
        </v-autocomplete>

        <!-- Coordinate inputs -->
        <div class="d-flex gap-4">
          <v-text-field
            v-model="latitude"
            label="Latitude"
            variant="outlined"
            type="number"
            step="any"
            :rules="[rules.required, rules.latitude]"
            placeholder="40.7128"
          />
          
          <v-text-field
            v-model="longitude"
            label="Longitude"
            variant="outlined"
            type="number"
            step="any"
            :rules="[rules.required, rules.longitude]"
            placeholder="-74.0060"
          />
        </div>

        <!-- Get current location button -->
        <div class="d-flex align-center gap-2 mb-4">
          <v-btn
            variant="outlined"
            prepend-icon="mdi-crosshairs-gps"
            :loading="gettingLocation"
            @click="getCurrentLocation"
          >
            Use Current Location
          </v-btn>
          
          <v-chip
            v-if="locationAccuracy"
            size="small"
            color="info"
          >
            Accuracy: ±{{ Math.round(locationAccuracy) }}m
          </v-chip>
        </div>

        <!-- Address field -->
        <v-text-field
          v-model="address"
          label="Address (Optional)"
          variant="outlined"
          placeholder="Enter address or description"
        />

        <!-- Notes field -->
        <v-textarea
          v-model="notes"
          label="Notes (Optional)"
          variant="outlined"
          placeholder="Additional notes about this location"
          rows="3"
        />

        <!-- Preview coordinates -->
        <div v-if="latitude && longitude" class="coordinates-preview">
          <v-icon size="16" class="mr-2">mdi-map-marker</v-icon>
          <span class="text-body-2">
            {{ parseFloat(latitude).toFixed(6) }}, {{ parseFloat(longitude).toFixed(6) }}
          </span>
        </div>
      </v-form>
    </v-card-text>

    <v-card-actions class="px-6 pb-6">
      <v-spacer />
      <v-btn
        variant="text"
        @click="$emit('close')"
      >
        Cancel
      </v-btn>
      
      <v-btn
        color="primary"
        :loading="locationsStore.isCreating"
        :disabled="!valid"
        @click="submitLocation"
      >
        Add Location
      </v-btn>
    </v-card-actions>

    <!-- Error display -->
    <v-alert
      v-if="locationsStore.error"
      type="error"
      class="mx-6 mb-4"
      variant="tonal"
    >
      {{ getErrorMessage(locationsStore.error) }}
    </v-alert>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAssetsStore } from '../../stores/assets'
import { useLocationsStore } from '../../stores/locations'

// Stores
const assetsStore = useAssetsStore()
const locationsStore = useLocationsStore()

// Component state
const form = ref(null)
const valid = ref(false)
const selectedAsset = ref('')
const latitude = ref('')
const longitude = ref('')
const address = ref('')
const notes = ref('')
const gettingLocation = ref(false)
const locationAccuracy = ref(null)

// Computed
const assets = computed(() => assetsStore.assets.filter(asset => asset.status !== 'retired'))

// Validation rules
const rules = {
  required: (value) => !!value || 'This field is required',
  latitude: (value) => {
    const num = parseFloat(value)
    return (!isNaN(num) && num >= -90 && num <= 90) || 'Latitude must be between -90 and 90'
  },
  longitude: (value) => {
    const num = parseFloat(value)
    return (!isNaN(num) && num >= -180 && num <= 180) || 'Longitude must be between -180 and 180'
  }
}

// Emits
const emit = defineEmits(['close', 'location-added'])

// Methods
const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    alert('Geolocation is not supported by this browser.')
    return
  }

  gettingLocation.value = true
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      latitude.value = position.coords.latitude.toString()
      longitude.value = position.coords.longitude.toString()
      locationAccuracy.value = position.coords.accuracy
      gettingLocation.value = false
    },
    (error) => {
      console.error('Error getting location:', error)
      let message = 'Failed to get current location.'
      
      switch (error.code) {
        case error.PERMISSION_DENIED:
          message = 'Location access denied by user.'
          break
        case error.POSITION_UNAVAILABLE:
          message = 'Location information is unavailable.'
          break
        case error.TIMEOUT:
          message = 'Location request timed out.'
          break
      }
      
      alert(message)
      gettingLocation.value = false
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 60000
    }
  )
}

const submitLocation = async () => {
  if (!form.value?.validate() || !valid.value) {
    return
  }

  try {
    const locationData = {
      asset_id: selectedAsset.value,
      latitude: parseFloat(latitude.value),
      longitude: parseFloat(longitude.value),
      address: address.value,
      notes: notes.value
    }

    await locationsStore.createManualLocationEntry(locationData)
    
    // Reset form
    selectedAsset.value = ''
    latitude.value = ''
    longitude.value = ''
    address.value = ''
    notes.value = ''
    locationAccuracy.value = null
    
    emit('location-added')
  } catch (error) {
    console.error('Failed to add location:', error)
  }
}

const searchAssets = (query) => {
  if (query && query.length > 0) {
    assetsStore.setSearchQuery(query)
    assetsStore.fetchAssets({ page: 1 })
  }
}

const getErrorMessage = (error) => {
  if (typeof error === 'string') {
    return error
  }
  
  if (error?.asset_id) {
    return `Asset: ${error.asset_id[0]}`
  }
  
  if (error?.latitude) {
    return `Latitude: ${error.latitude[0]}`
  }
  
  if (error?.longitude) {
    return `Longitude: ${error.longitude[0]}`
  }
  
  return 'Failed to add location entry'
}

// Lifecycle
onMounted(async () => {
  // Load assets if not already loaded
  if (!assetsStore.hasAssets) {
    await assetsStore.fetchAssets()
  }
})
</script>

<style scoped>
.coordinates-preview {
  background-color: #f5f5f5;
  padding: 8px 12px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  margin-top: 16px;
  color: #666;
}

.gap-4 {
  gap: 16px;
}

.gap-2 {
  gap: 8px;
}
</style>