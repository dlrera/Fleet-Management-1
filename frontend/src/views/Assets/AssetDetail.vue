<template>
  <v-container>
    <div v-if="assetsStore.isLoadingAsset" class="text-center pa-8">
      <v-progress-circular indeterminate size="64" />
      <p class="mt-4">Loading asset details...</p>
    </div>
    
    <div v-else-if="assetsStore.currentAsset">
      <!-- Breadcrumbs -->
      <v-breadcrumbs
        :items="breadcrumbs"
        class="pa-0 mb-4"
      />
      
      <!-- Asset Header -->
      <v-row class="mb-4">
        <v-col cols="12" md="8">
          <h1 class="text-h5 font-weight-medium mb-2">
            {{ assetsStore.currentAsset.asset_id }}
          </h1>
          <h2 class="text-subtitle-1 text-medium-emphasis mb-3">
            {{ assetsStore.currentAsset.year }} {{ assetsStore.currentAsset.make }} {{ assetsStore.currentAsset.model }}
          </h2>
          
          <div class="d-flex ga-3 mb-3">
            <span class="text-body-2">
              <strong>Type:</strong> {{ formatVehicleType(assetsStore.currentAsset.vehicle_type) }}
            </span>
            <span 
              class="text-body-2"
              :class="getStatusTextClass(assetsStore.currentAsset.status)"
            >
              <strong>Status:</strong> {{ formatStatus(assetsStore.currentAsset.status) }}
            </span>
          </div>
        </v-col>
        
        <v-col cols="12" md="4" class="text-md-right">
          <div class="d-flex flex-column ga-2">
            <v-btn
              variant="outlined"
              size="small"
              prepend-icon="mdi-pencil"
              :to="{ name: 'AssetEdit', params: { id: assetsStore.currentAsset.id } }"
            >
              Edit Asset
            </v-btn>
            
            <v-btn
              variant="outlined"
              size="small"
              prepend-icon="mdi-delete"
              @click="confirmDelete"
            >
              Delete Asset
            </v-btn>
          </div>
        </v-col>
      </v-row>
      
      <!-- Asset Details -->
      <v-row>
        <v-col cols="12" md="6">
          <v-card variant="outlined">
            <v-card-title class="text-subtitle-1 py-3">Vehicle Information</v-card-title>
            <v-card-text class="py-2">
              <v-list density="compact" lines="one">
                <v-list-item class="px-0">
                  <v-list-item-title class="text-caption text-medium-emphasis">VIN</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ assetsStore.currentAsset.vin || 'N/A' }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item class="px-0">
                  <v-list-item-title class="text-caption text-medium-emphasis">License Plate</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ assetsStore.currentAsset.license_plate || 'N/A' }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item class="px-0">
                  <v-list-item-title class="text-caption text-medium-emphasis">Department</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ assetsStore.currentAsset.department || 'N/A' }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item class="px-0">
                  <v-list-item-title class="text-caption text-medium-emphasis">Current Odometer</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ formatOdometer(assetsStore.currentAsset.current_odometer) }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="6">
          <v-card variant="outlined">
            <v-card-title class="text-subtitle-1 py-3">Purchase Information</v-card-title>
            <v-card-text class="py-2">
              <v-list density="compact" lines="one">
                <v-list-item class="px-0">
                  <v-list-item-title class="text-caption text-medium-emphasis">Purchase Date</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ formatDate(assetsStore.currentAsset.purchase_date) }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item class="px-0">
                  <v-list-item-title class="text-caption text-medium-emphasis">Purchase Cost</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ formatCurrency(assetsStore.currentAsset.purchase_cost) }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item class="px-0">
                  <v-list-item-title class="text-caption text-medium-emphasis">Created</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ formatDateTime(assetsStore.currentAsset.created_at) }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item class="px-0">
                  <v-list-item-title class="text-caption text-medium-emphasis">Last Updated</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ formatDateTime(assetsStore.currentAsset.updated_at) }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- Documents Section -->
      <v-row class="mt-6">
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-file-document-multiple</v-icon>
              Documents
              <v-spacer />
              <v-btn
                color="primary"
                variant="outlined"
                size="small"
                prepend-icon="mdi-plus"
                @click="showUploadDialog = true"
              >
                Upload Document
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <div v-if="assetsStore.isLoadingDocuments" class="text-center pa-4">
                <v-progress-circular indeterminate size="32" />
                Loading documents...
              </div>
              
              <div v-else-if="assetsStore.hasDocuments">
                <v-list>
                  <v-list-item
                    v-for="document in assetsStore.assetDocuments"
                    :key="document.id"
                  >
                    <template #prepend>
                      <v-icon>{{ getDocumentIcon(document.document_type) }}</v-icon>
                    </template>
                    
                    <v-list-item-title>{{ document.title }}</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ formatDocumentType(document.document_type) }} • 
                      {{ formatDateTime(document.uploaded_at) }}
                    </v-list-item-subtitle>
                    
                    <template #append>
                      <v-btn
                        icon="mdi-download"
                        variant="text"
                        size="small"
                        @click="downloadDocument(document)"
                      />
                    </template>
                  </v-list-item>
                </v-list>
              </div>
              
              <div v-else class="text-center pa-8">
                <v-icon size="48" color="grey-lighten-1">mdi-file-document-off</v-icon>
                <p class="text-body-2 text-medium-emphasis mt-2">No documents uploaded</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- Notes Section -->
      <v-row v-if="assetsStore.currentAsset.notes" class="mt-6">
        <v-col cols="12">
          <v-card>
            <v-card-title>Notes</v-card-title>
            <v-card-text>
              <p>{{ assetsStore.currentAsset.notes }}</p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
    
    <div v-else class="text-center pa-8">
      <v-icon size="64" color="error">mdi-alert-circle</v-icon>
      <h3 class="text-h6 mt-4 mb-2">Asset Not Found</h3>
      <p class="text-body-2 text-medium-emphasis mb-4">
        The requested asset could not be found.
      </p>
      <v-btn color="primary" :to="{ name: 'AssetsList' }">
        Back to Assets
      </v-btn>
    </div>
    
    <!-- Upload Dialog Placeholder -->
    <v-dialog v-model="showUploadDialog" max-width="500">
      <v-card>
        <v-card-title>Upload Document</v-card-title>
        <v-card-text>
          <p>Document upload functionality coming soon...</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showUploadDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
          Confirm Deletion
        </v-card-title>
        
        <v-card-text>
          <p>Are you sure you want to delete asset <strong>{{ assetsStore.currentAsset?.asset_id }}</strong>?</p>
          <p class="text-caption text-error">This action cannot be undone.</p>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">Cancel</v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="assetsStore.isDeleting"
            @click="deleteAsset"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'

