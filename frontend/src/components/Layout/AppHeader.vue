<template>
  <header class="header">
    <div class="header-content">
      <div class="header-left">
        <button class="menu-toggle" @click="$emit('toggle-sidebar')">
          <i class="ri-menu-2-line"></i>
        </button>
      </div>

      <div class="header-right">
        <div class="user-info">
          <div class="user-avatar">
            {{ userInitials }}
          </div>
          <div class="user-details" v-if="!isMobile">
            <div class="user-name">{{ userStore.user?.full_name }}</div>
            <div class="user-role">{{ roleLabel }}</div>
          </div>
        </div>
        
        <button class="logout-icon-btn" @click="handleLogout" title="Выйти">
          <i class="ri-logout-box-r-line"></i>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

defineEmits(['toggle-sidebar'])

const router = useRouter()
const userStore = useUserStore()
const isMobile = ref(window.innerWidth <= 1024)

const updateIsMobile = () => {
  isMobile.value = window.innerWidth <= 1024
}

onMounted(() => window.addEventListener('resize', updateIsMobile))
onUnmounted(() => window.removeEventListener('resize', updateIsMobile))

const roleLabels = {
  admin: 'Администратор',
  manager: 'Менеджер',
  worker: 'Сотрудник',
  wholesaler: 'Оптовик'
}

const roleLabel = computed(() => roleLabels[userStore.user?.role] || '')

const userInitials = computed(() => {
  const name = userStore.user?.full_name || ''
  const parts = name.split(' ')
  return parts.length > 1 
    ? (parts[0][0] + parts[1][0]).toUpperCase()
    : parts[0]?.slice(0, 2).toUpperCase() || '??'
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.header {
  background: white;
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
  position: sticky;
  top: 0;
  z-index: 100;
  height: 70px;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
}

.menu-toggle {
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.menu-toggle:hover {
  background: #f1f5f9;
  color: #3b82f6;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-right: 1.25rem;
  border-right: 1px solid #f1f5f9;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #eff6ff;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1e293b;
}

.user-role {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 600;
}

.logout-icon-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-icon-btn:hover {
  color: #ef4444;
}

@media (max-width: 1024px) {
  .header-content {
    padding: 0 1rem;
  }
}
</style>
