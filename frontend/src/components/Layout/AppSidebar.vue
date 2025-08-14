<template>
  <aside class="app-sidebar" :class="{ 'collapsed': isCollapsed }">
    <div class="sidebar-content">
      <nav class="sidebar-nav">
        <ul class="nav flex-column">
          <!-- Dashboard -->
          <li class="nav-item">
            <router-link 
              class="nav-link"
              to="/dashboard"
              :class="{ 'active': $route.path === '/dashboard' }"
            >
              <i class="bi bi-speedometer2"></i>
              <span class="nav-text">Dashboard</span>
            </router-link>
          </li>
          
          <!-- Assets -->
          <li class="nav-item">
            <a 
              class="nav-link"
              :class="{ 'active': isActiveSection('assets') }"
              @click="toggleSection('assets')"
              data-bs-toggle="collapse"
              :data-bs-target="'#assets-menu'"
              :aria-expanded="openSections.includes('assets')"
            >
              <i class="bi bi-truck"></i>
              <span class="nav-text">Assets</span>
              <i class="bi bi-chevron-down ms-auto expand-icon"></i>
            </a>
            <div 
              class="collapse" 
              id="assets-menu"
              :class="{ 'show': openSections.includes('assets') }"
            >
              <ul class="nav flex-column sub-menu">
                <li class="nav-item">
                  <router-link class="nav-link" to="/assets">
                    <span class="nav-text">All Assets</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/assets/create">
                    <span class="nav-text">Add Asset</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/departments">
                    <span class="nav-text">Departments</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
          
          <!-- Drivers -->
          <li class="nav-item">
            <a 
              class="nav-link"
              :class="{ 'active': isActiveSection('drivers') }"
              @click="toggleSection('drivers')"
              data-bs-toggle="collapse"
              :data-bs-target="'#drivers-menu'"
              :aria-expanded="openSections.includes('drivers')"
            >
              <i class="bi bi-person-badge"></i>
              <span class="nav-text">Drivers</span>
              <i class="bi bi-chevron-down ms-auto expand-icon"></i>
            </a>
            <div 
              class="collapse" 
              id="drivers-menu"
              :class="{ 'show': openSections.includes('drivers') }"
            >
              <ul class="nav flex-column sub-menu">
                <li class="nav-item">
                  <router-link class="nav-link" to="/drivers">
                    <span class="nav-text">All Drivers</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/drivers/create">
                    <span class="nav-text">Add Driver</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/drivers/training">
                    <span class="nav-text">Training</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/drivers/incidents">
                    <span class="nav-text">Incidents</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
          
          <!-- Maintenance -->
          <li class="nav-item">
            <a 
              class="nav-link"
              :class="{ 'active': isActiveSection('maintenance') }"
              @click="toggleSection('maintenance')"
              data-bs-toggle="collapse"
              :data-bs-target="'#maintenance-menu'"
              :aria-expanded="openSections.includes('maintenance')"
            >
              <i class="bi bi-tools"></i>
              <span class="nav-text">Maintenance</span>
              <i class="bi bi-chevron-down ms-auto expand-icon"></i>
            </a>
            <div 
              class="collapse" 
              id="maintenance-menu"
              :class="{ 'show': openSections.includes('maintenance') }"
            >
              <ul class="nav flex-column sub-menu">
                <li class="nav-item">
                  <router-link class="nav-link" to="/maintenance/schedules">
                    <span class="nav-text">Schedules</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/maintenance/records">
                    <span class="nav-text">Records</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/maintenance/parts">
                    <span class="nav-text">Parts Inventory</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/maintenance/due">
                    <span class="nav-text">Due Maintenance</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
          
          <!-- Work Orders -->
          <li class="nav-item">
            <a 
              class="nav-link"
              :class="{ 'active': isActiveSection('work-orders') }"
              @click="toggleSection('work-orders')"
              data-bs-toggle="collapse"
              :data-bs-target="'#workorders-menu'"
              :aria-expanded="openSections.includes('work-orders')"
            >
              <i class="bi bi-clipboard-check"></i>
              <span class="nav-text">Work Orders</span>
              <i class="bi bi-chevron-down ms-auto expand-icon"></i>
            </a>
            <div 
              class="collapse" 
              id="workorders-menu"
              :class="{ 'show': openSections.includes('work-orders') }"
            >
              <ul class="nav flex-column sub-menu">
                <li class="nav-item">
                  <router-link class="nav-link" to="/work-orders">
                    <span class="nav-text">All Work Orders</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/work-orders/create">
                    <span class="nav-text">Create Work Order</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/work-orders/board">
                    <span class="nav-text">Kanban Board</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
          
          <!-- Tracking -->
          <li class="nav-item">
            <a 
              class="nav-link"
              :class="{ 'active': isActiveSection('tracking') }"
              @click="toggleSection('tracking')"
              data-bs-toggle="collapse"
              :data-bs-target="'#tracking-menu'"
              :aria-expanded="openSections.includes('tracking')"
            >
              <i class="bi bi-geo-alt"></i>
              <span class="nav-text">Tracking</span>
              <i class="bi bi-chevron-down ms-auto expand-icon"></i>
            </a>
            <div 
              class="collapse" 
              id="tracking-menu"
              :class="{ 'show': openSections.includes('tracking') }"
            >
              <ul class="nav flex-column sub-menu">
                <li class="nav-item">
                  <router-link class="nav-link" to="/tracking/live">
                    <span class="nav-text">Live Tracking</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/tracking/trips">
                    <span class="nav-text">Trips</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/tracking/zones">
                    <span class="nav-text">Geofences</span>
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/tracking/routes">
                    <span class="nav-text">Routes</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
        </ul>
        
        <!-- Divider -->
        <hr class="sidebar-divider">
        
        <!-- System -->
        <ul class="nav flex-column">
          <li class="nav-item">
            <router-link 
              class="nav-link"
              to="/reports"
              :class="{ 'active': $route.path.startsWith('/reports') }"
            >
              <i class="bi bi-graph-up"></i>
              <span class="nav-text">Reports</span>
            </router-link>
          </li>
          
          <li class="nav-item">
            <router-link 
              class="nav-link"
              to="/settings"
              :class="{ 'active': $route.path.startsWith('/settings') }"
            >
              <i class="bi bi-gear"></i>
              <span class="nav-text">Settings</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </div>
    
    <!-- Sidebar Toggle Button (for mobile) -->
    <button 
      class="sidebar-toggle d-lg-none"
      @click="$emit('toggle')"
    >
      <i class="bi bi-x-lg"></i>
    </button>
  </aside>
