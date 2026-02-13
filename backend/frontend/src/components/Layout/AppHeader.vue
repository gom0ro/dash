<template>
  <header class="header">
    <div class="header-content">
      <div class="header-right">
        <div class="user-info">
          <div class="user-avatar">
            {{ userInitials }}
          </div>
          <div class="user-details">
            <div class="user-name">{{ userStore.user?.full_name }}</div>
            <div class="user-role">{{ roleLabel }}</div>
          </div>
        </div>
        
        <AppButton variant="secondary" size="sm" @click="handleLogout">
          Выйти
        </AppButton>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AppButton from '@/components/UI/AppButton.vue'

const router = useRouter()
const userStore = useUserStore()

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
  return parts.map(p => p[0]).join('').toUpperCase().slice(0, 2)
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.header {
  background: #2c3e50;
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0.75rem 2rem;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 500;
}

.user-role {
  font-size: 0.75rem;
  opacity: 0.8;
}

@media (max-width: 1024px) {
  .header-content {
    padding: 1rem;
    flex-wrap: wrap;
  }
  
  .header-nav {
    order: 3;
    width: 100%;
  }
  
  .user-details {
    display: none;
  }
}
</style>