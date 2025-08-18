<template>
  <v-dialog 
    v-model="isOpen" 
    max-width="1200"
    @update:model-value="$emit('update:modelValue', $event)"
    @click:outside="closeModal"
  >
    <v-card class="path-modal">
      <v-card-title class="d-flex align-center justify-space-between pa-6">
        <div class="d-flex align-center">
          <v-icon class="mr-3" size="28" color="primary">mdi-map-marker-path</v-icon>
          <div>
            <h2 class="text-h5 mb-1">Location Path for {{ asset.asset_id }}</h2>
            <p class="text-body-2 text-medium-emphasis">
              {{ asset.make }} {{ asset.model }} ({{ asset.year }})
            </p>
          </div>
        </div>
        
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="closeModal"
        />
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-0">
        <!-- Filter Controls -->
        <div class="pa-4 bg-grey-lighten-5">
          <v-row align="center" no-gutters class="gap-3">
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="localHistoryDays"
                :items="historyDayOptions"
                label="Time Period"
                density="compact"
                variant="outlined"
                hide-details
                @update:model-value="fetchPathData"
              />
            </v-col>
            
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="localHistoryLimit"
                :items="historyLimitOptions"
                label="Max Results"
                density="compact"
                variant="outlined"
                hide-details
                @update:model-value="fetchPathData"
              />
            </v-col>
            
            <v-col cols="12" sm="4" md="2">
              <v-btn
                color="primary"
                variant="outlined"
                prepend-icon="mdi-refresh"
                :loading="isLoading"
                @click="fetchPathData"
                block
                density="compact"
                height="40"
              >
                Refresh
              </v-btn>
            </v-col>
            
            <v-col cols="12" sm="8" md="4">
              <div class="d-flex align-center justify-end gap-2 flex-wrap h-100">
                <v-chip
                  v-if="pathData.length > 0"
                  color="primary"
                  size="small"
                  variant="flat"
                >
                  {{ pathData.length }} locations
                </v-chip>
                
                <v-chip
                  v-if="totalDistance > 0"
                  color="success"
                  size="small"
                  variant="flat"
                >
                  {{ totalDistance.toFixed(1) }} km total
                </v-chip>
              </div>
            </v-col>
          </v-row>
        </div>

        <!-- Map Container -->
        <div id="path-map" class="path-map-container">
          <div v-if="isLoading" class="map-loading-overlay">
            <v-progress-circular indeterminate color="primary" size="48" />
            <div class="mt-3">Loading path data...</div>
          </div>
        </div>

        <!-- No Data State -->
        <div v-if="!isLoading && pathData.length === 0" class="no-data-overlay">
          <v-icon size="64" color="grey-lighten-1">mdi-map-marker-off</v-icon>
          <h3 class="text-h6 mt-4 mb-2">No Location Data</h3>
          <p class="text-body-2 text-medium-emphasis">
            No location history found for the selected time period.
          </p>
          <v-btn
            color="primary"
            variant="outlined"
            prepend-icon="mdi-plus"
            class="mt-4"
            @click="$emit('add-location')"
          >
            Add Manual Location
          </v-btn>
        </div>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <!-- Path Statistics -->
        <div v-if="pathData.length > 0" class="d-flex gap-6 align-center flex-grow-1">
          <div class="stat-item">
            <div class="stat-label">Duration</div>
            <div class="stat-value">{{ formatDuration(pathDuration) }}</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-label">Avg Speed</div>
            <div class="stat-value">{{ averageSpeed.toFixed(1) }} km/h</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-label">Data Points</div>
            <div class="stat-value">{{ pathData.length }}</div>
          </div>
        </div>
        
        <div v-else class="flex-grow-1"></div>
        
        <v-spacer />
        
        <v-btn
          variant="text"
          @click="closeModal"
        >
          Close
        </v-btn>
        
        <v-menu>
          <template v-slot:activator="{ props: menuProps }">
            <v-btn
              color="primary"
              prepend-icon="mdi-download"
              append-icon="mdi-chevron-down"
              v-bind="menuProps"
            >
              Export Path
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="exportPath('json')">
              <template v-slot:prepend>
                <v-icon>mdi-code-braces</v-icon>
              </template>
              <v-list-item-title>JSON Format</v-list-item-title>
              <v-list-item-subtitle>Full data with metadata</v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item @click="exportPath('csv')">
              <template v-slot:prepend>
                <v-icon>mdi-file-delimited</v-icon>
              </template>
              <v-list-item-title>CSV Format</v-list-item-title>
              <v-list-item-subtitle>Spreadsheet compatible</v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item @click="exportPath('gpx')">
              <template v-slot:prepend>
                <v-icon>mdi-map-marker-path</v-icon>
              </template>
              <v-list-item-title>GPX Format</v-list-item-title>
              <v-list-item-subtitle>GPS exchange format</v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item @click="exportPath('kml')">
              <template v-slot:prepend>
                <v-icon>mdi-earth</v-icon>
              </template>
              <v-list-item-title>KML Format</v-list-item-title>
              <v-list-item-subtitle>Google Earth compatible</v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item @click="exportPath('geojson')">
              <template v-slot:prepend>
                <v-icon>mdi-map</v-icon>
              </template>
              <v-list-item-title>GeoJSON Format</v-list-item-title>
              <v-list-item-subtitle>Geographic data format</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useLocationsStore } from '../../stores/locations'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  asset: {
    type: Object,
    required: true
  },
  initialDays: {
    type: Number,
    default: 7
  },
  initialLimit: {
    type: Number,
    default: 100
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'add-location'])

