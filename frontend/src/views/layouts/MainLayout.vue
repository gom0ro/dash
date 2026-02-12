<template>
  <div class="main-layout" :class="{ 'sidebar-collapsed': !isSidebarOpen && !isMobile }">
    <!-- Overlay for mobile -->
    <div 
      v-if="isMobile && isSidebarOpen" 
      class="mobile-overlay" 
      @click="isSidebarOpen = false"
    ></div>

    <Sidebar 
      :is-open="isSidebarOpen" 
      :is-mobile="isMobile"
      @toggle="toggleSidebar"
      @close="isSidebarOpen = false"
    />
    
    <div class="layout-content">
      <AppHeader @toggle-sidebar="toggleSidebar" />
      
      <main class="main-container">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'
import AppHeader from '@/components/Layout/AppHeader.vue'

const route = useRoute()
const isSidebarOpen = ref(window.innerWidth > 1024)
const isMobile = ref(window.innerWidth <= 1024)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const updateLayout = () => {
  const width = window.innerWidth
  isMobile.value = width <= 1024
  if (width > 1024) {
    isSidebarOpen.value = true
  } else {
    isSidebarOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', updateLayout)
  updateLayout()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateLayout)
})

// Close sidebar on mobile when route changes
watch(() => route.path, () => {
  if (isMobile.value) {
    isSidebarOpen.value = false
  }
})
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  background-color: #f8fafc;
  transition: all 0.3s ease;
}

.layout-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: all 0.3s ease;
}

.main-container {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
}

.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 999;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .main-container {
    padding: 1rem;
  }
}
</style>