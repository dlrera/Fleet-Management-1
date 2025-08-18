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
      
      <!-- Image Section -->
      <v-row class="mt-6">
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-image</v-icon>
              Asset Image
              <v-spacer />
              <v-btn
                color="primary"
                variant="outlined"
                size="small"
                prepend-icon="mdi-camera-plus"
                @click="showImageUploadDialog = true"
              >
                Upload Image
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <div v-if="assetsStore.currentAsset?.image" class="text-center">
                <v-img
                  :src="assetsStore.currentAsset.image"
                  :alt="`${assetsStore.currentAsset.asset_id} image`"
                  class="asset-main-image mx-auto"
                  cover
                />
                <p class="text-caption text-medium-emphasis mt-2">
                  Click image to view full size
                </p>
              </div>
              <div v-else class="text-center py-8">
                <v-icon size="48" color="grey-lighten-1">mdi-image-off</v-icon>
                <p class="text-body-2 text-medium-emphasis mt-2">No image uploaded</p>
                <v-btn
                  color="primary"
                  variant="text"
                  prepend-icon="mdi-camera-plus"
                  @click="showImageUploadDialog = true"
                >
                  Upload Image
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- Driver Assignments Section -->
      <v-row class="mt-6">
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-account-group</v-icon>
              Assigned Drivers
              <v-spacer />
              <v-chip size="small" variant="outlined" class="mr-2">
                {{ driverAssignments.length }} driver{{ driverAssignments.length !== 1 ? 's' : '' }}
              </v-chip>
              <div class="d-flex gap-2">
                <v-btn
                  v-if="selectedDriverAssignments.length > 0"
                  size="small"
                  variant="outlined"
                  color="error"
                  prepend-icon="mdi-account-minus"
                  @click="confirmUnassignDrivers"
                >
                  Unassign {{ selectedDriverAssignments.length }} Driver{{ selectedDriverAssignments.length !== 1 ? 's' : '' }}
                </v-btn>
                <v-btn
                  size="small"
                  variant="flat"
                  color="primary"
                  prepend-icon="mdi-account-plus"
                  @click="openAssignDriverDialog"
                >
                  Assign Driver
                </v-btn>
              </div>
            </v-card-title>
            
            <v-card-text>
              <div v-if="isLoadingAssignments" class="text-center pa-4">
                <v-progress-circular indeterminate size="32" />
                Loading driver assignments...
              </div>
              
              <div v-else-if="driverAssignments.length === 0" class="text-center py-8">
                <v-alert
                  type="warning"
                  variant="tonal"
                  class="mb-4"
                  icon="mdi-alert"
                >
                  <div class="text-subtitle-2 mb-2">⚠️ No Drivers Assigned</div>
                  <div class="text-body-2">
                    This asset currently has no assigned drivers. For operational safety and accountability, 
                    consider assigning at least one qualified driver to this asset.
                  </div>
                </v-alert>
                <v-icon size="48" color="grey-lighten-1">mdi-account-off</v-icon>
                <p class="text-body-2 text-medium-emphasis mt-2">No drivers assigned to this asset</p>
              </div>
              
              <div v-else>
                <v-list lines="three">
                  <v-list-item
                    v-for="assignment in driverAssignments"
                    :key="assignment.id"
                    class="pa-3"
                  >
                    <template v-slot:prepend>
                      <div class="d-flex align-center gap-3">
                        <v-checkbox
                          v-model="selectedDriverAssignments"
                          :value="assignment.id"
                          hide-details
                          @click.stop
                        />
                        <v-avatar size="40" class="cursor-pointer" @click="viewDriver(assignment.driver)">
                          <v-img
                            v-if="assignment.driver.profile_photo"
                            :src="assignment.driver.profile_photo"
                            :alt="assignment.driver.full_name"
                          />
                          <v-icon v-else color="grey-lighten-1">mdi-account</v-icon>
                        </v-avatar>
                      </div>
                    </template>
                    
                    <div class="cursor-pointer" @click="viewDriver(assignment.driver)">
                      <v-list-item-title class="font-weight-medium">
                        {{ assignment.driver.full_name }}
                      </v-list-item-title>
                      
                      <v-list-item-subtitle>
                        {{ assignment.driver.driver_id }} • {{ assignment.driver.department || 'No department' }}
                      </v-list-item-subtitle>
                    </div>
                    
                    <template v-slot:append>
                      <div class="text-right">
                        <v-chip
                          :color="getAssignmentTypeColor(assignment.assignment_type)"
                          size="small"
                          variant="flat"
                          class="mb-1"
                        >
                          {{ formatAssignmentType(assignment.assignment_type) }}
                        </v-chip>
                        
                        <!-- Safety Warnings -->
                        <div v-if="getDriverSafetyWarnings(assignment.driver, assetsStore.currentAsset).length > 0" class="mt-1">
                          <v-chip
                            v-for="warning in getDriverSafetyWarnings(assignment.driver, assetsStore.currentAsset)"
                            :key="warning.title"
                            :color="warning.type === 'error' ? 'error' : 'warning'"
                            size="x-small"
                            variant="flat"
                            class="mr-1 mb-1"
                            :title="warning.message"
                          >
                            <v-icon start size="x-small">
                              {{ warning.type === 'error' ? 'mdi-alert-circle' : 'mdi-alert' }}
                            </v-icon>
                            {{ warning.title }}
                          </v-chip>
                        </div>
                        
                        <div class="text-caption text-medium-emphasis">
                          Since {{ formatDate(assignment.assigned_date) }}
                        </div>
                      </div>
                    </template>
                  </v-list-item>
                </v-list>
              </div>
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
      
      <!-- Location History Section -->
      <v-row class="mt-6">
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-map-marker-path</v-icon>
              Location History
              <v-spacer />
              <div class="d-flex gap-2">
                <v-btn
                  color="primary"
                  variant="flat"
                  size="small"
                  prepend-icon="mdi-map-marker-path"
                  :disabled="!locationHistory || locationHistory.length === 0"
                  @click="showPathTracing = true"
                >
                  Trace Path
                </v-btn>
                
                <v-btn
                  color="primary"
                  variant="outlined"
                  size="small"
                  prepend-icon="mdi-refresh"
                  :loading="locationsStore.isLoadingAsset"
                  @click="fetchLocationHistory"
                >
                  Refresh
                </v-btn>
              </div>
            </v-card-title>
            
            <v-card-text>
              <div v-if="locationsStore.isLoadingAsset" class="text-center pa-4">
                <v-progress-circular indeterminate size="32" />
                Loading location history...
              </div>
              
              <div v-else-if="locationHistory && locationHistory.length > 0">
                <!-- Filter Controls -->
                <div class="d-flex gap-4 mb-4">
                  <v-select
                    v-model="historyDays"
                    :items="historyDayOptions"
                    label="Time Period"
                    density="compact"
                    variant="outlined"
                    style="max-width: 200px"
                    @update:model-value="fetchLocationHistory"
                  />
                  
                  <v-select
                    v-model="historyLimit"
                    :items="historyLimitOptions"
                    label="Max Results"
                    density="compact"
                    variant="outlined"
                    style="max-width: 150px"
                    @update:model-value="fetchLocationHistory"
                  />
                </div>

                <!-- Location History Table -->
                <v-data-table
                  :headers="locationHeaders"
                  :items="locationHistory"
                  :items-per-page="10"
                  class="elevation-0"
                >
                  <template #item.timestamp="{ item }">
                    {{ formatDateTime(item.timestamp) }}
                  </template>
                  
                  <template #item.coordinates="{ item }">
                    <code class="text-caption">
                      {{ parseFloat(item.latitude).toFixed(6) }}, {{ parseFloat(item.longitude).toFixed(6) }}
                    </code>
                  </template>
                  
                  <template #item.source="{ item }">
                    <v-chip
                      :color="getSourceColor(item.source)"
                      size="small"
                      variant="flat"
                    >
                      {{ formatSource(item.source) }}
                    </v-chip>
                  </template>
                  
                  <template #item.speed="{ item }">
                    <span v-if="item.speed">{{ item.speed }} km/h</span>
                    <span v-else class="text-medium-emphasis">-</span>
                  </template>
                  
                  <template #item.address="{ item }">
                    <span v-if="item.address">{{ item.address }}</span>
                    <span v-else class="text-medium-emphasis">-</span>
                  </template>
                  
                  <template #item.actions="{ item }">
                    <v-btn
                      icon="mdi-map"
                      variant="text"
                      size="small"
                      @click="viewOnMap(item)"
                      title="View on Map"
                    />
                  </template>
                </v-data-table>
              </div>
              
              <div v-else class="text-center pa-8">
                <v-icon size="48" color="grey-lighten-1">mdi-map-marker-off</v-icon>
                <p class="text-body-2 text-medium-emphasis mt-2">No location history available</p>
                <p class="text-caption text-medium-emphasis mb-4">
                  Location updates will appear here once the asset starts reporting its position
                </p>
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
    
    <!-- Upload Dialog -->
    <v-dialog v-model="showUploadDialog" max-width="600">
      <v-card>
        <v-card-title>Upload Document</v-card-title>
        <v-card-text>
          <v-form ref="uploadForm" @submit.prevent="uploadDocument">
            <!-- Document Type Selection -->
            <v-select
              v-model="uploadData.document_type"
              :items="documentTypes"
              item-value="value"
              item-title="text"
              label="Document Type"
              required
              class="mb-4"
            />
            
            <!-- Title Input -->
            <v-text-field
              v-model="uploadData.title"
              label="Document Title"
              required
              class="mb-4"
            />
            
            <!-- Description Input -->
            <v-textarea
              v-model="uploadData.description"
              label="Description (Optional)"
              rows="2"
              class="mb-4"
            />
            
            <!-- File Upload Area -->
            <div
              class="upload-zone pa-6 text-center rounded"
              :class="{ 'upload-zone--active': isDragging }"
              @drop.prevent="handleDrop"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
            >
              <v-icon size="48" class="mb-2" color="grey">
                {{ selectedFile ? 'mdi-file-check' : 'mdi-cloud-upload' }}
              </v-icon>
              
              <p v-if="!selectedFile" class="text-body-2 mb-2">
                Drag and drop file here or click to browse
              </p>
              
              <p v-else class="text-body-2 mb-2 font-weight-medium">
                {{ selectedFile.name }}
                <v-chip size="small" class="ml-2">
                  {{ formatFileSize(selectedFile.size) }}
                </v-chip>
              </p>
              
              <input
                ref="fileInput"
                type="file"
                hidden
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx"
                @change="handleFileSelect"
              />
              
              <v-btn
                v-if="!selectedFile"
                size="small"
                variant="outlined"
                @click="$refs.fileInput.click()"
              >
                Choose File
              </v-btn>
              
              <v-btn
                v-else
                size="small"
                variant="text"
                color="error"
                @click="clearFile"
              >
                Remove File
              </v-btn>
            </div>
            
            <p class="text-caption text-medium-emphasis mt-2">
              Accepted formats: PDF, JPG, PNG, DOC, DOCX, XLS, XLSX (Max 10MB)
            </p>
            
            <!-- Upload Error -->
            <v-alert
              v-if="uploadError"
              type="error"
              class="mt-4"
              closable
              @click:close="uploadError = ''"
            >
              {{ uploadError }}
            </v-alert>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeUploadDialog">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isUploading"
            :disabled="!canUpload"
            @click="uploadDocument"
          >
            Upload
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Image Upload Dialog -->
    <v-dialog v-model="showImageUploadDialog" max-width="600">
      <v-card>
        <v-card-title>Upload Asset Image</v-card-title>
        <v-card-text>
          <v-form ref="imageUploadForm" @submit.prevent="uploadImage">
            <v-alert
              type="info"
              variant="tonal"
              class="mb-4"
            >
              <div class="text-body-2">
                Upload a high-quality image of the asset. Images will be automatically resized to 800x600px and a thumbnail will be generated.
                <br><strong>Accepted formats:</strong> JPEG, PNG, WebP (Max 5MB)
              </div>
            </v-alert>
            
            <!-- Image Upload Area -->
            <div
              class="image-upload-zone pa-6 text-center rounded"
              :class="{ 'image-upload-zone--active': isImageDragging }"
              @drop.prevent="handleImageDrop"
              @dragover.prevent="isImageDragging = true"
              @dragleave.prevent="isImageDragging = false"
            >
              <v-icon size="48" class="mb-2" color="grey">
                {{ selectedImageFile ? 'mdi-file-image' : 'mdi-camera-plus' }}
              </v-icon>
              
              <p v-if="!selectedImageFile" class="text-body-2 mb-2">
                Drag and drop image here or click to browse
              </p>
              
              <div v-else class="mb-2">
                <p class="text-body-2 font-weight-medium">
                  {{ selectedImageFile.name }}
                  <v-chip size="small" class="ml-2">
                    {{ formatFileSize(selectedImageFile.size) }}
                  </v-chip>
                </p>
                
                <!-- Image Preview -->
                <div v-if="imagePreviewUrl" class="mt-3">
                  <v-img
                    :src="imagePreviewUrl"
                    class="image-preview mx-auto"
                    cover
                  />
                </div>
              </div>
              
              <input
                ref="imageFileInput"
                type="file"
                hidden
                accept="image/jpeg,image/jpg,image/png,image/webp"
                @change="handleImageFileSelect"
              />
              
              <v-btn
                v-if="!selectedImageFile"
                size="small"
                variant="outlined"
                @click="$refs.imageFileInput.click()"
              >
                Choose Image
              </v-btn>
              
              <v-btn
                v-else
                size="small"
                variant="text"
                color="error"
                @click="clearImageFile"
              >
                Remove Image
              </v-btn>
            </div>
            
            <p class="text-caption text-medium-emphasis mt-2">
              Recommended aspect ratio: 4:3 (e.g., 800x600px)
            </p>
            
            <!-- Upload Error -->
            <v-alert
              v-if="imageUploadError"
              type="error"
              class="mt-4"
              closable
              @click:close="imageUploadError = ''"
            >
              {{ imageUploadError }}
            </v-alert>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeImageUploadDialog">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isUploadingImage"
            :disabled="!selectedImageFile"
            @click="uploadImage"
          >
            Upload
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Location Path Tracing Modal -->
    <LocationPathModal
      v-model="showPathTracing"
      :asset="assetsStore.currentAsset"
      :initial-days="historyDays"
      :initial-limit="historyLimit"
      @add-location="() => router.push('/locations')"
    />
    
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

    <!-- Assign Driver Dialog -->
    <v-dialog v-model="showAssignDriverDialog" max-width="600">
      <v-card>
        <v-card-title class="text-h6">Assign Driver to Asset</v-card-title>
        <v-card-text>
          <v-alert
            type="info"
            variant="tonal"
            class="mb-4"
          >
            <div class="text-body-2">
              Only drivers with <strong>active employment</strong>, <strong>valid licenses</strong>, and <strong>current certifications</strong> are shown for safety and compliance.
            </div>
          </v-alert>
          <v-form ref="assignmentForm" v-model="isAssignmentFormValid">
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="selectedDriver"
                  :items="availableDrivers"
                  :loading="loadingDrivers"
                  item-title="full_name"
                  item-value="id"
                  label="Select Driver *"
                  variant="outlined"
                  :rules="[rules.required]"
                  required
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props">
                      <template v-slot:prepend>
                        <v-avatar size="32" class="mr-2">
                          <v-img
                            v-if="item.raw.profile_photo"
                            :src="item.raw.profile_photo"
                            :alt="item.raw.full_name"
                          />
                          <v-icon v-else size="16" color="grey-lighten-1">mdi-account</v-icon>
                        </v-avatar>
                      </template>
                      <v-list-item-title>
                        {{ item.raw.full_name }}
                        <v-chip
                          v-if="item.raw.license_expires_soon"
                          size="x-small"
                          color="warning"
                          variant="flat"
                          class="ml-2"
                        >
                          License Expiring
                        </v-chip>
                        <v-chip
                          v-if="item.raw.employment_status !== 'active'"
                          size="x-small"
                          color="error"
                          variant="flat"
                          class="ml-2"
                        >
                          {{ item.raw.employment_status_display }}
                        </v-chip>
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        {{ item.raw.driver_id }} • {{ item.raw.license_type_display }}
                        <span v-if="item.raw.license_expiration">
                          • Expires: {{ new Date(item.raw.license_expiration).toLocaleDateString() }}
                        </span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </template>
                </v-select>
              </v-col>

              <!-- Safety Warnings for Selected Driver -->
              <v-col cols="12" v-if="selectedDriver && availableDrivers.find(d => d.id === selectedDriver)">
                <div v-if="getDriverSafetyWarnings(availableDrivers.find(d => d.id === selectedDriver), assetsStore.currentAsset).length > 0">
                  <v-alert
                    type="warning"
                    variant="tonal"
                    class="mb-2"
                    icon="mdi-alert"
                  >
                    <div class="text-subtitle-2 mb-2">⚠️ Safety Warnings</div>
                    <div 
                      v-for="warning in getDriverSafetyWarnings(availableDrivers.find(d => d.id === selectedDriver), assetsStore.currentAsset)"
                      :key="warning.title"
                      class="text-body-2 mb-1"
                    >
                      <strong>{{ warning.title }}:</strong> {{ warning.message }}
                    </div>
                    <div class="text-body-2 mt-2">
                      <strong>Consider addressing these issues before proceeding with the assignment.</strong>
                    </div>
                  </v-alert>
                </div>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="assignmentType"
                  :items="assignmentTypeOptions"
                  label="Assignment Type *"
                  variant="outlined"
                  :rules="[rules.required]"
                  required
                />
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="assignedBy"
                  label="Assigned By *"
                  variant="outlined"
                  :rules="[rules.required]"
                  required
                  placeholder="Fleet Manager"
                />
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="assignmentNotes"
                  label="Notes"
                  variant="outlined"
                  rows="3"
                  placeholder="Additional notes about this assignment..."
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeAssignDriverDialog">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isAssigningDriver"
            :disabled="!isAssignmentFormValid"
            @click="assignDriver"
          >
            Assign Driver
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Unassign Drivers Confirmation Dialog -->
    <v-dialog v-model="showUnassignDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon class="mr-2" color="warning">mdi-alert</v-icon>
          Confirm Driver Unassignment
        </v-card-title>
        
        <v-card-text>
          <p class="text-body-1 mb-4">
            Are you sure you want to unassign <strong>{{ selectedDriverAssignments.length }}</strong> 
            driver{{ selectedDriverAssignments.length !== 1 ? 's' : '' }} from this asset?
          </p>
          
          <v-alert type="info" variant="tonal" class="mb-4">
            This action will mark the assignment{{ selectedDriverAssignments.length !== 1 ? 's' : '' }} as completed 
            and set the unassigned date to now. This action cannot be undone.
          </v-alert>
          
          <div v-if="selectedDriverAssignments.length > 0">
            <p class="text-subtitle-2 mb-2">Drivers to be unassigned:</p>
            <v-list dense>
              <v-list-item
                v-for="assignment in driverAssignments.filter(a => selectedDriverAssignments.includes(a.id))"
                :key="assignment.id"
                class="pl-4"
              >
                <v-list-item-title class="text-body-2">
                  {{ assignment.driver.full_name }} ({{ assignment.driver.driver_id }})
                  - {{ assignment.assignment_type_display }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeUnassignDialog">Cancel</v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="isUnassigningDrivers"
            @click="unassignSelectedDrivers"
          >
            Unassign Driver{{ selectedDriverAssignments.length !== 1 ? 's' : '' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'
import { useLocationsStore } from '@/stores/locations'
import { useDriversStore } from '@/stores/drivers'
import LocationPathModal from '@/components/Locations/LocationPathModal.vue'

const route = useRoute()
const router = useRouter()
const assetsStore = useAssetsStore()
const locationsStore = useLocationsStore()
const driversStore = useDriversStore()

const showUploadDialog = ref(false)
const showImageUploadDialog = ref(false)
const deleteDialog = ref(false)

// Driver assignments state
const driverAssignments = ref([])
const isLoadingAssignments = ref(false)

// Driver unassign state
const selectedDriverAssignments = ref([])
const showUnassignDialog = ref(false)
const isUnassigningDrivers = ref(false)

// Assignment dialog state
const showAssignDriverDialog = ref(false)
const assignmentForm = ref(null)
const isAssignmentFormValid = ref(false)
const selectedDriver = ref(null)
const assignmentType = ref('primary')
const assignedBy = ref('Fleet Manager')
const assignmentNotes = ref('')
const availableDrivers = ref([])
const loadingDrivers = ref(false)
const isAssigningDriver = ref(false)

// Form validation rules
const rules = {
  required: value => !!value || 'Field is required'
}

// Assignment type options
const assignmentTypeOptions = [
  { title: 'Primary Driver', value: 'primary' },
  { title: 'Secondary Driver', value: 'secondary' },
  { title: 'Temporary Assignment', value: 'temporary' },
  { title: 'Backup Driver', value: 'backup' },
  { title: 'Shared Assignment', value: 'shared' }
]

// Location history state
const locationHistory = ref([])
const historyDays = ref(7)
const historyLimit = ref(100)
const showPathTracing = ref(false)

// Location history options
const historyDayOptions = [
  { title: 'Last 24 hours', value: 1 },
  { title: 'Last 3 days', value: 3 },
  { title: 'Last week', value: 7 },
  { title: 'Last 2 weeks', value: 14 },
  { title: 'Last month', value: 30 }
]

const historyLimitOptions = [
  { title: '50 results', value: 50 },
  { title: '100 results', value: 100 },
  { title: '200 results', value: 200 },
  { title: '500 results', value: 500 }
]

// Location history table headers
const locationHeaders = [
  { title: 'Date & Time', key: 'timestamp', sortable: true },
  { title: 'Coordinates', key: 'coordinates', sortable: false },
  { title: 'Source', key: 'source', sortable: true },
  { title: 'Speed', key: 'speed', sortable: true },
  { title: 'Address', key: 'address', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false }
]

// File upload state
const fileInput = ref(null)
const uploadForm = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)
const isUploading = ref(false)
const uploadError = ref('')
const uploadData = ref({
  document_type: '',
  title: '',
  description: ''
})

// Image upload state
const imageFileInput = ref(null)
const imageUploadForm = ref(null)
const selectedImageFile = ref(null)
const isImageDragging = ref(false)
const isUploadingImage = ref(false)
const imageUploadError = ref('')
const imagePreviewUrl = ref('')

const documentTypes = [
  { value: 'registration', text: 'Registration' },
  { value: 'insurance', text: 'Insurance' },
  { value: 'manual', text: 'Manual' },
  { value: 'maintenance', text: 'Maintenance Record' },
  { value: 'inspection', text: 'Inspection Report' },
  { value: 'photo', text: 'Photo' },
  { value: 'other', text: 'Other' }
]

const canUpload = computed(() => {
  return selectedFile.value && uploadData.value.document_type && uploadData.value.title
})

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

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Location history functions
const fetchLocationHistory = async () => {
  if (!assetsStore.currentAsset?.asset_id) return
  
  try {
    const response = await locationsStore.fetchAssetLocationHistory(
      assetsStore.currentAsset.asset_id,
      {
        days: historyDays.value,
        limit: historyLimit.value
      }
    )
    locationHistory.value = response.locations || []
  } catch (error) {
    console.error('Failed to fetch location history:', error)
    locationHistory.value = []
  }
}

const formatSource = (source) => {
  const sourceMap = {
    manual: 'Manual',
    gps_device: 'GPS',
    mobile_app: 'Mobile',
    telematics: 'Telematics'
  }
  return sourceMap[source] || source
}

const getSourceColor = (source) => {
  const colorMap = {
    manual: 'blue',
    gps_device: 'green',
    mobile_app: 'orange',
    telematics: 'purple'
  }
  return colorMap[source] || 'grey'
}

const viewOnMap = (locationItem) => {
  // Navigate to map with location centered
  router.push({
    name: 'LocationMap',
    query: {
      lat: locationItem.latitude,
      lng: locationItem.longitude,
      asset: assetsStore.currentAsset.asset_id
    }
  })
}

// Driver assignment functions
const fetchDriverAssignments = async () => {
  if (!assetsStore.currentAsset?.id) return
  
  isLoadingAssignments.value = true
  try {
    // Driver assignments are included in the asset data from the API
    driverAssignments.value = assetsStore.currentAsset.driver_assignments || []
  } catch (error) {
    console.error('Failed to fetch driver assignments:', error)
    driverAssignments.value = []
  } finally {
    isLoadingAssignments.value = false
  }
}

const viewDriver = (driver) => {
  router.push(`/drivers/${driver.id}`)
}

const getAssignmentTypeColor = (type) => {
  const colors = {
    primary: 'primary',
    secondary: 'secondary', 
    temporary: 'warning',
    backup: 'info',
    shared: 'success'
  }
  return colors[type] || 'default'
}

const formatAssignmentType = (type) => {
  const types = {
    primary: 'Primary',
    secondary: 'Secondary',
    temporary: 'Temporary',
    backup: 'Backup',
    shared: 'Shared'
  }
  return types[type] || type
}

// Safety validation functions
const getDriverSafetyWarnings = (driver, asset) => {
  const warnings = []
  
  if (!driver || !asset) return warnings
  
  // License type compatibility warnings
  const vehicleRequirements = getVehicleLicenseRequirements(asset.vehicle_type)
  if (vehicleRequirements.length > 0 && !vehicleRequirements.includes(driver.license_type)) {
    warnings.push({
      type: 'error',
      title: 'License Incompatible',
      message: `Driver has ${driver.license_type_display} but this ${asset.vehicle_type} requires ${vehicleRequirements.map(r => getLicenseTypeDisplay(r)).join(' or ')}`
    })
  }
  
  // License expiration warnings
  if (driver.license_is_expired) {
    warnings.push({
      type: 'error',
      title: 'Expired License',
      message: `Driver's license expired on ${formatDate(driver.license_expiration)}`
    })
  } else if (driver.license_expires_soon) {
    warnings.push({
      type: 'warning',
      title: 'License Expires Soon',
      message: `License expires on ${formatDate(driver.license_expiration)}`
    })
  }
  
  // Employment status warnings
  if (driver.employment_status !== 'active') {
    warnings.push({
      type: 'error',
      title: 'Inactive Employee',
      message: `Driver status: ${driver.employment_status_display}`
    })
  }
  
  return warnings
}

const getVehicleLicenseRequirements = (vehicleType) => {
  const requirements = {
    'bus': ['class_a', 'class_b'],
    'truck': ['class_a', 'class_b'], 
    'tractor': ['class_a'],
    'trailer': ['class_a'],
    'van': ['regular', 'chauffeur', 'class_c'],
    'car': ['regular', 'chauffeur', 'class_c'],
    'equipment': ['regular', 'class_c'],
    'other': ['regular']
  }
  return requirements[vehicleType] || ['regular']
}

const getLicenseTypeDisplay = (licenseType) => {
  const types = {
    'class_a': 'Class A CDL',
    'class_b': 'Class B CDL', 
    'class_c': 'Class C CDL',
    'chauffeur': 'Chauffeur License',
    'regular': 'Regular License',
    'motorcycle': 'Motorcycle License'
  }
  return types[licenseType] || licenseType
}

// File upload handlers
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const validateAndSetFile = (file) => {
  // Check file size (10MB max)
  if (file.size > 10485760) {
    uploadError.value = 'File size must be less than 10MB'
    return
  }
  
  // Check file type
  const allowedTypes = [
    'application/pdf',
    'image/jpeg',
    'image/jpg',
    'image/png',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]
  
  if (!allowedTypes.includes(file.type)) {
    uploadError.value = 'Invalid file type. Please upload PDF, JPG, PNG, DOC, DOCX, XLS, or XLSX files.'
    return
  }
  
  selectedFile.value = file
  uploadError.value = ''
  
  // Auto-fill title if empty
  if (!uploadData.value.title) {
    uploadData.value.title = file.name.replace(/\.[^/.]+$/, '')
  }
}

const clearFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const closeUploadDialog = () => {
  showUploadDialog.value = false
  selectedFile.value = null
  uploadData.value = {
    document_type: '',
    title: '',
    description: ''
  }
  uploadError.value = ''
  isDragging.value = false
}

const uploadDocument = async () => {
  if (!canUpload.value) return
  
  isUploading.value = true
  uploadError.value = ''
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('document_type', uploadData.value.document_type)
    formData.append('title', uploadData.value.title)
    formData.append('description', uploadData.value.description || '')
    
    await assetsStore.uploadDocument(route.params.id, formData)
    
    // Refresh documents list
    await assetsStore.fetchAssetDocuments(route.params.id)
    
    closeUploadDialog()
  } catch (error) {
    console.error('Upload failed:', error)
    uploadError.value = error.response?.data?.detail || 'Failed to upload document. Please try again.'
  } finally {
    isUploading.value = false
  }
}

// Image upload handlers
const handleImageFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndSetImageFile(file)
  }
}

