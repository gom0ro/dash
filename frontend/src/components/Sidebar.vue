<template>
  <div 
    class="sidebar" 
    :class="{ 
      'closed': !isOpen && !isMobile, 
      'mobile-open': isOpen && isMobile 
    }"
  >
    <div class="sidebar-header">
      <div class="logo-area">
        <div class="logo-box">G</div>
        <h1 class="logo" v-if="isOpen || isMobile">Dash<span>board</span></h1>
      </div>
      <p class="role-badge" v-if="isOpen || isMobile">{{ userRoleLabel }}</p>
      <button v-if="isMobile" @click="$emit('toggle')" class="close-mobile">
        <i class="ri-close-line"></i>
      </button>
    </div>

    <nav class="sidebar-nav">
      <ul class="nav-list">
        <li v-for="link in currentLinks" :key="link.to">
          <router-link 
            :to="link.to" 
            class="nav-link" 
            active-class="active"
            @click="onLinkClick"
          >
            <i :class="[link.icon, 'nav-icon']"></i>
            <span class="text" v-if="isOpen || isMobile">{{ link.label }}</span>
          </router-link>
        </li>
      </ul>
    </nav>
    
    <div class="sidebar-footer">
        <button @click="logout" class="logout-btn">
            <i class="ri-logout-box-r-line nav-icon"></i>
            <span class="text" v-if="isOpen || isMobile">Выход</span>
        </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: true
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle', 'close'])

const userStore = useUserStore()
const router = useRouter()

const onLinkClick = () => {
  if (props.isMobile) {
    emit('close')
  }
}

const userRoleLabel = computed(() => {
  const roles = {
    admin: 'Администратор',
    manager: 'Менеджер',
    worker: 'Сотрудник',
    wholesaler: 'Оптовик'
  }
  return roles[userStore.user?.role] || 'Пользователь'
})

const menuItems = {
  admin: [
    { to: '/admin/dashboard', label: 'Дашборд', icon: 'ri-dashboard-3-line' },
    { to: '/admin/warehouse', label: 'Склад', icon: 'ri-archive-line' },
    { to: '/admin/products', label: 'Товары', icon: 'ri-price-tag-3-line' },
    { to: '/admin/staff', label: 'Персонал', icon: 'ri-group-line' },
    { to: '/admin/finance', label: 'Касса', icon: 'ri-wallet-line' },
    { to: '/admin/expenses', label: 'Расходы', icon: 'ri-money-dollar-circle-line' },
    { to: '/admin/reports', label: 'Отчеты', icon: 'ri-bar-chart-box-line' },
    { to: '/admin/salaries', label: 'Зарплаты', icon: 'ri-bank-card-line' },
    { to: '/admin/wip', label: 'Временный склад', icon: 'ri-hammer-line' },
    { to: '/manager/orders', label: 'Заказы', icon: 'ri-file-list-3-line' }
  ],
  manager: [
    { to: '/manager/orders', label: 'Заказы', icon: 'ri-file-list-3-line' },
    { to: '/manager/orders/create', label: 'Новый заказ', icon: 'ri-add-box-line' }
  ],
  worker: [
    { to: '/employee/tasks', label: 'Мои задачи', icon: 'ri-list-check' },
    { to: '/employee/salary', label: 'Зарплата', icon: 'ri-money-cny-box-line' }
  ],
  wholesaler: [
    { to: '/wholesaler/catalog', label: 'Каталог', icon: 'ri-book-open-line' },
    { to: '/wholesaler/my-orders', label: 'Мои заказы', icon: 'ri-shopping-cart-2-line' },
    { to: '/wholesaler/profile', label: 'Профиль', icon: 'ri-user-settings-line' }
  ]
}

const currentLinks = computed(() => {
  const role = userStore.user?.role
  return menuItems[role] || []
})

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  background: #1e293b;
  color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  flex-shrink: 0;
  z-index: 1000;
  border-right: 1px solid rgba(255,255,255,0.05);
}

.sidebar.closed {
  width: 80px;
}

@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    left: -260px;
    width: 260px;
  }
  
  .sidebar.mobile-open {
    left: 0;
    box-shadow: 20px 0 50px rgba(0,0,0,0.3);
  }

  .sidebar.closed {
    width: 260px;
  }
}

.sidebar-header {
  padding: 1.5rem;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.logo-box {
  width: 32px;
  height: 32px;
  background: #3b82f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 1.2rem;
}

.logo {
  font-size: 1.25rem;
  font-weight: 800;
  margin: 0;
  white-space: nowrap;
  letter-spacing: -0.5px;
}

.logo span { color: #3b82f6; }

.role-badge {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: -2px;
  white-space: nowrap;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.close-mobile {
  position: absolute;
  top: 1.5rem;
  right: 1.25rem;
  background: rgba(255,255,255,0.05);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0.75rem;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.85rem 1rem;
  color: #94a3b8;
  text-decoration: none;
  transition: all 0.2s;
  white-space: nowrap;
  border-radius: 12px;
  font-weight: 600;
}

.sidebar.closed .nav-link {
  justify-content: center;
  padding: 0.85rem 0;
}

.nav-link:hover {
  background: rgba(255,255,255,0.03);
  color: white;
}

.nav-link.active {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.nav-icon {
  font-size: 1.4rem;
  min-width: 24px;
  display: flex;
  justify-content: center;
}

.sidebar:not(.closed) .nav-icon {
  margin-right: 12px;
}

.sidebar-footer {
  padding: 1rem 0.75rem;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.logout-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.85rem 1rem;
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  font-weight: 600;
  border-radius: 12px;
}

.sidebar.closed .logout-btn {
  justify-content: center;
  padding: 0.85rem 0;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}
</style>