</template>

<script>
export default {
  name: 'AppSidebar',
  props: {
    isCollapsed: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      openSections: []
    }
  },
  mounted() {
    // Auto-expand section based on current route
    this.expandCurrentSection()
  },
  watch: {
    '$route'() {
      this.expandCurrentSection()
    }
  },
  methods: {
    toggleSection(section) {
      if (this.openSections.includes(section)) {
        this.openSections = this.openSections.filter(s => s !== section)
      } else {
        this.openSections.push(section)
      }
    },
    
    isActiveSection(section) {
      return this.$route.path.startsWith(`/${section}`)
    },
    
    expandCurrentSection() {
      const path = this.$route.path
      
      if (path.startsWith('/assets') || path.startsWith('/departments')) {
        if (!this.openSections.includes('assets')) {
          this.openSections.push('assets')
        }
      } else if (path.startsWith('/drivers')) {
        if (!this.openSections.includes('drivers')) {
          this.openSections.push('drivers')
        }
      } else if (path.startsWith('/maintenance')) {
        if (!this.openSections.includes('maintenance')) {
          this.openSections.push('maintenance')
        }
      } else if (path.startsWith('/work-orders')) {
        if (!this.openSections.includes('work-orders')) {
          this.openSections.push('work-orders')
        }
      } else if (path.startsWith('/tracking')) {
        if (!this.openSections.includes('tracking')) {
          this.openSections.push('tracking')
        }
      }
    }
  }
}
</script>

<style scoped>
.app-sidebar {
  width: 280px;
  min-height: 100vh;
  background: #fff;
  border-right: 1px solid #dee2e6;
  transition: all 0.3s ease;
  position: relative;
}

.app-sidebar.collapsed {
  width: 60px;
}

.app-sidebar.collapsed .nav-text {
  display: none;
}

.app-sidebar.collapsed .expand-icon {
  display: none;
}

.sidebar-content {
  padding: 1rem 0;
  height: 100%;
  overflow-y: auto;
}

.sidebar-nav .nav-link {
  padding: 12px 20px;
  color: #495057;
  text-decoration: none;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  border-radius: 0;
}

.sidebar-nav .nav-link:hover {
  background-color: #f8f9fa;
  color: #0d6efd;
}

.sidebar-nav .nav-link.active {
  background-color: #e3f2fd;
  color: #0d6efd;
  border-right: 3px solid #0d6efd;
}

.sidebar-nav .nav-link i {
  width: 20px;
  margin-right: 12px;
  text-align: center;
  font-size: 1.1rem;
}

.sub-menu {
  background-color: #f8f9fa;
  padding-left: 0;
}

.sub-menu .nav-link {
  padding: 8px 20px 8px 52px;
  font-size: 0.9rem;
}

.sub-menu .nav-link.active {
  background-color: #e3f2fd;
  border-right: 3px solid #0d6efd;
}

.expand-icon {
  transition: transform 0.2s ease;
}

.nav-link[aria-expanded="true"] .expand-icon {
  transform: rotate(180deg);
}

.sidebar-divider {
  margin: 1rem 20px;
  border-color: #dee2e6;
}

.sidebar-toggle {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #6c757d;
  padding: 5px;
  border-radius: 4px;
}

.sidebar-toggle:hover {
  background-color: #f8f9fa;
  color: #495057;
}

/* Mobile Responsiveness */
@media (max-width: 991.98px) {
  .app-sidebar {
    position: fixed;
    left: -280px;
    top: 0;
    z-index: 1040;
    height: 100vh;
    box-shadow: 2px 0 5px rgba(0,0,0,0.1);
  }
  
  .app-sidebar.show {
    left: 0;
  }
}

/* Scrollbar Styling */
.sidebar-content::-webkit-scrollbar {
  width: 4px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>