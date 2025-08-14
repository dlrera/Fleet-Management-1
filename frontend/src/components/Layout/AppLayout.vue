<template>
  <div class="app-layout">
    <!-- Header/Navbar -->
    <AppHeader />
    
    <!-- Main Content Area -->
    <div class="main-container">
      <!-- Sidebar Navigation -->
      <AppSidebar />
      
      <!-- Page Content -->
      <main class="page-content">
        <div class="container-fluid">
          <!-- Breadcrumb -->
          <AppBreadcrumb v-if="showBreadcrumb" />
          
          <!-- Page Content -->
          <router-view />
        </div>
      </main>
    </div>
    
    <!-- Toast Notifications -->
    <AppToasts />
  </div>
</template>

<script>
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppBreadcrumb from './AppBreadcrumb.vue'
import AppToasts from './AppToasts.vue'

export default {
  name: 'AppLayout',
  components: {
    AppHeader,
    AppSidebar,
    AppBreadcrumb,
    AppToasts
  },
  computed: {
    showBreadcrumb() {
      return this.$route.meta?.showBreadcrumb !== false
    }
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-container {
  display: flex;
  flex: 1;
}

.page-content {
  flex: 1;
  padding: 20px;
  background-color: #f8f9fa;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .page-content {
    padding: 15px;
  }
}
</style>