<template>
  <v-container fluid>
    <!-- Page Header -->
    <v-row class="mb-3">
      <v-col cols="12" md="8">
        <h1 class="text-h5 font-weight-medium mb-1">
          Fleet Location Map
        </h1>
        <p class="text-body-2 text-medium-emphasis">
          Real-time vehicle tracking and location management
        </p>
      </v-col>
        
      <v-col cols="12" md="4" class="text-md-right">
        <v-btn
          color="primary"
          size="small"
          prepend-icon="mdi-map-marker-plus"
          @click="showManualEntryDialog = true"
          class="mr-2"
        >
          Add Location
        </v-btn>
        <v-btn
          variant="outlined"
          size="small"
          prepend-icon="mdi-map-marker-radius"
          :to="{ name: 'ZoneManagement' }"
        >
          Manage Zones
        </v-btn>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <div class="stat-card pa-3">
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ mapData?.assets?.length || 0 }}
              </div>
              <div class="text-caption text-medium-emphasis">Assets Tracked</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-truck</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div class="stat-card pa-3">
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium d-flex align-center">
                {{ locationStats.tracking_coverage }}%
                <v-tooltip location="top">
                  <template v-slot:activator="{ props }">
                    <v-icon 
                      v-bind="props"
                      size="small"
                      class="ml-1"
                      style="cursor: help; opacity: 0.7;"
                    >
                      mdi-information-outline
                    </v-icon>
                  </template>
                  <div style="max-width: 300px;">
                    <strong>Coverage Calculation</strong><br>
                    Percentage of fleet assets that have reported their location in the last 24 hours.<br><br>
                    Formula: (Assets with recent updates ÷ Total active assets) × 100
                  </div>
                </v-tooltip>
              </div>
              <div class="text-caption text-medium-emphasis">Coverage</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-radar</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div 
          class="stat-card pa-3 cursor-pointer"
          @click="$router.push('/locations/zones')"
        >
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ mapData?.zones?.length || 0 }}
              </div>
              <div class="text-caption text-medium-emphasis">Active Zones</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-map-marker-radius</v-icon>
          </div>
        </div>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <div class="stat-card pa-3">
          <div class="d-flex align-center">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-medium">
                {{ locationStats.today_updates }}
              </div>
              <div class="text-caption text-medium-emphasis">Today's Updates</div>
            </div>
            <v-icon size="24" class="text-medium-emphasis">mdi-update</v-icon>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Map container -->
    <div class="map-wrapper">
      <div id="fleet-map" class="map-container" :style="{ height: mapHeight + 'px' }">
        <!-- Loading overlay -->
        <div v-if="locationsStore.isLoadingMap" class="map-loading-overlay">
          <v-progress-circular indeterminate color="primary" size="48" />
          <div class="mt-3">Loading map data...</div>
        </div>
      </div>

      <!-- Map legend (positioned upper-right) -->
      <div class="map-legend map-legend-top-right">
        <div class="legend-title">Legend</div>
        <div class="legend-item">
          <div class="legend-marker marker-active"></div>
          <span>Active Vehicle</span>
        </div>
        <div class="legend-item">
          <div class="legend-marker marker-maintenance"></div>
          <span>Maintenance</span>
        </div>
        <div class="legend-item">
          <div class="legend-marker marker-retired"></div>
          <span>Retired</span>
        </div>
        <div class="legend-item">
          <div class="legend-marker marker-zone"></div>
          <span>Location Zone</span>
        </div>
      </div>
    </div>

    <!-- Asset info panel -->
    <v-navigation-drawer
      v-model="showAssetPanel"
      location="right"
      temporary
      width="400"
    >
      <div v-if="selectedAsset" class="pa-4">
        <div class="d-flex align-center justify-space-between mb-4">
          <h3 class="text-h6">{{ selectedAsset.asset_details.asset_id }}</h3>
          <v-btn
            icon="mdi-close"
            variant="text"
            size="small"
            @click="showAssetPanel = false"
          />
        </div>

        <div class="asset-info">
          <div class="info-row">
            <span class="label">Vehicle:</span>
            <span>{{ selectedAsset.asset_details.make }} {{ selectedAsset.asset_details.model }}</span>
          </div>
          
          <div class="info-row">
            <span class="label">Type:</span>
            <span>{{ selectedAsset.asset_details.vehicle_type }}</span>
          </div>
          
          <div class="info-row">
            <span class="label">Status:</span>
            <v-chip
              :color="getStatusColor(selectedAsset.asset_details.status)"
              size="small"
              variant="flat"
            >
              {{ selectedAsset.asset_details.status }}
            </v-chip>
          </div>
          
          <div class="info-row">
            <span class="label">Department:</span>
            <span>{{ selectedAsset.asset_details.department }}</span>
          </div>
          
          <div class="info-row">
            <span class="label">Last Update:</span>
            <span>{{ formatTimestamp(selectedAsset.timestamp) }}</span>
          </div>
          
          <div class="info-row">
            <span class="label">Source:</span>
            <span>{{ selectedAsset.source }}</span>
          </div>
          
          <div v-if="selectedAsset.address" class="info-row">
            <span class="label">Address:</span>
            <span>{{ selectedAsset.address }}</span>
          </div>
          
          <div v-if="selectedAsset.zone_details" class="info-row">
            <span class="label">Zone:</span>
            <v-chip
              :color="selectedAsset.zone_details.color"
              size="small"
              variant="flat"
            >
              {{ selectedAsset.zone_details.name }}
            </v-chip>
          </div>
        </div>

        <div class="mt-4">
          <v-btn
            block
            variant="outlined"
            prepend-icon="mdi-history"
            @click="viewAssetHistory"
          >
            View Location History
          </v-btn>
        </div>
      </div>
    </v-navigation-drawer>

    <!-- Manual location entry dialog -->
    <v-dialog v-model="showManualEntryDialog" max-width="500">
      <ManualLocationEntry
        @close="showManualEntryDialog = false"
        @location-added="handleLocationAdded"
      />
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useLocationsStore } from '../../stores/locations'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import ManualLocationEntry from '../../components/Locations/ManualLocationEntry.vue'