const handleImageDrop = (event) => {
  isImageDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndSetImageFile(file)
  }
}

const validateAndSetImageFile = (file) => {
  // Check file type
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    imageUploadError.value = 'Invalid file type. Please upload JPEG, PNG, or WebP images.'
    return
  }
  
  // Check file size (5MB max)
  if (file.size > 5242880) {
    imageUploadError.value = 'Image size must be less than 5MB'
    return
  }
  
  selectedImageFile.value = file
  imageUploadError.value = ''
  
  // Create preview URL
  if (imagePreviewUrl.value) {
    URL.revokeObjectURL(imagePreviewUrl.value)
  }
  imagePreviewUrl.value = URL.createObjectURL(file)
}

const clearImageFile = () => {
  selectedImageFile.value = null
  if (imageFileInput.value) {
    imageFileInput.value.value = ''
  }
  if (imagePreviewUrl.value) {
    URL.revokeObjectURL(imagePreviewUrl.value)
    imagePreviewUrl.value = ''
  }
}

const closeImageUploadDialog = () => {
  showImageUploadDialog.value = false
  clearImageFile()
  imageUploadError.value = ''
  isImageDragging.value = false
}

const uploadImage = async () => {
  if (!selectedImageFile.value) return
  
  isUploadingImage.value = true
  imageUploadError.value = ''
  
  try {
    const formData = new FormData()
    formData.append('image', selectedImageFile.value)
    
    await assetsStore.uploadImage(route.params.id, formData)
    
    closeImageUploadDialog()
  } catch (error) {
    console.error('Image upload failed:', error)
    imageUploadError.value = error.response?.data?.error || 'Failed to upload image. Please try again.'
  } finally {
    isUploadingImage.value = false
  }
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

// Driver assignment methods
const loadAvailableDrivers = async () => {
  if (loadingDrivers.value) return
  
  loadingDrivers.value = true
  try {
    // Import drivers store
    const { useDriversStore } = await import('@/stores/drivers')
    const driversStore = useDriversStore()
    
    // Fetch all drivers (we'll filter them ourselves for safety)
    await driversStore.fetchDrivers({ 
      per_page: 100 
    })
    
    // Filter out drivers already assigned to this asset
    const assignedDriverIds = new Set(driverAssignments.value.map(a => a.driver.id))
    
    // Filter for eligible drivers only
    availableDrivers.value = driversStore.drivers.filter(driver => {
      // Must not already be assigned to this asset
      if (assignedDriverIds.has(driver.id)) {
        return false
      }
      
      // Must have active employment status
      if (driver.employment_status !== 'active') {
        return false
      }
      
      // Must have valid, non-expired license
      if (driver.license_is_expired) {
        return false
      }
      
      // Allow drivers with licenses expiring soon, but they'll show a warning in the UI
      // This is more user-friendly than excluding them entirely
      // The warning is shown in the v-select item template (lines 771-778)
      
      // Must have required license information
      if (!driver.license_number || !driver.license_type) {
        return false
      }
      
      return true
    })
    
    // Driver filtering complete
  } catch (error) {
    console.error('Failed to load available drivers:', error)
    availableDrivers.value = []
  } finally {
    loadingDrivers.value = false
  }
}

const assignDriver = async () => {
  if (!selectedDriver.value || !assetsStore.currentAsset) return
  
  isAssigningDriver.value = true
  try {
    // Import drivers store
    const { useDriversStore } = await import('@/stores/drivers')
    const driversStore = useDriversStore()
    
    // Create assignment payload
    const assignmentData = {
      driver: selectedDriver.value,
      asset: assetsStore.currentAsset.id,
      assignment_type: assignmentType.value,
      assigned_by: assignedBy.value,
      assigned_date: new Date().toISOString(),
      notes: assignmentNotes.value || ''
    }
    
    // Submit assignment through drivers store
    await driversStore.createDriverAssetAssignment(assignmentData)
    
    // Refresh asset data to get updated driver assignments
    await assetsStore.fetchAsset(assetsStore.currentAsset.id)
    await fetchDriverAssignments()
    
    // Close dialog and reset form
    closeAssignDriverDialog()
  } catch (error) {
    console.error('Failed to assign driver:', error)
    // TODO: Show error message to user
  } finally {
    isAssigningDriver.value = false
  }
}

const openAssignDriverDialog = () => {
  showAssignDriverDialog.value = true
}

const closeAssignDriverDialog = () => {
  showAssignDriverDialog.value = false
  selectedDriver.value = null
  assignmentType.value = 'primary'
  assignmentNotes.value = ''
  availableDrivers.value = []
  
  // Reset form validation
  if (assignmentForm.value) {
    assignmentForm.value.reset()
  }
}

// Driver unassign functions
const confirmUnassignDrivers = () => {
  showUnassignDialog.value = true
}

const unassignSelectedDrivers = async () => {
  if (selectedDriverAssignments.value.length === 0) return
  
  isUnassigningDrivers.value = true
  try {
    // Get assignment details for each selected assignment
    const assignmentsToUnassign = driverAssignments.value.filter(
      assignment => selectedDriverAssignments.value.includes(assignment.id)
    )
    
    // Unassign each driver
    for (const assignment of assignmentsToUnassign) {
      await driversStore.unassignAssetFromDriver(assignment.driver.id, assetsStore.currentAsset.id)
    }
    
    // Refresh asset data to get updated driver assignments
    await assetsStore.fetchAsset(assetsStore.currentAsset.id)
    await fetchDriverAssignments()
    
    // Clear selection and close dialog
    selectedDriverAssignments.value = []
    showUnassignDialog.value = false
  } catch (error) {
    console.error('Failed to unassign drivers:', error)
    // TODO: Show error message to user
  } finally {
    isUnassigningDrivers.value = false
  }
}

const closeUnassignDialog = () => {
  showUnassignDialog.value = false
}

// Watch for dialog opening to load drivers
const handleAssignDriverDialogOpen = () => {
  if (showAssignDriverDialog.value) {
    loadAvailableDrivers()
  }
}

onMounted(async () => {
  const assetId = route.params.id
  if (assetId) {
    try {
      await Promise.all([
        assetsStore.fetchAsset(assetId),
        assetsStore.fetchAssetDocuments(assetId)
      ])
      
      // Fetch location history and driver assignments after asset is loaded
      if (assetsStore.currentAsset?.asset_id) {
        fetchLocationHistory()
        fetchDriverAssignments()
      }
    } catch (error) {
      console.error('Failed to load asset:', error)
    }
  }
})

// Watch for dialog opening to load drivers
watch(showAssignDriverDialog, (newValue) => {
  if (newValue) {
    loadAvailableDrivers()
  }
})
</script>

<style scoped>
.upload-zone {
  border: 2px dashed #e0e0e0;
  background-color: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-zone:hover {
  border-color: #1976d2;
  background-color: #f5f5f5;
}

.upload-zone--active {
  border-color: #1976d2;
  background-color: #e3f2fd;
}

.asset-main-image {
  max-width: 400px;
  max-height: 300px;
  border-radius: 8px;
  cursor: pointer;
}

.image-upload-zone {
  border: 2px dashed #e0e0e0;
  background-color: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-upload-zone:hover {
  border-color: #1976d2;
  background-color: #f5f5f5;
}

.image-upload-zone--active {
  border-color: #1976d2;
  background-color: #e3f2fd;
}

.image-preview {
  max-width: 200px;
  max-height: 150px;
  border-radius: 4px;
}
</style>