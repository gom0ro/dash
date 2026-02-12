<template>
  <div class="main-layout">
    <Sidebar :is-open="isSidebarOpen" />
    
    <div class="layout-content">
      <AppHeader @toggle-sidebar="toggleSidebar" />
      
      <main class="main-container">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from '@/components/Sidebar.vue'
import AppHeader from '@/components/Layout/AppHeader.vue'

const isSidebarOpen = ref(true)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  background-color: #f3f4f6;
}

.layout-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  /* Sidebar handles its own width/visibility, so Flexbox takes care of the rest */
}

.main-container {
  flex: 1;
  padding: 2rem;
  overflow-x: auto;
}
</style>