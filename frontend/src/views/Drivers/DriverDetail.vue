<template>
  <div class="driver-detail-container">
    <!-- Loading State -->
    <div v-if="driversStore.isLoading" class="text-center pa-8">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p class="text-body-1 mt-4">Loading driver details...</p>
    </div>

    <!-- Driver Details -->
    <template v-else-if="driver">
      <!-- Header with Actions -->
      <div class="page-header">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center gap-4">
            <v-badge
              overlap
              class="driver-avatar-container"
            >
              <template v-slot:badge>
                <v-menu v-if="driver.profile_photo" location="bottom">
                  <template v-slot:activator="{ props }">
                    <v-btn
                      icon="mdi-dots-horizontal"
                      size="x-small"
                      color="primary"
                      v-bind="props"
                    />
                  </template>
                  <v-list>
                    <v-list-item
                      prepend-icon="mdi-camera"
                      title="Change Photo"
                      @click="showPhotoUploadDialog = true"
                    />
                    <v-list-item
                      prepend-icon="mdi-delete"
                      title="Delete Photo"
                      @click="showPhotoDeleteDialog = true"
                    />
                  </v-list>
                </v-menu>
                <v-btn
                  v-else
                  icon="mdi-camera"
                  size="x-small"
                  color="primary"
                  @click="showPhotoUploadDialog = true"
                />
              </template>
              <v-avatar size="80" class="driver-avatar">
                <v-img
                  v-if="driver.profile_photo"
                  :src="driver.profile_photo"
                  :alt="driver.full_name"
                />
                <v-icon v-else size="40" color="grey-lighten-1">mdi-account</v-icon>
              </v-avatar>
            </v-badge>
            
            <div>
              <h1 class="text-h4 mb-1">{{ driver.full_name }}</h1>
              <p class="text-h6 text-medium-emphasis mb-1">{{ driver.driver_id }}</p>
              <v-chip
                :color="getEmploymentStatusColor(driver.employment_status)"
                size="small"
                variant="flat"
              >
                {{ driver.employment_status_display }}
              </v-chip>
            </div>
          </div>
          
          <div class="d-flex align-center gap-3">
            <v-btn
              variant="outlined"
              prepend-icon="mdi-arrow-left"
              @click="goBack"
            >
              Back to Drivers
            </v-btn>
            <v-btn
              color="primary"
              prepend-icon="mdi-pencil"
              @click="editDriver"
            >
              Edit Driver
            </v-btn>
          </div>
        </div>
      </div>

      <v-row class="ma-0">
        <!-- Main Information Column -->
        <v-col cols="12" md="8" class="pa-3">
          <!-- Personal Information -->
          <v-card class="mb-6">
            <v-card-title class="bg-primary text-white">
              <v-icon class="mr-2">mdi-account</v-icon>
              Personal Information
            </v-card-title>
            <v-card-text class="pa-6">
              <v-row>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Full Name:</span>
                    <span class="info-value">{{ driver.full_name }}</span>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Email:</span>
                    <span class="info-value">{{ driver.email }}</span>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Phone:</span>
                    <span class="info-value">{{ driver.phone }}</span>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Date of Birth:</span>
                    <span class="info-value">{{ formatDate(driver.date_of_birth) }} (Age: {{ driver.age }})</span>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Employment Information -->
          <v-card class="mb-6">
            <v-card-title class="bg-primary text-white">
              <v-icon class="mr-2">mdi-briefcase</v-icon>
              Employment Information
            </v-card-title>
            <v-card-text class="pa-6">
              <v-row>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Hire Date:</span>
                    <span class="info-value">{{ formatDate(driver.hire_date) }}</span>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Employment Status:</span>
                    <v-chip
                      :color="getEmploymentStatusColor(driver.employment_status)"
                      size="small"
                      variant="flat"
                    >
                      {{ driver.employment_status_display }}
                    </v-chip>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Department:</span>
                    <span class="info-value">{{ driver.department || 'Not specified' }}</span>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Position:</span>
                    <span class="info-value">{{ driver.position || 'Not specified' }}</span>
                  </div>
                </v-col>
                <v-col cols="6" v-if="driver.employee_number">
                  <div class="info-item">
                    <span class="info-label">Employee Number:</span>
                    <span class="info-value">{{ driver.employee_number }}</span>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- License Information -->
          <v-card class="mb-6">
            <v-card-title class="bg-primary text-white">
              <v-icon class="mr-2">mdi-card-account-details</v-icon>
              License Information
            </v-card-title>
            <v-card-text class="pa-6">
              <v-row>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">License Number:</span>
                    <span class="info-value">{{ driver.license_number }}</span>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">License Type:</span>
                    <span class="info-value">{{ driver.license_type_display }}</span>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">License State:</span>
                    <span class="info-value">{{ driver.license_state }}</span>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Expiration Date:</span>
                    <div class="d-flex align-center gap-2">
                      <span class="info-value">{{ formatDate(driver.license_expiration) }}</span>
                      <v-chip
                        v-if="driver.license_is_expired"
                        color="error"
                        size="x-small"
                        variant="flat"
                      >
                        Expired
                      </v-chip>
                      <v-chip
                        v-else-if="driver.license_expires_soon"
                        color="warning"
                        size="x-small"
                        variant="flat"
                      >
                        Expires Soon
                      </v-chip>
                      <v-chip
                        v-else
                        color="success"
                        size="x-small"
                        variant="flat"
                      >
                        Valid
                      </v-chip>
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Address Information -->
          <v-card class="mb-6">
            <v-card-title class="bg-primary text-white">
              <v-icon class="mr-2">mdi-map-marker</v-icon>
              Address Information
            </v-card-title>
            <v-card-text class="pa-6">
              <div class="info-item">
                <span class="info-label">Address:</span>
                <div class="info-value">
                  <div>{{ driver.address_line1 }}</div>
                  <div v-if="driver.address_line2">{{ driver.address_line2 }}</div>
                  <div>{{ driver.city }}, {{ driver.state }} {{ driver.zip_code }}</div>
                </div>
              </div>
            </v-card-text>
          </v-card>

          <!-- Emergency Contact -->
          <v-card class="mb-6">
            <v-card-title class="bg-primary text-white">
              <v-icon class="mr-2">mdi-phone-alert</v-icon>
              Emergency Contact
            </v-card-title>
            <v-card-text class="pa-6">
              <v-row>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Name:</span>
                    <span class="info-value">{{ driver.emergency_contact_name }}</span>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Phone:</span>
                    <span class="info-value">{{ driver.emergency_contact_phone }}</span>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="info-item">
                    <span class="info-label">Relationship:</span>
                    <span class="info-value">{{ driver.emergency_contact_relationship }}</span>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Notes -->
          <v-card v-if="driver.notes" class="mb-6">
            <v-card-title class="bg-primary text-white">
              <v-icon class="mr-2">mdi-note-text</v-icon>
              Notes
            </v-card-title>
            <v-card-text class="pa-6">
              <p class="text-body-1">{{ driver.notes }}</p>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Sidebar Column -->
        <v-col cols="12" md="4" class="pa-3">
          <!-- Asset Assignments -->
          <v-card class="mb-6">
            <v-card-title class="bg-secondary text-white d-flex align-center justify-space-between">
              <div>
                <v-icon class="mr-2">mdi-truck</v-icon>
                Asset Assignments
              </div>
              <div class="d-flex align-center gap-2">
                <v-chip color="white" size="small" variant="flat" class="text-secondary">
                  {{ uniqueAssignments.length }}
                </v-chip>
                <button
                  v-if="selectedAssetAssignments.length > 0"
                  @click="confirmUnassignAssets"
                  style="background: #db162f; color: white; padding: 6px 12px; border: 1px solid #db162f; border-radius: 4px; cursor: pointer; font-size: 14px; display: flex; align-items: center; gap: 4px; margin-right: 8px;"
                >
                  <span style="font-size: 16px;">-</span>
                  Unassign {{ selectedAssetAssignments.length }}
                </button>
                <button 
                  @click="openAssignAssetDialog"
                  style="background: #216093; color: white; padding: 6px 12px; border: 1px solid #216093; border-radius: 4px; cursor: pointer; font-size: 14px; display: flex; align-items: center; gap: 4px;"
                >
                  <span style="font-size: 16px;">+</span>
                  Assign Asset
                </button>
              </div>
            </v-card-title>
            <v-card-text class="pa-0">
              <div v-if="uniqueAssignments.length === 0" class="text-center pa-6">
                <v-alert
                  type="warning"
                  variant="tonal"
                  class="mb-4"
                  icon="mdi-alert"
                >
                  <div class="text-subtitle-2 mb-2">⚠️ No Assets Assigned</div>
                  <div class="text-body-2">
                    This driver currently has no assigned assets. To ensure operational efficiency, 
                    consider assigning appropriate vehicles or equipment to this driver.
                  </div>
                </v-alert>
                <v-icon size="48" color="grey-lighten-2" class="mb-2">mdi-truck-off</v-icon>
                <p class="text-body-2 text-medium-emphasis">No active asset assignments</p>
              </div>
              <div v-else>
                <v-list lines="three">
                  <v-list-item
                    v-for="assignment in uniqueAssignments"
                    :key="`${assignment.asset_details?.id || assignment.asset}-${assignment.assignment_type}`"
                    class="assignment-item pa-3"
                  >
                    <template v-slot:prepend>
                      <div class="d-flex align-center gap-3">
                        <v-checkbox
                          v-model="selectedAssetAssignments"
                          :value="assignment.id"
                          hide-details
                          @click.stop
                        />
                        <v-avatar size="40" class="cursor-pointer" @click="viewAsset(assignment.asset_details)">
                          <v-img
                            v-if="assignment.asset_details?.thumbnail"
                            :src="assignment.asset_details.thumbnail"
                            :alt="assignment.asset_details.asset_id"
                          />
                          <v-icon v-else color="grey-lighten-1">mdi-truck</v-icon>
                        </v-avatar>
                      </div>
                    </template>
                    
                    <div class="cursor-pointer" @click="viewAsset(assignment.asset_details)">
                      <v-list-item-title class="font-weight-medium">
                        {{ assignment.asset_details?.asset_id || assignment.asset || 'Unknown Asset' }}
                      </v-list-item-title>
                      
                      <v-list-item-subtitle>
                        <div v-if="assignment.asset_details">
                          {{ assignment.asset_details.year }} {{ assignment.asset_details.make }} {{ assignment.asset_details.model }}
                          • {{ assignment.asset_details.department || 'No department' }}
                        </div>
                        <div v-else>Asset details not available</div>
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
                          {{ assignment.assignment_type_display }}
                        </v-chip>
                        
                        <!-- Safety Warnings -->
                        <div v-if="getAssetSafetyWarnings(assignment, driver).length > 0" class="mt-1">
                          <v-chip
                            v-for="warning in getAssetSafetyWarnings(assignment, driver)"
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
                        <div v-if="assignment.notes" class="text-caption mt-1">
                          {{ assignment.notes }}
                        </div>
                      </div>
                    </template>
                  </v-list-item>
                </v-list>
              </div>
            </v-card-text>
          </v-card>

          <!-- Certifications -->
          <v-card class="mb-6">
            <v-card-title class="bg-secondary text-white d-flex align-center justify-space-between">
              <div>
                <v-icon class="mr-2">mdi-certificate</v-icon>
                Certifications
              </div>
              <v-chip color="white" size="small" variant="flat" class="text-secondary">
                {{ certifications.length }}
              </v-chip>
            </v-card-title>
            <v-card-text class="pa-0">
              <div v-if="certifications.length === 0" class="text-center pa-6">
                <v-icon size="48" color="grey-lighten-2" class="mb-2">mdi-certificate-outline</v-icon>
                <p class="text-body-2 text-medium-emphasis">No certifications on file</p>
              </div>
              <div v-else>
                <div
                  v-for="cert in certifications"
                  :key="cert.id"
                  class="certification-item pa-4 border-b"
                >
                  <div class="d-flex align-center justify-space-between">
                    <div>
                      <div class="font-weight-medium">{{ cert.certification_name || cert.certification_type_display }}</div>
                      <div class="text-caption text-medium-emphasis">{{ cert.issuing_authority }}</div>
                    </div>
                    <v-chip
                      :color="getCertificationStatusColor(cert)"
                      size="small"
                      variant="flat"
                    >
                      {{ cert.status_display }}
                    </v-chip>
                  </div>
                  <div v-if="cert.expiration_date" class="text-caption text-medium-emphasis mt-2">
                    Expires: {{ formatDate(cert.expiration_date) }}
                    <v-chip
                      v-if="cert.is_expired"
                      color="error"
                      size="x-small"
                      variant="flat"
                      class="ml-2"
                    >
                      Expired
                    </v-chip>
                    <v-chip
                      v-else-if="cert.expires_soon"
                      color="warning"
                      size="x-small"
                      variant="flat"
                      class="ml-2"
                    >
                      Expires Soon
                    </v-chip>
                  </div>
                </div>
              </div>
            </v-card-text>
          </v-card>

          <!-- Quick Stats -->
          <v-card>
            <v-card-title class="bg-secondary text-white">
              <v-icon class="mr-2">mdi-chart-line</v-icon>
              Quick Stats
            </v-card-title>
            <v-card-text class="pa-4">
              <div class="d-flex justify-space-between mb-3">
                <span class="text-body-2">Active Assignments:</span>
                <span class="font-weight-medium">{{ uniqueAssignments.length }}</span>
              </div>
              <div class="d-flex justify-space-between mb-3">
                <span class="text-body-2">Certifications:</span>
                <span class="font-weight-medium">{{ certifications.length }}</span>
              </div>
              <div class="d-flex justify-space-between mb-3">
                <span class="text-body-2">Years of Service:</span>
                <span class="font-weight-medium">{{ calculateYearsOfService(driver.hire_date) }}</span>
              </div>
              <div class="d-flex justify-space-between">
                <span class="text-body-2">License Status:</span>
                <v-chip
                  :color="driver.license_is_expired ? 'error' : driver.license_expires_soon ? 'warning' : 'success'"
                  size="x-small"
                  variant="flat"
                >
                  {{ driver.license_is_expired ? 'Expired' : driver.license_expires_soon ? 'Expires Soon' : 'Valid' }}
                </v-chip>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Error State -->
    <div v-else class="text-center pa-8">
      <v-icon size="64" color="error" class="mb-4">mdi-alert-circle</v-icon>
      <h3 class="text-h6 text-error mb-2">Driver Not Found</h3>
      <p class="text-body-2 text-medium-emphasis mb-4">
        The requested driver could not be found or may have been deleted.
      </p>
      <v-btn color="primary" @click="goBack">Back to Drivers</v-btn>
    </div>

    <!-- Assign Asset Dialog -->
    <v-dialog v-model="showAssignAssetDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="text-h6">Assign Asset to Driver</v-card-title>
        <v-card-text>
          <v-alert
            type="info"
            variant="tonal"
            class="mb-4"
          >
            <div class="text-body-2">
              Only <strong>active assets</strong> in good working condition are available for assignment to ensure driver safety and operational efficiency.
            </div>
          </v-alert>
          <v-form ref="assignmentForm" v-model="isAssignmentFormValid">
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="selectedAsset"
                  :items="availableAssets"
                  :loading="loadingAssets"
                  item-title="asset_id"
                  item-value="id"
                  label="Select Asset *"
                  variant="outlined"
                  :rules="[rules.required]"
                  required
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props">
                      <template v-slot:prepend>
                        <v-avatar size="32" class="mr-2">
                          <v-img
                            v-if="item.raw.thumbnail"
                            :src="item.raw.thumbnail"
                            :alt="item.raw.asset_id"
                          />
                          <v-icon v-else size="16" color="grey-lighten-1">mdi-truck</v-icon>
                        </v-avatar>
                      </template>
                      <v-list-item-title>{{ item.raw.asset_id }}</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ item.raw.year }} {{ item.raw.make }} {{ item.raw.model }}
                        <span v-if="item.raw.department"> • {{ item.raw.department }}</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </template>
                </v-select>
              </v-col>

              <v-col cols="12">
                <v-select
                  v-model="assignmentType"
                  :items="assignmentTypeOptions"
                  label="Assignment Type *"
                  variant="outlined"
                  :rules="[rules.required]"
                  required
                />
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="assignedBy"
                  label="Assigned By"
                  variant="outlined"
                  hint="Person responsible for this assignment"
                  persistent-hint
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="assignmentNotes"
                  label="Notes (Optional)"
                  variant="outlined"
                  rows="3"
                  hint="Any additional notes about this assignment"
                  persistent-hint
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeAssignAssetDialog">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isAssigningAsset"
            :disabled="!isAssignmentFormValid"
            @click="assignAsset"
          >
            Assign Asset
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Unassign Assets Confirmation Dialog -->
    <v-dialog v-model="showUnassignAssetDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon class="mr-2" color="warning">mdi-alert</v-icon>
          Confirm Asset Unassignment
        </v-card-title>
        
        <v-card-text>
          <p class="text-body-1 mb-4">
            Are you sure you want to unassign <strong>{{ selectedAssetAssignments.length }}</strong> 
            asset{{ selectedAssetAssignments.length !== 1 ? 's' : '' }} from this driver?
          </p>
          
          <v-alert type="info" variant="tonal" class="mb-4">
            This action will mark the assignment{{ selectedAssetAssignments.length !== 1 ? 's' : '' }} as completed 
            and set the unassigned date to now. This action cannot be undone.
          </v-alert>
          
          <div v-if="selectedAssetAssignments.length > 0">
            <p class="text-subtitle-2 mb-2">Assets to be unassigned:</p>
            <v-list dense>
              <v-list-item
                v-for="assignment in assignments.filter(a => selectedAssetAssignments.includes(a.id))"
                :key="assignment.id"
                class="pl-4"
              >
                <v-list-item-title class="text-body-2">
                  {{ assignment.asset_details?.asset_id || assignment.asset || 'Unknown Asset' }}
                  - {{ assignment.assignment_type_display }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeUnassignAssetDialog">Cancel</v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="isUnassigningAssets"
            @click="unassignSelectedAssets"
          >
            Unassign Asset{{ selectedAssetAssignments.length !== 1 ? 's' : '' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Photo Upload Dialog -->
    <v-dialog v-model="showPhotoUploadDialog" max-width="600">
      <v-card>
        <v-card-title>Upload Driver Photo</v-card-title>
        <v-card-text>
          <v-form ref="photoUploadForm" @submit.prevent="uploadPhoto">
            <v-alert
              type="info"
              variant="tonal"
              class="mb-4"
            >
              <div class="text-body-2">
                Upload a professional photo of the driver. The image will be automatically resized to 300x300px.
                <br><strong>Accepted formats:</strong> JPEG, PNG, WebP (Max 2MB)
              </div>
            </v-alert>
            
            <!-- Photo Upload Area -->
            <div
              class="photo-upload-zone pa-6 text-center rounded"
              :class="{ 'photo-upload-zone--active': isPhotoDragging }"
              @drop.prevent="handlePhotoDrop"
              @dragover.prevent="isPhotoDragging = true"
              @dragleave.prevent="isPhotoDragging = false"
            >
              <v-icon size="48" class="mb-2" color="grey">
                {{ selectedPhotoFile ? 'mdi-file-image' : 'mdi-camera-plus' }}
              </v-icon>
              
              <p v-if="!selectedPhotoFile" class="text-body-2 mb-2">
                Drag and drop photo here or click to browse
              </p>
              
              <div v-else class="mb-2">
                <p class="text-body-2 font-weight-medium">
                  {{ selectedPhotoFile.name }}
                  <v-chip size="small" class="ml-2">
                    {{ formatFileSize(selectedPhotoFile.size) }}
                  </v-chip>
                </p>
                
                <!-- Photo Preview -->
                <div v-if="photoPreviewUrl" class="mt-3">
                  <v-img
                    :src="photoPreviewUrl"
                    class="photo-preview mx-auto"
                    max-width="300"
                    cover
                  />
                </div>
              </div>
              
              <input
                ref="photoFileInput"
                type="file"
                hidden
                accept="image/jpeg,image/jpg,image/png,image/webp"
                @change="handlePhotoFileSelect"
              />
              
              <v-btn
                v-if="!selectedPhotoFile"
                size="small"
                variant="outlined"
                @click="$refs.photoFileInput.click()"
              >
                Choose Photo
              </v-btn>
              
              <v-btn
                v-else
                size="small"
                variant="text"
                color="error"
                @click="clearPhotoFile"
              >
                Remove Photo
              </v-btn>
            </div>
            
            <p class="text-caption text-medium-emphasis mt-2">
              Recommended: Square photo (e.g., 300x300px)
            </p>
            
            <!-- Upload Error -->
            <v-alert
              v-if="photoUploadError"
              type="error"
              class="mt-4"
              closable
              @click:close="photoUploadError = ''"
            >
              {{ photoUploadError }}
            </v-alert>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closePhotoUploadDialog">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isUploadingPhoto"
            :disabled="!selectedPhotoFile"
            @click="uploadPhoto"
          >
            Upload
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Photo Delete Confirmation Dialog -->
    <v-dialog v-model="showPhotoDeleteDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h5">
          <v-icon color="error" class="mr-2">mdi-alert</v-icon>
          Delete Driver Photo
        </v-card-title>
        <v-card-text>
          <p class="text-body-1 mb-4">
            Are you sure you want to delete {{ driver?.full_name }}'s profile photo? This action cannot be undone.
          </p>
          <div v-if="driver?.profile_photo" class="text-center">
            <v-avatar size="100" class="mx-auto">
              <v-img :src="driver.profile_photo" />
            </v-avatar>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showPhotoDeleteDialog = false">Cancel</v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="isUploadingPhoto"
            @click="deleteDriverPhoto"
          >
            Delete Photo
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDriversStore } from '../../stores/drivers'

// Router and store
const router = useRouter()
const route = useRoute()
const driversStore = useDriversStore()

// Component state
const assignments = ref([])
const certifications = ref([])

// Photo upload state
const showPhotoUploadDialog = ref(false)
const showPhotoDeleteDialog = ref(false)
const selectedPhotoFile = ref(null)
const photoPreviewUrl = ref('')
const isPhotoDragging = ref(false)
const isUploadingPhoto = ref(false)
const photoUploadError = ref('')
const photoFileInput = ref(null)


// Computed property to remove duplicate assignments per asset
const uniqueAssignments = computed(() => {
  if (!assignments.value || assignments.value.length === 0) {
    return []
  }
  
  // Create a map to track the best assignment per asset
  const assetMap = {}
  
  assignments.value.forEach(assignment => {
    const assetId = assignment.asset_details?.id || assignment.asset
    if (!assetId) return
    
    // If we haven't seen this asset, or this assignment is better
    if (!assetMap[assetId] || isHigherPriority(assignment, assetMap[assetId])) {
      assetMap[assetId] = assignment
    }
  })
  
  return Object.values(assetMap)
})

// Simple priority comparison function
const isHigherPriority = (newAssignment, existingAssignment) => {
  const priorityOrder = { 'primary': 1, 'secondary': 2, 'temporary': 3, 'backup': 4, 'shared': 5 }
  
  const newPriority = priorityOrder[newAssignment.assignment_type] || 999
  const existingPriority = priorityOrder[existingAssignment.assignment_type] || 999
  
  // Lower number = higher priority
  if (newPriority < existingPriority) return true
  if (newPriority > existingPriority) return false
  
  // Same priority - prefer more recent
  return new Date(newAssignment.assigned_date || 0) > new Date(existingAssignment.assigned_date || 0)
}

// Asset unassign state
const selectedAssetAssignments = ref([])
const showUnassignAssetDialog = ref(false)
const isUnassigningAssets = ref(false)

// Assignment dialog state
const showAssignAssetDialog = ref(false)
const assignmentForm = ref(null)
const isAssignmentFormValid = ref(false)
const selectedAsset = ref(null)
const assignmentType = ref('primary')
const assignedBy = ref('Fleet Manager')
const assignmentNotes = ref('')
const availableAssets = ref([])
const loadingAssets = ref(false)
const isAssigningAsset = ref(false)

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

// Computed properties
const driver = computed(() => driversStore.currentDriver)

// Methods
const loadDriverData = async () => {
  try {
    await driversStore.fetchDriver(route.params.id)
    // Load related data from the driver object (assignments and certifications are included in API response)
    assignments.value = driver.value?.asset_assignments || []
    certifications.value = driver.value?.certifications || []
  } catch (error) {
    console.error('Failed to load driver:', error)
  }
}

const editDriver = () => {
  router.push(`/drivers/${route.params.id}/edit`)
}

const viewAsset = (asset) => {
  if (asset?.id) {
    router.push(`/assets/${asset.id}`)
  }
}

const goBack = () => {
  router.push('/drivers')
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const calculateYearsOfService = (hireDate) => {
  const today = new Date()
  const hire = new Date(hireDate)
  const years = Math.floor((today - hire) / (365.25 * 24 * 60 * 60 * 1000))
  return years
}

const getEmploymentStatusColor = (status) => {
  const colors = {
    active: 'success',
    inactive: 'warning',
    suspended: 'error',
    terminated: 'error',
    on_leave: 'info'
  }
  return colors[status] || 'default'
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

const getCertificationStatusColor = (cert) => {
  if (cert.is_expired) return 'error'
  if (cert.expires_soon) return 'warning'
  return 'success'
}

// Photo upload handlers
const handlePhotoFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndSetPhotoFile(file)
  }
}

const handlePhotoDrop = (event) => {
  isPhotoDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndSetPhotoFile(file)
  }
}

const validateAndSetPhotoFile = (file) => {
  // Check file type
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    photoUploadError.value = 'Invalid file type. Please upload JPEG, PNG, or WebP images.'
    return
  }
  
  // Check file size (2MB max)
  if (file.size > 2097152) {
    photoUploadError.value = 'Photo size must be less than 2MB'
    return
  }
  
  selectedPhotoFile.value = file
  photoUploadError.value = ''
  
  // Create preview URL
  if (photoPreviewUrl.value) {
    URL.revokeObjectURL(photoPreviewUrl.value)
  }
  photoPreviewUrl.value = URL.createObjectURL(file)
}