// Store
const locationsStore = useLocationsStore()

// Reactive state
const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isLoading = ref(false)
const pathData = ref([])
const map = ref(null)
const pathPolyline = ref(null)
const markers = ref([])

// Filter state
const localHistoryDays = ref(props.initialDays)
const localHistoryLimit = ref(props.initialLimit)

// Options
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

// Computed properties
const totalDistance = computed(() => {
  if (pathData.value.length < 2) return 0
  
  let distance = 0
  for (let i = 1; i < pathData.value.length; i++) {
    const prev = pathData.value[i - 1]
    const curr = pathData.value[i]
    distance += calculateDistance(
      prev.latitude, prev.longitude,
      curr.latitude, curr.longitude
    )
  }
  return distance
})

const pathDuration = computed(() => {
  if (pathData.value.length < 2) return 0
  
  const start = new Date(pathData.value[0].timestamp)
  const end = new Date(pathData.value[pathData.value.length - 1].timestamp)
  return end - start
})

const averageSpeed = computed(() => {
  if (pathDuration.value === 0 || totalDistance.value === 0) return 0
  
  const hours = pathDuration.value / (1000 * 60 * 60)
  return totalDistance.value / hours
})

// Methods
const initializeMap = async () => {
  await nextTick()
  
  if (map.value) {
    map.value.remove()
  }
  
  // Initialize map
  map.value = L.map('path-map').setView([40.7128, -74.0060], 10)
  
  // Add tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map.value)
  
  // Initialize path polyline
  pathPolyline.value = L.polyline([], {
    color: '#216093',
    weight: 4,
    opacity: 0.8
  }).addTo(map.value)
}

const fetchPathData = async () => {
  if (!props.asset?.asset_id) return
  
  isLoading.value = true
  
  try {
    const response = await locationsStore.fetchAssetLocationHistory(
      props.asset.asset_id,
      {
        days: localHistoryDays.value,
        limit: localHistoryLimit.value
      }
    )
    
    pathData.value = response.locations || []
    updateMapPath()
  } catch (error) {
    console.error('Failed to fetch path data:', error)
    pathData.value = []
  } finally {
    isLoading.value = false
  }
}