// Store and router
const router = useRouter()
const locationsStore = useLocationsStore()

// Component state
const map = ref(null)
const mapHeight = ref(600)
const timeFilter = ref(24)
const showAssetPanel = ref(false)
const showManualEntryDialog = ref(false)
const selectedAsset = ref(null)
const assetMarkers = ref(new Map())
const zoneCircles = ref(new Map())

// Time filter options
const timeFilterOptions = [
  { title: 'Last hour', value: 1 },
  { title: 'Last 6 hours', value: 6 },
  { title: 'Last 24 hours', value: 24 },
  { title: 'Last 3 days', value: 72 },
  { title: 'Last week', value: 168 }
]

// Computed data
const mapData = computed(() => locationsStore.mapData)
const locationStats = computed(() => locationsStore.locationStats)

// Map configuration
const defaultCenter = [40.7128, -74.0060] // New York City as default
const defaultZoom = 10

// Leaflet marker icons
const createMarkerIcon = (status, size = 'medium') => {
  const colors = {
    active: '#2E933C',
    maintenance: '#E18331',
    retired: '#DB162F'
  }
  
  const sizes = {
    small: 20,
    medium: 25,
    large: 30
  }
  
  return L.divIcon({
    html: `<div style="
      background-color: ${colors[status] || colors.active};
      width: ${sizes[size]}px;
      height: ${sizes[size]}px;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 12px;
      font-weight: bold;
    ">🚗</div>`,
    className: 'custom-marker',
    iconSize: [sizes[size], sizes[size]],
    iconAnchor: [sizes[size] / 2, sizes[size] / 2]
  })
}

// Component methods
const initializeMap = () => {
  // Initialize Leaflet map with a wider initial view
  map.value = L.map('fleet-map', {
    center: defaultCenter,
    zoom: 8,  // Start more zoomed out for better initial view
    zoomControl: true,
    scrollWheelZoom: true
  })
  
  // Add tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18,
    minZoom: 3
  }).addTo(map.value)
  
  // Set map height
  calculateMapHeight()
  
  // Handle window resize
  window.addEventListener('resize', calculateMapHeight)
}

const calculateMapHeight = () => {
  const headerHeight = 200 // Approximate header height
  const availableHeight = window.innerHeight - headerHeight
  mapHeight.value = Math.max(400, Math.min(800, availableHeight))
  
  if (map.value) {
    map.value.invalidateSize()
  }
}

const loadMapData = async () => {
  try {
    await locationsStore.fetchMapData({
      within_hours: timeFilter.value
    })
    await locationsStore.fetchLocationStats()
    
    updateMapMarkers()
  } catch (error) {
    console.error('Failed to load map data:', error)
  }
}