const clearPhotoFile = () => {
  selectedPhotoFile.value = null
  if (photoFileInput.value) {
    photoFileInput.value.value = ''
  }
  if (photoPreviewUrl.value) {
    URL.revokeObjectURL(photoPreviewUrl.value)
    photoPreviewUrl.value = ''
  }
}

const closePhotoUploadDialog = () => {
  showPhotoUploadDialog.value = false
  clearPhotoFile()
  photoUploadError.value = ''
  isPhotoDragging.value = false
}

const uploadPhoto = async () => {
  if (!selectedPhotoFile.value) return
  
  isUploadingPhoto.value = true
  photoUploadError.value = ''
  
  try {
    const formData = new FormData()
    formData.append('photo', selectedPhotoFile.value)
    
    await driversStore.uploadDriverPhoto(route.params.id, formData)
    
    closePhotoUploadDialog()
  } catch (error) {
    console.error('Photo upload failed:', error)
    photoUploadError.value = error.response?.data?.error || 'Failed to upload photo. Please try again.'
  } finally {
    isUploadingPhoto.value = false
  }
}

const deleteDriverPhoto = async () => {
  try {
    await driversStore.deleteDriverPhoto(route.params.id)
    showPhotoDeleteDialog.value = false
  } catch (error) {
    console.error('Photo delete failed:', error)
    // Error handling is managed by the store
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Safety validation functions
const getAssetSafetyWarnings = (assignment, driver) => {
  const warnings = []
  const asset = assignment.asset_details
  
  if (!asset || !driver) return warnings
  
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

// Asset assignment methods
const loadAvailableAssets = async () => {
  if (loadingAssets.value) return
  
  loadingAssets.value = true
  try {
    // Import assets store
    const { useAssetsStore } = await import('../../stores/assets')
    const assetsStore = useAssetsStore()
    
    // Fetch all assets (we'll filter them ourselves for safety)
    await assetsStore.fetchAssets({ 
      per_page: 100 
    })
    
    // Filter out assets already assigned to this driver
    const assignedAssetIds = new Set(assignments.value.map(a => a.asset_details?.id).filter(Boolean))
    
    // Filter for eligible assets only
    availableAssets.value = assetsStore.assets.filter(asset => {
      // Must not already be assigned to this driver
      if (assignedAssetIds.has(asset.id)) {
        return false
      }
      
      // Must have active status (not maintenance, retired, etc.)
      if (asset.status !== 'active') {
        return false
      }
      
      // Additional safety checks could include:
      // - Vehicle inspection status
      // - Insurance validity
      // - Registration status
      // For now, we'll just check basic status
      
      return true
    })
    
  } catch (error) {
    console.error('Failed to load available assets:', error)
    availableAssets.value = []
  } finally {
    loadingAssets.value = false
  }
}

const assignAsset = async () => {
  if (!selectedAsset.value || !driver.value) return
  
  isAssigningAsset.value = true
  try {
    // Create assignment payload
    const assignmentData = {
      driver: driver.value.id,
      asset: selectedAsset.value,
      assignment_type: assignmentType.value,
      assigned_by: assignedBy.value,
      notes: assignmentNotes.value || '',
      assigned_date: new Date().toISOString().split('T')[0]
    }
    
    // Submit assignment through drivers store
    await driversStore.createDriverAssetAssignment(assignmentData)
    
    // Refresh driver data to get updated assignments
    await loadDriverData()
    
    // Close dialog and reset form
    closeAssignAssetDialog()
  } catch (error) {
    console.error('Failed to assign asset:', error)
    // TODO: Show error message to user
  } finally {
    isAssigningAsset.value = false
  }
}


const openAssignAssetDialog = () => {
  showAssignAssetDialog.value = true
}

const closeAssignAssetDialog = () => {
  showAssignAssetDialog.value = false
  selectedAsset.value = null
  assignmentType.value = 'primary'
  assignmentNotes.value = ''
  availableAssets.value = []
  
  // Reset form validation
  if (assignmentForm.value) {
    assignmentForm.value.reset()
  }
}

// Asset unassign functions
const confirmUnassignAssets = () => {
  showUnassignAssetDialog.value = true
}

const unassignSelectedAssets = async () => {
  if (selectedAssetAssignments.value.length === 0) return
  
  isUnassigningAssets.value = true
  try {
    // Get assignment details for each selected assignment
    const assignmentsToUnassign = assignments.value.filter(
      assignment => selectedAssetAssignments.value.includes(assignment.id)
    )
    
    // Unassign each asset
    for (const assignment of assignmentsToUnassign) {
      const assetId = assignment.asset_details?.id || assignment.asset
      await driversStore.unassignAssetFromDriver(driver.value.id, assetId)
    }
    
    // Refresh driver data to get updated assignments
    await loadDriverData()
    
    // Clear selection and close dialog
    selectedAssetAssignments.value = []
    showUnassignAssetDialog.value = false
  } catch (error) {
    console.error('Failed to unassign assets:', error)
    // TODO: Show error message to user
  } finally {
    isUnassigningAssets.value = false
  }
}

const closeUnassignAssetDialog = () => {
  showUnassignAssetDialog.value = false
}

// Lifecycle hooks
onMounted(() => {
  loadDriverData()
})

// Watch for dialog opening to load assets
watch(showAssignAssetDialog, (newValue) => {
  if (newValue) {
    loadAvailableAssets()
  }
})
</script>

<style scoped>
.driver-detail-container {
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

.driver-avatar {
  border: 3px solid #216093;
}

.info-item {
  margin-bottom: 16px;
}

.info-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  margin-bottom: 4px;
}

.info-value {
  display: block;
  font-size: 16px;
  color: #333;
}

.assignment-item,
.certification-item {
  border-bottom: 1px solid #eee;
}

.assignment-item:last-child,
.certification-item:last-child {
  border-bottom: none;
}

.border-b {
  border-bottom: 1px solid #eee;
}

.gap-3 {
  gap: 12px;
}

.gap-4 {
  gap: 16px;
}

.cursor-pointer {
  cursor: pointer;
}

.assignment-item:hover {
  background-color: #f5f5f5;
}

/* Photo Upload Styles */
.photo-upload-zone {
  border: 2px dashed #e0e0e0;
  background-color: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.photo-upload-zone:hover {
  border-color: #57949A;
  background-color: rgba(87, 148, 154, 0.05);
}

.photo-upload-zone--active {
  border-color: #216093;
  background-color: rgba(33, 96, 147, 0.05);
}

.photo-preview {
  border-radius: 8px;
  border: 2px solid #e0e0e0;
  overflow: hidden;
}

.driver-avatar-container {
  position: relative;
}

.driver-avatar-container :deep(.v-badge__badge) {
  bottom: 0;
  right: 0;
}
</style>