const updateMapPath = () => {
  if (!map.value || !pathData.value.length) return
  
  // Clear existing markers
  markers.value.forEach(marker => map.value.removeLayer(marker))
  markers.value = []
  
  // Prepare coordinates for polyline
  const coordinates = pathData.value.map(point => [
    parseFloat(point.latitude),
    parseFloat(point.longitude)
  ])
  
  // Update polyline
  pathPolyline.value.setLatLngs(coordinates)
  
  // Add start marker (green)
  if (pathData.value.length > 0) {
    const start = pathData.value[0]
    const startMarker = L.marker([start.latitude, start.longitude], {
      icon: createCustomIcon('start')
    }).bindPopup(`
      <strong>Start Point</strong><br>
      Time: ${formatDateTime(start.timestamp)}<br>
      Source: ${formatSource(start.source)}
    `).addTo(map.value)
    markers.value.push(startMarker)
  }
  
  // Add end marker (red)
  if (pathData.value.length > 1) {
    const end = pathData.value[pathData.value.length - 1]
    const endMarker = L.marker([end.latitude, end.longitude], {
      icon: createCustomIcon('end')
    }).bindPopup(`
      <strong>End Point</strong><br>
      Time: ${formatDateTime(end.timestamp)}<br>
      Source: ${formatSource(end.source)}
    `).addTo(map.value)
    markers.value.push(endMarker)
  }
  
  // Add waypoint markers for significant stops
  if (pathData.value.length > 2) {
    const waypoints = pathData.value.slice(1, -1)
    waypoints.forEach((point, index) => {
      // Only show every nth waypoint to avoid clutter
      if (index % Math.max(1, Math.floor(waypoints.length / 10)) === 0) {
        const waypoint = L.marker([point.latitude, point.longitude], {
          icon: createCustomIcon('waypoint')
        }).bindPopup(`
          <strong>Waypoint</strong><br>
          Time: ${formatDateTime(point.timestamp)}<br>
          Source: ${formatSource(point.source)}<br>
          ${point.speed ? `Speed: ${point.speed} km/h` : ''}
        `).addTo(map.value)
        markers.value.push(waypoint)
      }
    })
  }
  
  // Fit map to path bounds
  if (coordinates.length > 0) {
    map.value.fitBounds(pathPolyline.value.getBounds(), { padding: [20, 20] })
  }
}

const createCustomIcon = (type) => {
  const colors = {
    start: '#2E933C',
    end: '#DB162F',
    waypoint: '#216093'
  }
  
  const sizes = {
    start: 30,
    end: 30,
    waypoint: 20
  }
  
  const symbols = {
    start: '🏁',
    end: '🏁',
    waypoint: '📍'
  }
  
  return L.divIcon({
    html: `<div style="
      background-color: ${colors[type]};
      width: ${sizes[type]}px;
      height: ${sizes[type]}px;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: ${type === 'waypoint' ? '12px' : '14px'};
    ">${symbols[type]}</div>`,
    className: 'custom-path-marker',
    iconSize: [sizes[type], sizes[type]],
    iconAnchor: [sizes[type] / 2, sizes[type] / 2]
  })
}

const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371 // Earth's radius in kilometers
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString()
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

