<template>
  <div class="driver-detail" v-if="!loading">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/drivers">Drivers</router-link>
            </li>
            <li class="breadcrumb-item active">{{ driver.user?.first_name }} {{ driver.user?.last_name }}</li>
          </ol>
        </nav>
        <h1 class="mb-1">{{ driver.user?.first_name }} {{ driver.user?.last_name }}</h1>
        <p class="text-muted mb-0">Employee ID: {{ driver.employee_id || 'Not assigned' }}</p>
      </div>
      <div class="d-flex gap-2">
        <router-link :to="`/drivers/${driver.driver_id}/edit`" class="btn btn-primary">
          <i class="bi bi-pencil me-2"></i>Edit Driver
        </router-link>
        <div class="dropdown">
          <button class="btn btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
            Actions
          </button>
          <ul class="dropdown-menu">
            <li>
              <button @click="addTraining" class="dropdown-item">
                <i class="bi bi-mortarboard me-2"></i>Add Training
              </button>
            </li>
            <li>
              <button @click="reportIncident" class="dropdown-item">
                <i class="bi bi-exclamation-triangle me-2"></i>Report Incident
              </button>
            </li>
            <li>
              <button @click="addCertification" class="dropdown-item">
                <i class="bi bi-award me-2"></i>Add Certification
              </button>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <button @click="viewSchedule" class="dropdown-item">
                <i class="bi bi-calendar3 me-2"></i>View Schedule
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Status and Key Metrics -->
    <div class="row g-4 mb-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-3 text-center">
                <h6 class="text-muted mb-1">Status</h6>
                <span class="badge fs-6 px-3 py-2" :class="getStatusClass(driver.status)">
                  {{ formatStatus(driver.status) }}
                </span>
              </div>
              <div class="col-md-3 text-center">
                <h6 class="text-muted mb-1">Safety Rating</h6>
                <h5 class="mb-0">
                  {{ Math.round(driver.safety_rating || 0) }}%
                  <small class="text-muted">avg</small>
                </h5>
              </div>
              <div class="col-md-3 text-center">
                <h6 class="text-muted mb-1">License Type</h6>
                <h5 class="mb-0">{{ formatLicenseType(driver.license_type) }}</h5>
              </div>
              <div class="col-md-3 text-center">
                <h6 class="text-muted mb-1">Total Incidents</h6>
                <h5 class="mb-0">{{ incidents.length }}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card" :class="licenseExpiryClass">
          <div class="card-body">
            <h6 class="card-title">License Status</h6>
            <div v-if="driver.license_expiry_date">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <strong>{{ driver.license_number }}</strong>
                  <div class="small text-muted">
                    Expires: {{ formatDate(driver.license_expiry_date) }}
                  </div>
                </div>
                <span class="badge" :class="getLicenseStatusClass()">
                  {{ getLicenseStatusText() }}
                </span>
              </div>
            </div>
            <div v-else class="text-muted">
              No license information available
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <div class="card">
      <div class="card-header">
        <ul class="nav nav-tabs card-header-tabs" role="tablist">
          <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#profile-tab">
              <i class="bi bi-person me-2"></i>Profile
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#certifications-tab">
              <i class="bi bi-award me-2"></i>Certifications
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#training-tab">
              <i class="bi bi-mortarboard me-2"></i>Training
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#incidents-tab">
              <i class="bi bi-exclamation-triangle me-2"></i>Incidents
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#assignments-tab">
              <i class="bi bi-truck me-2"></i>Assignments
            </button>
          </li>
        </ul>
      </div>
      <div class="card-body">
        <div class="tab-content">
          <!-- Profile Tab -->
          <div class="tab-pane fade show active" id="profile-tab">
            <div class="row">
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Personal Information</h6>
                <table class="table table-borderless">
                  <tr>
                    <td class="text-muted">Full Name:</td>
                    <td class="fw-bold">{{ driver.user?.first_name }} {{ driver.user?.last_name }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Email:</td>
                    <td>{{ driver.user?.email || 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Phone:</td>
                    <td>{{ driver.phone_number || 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Address:</td>
                    <td>{{ driver.address || 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Date of Birth:</td>
                    <td>{{ driver.date_of_birth ? formatDate(driver.date_of_birth) : 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Hire Date:</td>
                    <td>{{ driver.hire_date ? formatDate(driver.hire_date) : 'N/A' }}</td>
                  </tr>
                </table>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">License Information</h6>
                <table class="table table-borderless">
                  <tr>
                    <td class="text-muted">License Number:</td>
                    <td class="fw-bold">{{ driver.license_number || 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">License Type:</td>
                    <td>{{ formatLicenseType(driver.license_type) }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Issue Date:</td>
                    <td>{{ driver.license_issue_date ? formatDate(driver.license_issue_date) : 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Expiry Date:</td>
                    <td>{{ driver.license_expiry_date ? formatDate(driver.license_expiry_date) : 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Issuing State:</td>
                    <td>{{ driver.license_state || 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Medical Certificate:</td>
                    <td>{{ driver.medical_cert_expiry ? formatDate(driver.medical_cert_expiry) : 'N/A' }}</td>
                  </tr>
                </table>
              </div>
            </div>
            
            <div v-if="driver.notes" class="mt-4">
              <h6 class="fw-bold mb-3">Notes</h6>
              <div class="p-3 bg-light rounded">
                {{ driver.notes }}
              </div>
            </div>
          </div>

          <!-- Certifications Tab -->
          <div class="tab-pane fade" id="certifications-tab">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="mb-0">Driver Certifications</h6>
              <button @click="addCertification" class="btn btn-sm btn-primary">
                <i class="bi bi-plus-circle me-2"></i>Add Certification
              </button>
            </div>
            
            <div v-if="certifications.length === 0" class="text-center py-4">
              <i class="bi bi-award fs-1 text-muted opacity-50"></i>
              <p class="text-muted mt-2">No certifications found</p>
            </div>
            
            <div v-else class="row g-3">
              <div v-for="cert in certifications" :key="cert.certification_id" class="col-md-6">
                <div class="card border-start border-3" :class="getCertificationBorderClass(cert)">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 class="card-title mb-1">{{ cert.certification_type }}</h6>
                        <p class="text-muted small mb-1">{{ cert.issuing_agency }}</p>
                        <div class="small">
                          <span class="text-muted me-3">
                            <i class="bi bi-calendar3 me-1"></i>
                            Issued: {{ formatDate(cert.issue_date) }}
                          </span>
                          <span class="text-muted">
                            <i class="bi bi-calendar-x me-1"></i>
                            Expires: {{ formatDate(cert.expiry_date) }}
                          </span>
                        </div>
                      </div>
                      <span class="badge" :class="getCertificationStatusClass(cert.expiry_date)">
                        {{ getCertificationStatus(cert.expiry_date) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Training Tab -->
          <div class="tab-pane fade" id="training-tab">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="mb-0">Training History</h6>
              <button @click="addTraining" class="btn btn-sm btn-primary">
                <i class="bi bi-plus-circle me-2"></i>Add Training
              </button>
            </div>
            
            <div v-if="trainingRecords.length === 0" class="text-center py-4">
              <i class="bi bi-mortarboard fs-1 text-muted opacity-50"></i>
              <p class="text-muted mt-2">No training records found</p>
            </div>
            
            <div v-else class="timeline">
              <div v-for="training in trainingRecords" :key="training.training_id" class="timeline-item">
                <div class="timeline-marker bg-primary"></div>
                <div class="timeline-content">
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <h6 class="mb-1">{{ training.training_type }}</h6>
                      <p class="text-muted small mb-1">{{ formatDate(training.completion_date) }}</p>
                      <p class="mb-1">{{ training.description }}</p>
                      <div class="small">
                        <span class="text-muted me-3">
                          <i class="bi bi-building me-1"></i>
                          {{ training.training_provider }}
                        </span>
                        <span v-if="training.certificate_number" class="text-muted">
                          <i class="bi bi-file-text me-1"></i>
                          Cert: {{ training.certificate_number }}
                        </span>
                      </div>
                    </div>
                    <span class="badge bg-success">
                      Completed
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Incidents Tab -->
          <div class="tab-pane fade" id="incidents-tab">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="mb-0">Incident Reports</h6>
              <button @click="reportIncident" class="btn btn-sm btn-warning">
                <i class="bi bi-plus-circle me-2"></i>Report Incident
              </button>
            </div>
            
            <div v-if="incidents.length === 0" class="text-center py-4">
              <i class="bi bi-shield-check fs-1 text-success opacity-50"></i>
              <p class="text-muted mt-2">No incidents reported</p>
              <p class="small text-muted">Clean driving record!</p>
            </div>
            
            <div v-else class="list-group list-group-flush">
              <div v-for="incident in incidents" :key="incident.incident_id" class="list-group-item px-0 border-start border-3" :class="getIncidentBorderClass(incident.severity)">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <div class="d-flex align-items-center mb-2">
                      <span class="badge me-2" :class="getIncidentSeverityClass(incident.severity)">
                        {{ incident.severity }}
                      </span>
                      <h6 class="mb-0">{{ incident.incident_type }}</h6>
                    </div>
                    <p class="mb-1">{{ incident.description }}</p>
                    <div class="small text-muted">
                      <span class="me-3">
                        <i class="bi bi-calendar3 me-1"></i>
                        {{ formatDate(incident.incident_date) }}
                      </span>
                      <span v-if="incident.location" class="me-3">
                        <i class="bi bi-geo-alt me-1"></i>
                        {{ incident.location }}
                      </span>
                      <span v-if="incident.resolved">
                        <i class="bi bi-check-circle me-1 text-success"></i>
                        Resolved
                      </span>
                    </div>
                  </div>
                  <div class="text-end">
                    <small class="text-muted">{{ formatDateTime(incident.created_at) }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Assignments Tab -->
          <div class="tab-pane fade" id="assignments-tab">
            <h6 class="mb-3">Current Asset Assignments</h6>
            
            <div v-if="currentAssignments.length === 0" class="text-center py-4">
              <i class="bi bi-truck fs-1 text-muted opacity-50"></i>
              <p class="text-muted mt-2">No current assignments</p>
            </div>
            
            <div v-else class="row g-3">
              <div v-for="assignment in currentAssignments" :key="assignment.asset_id" class="col-md-6">
                <div class="card">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 class="card-title mb-1">{{ assignment.asset_number }}</h6>
                        <p class="text-muted mb-1">{{ assignment.make }} {{ assignment.model }} {{ assignment.year }}</p>
                        <div class="small text-muted">
                          <span class="me-3">
                            <i class="bi bi-speedometer2 me-1"></i>
                            {{ assignment.current_mileage?.toLocaleString() || 'N/A' }} {{ assignment.mileage_unit }}
                          </span>
                          <span>
                            <i class="bi bi-fuel-pump me-1"></i>
                            {{ assignment.fuel_type || 'N/A' }}
                          </span>
                        </div>
                      </div>
                      <span class="badge" :class="getStatusClass(assignment.status)">
                        {{ formatStatus(assignment.status) }}
                      </span>
                    </div>
                    <div class="mt-2">
                      <router-link :to="`/assets/${assignment.asset_id}`" class="btn btn-sm btn-outline-primary">
                        View Asset
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Loading State -->
  <div v-else class="text-center py-5">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { driversAPI, assetsAPI } from '@/services/api'
import { toast } from '@/utils/toast'

export default {
  name: 'DriverDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const driverId = route.params.id
    
    const loading = ref(true)
    const driver = ref({})
    const certifications = ref([])
    const trainingRecords = ref([])
    const incidents = ref([])
    const currentAssignments = ref([])

    const licenseExpiryClass = computed(() => {
      if (!driver.value.license_expiry_date) return ''
      const expiry = new Date(driver.value.license_expiry_date)
      const thirtyDaysFromNow = new Date()
      thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30)
      return expiry <= thirtyDaysFromNow ? 'bg-warning-subtle border-warning' : ''
    })

    const loadDriverDetail = async () => {
      try {
        const response = await driversAPI.getDriver(driverId)
        driver.value = response.data
      } catch (error) {
        console.error('Error loading driver:', error)
        toast.error('Failed to load driver details')
        router.push('/drivers')
      }
    }

    const loadCertifications = async () => {
      try {
        const response = await driversAPI.getDriverCertifications(driverId)
        certifications.value = response.data.results || []
      } catch (error) {
        console.error('Error loading certifications:', error)
      }
    }

    const loadTrainingRecords = async () => {
      try {
        const response = await driversAPI.getDriverTraining(driverId)
        trainingRecords.value = response.data.results || []
      } catch (error) {
        console.error('Error loading training records:', error)
      }
    }

    const loadIncidents = async () => {
      try {
        const response = await driversAPI.getDriverIncidents(driverId)
        incidents.value = response.data.results || []
      } catch (error) {
        console.error('Error loading incidents:', error)
      }
    }

    const loadCurrentAssignments = async () => {
      try {
        const response = await assetsAPI.getAssets({ assigned_driver: driverId })
        currentAssignments.value = response.data.results || []
      } catch (error) {
        console.error('Error loading assignments:', error)
      }
    }

    const addTraining = () => {
      router.push({
        path: '/drivers/training/create',
        query: { driver_id: driverId }
      })
    }

    const reportIncident = () => {
      router.push({
        path: '/drivers/incidents/create',
        query: { driver_id: driverId }
      })
    }

    const addCertification = () => {
      router.push({
        path: '/drivers/certifications/create',
        query: { driver_id: driverId }
      })
    }

    const viewSchedule = () => {
      toast.info('Driver scheduling feature coming soon')
    }

    const getStatusClass = (status) => {
      const statusClasses = {
        'active': 'bg-success',
        'inactive': 'bg-secondary',
        'suspended': 'bg-danger'
      }
      return statusClasses[status] || 'bg-secondary'
    }

    const formatStatus = (status) => {
      return status.charAt(0).toUpperCase() + status.slice(1)
    }

    const formatLicenseType = (type) => {
      const types = {
        'cdl_a': 'CDL Class A',
        'cdl_b': 'CDL Class B',
        'cdl_c': 'CDL Class C',
        'regular': 'Regular License'
      }
      return types[type] || 'Unknown'
    }

    const getLicenseStatusClass = () => {
      if (!driver.value.license_expiry_date) return 'bg-secondary'
      const expiry = new Date(driver.value.license_expiry_date)
      const now = new Date()
      const thirtyDaysFromNow = new Date()
      thirtyDaysFromNow.setDate(now.getDate() + 30)
      
      if (expiry <= now) return 'bg-danger'
      if (expiry <= thirtyDaysFromNow) return 'bg-warning'
      return 'bg-success'
    }

    const getLicenseStatusText = () => {
      if (!driver.value.license_expiry_date) return 'Unknown'
      const expiry = new Date(driver.value.license_expiry_date)
      const now = new Date()
      const thirtyDaysFromNow = new Date()
      thirtyDaysFromNow.setDate(now.getDate() + 30)
      
      if (expiry <= now) return 'Expired'
      if (expiry <= thirtyDaysFromNow) return 'Expiring Soon'
      return 'Valid'
    }

    const getCertificationBorderClass = (cert) => {
      const expiry = new Date(cert.expiry_date)
      const now = new Date()
      const thirtyDaysFromNow = new Date()
      thirtyDaysFromNow.setDate(now.getDate() + 30)
      
      if (expiry <= now) return 'border-danger'
      if (expiry <= thirtyDaysFromNow) return 'border-warning'
      return 'border-success'
    }

    const getCertificationStatusClass = (expiryDate) => {
      const expiry = new Date(expiryDate)
      const now = new Date()
      const thirtyDaysFromNow = new Date()
      thirtyDaysFromNow.setDate(now.getDate() + 30)
      
      if (expiry <= now) return 'bg-danger'
      if (expiry <= thirtyDaysFromNow) return 'bg-warning'
      return 'bg-success'
    }

    const getCertificationStatus = (expiryDate) => {
      const expiry = new Date(expiryDate)
      const now = new Date()
      const thirtyDaysFromNow = new Date()
      thirtyDaysFromNow.setDate(now.getDate() + 30)
      
      if (expiry <= now) return 'Expired'
      if (expiry <= thirtyDaysFromNow) return 'Expiring Soon'
      return 'Valid'
    }

    const getIncidentSeverityClass = (severity) => {
      const severityClasses = {
        'minor': 'bg-warning',
        'major': 'bg-danger',
        'critical': 'bg-dark'
      }
      return severityClasses[severity] || 'bg-secondary'
    }

    const getIncidentBorderClass = (severity) => {
      const borderClasses = {
        'minor': 'border-warning',
        'major': 'border-danger',
        'critical': 'border-dark'
      }
      return borderClasses[severity] || 'border-secondary'
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

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(async () => {
      loading.value = true
      try {
        await Promise.all([
          loadDriverDetail(),
          loadCertifications(),
          loadTrainingRecords(),
          loadIncidents(),
          loadCurrentAssignments()
        ])
      } finally {
        loading.value = false
      }
    })

    return {
      loading,
      driver,
      certifications,
      trainingRecords,
      incidents,
      currentAssignments,
      licenseExpiryClass,
      addTraining,
      reportIncident,
      addCertification,
      viewSchedule,
      getStatusClass,
      formatStatus,
      formatLicenseType,
      getLicenseStatusClass,
      getLicenseStatusText,
      getCertificationBorderClass,
      getCertificationStatusClass,
      getCertificationStatus,
      getIncidentSeverityClass,
      getIncidentBorderClass,
      formatDate,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 1rem;
  top: 0;
  height: 100%;
  width: 2px;
  background-color: #dee2e6;
}

.timeline-item {
  position: relative;
  margin-bottom: 2rem;
}

.timeline-marker {
  position: absolute;
  left: -2rem;
  top: 0.25rem;
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #dee2e6;
}

.timeline-content {
  background: #f8f9fa;
  border-radius: 0.375rem;
  padding: 1rem;
  border-left: 3px solid #007bff;
}

.nav-tabs .nav-link {
  color: #6c757d;
  border: none;
  border-bottom: 2px solid transparent;
}

.nav-tabs .nav-link.active {
  color: #007bff;
  border-bottom-color: #007bff;
  background: none;
}

.border-start.border-3 {
  border-left-width: 3px !important;
}
</style>