const updateMapMarkers = () => {
  if (!map.value || !mapData.value) return
  
  // Clear existing markers
  assetMarkers.value.forEach(marker => map.value.removeLayer(marker))
  assetMarkers.value.clear()
  
  zoneCircles.value.forEach(circle => map.value.removeLayer(circle))
  zoneCircles.value.clear()
  
  // Add asset markers
  if (mapData.value.assets) {
    mapData.value.assets.forEach(asset => {
      const marker = L.marker(
        [asset.latitude, asset.longitude],
        { icon: createMarkerIcon(asset.asset_details.status) }
      )
      
      marker.bindTooltip(
        `${asset.asset_details.asset_id}<br>${asset.asset_details.make} ${asset.asset_details.model}`,
        { direction: 'top', offset: [0, -10] }
      )
      
      marker.on('click', () => {
        selectedAsset.value = asset
        showAssetPanel.value = true
      })
      
      marker.addTo(map.value)
      assetMarkers.value.set(asset.asset.id, marker)
    })
  }
  
  // Add zone circles
  if (mapData.value.zones) {
    mapData.value.zones.forEach(zone => {
      const circle = L.circle(
        [zone.center_lat, zone.center_lng],
        {
          radius: zone.radius,
          color: zone.color,
          fillColor: zone.color,
          fillOpacity: 0.1,
          weight: 2
        }
      )
      
      circle.bindTooltip(
        `${zone.name}<br>Type: ${zone.zone_type}`,
        { direction: 'center' }
      )
      
      circle.addTo(map.value)
      zoneCircles.value.set(zone.id, circle)
    })
  }
  
  // Fit map to show all markers and zones
  const allFeatures = []
  
  // Add all asset markers to the feature group
  if (assetMarkers.value.size > 0) {
    allFeatures.push(...assetMarkers.value.values())
  }
  
  // Add all zone circles to the feature group
  if (zoneCircles.value.size > 0) {
    allFeatures.push(...zoneCircles.value.values())
  }
  
  // Fit bounds to show all features with proper padding
  if (allFeatures.length > 0) {
    const group = new L.featureGroup(allFeatures)
    const bounds = group.getBounds()
    
    // Use setTimeout to ensure map is fully rendered before fitting bounds
    setTimeout(() => {
      if (map.value && bounds.isValid()) {
        map.value.fitBounds(bounds, { 
          padding: [50, 50],  // More padding for better visibility
          maxZoom: 15,        // Don't zoom in too much for single markers
          animate: true,      // Smooth animation
          duration: 0.5       // Animation duration in seconds
        })
      }
    }, 100)
  } else if (map.value) {
    // If no features, keep default view
    map.value.setView(defaultCenter, defaultZoom)
  }
}

const handleTimeFilterChange = () => {
  loadMapData()
}

const refreshMapData = () => {
  loadMapData()
}

const viewAssetHistory = () => {
  if (selectedAsset.value) {
    router.push(`/assets/${selectedAsset.value.asset_details.id}`)
  }
}

const handleLocationAdded = () => {
  showManualEntryDialog.value = false
  refreshMapData()
}

const getStatusColor = (status) => {
  const colors = {
    active: 'success',
    maintenance: 'warning',
    retired: 'error'
  }
  return colors[status] || 'primary'
}

const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

// Lifecycle hooks
onMounted(async () => {
  initializeMap()
  await loadMapData()
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
  window.removeEventListener('resize', calculateMapHeight)
})

// Watch for map data changes
watch(mapData, updateMapMarkers)
</script>

<style scoped>
/* Statistics cards styling - matching Assets */
.stat-card {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  background-color: rgb(var(--v-theme-surface));
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: rgba(var(--v-theme-primary), 0.3);
  background-color: rgba(var(--v-theme-primary), 0.02);
}

.stat-card--active {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.08);
}

/* Filter section styling - matching Assets */
.filter-section {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  background-color: rgb(var(--v-theme-surface));
}

/* Table section styling - matching Assets (used for map container) */
.table-section {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  background-color: rgb(var(--v-theme-surface));
  overflow: hidden;
  position: relative;
}

.map-container {
  width: 100%;
  position: relative;
}

.map-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.map-legend {
  position: absolute;
  top: 16px;
  left: 16px;
  background: white;
  padding: 12px;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  z-index: 1000;
}

.map-legend-top-right {
  left: auto;
  right: 16px;
}

.legend-title {
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 14px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  font-size: 12px;
}

.legend-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
}

.marker-active {
  background-color: #2E933C;
}

.marker-maintenance {
  background-color: #E18331;
}

.marker-retired {
  background-color: #DB162F;
}

.marker-zone {
  background-color: #216093;
  border: 2px solid white;
}

.asset-info {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  font-weight: 500;
  color: #666;
  min-width: 100px;
}

.cursor-pointer {
  cursor: pointer;
}

/* Leaflet marker customization */
:deep(.custom-marker) {
  background: transparent !important;
  border: none !important;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-controls {
    width: 100%;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .location-map-container {
    padding: 16px;
  }
  
  .map-header {
    padding: 16px;
  }
  
  .header-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-controls .v-select,
  .header-controls .v-btn {
    width: 100%;
  }
  
  .map-legend {
    position: relative;
    margin: 16px;
    width: calc(100% - 32px);
  }
}
</style>