const formatDuration = (milliseconds) => {
  const hours = Math.floor(milliseconds / (1000 * 60 * 60))
  const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

const exportPath = (format = 'json') => {
  const timestamp = new Date().toISOString().split('T')[0]
  const filename = `${props.asset.asset_id}_path_${timestamp}`
  
  let content = ''
  let mimeType = 'text/plain'
  let extension = 'txt'
  
  switch (format) {
    case 'json':
      content = generateJSONExport()
      mimeType = 'application/json'
      extension = 'json'
      break
    case 'csv':
      content = generateCSVExport()
      mimeType = 'text/csv'
      extension = 'csv'
      break
    case 'gpx':
      content = generateGPXExport()
      mimeType = 'application/gpx+xml'
      extension = 'gpx'
      break
    case 'kml':
      content = generateKMLExport()
      mimeType = 'application/vnd.google-earth.kml+xml'
      extension = 'kml'
      break
    case 'geojson':
      content = generateGeoJSONExport()
      mimeType = 'application/geo+json'
      extension = 'geojson'
      break
    default:
      content = generateJSONExport()
      mimeType = 'application/json'
      extension = 'json'
  }
  
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${filename}.${extension}`
  a.click()
  URL.revokeObjectURL(url)
}

const generateJSONExport = () => {
  const data = {
    asset: {
      asset_id: props.asset.asset_id,
      make: props.asset.make,
      model: props.asset.model,
      year: props.asset.year,
      vehicle_type: props.asset.vehicle_type,
      status: props.asset.status,
      department: props.asset.department
    },
    pathData: pathData.value,
    statistics: {
      totalDistance: totalDistance.value,
      duration: pathDuration.value,
      averageSpeed: averageSpeed.value,
      dataPoints: pathData.value.length
    },
    exportedAt: new Date().toISOString(),
    exportFormat: 'JSON'
  }
  
  return JSON.stringify(data, null, 2)
}

const generateCSVExport = () => {
  const headers = [
    'Timestamp',
    'Latitude',
    'Longitude',
    'Source',
    'Speed (km/h)',
    'Heading (degrees)',
    'Address'
  ]
  
  const rows = pathData.value.map(point => [
    point.timestamp,
    point.latitude,
    point.longitude,
    formatSource(point.source),
    point.speed || '',
    point.heading || '',
    point.address || ''
  ])
  
  const csvContent = [
    `# Asset Path Export - ${props.asset.asset_id} (${props.asset.make} ${props.asset.model})`,
    `# Generated: ${new Date().toISOString()}`,
    `# Total Distance: ${totalDistance.value.toFixed(2)} km`,
    `# Duration: ${formatDuration(pathDuration.value)}`,
    `# Average Speed: ${averageSpeed.value.toFixed(1)} km/h`,
    `# Data Points: ${pathData.value.length}`,
    '',
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n')
  
  return csvContent
}

const generateGPXExport = () => {
  const gpxHeader = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Fleet Management System" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata>
    <name>${props.asset.asset_id} Path</name>
    <desc>Vehicle path for ${props.asset.make} ${props.asset.model} (${props.asset.asset_id})</desc>
    <time>${new Date().toISOString()}</time>
  </metadata>
  <trk>
    <name>${props.asset.asset_id} Route</name>
    <desc>Distance: ${totalDistance.value.toFixed(2)} km, Duration: ${formatDuration(pathDuration.value)}</desc>
    <trkseg>`

  const trackPoints = pathData.value.map(point => {
    const time = new Date(point.timestamp).toISOString()
    return `      <trkpt lat="${point.latitude}" lon="${point.longitude}">
        <time>${time}</time>
        ${point.speed ? `<speed>${(point.speed / 3.6).toFixed(2)}</speed>` : ''}
        ${point.heading ? `<course>${point.heading}</course>` : ''}
      </trkpt>`
  }).join('\n')

  const gpxFooter = `    </trkseg>
  </trk>
</gpx>`

  return gpxHeader + '\n' + trackPoints + '\n' + gpxFooter
}

const generateKMLExport = () => {
  const kmlHeader = `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>${props.asset.asset_id} Path</name>
    <description>Vehicle path for ${props.asset.make} ${props.asset.model}</description>
    
    <Style id="pathLine">
      <LineStyle>
        <color>ff216093</color>
        <width>4</width>
      </LineStyle>
    </Style>
    
    <Style id="startPoint">
      <IconStyle>
        <color>ff2E933C</color>
        <scale>1.2</scale>
      </IconStyle>
    </Style>
    
    <Style id="endPoint">
      <IconStyle>
        <color>ffDB162F</color>
        <scale>1.2</scale>
      </IconStyle>
    </Style>
    
    <Placemark>
      <name>Start Point</name>
      <description>Start: ${pathData.value[0]?.address || 'Unknown location'}</description>
      <styleUrl>#startPoint</styleUrl>
      <Point>
        <coordinates>${pathData.value[0]?.longitude},${pathData.value[0]?.latitude},0</coordinates>
      </Point>
    </Placemark>
    
    <Placemark>
      <name>End Point</name>
      <description>End: ${pathData.value[pathData.value.length - 1]?.address || 'Unknown location'}</description>
      <styleUrl>#endPoint</styleUrl>
      <Point>
        <coordinates>${pathData.value[pathData.value.length - 1]?.longitude},${pathData.value[pathData.value.length - 1]?.latitude},0</coordinates>
      </Point>
    </Placemark>
    
    <Placemark>
      <name>Vehicle Path</name>
      <description>Distance: ${totalDistance.value.toFixed(2)} km, Duration: ${formatDuration(pathDuration.value)}</description>
      <styleUrl>#pathLine</styleUrl>
      <LineString>
        <coordinates>`

  const coordinates = pathData.value.map(point => 
    `${point.longitude},${point.latitude},0`
  ).join(' ')

  const kmlFooter = `        </coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>`

  return kmlHeader + coordinates + kmlFooter
}

const generateGeoJSONExport = () => {
  const features = [
    // Path LineString
    {
      type: 'Feature',
      properties: {
        name: `${props.asset.asset_id} Path`,
        description: `Vehicle path for ${props.asset.make} ${props.asset.model}`,
        totalDistance: totalDistance.value,
        duration: pathDuration.value,
        averageSpeed: averageSpeed.value,
        dataPoints: pathData.value.length
      },
      geometry: {
        type: 'LineString',
        coordinates: pathData.value.map(point => [
          parseFloat(point.longitude),
          parseFloat(point.latitude)
        ])
      }
    },
    // Start point
    {
      type: 'Feature',
      properties: {
        name: 'Start Point',
        type: 'start',
        timestamp: pathData.value[0]?.timestamp,
        address: pathData.value[0]?.address
      },
      geometry: {
        type: 'Point',
        coordinates: [
          parseFloat(pathData.value[0]?.longitude),
          parseFloat(pathData.value[0]?.latitude)
        ]
      }
    },
    // End point
    {
      type: 'Feature',
      properties: {
        name: 'End Point',
        type: 'end',
        timestamp: pathData.value[pathData.value.length - 1]?.timestamp,
        address: pathData.value[pathData.value.length - 1]?.address
      },
      geometry: {
        type: 'Point',
        coordinates: [
          parseFloat(pathData.value[pathData.value.length - 1]?.longitude),
          parseFloat(pathData.value[pathData.value.length - 1]?.latitude)
        ]
      }
    }
  ]

  const geoJSON = {
    type: 'FeatureCollection',
    properties: {
      asset: {
        asset_id: props.asset.asset_id,
        make: props.asset.make,
        model: props.asset.model,
        year: props.asset.year
      },
      exportedAt: new Date().toISOString()
    },
    features: features
  }

  return JSON.stringify(geoJSON, null, 2)
}

const closeModal = () => {
  emit('update:modelValue', false)
}

// Watchers
watch(() => props.modelValue, async (newValue) => {
  if (newValue) {
    await initializeMap()
    await fetchPathData()
  }
})

// Lifecycle
onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style scoped>
.path-modal {
  height: 90vh;
  display: flex;
  flex-direction: column;
}

.path-map-container {
  height: 500px;
  position: relative;
  background: #f5f5f5;
}

.map-loading-overlay,
.no-data-overlay {
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


.stat-item {
  text-align: center;
  min-width: 80px;
  flex-shrink: 0;
}

.stat-label {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #216093;
  line-height: 1.2;
  margin-top: 2px;
}


:deep(.custom-path-marker) {
  background: transparent !important;
  border: none !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .path-map-container {
    height: 400px;
  }
  
  .stat-item {
    margin-bottom: 16px;
    min-width: 60px;
  }
  
  .stat-value {
    font-size: 16px;
  }
}
</style>