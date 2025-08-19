<template>
  <div class="zone-management">
    <!-- Navigation header -->
    <div class="navigation-header mb-4">
      <v-btn
        variant="text"
        prepend-icon="mdi-arrow-left"
        @click="$router.push('/locations')"
      >
        Back to Locations
      </v-btn>
      <v-breadcrumbs :items="breadcrumbs" divider=">" />
    </div>

    <v-card>
      <v-card-title>
        <div class="d-flex justify-space-between align-center w-100">
          <span>Location Zone Management</span>
          <v-btn
            color="primary"
            @click="showCreateDialog = true"
          >
            <v-icon left>mdi-plus</v-icon>
            Add Zone
          </v-btn>
        </div>
      </v-card-title>

      <v-card-text>
        <!-- Zone Statistics -->
        <v-row class="mb-4" style="gap: 12px;">
          <v-col cols="12" md="3" style="padding: 0;">
            <div 
              class="stat-card" 
              :class="{ 'stat-card-active': activeFilter === 'all' }"
              @click="setFilter('all')"
            >
              <div class="stat-value">{{ totalZones }}</div>
              <div class="stat-label">Total Zones</div>
            </div>
          </v-col>
          <v-col cols="12" md="3" style="padding: 0;">
            <div 
              class="stat-card"
              :class="{ 'stat-card-active': activeFilter === 'active' }"
              @click="setFilter('active')"
            >
              <div class="stat-value">{{ activeZones }}</div>
              <div class="stat-label">Active Zones</div>
            </div>
          </v-col>
          <v-col cols="12" md="3" style="padding: 0;">
            <div 
              class="stat-card"
              :class="{ 'stat-card-active': activeFilter === 'depot' }"
              @click="setFilter('depot')"
            >
              <div class="stat-value">{{ depotCount }}</div>
              <div class="stat-label">Depots</div>
            </div>
          </v-col>
          <v-col cols="12" md="3" style="padding: 0;">
            <div 
              class="stat-card"
              :class="{ 'stat-card-active': activeFilter === 'service' }"
              @click="setFilter('service')"
            >
              <div class="stat-value">{{ serviceCount }}</div>
              <div class="stat-label">Service Areas</div>
            </div>
          </v-col>
        </v-row>

        <!-- Zone List -->
        <v-data-table
          :headers="headers"
          :items="filteredZones"
          :loading="loading"
          density="compact"
          :no-data-text="loading ? 'Loading zones...' : 'No zones found. Click Add Zone to create one.'"
        >
          <template v-slot:item.is_active="{ item }">
            <v-switch
              v-model="item.is_active"
              @change="toggleZoneActive(item)"
              density="compact"
              hide-details
            />
          </template>

          <template v-slot:item.zone_type="{ item }">
            <v-chip
              :color="getZoneTypeColor(item.zone_type)"
              size="small"
              label
            >
              {{ item.zone_type }}
            </v-chip>
          </template>

          <template v-slot:item.location="{ item }">
            {{ parseFloat(item.center_lat).toFixed(3) }}, {{ parseFloat(item.center_lng).toFixed(3) }}
          </template>

          <template v-slot:item.radius="{ item }">
            {{ (item.radius / 1000).toFixed(1) }} km
          </template>

          <template v-slot:item.actions="{ item }">
            <v-btn
              icon="mdi-pencil"
              size="small"
              variant="text"
              @click="editZone(item)"
            />
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="confirmDelete(item)"
            />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Create/Edit Dialog -->
    <v-dialog
      v-model="showCreateDialog"
      max-width="600"
    >
      <v-card>
        <v-card-title>
          {{ editingZone ? 'Edit Zone' : 'Create New Zone' }}
        </v-card-title>
        <v-card-text>
          <v-form ref="zoneForm">
            <v-text-field
              v-model="zoneForm.name"
              label="Zone Name"
              required
              :rules="nameRules"
            />
            
            <v-select
              v-model="zoneForm.zone_type"
              :items="zoneTypes"
              label="Zone Type"
              required
              :rules="[v => !!v || 'Zone type is required']"
            />

            <v-textarea
              v-model="zoneForm.description"
              label="Description"
              rows="2"
            />

            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model.number="zoneForm.center_lat"
                  label="Latitude"
                  type="number"
                  step="0.0001"
                  :rules="latitudeRules"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model.number="zoneForm.center_lng"
                  label="Longitude"
                  type="number"
                  step="0.0001"
                  :rules="longitudeRules"
                />
              </v-col>
            </v-row>

            <v-text-field
              v-model.number="zoneForm.radius"
              label="Radius (meters)"
              type="number"
              min="100"
              max="50000"
              :rules="radiusRules"
            />

            <v-text-field
              v-model="zoneForm.color"
              label="Zone Color (Hex)"
              placeholder="#1976d2"
              :rules="colorRules"
            />

            <v-checkbox
              v-model="zoneForm.is_active"
              label="Active"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="cancelEdit"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            @click="saveZone"
            :loading="saving"
          >
            {{ editingZone ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation -->
    <v-dialog
      v-model="showDeleteDialog"
      max-width="400"
    >
      <v-card>
        <v-card-title>Confirm Deletion</v-card-title>
        <v-card-text>
          Are you sure you want to delete the zone "{{ zoneToDelete?.name }}"?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showDeleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            @click="deleteZone"
            :loading="deleting"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { locationsAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
// import { useSnackbar } from '@/composables/useSnackbar'

const authStore = useAuthStore()
const router = useRouter()
// const { showSuccess, showError } = useSnackbar()

// Temporary notification functions
const showSuccess = (message) => {
  console.log('[SUCCESS]', message)
}
const showError = (message) => {
  console.error('[ERROR]', message)
}

// Data
const zones = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const editingZone = ref(null)
const zoneToDelete = ref(null)
const activeFilter = ref('all')

// Breadcrumbs
const breadcrumbs = [
  { title: 'Home', to: '/' },
  { title: 'Locations', to: '/locations' },
  { title: 'Zone Management', disabled: true }
]

// Form data
const zoneForm = ref({
  name: '',
  zone_type: 'depot',
  description: '',
  center_lat: 42.8864,  // Default to Buffalo
  center_lng: -78.8784,
  radius: 5000,
  color: '#1976d2',
  is_active: true
})

// Zone types
const zoneTypes = [
  { title: 'Depot', value: 'depot' },
  { title: 'Service Area', value: 'service_area' },
  { title: 'Customer Site', value: 'customer_site' },
  { title: 'Restricted Zone', value: 'restricted' },
  { title: 'Maintenance Facility', value: 'maintenance' },
  { title: 'Other', value: 'other' }
]

// Validation rules
const nameRules = [
  v => !!v || 'Name is required',
  v => (v && v.length >= 3) || 'Name must be at least 3 characters'
]

const latitudeRules = [
  v => v !== null && v !== '' || 'Latitude is required',
  v => (v >= -90 && v <= 90) || 'Latitude must be between -90 and 90'
]

const longitudeRules = [
  v => v !== null && v !== '' || 'Longitude is required',
  v => (v >= -180 && v <= 180) || 'Longitude must be between -180 and 180'
]

const radiusRules = [
  v => v !== null && v !== '' || 'Radius is required',
  v => (v >= 100 && v <= 50000) || 'Radius must be between 100m and 50km'
]

const colorRules = [
  v => !v || /^#[0-9A-Fa-f]{6}$/.test(v) || 'Must be a valid hex color (e.g., #1976d2)'
]

// Table headers
const headers = [
  { title: 'Active', key: 'is_active', width: '80px' },
  { title: 'Name', key: 'name' },
  { title: 'Type', key: 'zone_type' },
  { title: 'Location', key: 'location' },
  { title: 'Radius', key: 'radius' },
  { title: 'Description', key: 'description' },
  { title: 'Actions', key: 'actions', sortable: false, width: '120px' }
]

// Computed
const totalZones = computed(() => zones.value.length)
const activeZones = computed(() => zones.value.filter(z => z.is_active).length)
const depotCount = computed(() => zones.value.filter(z => z.zone_type === 'depot').length)
const serviceCount = computed(() => zones.value.filter(z => z.zone_type === 'service_area').length)

const filteredZones = computed(() => {
  if (activeFilter.value === 'all') {
    return zones.value
  } else if (activeFilter.value === 'active') {
    return zones.value.filter(z => z.is_active)
  } else if (activeFilter.value === 'depot') {
    return zones.value.filter(z => z.zone_type === 'depot')
  } else if (activeFilter.value === 'service') {
    return zones.value.filter(z => z.zone_type === 'service_area')
  }
  return zones.value
})

// Methods
const setFilter = (filter) => {
  activeFilter.value = filter
}

const loadZones = async () => {
  loading.value = true
  try {
    // Fetch all zones by using a large page size
    const response = await locationsAPI.getLocationZones({ page_size: 100 })
    zones.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading zones:', error)
    showError('Failed to load zones')
  } finally {
    loading.value = false
  }
}

const toggleZoneActive = async (zone) => {
  const originalState = zone.is_active
  try {
    // Use updateLocationZone with partial update
    await locationsAPI.updateLocationZone(zone.id, {
      ...zone,
      is_active: zone.is_active
    })
    showSuccess(`Zone ${zone.is_active ? 'activated' : 'deactivated'}`)
  } catch (error) {
    console.error('Error updating zone:', error)
    // Revert on error
    zone.is_active = !zone.is_active
    showError('Failed to update zone status')
  }
}

const editZone = (zone) => {
  editingZone.value = zone
  zoneForm.value = {
    name: zone.name,
    zone_type: zone.zone_type,
    description: zone.description || '',
    center_lat: parseFloat(zone.center_lat),
    center_lng: parseFloat(zone.center_lng),
    radius: zone.radius,
    color: zone.color || '#1976d2',
    is_active: zone.is_active
  }
  showCreateDialog.value = true
}

const saveZone = async () => {
  // Validate form first
  const form = document.querySelector('.v-form')
  const isValid = form?.checkValidity()
  
  if (!isValid) {
    showError('Please fix the form errors before saving')
    return
  }
  
  saving.value = true
  try {
    if (editingZone.value) {
      // Update existing zone
      await locationsAPI.updateLocationZone(editingZone.value.id, zoneForm.value)
      showSuccess('Zone updated successfully')
    } else {
      // Create new zone
      await locationsAPI.createLocationZone(zoneForm.value)
      showSuccess('Zone created successfully')
    }
    await loadZones()
    cancelEdit()
  } catch (error) {
    console.error('Error saving zone:', error)
    showError(editingZone.value ? 'Failed to update zone' : 'Failed to create zone')
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => {
  showCreateDialog.value = false
  editingZone.value = null
  zoneForm.value = {
    name: '',
    zone_type: 'depot',
    description: '',
    center_lat: 42.8864,
    center_lng: -78.8784,
    radius: 5000,
    color: '#1976d2',
    is_active: true
  }
}

const confirmDelete = (zone) => {
  zoneToDelete.value = zone
  showDeleteDialog.value = true
}

const deleteZone = async () => {
  deleting.value = true
  try {
    await locationsAPI.deleteLocationZone(zoneToDelete.value.id)
    showSuccess('Zone deleted successfully')
    await loadZones()
    showDeleteDialog.value = false
    zoneToDelete.value = null
  } catch (error) {
    console.error('Error deleting zone:', error)
    showError('Failed to delete zone')
  } finally {
    deleting.value = false
  }
}

const getZoneTypeColor = (type) => {
  const colors = {
    depot: 'blue',
    service_area: 'orange',
    customer_site: 'green',
    restricted: 'red',
    maintenance: 'purple',
    other: 'grey'
  }
  return colors[type] || 'grey'
}

// Lifecycle
onMounted(() => {
  loadZones()
})
</script>

<style scoped>
.zone-management {
  padding: 20px;
}

.navigation-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-color: #1976d2;
}

.stat-card-active {
  background: #E3F2FD;
  border-color: #1976d2;
  box-shadow: 0 2px 4px rgba(25, 118, 210, 0.2);
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #1976d2;
}

.stat-label {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
}

.stat-card-active .stat-label {
  color: #1976d2;
  font-weight: 500;
}
</style>