const route = useRoute()
const router = useRouter()
const assetsStore = useAssetsStore()

const showUploadDialog = ref(false)
const deleteDialog = ref(false)

const breadcrumbs = computed(() => [
  { title: 'Assets', to: { name: 'AssetsList' } },
  { title: assetsStore.currentAsset?.asset_id || 'Asset Detail', disabled: true }
])

// Utility functions
const getVehicleTypeColor = (type) => {
  const colors = {
    bus: 'blue',
    truck: 'green',
    tractor: 'orange',
    trailer: 'purple',
    van: 'cyan',
    car: 'indigo',
    equipment: 'brown',
    other: 'grey'
  }
  return colors[type] || 'grey'
}

const getVehicleTypeIcon = (type) => {
  const icons = {
    bus: 'mdi-bus',
    truck: 'mdi-truck',
    tractor: 'mdi-tractor',
    trailer: 'mdi-truck-trailer',
    van: 'mdi-van-passenger',
    car: 'mdi-car',
    equipment: 'mdi-excavator',
    other: 'mdi-help-circle'
  }
  return icons[type] || 'mdi-help-circle'
}

const getStatusColor = (status) => {
  const colors = {
    active: 'success',
    maintenance: 'warning',
    retired: 'error',
    out_of_service: 'grey'
  }
  return colors[status] || 'grey'
}

const getStatusTextClass = (status) => {
  const classes = {
    active: 'text-success',
    maintenance: 'text-warning',
    retired: 'text-error',
    out_of_service: 'text-medium-emphasis'
  }
  return classes[status] || 'text-medium-emphasis'
}

const getStatusIcon = (status) => {
  const icons = {
    active: 'mdi-check-circle',
    maintenance: 'mdi-wrench',
    retired: 'mdi-archive',
    out_of_service: 'mdi-close-circle'
  }
  return icons[status] || 'mdi-help-circle'
}

const getDocumentIcon = (type) => {
  const icons = {
    registration: 'mdi-card-account-details',
    insurance: 'mdi-shield-check',
    manual: 'mdi-book-open',
    maintenance: 'mdi-wrench',
    inspection: 'mdi-clipboard-check',
    photo: 'mdi-camera',
    other: 'mdi-file-document'
  }
  return icons[type] || 'mdi-file-document'
}

const formatVehicleType = (type) => {
  return type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')
}

const formatStatus = (status) => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatDocumentType = (type) => {
  return type.charAt(0).toUpperCase() + type.slice(1)
}

const formatOdometer = (odometer) => {
  if (!odometer) return '0'
  return new Intl.NumberFormat().format(odometer)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const formatCurrency = (amount) => {
  if (!amount) return 'N/A'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const confirmDelete = () => {
  deleteDialog.value = true
}

const deleteAsset = async () => {
  if (!assetsStore.currentAsset) return
  
  try {
    await assetsStore.deleteAsset(assetsStore.currentAsset.id)
    router.push({ name: 'AssetsList' })
  } catch (error) {
    console.error('Failed to delete asset:', error)
  } finally {
    deleteDialog.value = false
  }
}

const downloadDocument = (document) => {
  // Open document in new tab
  window.open(document.file, '_blank')
}

onMounted(async () => {
  const assetId = route.params.id
  if (assetId) {
    try {
      await Promise.all([
        assetsStore.fetchAsset(assetId),
        assetsStore.fetchAssetDocuments(assetId)
      ])
    } catch (error) {
      console.error('Failed to load asset:', error)
    }
  }
})
</script>