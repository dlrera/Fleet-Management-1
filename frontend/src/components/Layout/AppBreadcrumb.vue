<template>
  <nav aria-label="breadcrumb" class="app-breadcrumb mb-4">
    <ol class="breadcrumb mb-0">
      <li 
        v-for="(crumb, index) in breadcrumbs" 
        :key="index"
        class="breadcrumb-item"
        :class="{ 'active': index === breadcrumbs.length - 1 }"
      >
        <router-link 
          v-if="index < breadcrumbs.length - 1 && crumb.to"
          :to="crumb.to"
          class="text-decoration-none"
        >
          <i v-if="crumb.icon" :class="crumb.icon" class="me-1"></i>
          {{ crumb.text }}
        </router-link>
        <span v-else>
          <i v-if="crumb.icon" :class="crumb.icon" class="me-1"></i>
          {{ crumb.text }}
        </span>
      </li>
    </ol>
  </nav>
</template>

<script>
export default {
  name: 'AppBreadcrumb',
  computed: {
    breadcrumbs() {
      const route = this.$route
      const breadcrumbs = []
      
      // Always start with Dashboard
      breadcrumbs.push({
        text: 'Dashboard',
        to: '/dashboard',
        icon: 'bi bi-house'
      })
      
      // Generate breadcrumbs based on current route
      const pathSegments = route.path.split('/').filter(segment => segment)
      
      let currentPath = ''
      pathSegments.forEach((segment, index) => {
        currentPath += `/${segment}`
        
        // Skip dashboard as it's already added
        if (segment === 'dashboard') return
        
        const breadcrumb = this.generateBreadcrumb(segment, currentPath, index, pathSegments)
        if (breadcrumb) {
          breadcrumbs.push(breadcrumb)
        }
      })
      
      // If we have route meta title, use it for the last breadcrumb
      if (route.meta?.title && breadcrumbs.length > 0) {
        breadcrumbs[breadcrumbs.length - 1].text = route.meta.title
      }
      
      return breadcrumbs
    }
  },
  methods: {
    generateBreadcrumb(segment, path, index, segments) {
      const breadcrumbMap = {
        'assets': { text: 'Assets', icon: 'bi bi-truck' },
        'drivers': { text: 'Drivers', icon: 'bi bi-person-badge' },
        'maintenance': { text: 'Maintenance', icon: 'bi bi-tools' },
        'work-orders': { text: 'Work Orders', icon: 'bi bi-clipboard-check' },
        'tracking': { text: 'Tracking', icon: 'bi bi-geo-alt' },
        'reports': { text: 'Reports', icon: 'bi bi-graph-up' },
        'settings': { text: 'Settings', icon: 'bi bi-gear' },
        'departments': { text: 'Departments', icon: 'bi bi-building' },
        'create': { text: 'Create', icon: 'bi bi-plus-circle' },
        'edit': { text: 'Edit', icon: 'bi bi-pencil' },
        'view': { text: 'View', icon: 'bi bi-eye' },
        'schedules': { text: 'Schedules', icon: 'bi bi-calendar-check' },
        'records': { text: 'Records', icon: 'bi bi-journal-text' },
        'parts': { text: 'Parts', icon: 'bi bi-gear-wide-connected' },
        'due': { text: 'Due Maintenance', icon: 'bi bi-exclamation-triangle' },
        'training': { text: 'Training', icon: 'bi bi-mortarboard' },
        'incidents': { text: 'Incidents', icon: 'bi bi-exclamation-triangle-fill' },
        'board': { text: 'Kanban Board', icon: 'bi bi-kanban' },
        'live': { text: 'Live Tracking', icon: 'bi bi-broadcast' },
        'trips': { text: 'Trips', icon: 'bi bi-map' },
        'zones': { text: 'Geofences', icon: 'bi bi-geo-alt-fill' },
        'routes': { text: 'Routes', icon: 'bi bi-signpost-2' },
        'profile': { text: 'Profile', icon: 'bi bi-person' }
      }
      
      const breadcrumb = breadcrumbMap[segment]
      
      if (breadcrumb) {
        return {
          text: breadcrumb.text,
          icon: breadcrumb.icon,
          to: index < segments.length - 1 ? path : null
        }
      }
      
      // If it looks like an ID (UUID or number), don't show it
      if (segment.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i) || 
          segment.match(/^\d+$/)) {
        return null
      }
      
      // Default: capitalize the segment
      return {
        text: segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' '),
        to: index < segments.length - 1 ? path : null
      }
    }
  }
}
</script>

<style scoped>
.app-breadcrumb .breadcrumb {
  background-color: transparent;
  padding: 0;
}

.app-breadcrumb .breadcrumb-item {
  font-size: 0.9rem;
}

.app-breadcrumb .breadcrumb-item a {
  color: #6c757d;
}

.app-breadcrumb .breadcrumb-item a:hover {
  color: #0d6efd;
}

.app-breadcrumb .breadcrumb-item.active {
  color: #495057;
  font-weight: 500;
}

.app-breadcrumb .breadcrumb-item + .breadcrumb-item::before {
  content: ">";
  color: #6c757d;
}
</style>