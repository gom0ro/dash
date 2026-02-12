<template>
  <div class="sidebar" :class="{ 'closed': !isOpen }">
    <div class="sidebar-header">
      <h1 class="logo">CRM System</h1>
      <p class="role-badge">{{ userRoleLabel }}</p>
    </div>

    <nav class="sidebar-nav">
      <ul class="nav-list">
        <li v-for="link in currentLinks" :key="link.to">
          <router-link :to="link.to" class="nav-link" active-class="active">
            <i :class="[link.icon, 'nav-icon']"></i>
            <span class="text">{{ link.label }}</span>
          </router-link>
        </li>
      </ul>
    </nav>
    
    <div class="sidebar-footer">
        <button @click="logout" class="logout-btn">
            <i class="ri-logout-box-r-line nav-icon"></i>
            <span class="text">Выход</span>
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
  }
})

const userStore = useUserStore()
const router = useRouter()

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
  background: #1f2937;
  color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
  transition: width 0.3s ease;
  overflow: hidden;
  flex-shrink: 0;
}

.sidebar.closed {
  width: 0;
  padding: 0;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #374151;
}

.logo {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  white-space: nowrap;
}

.role-badge {
  font-size: 0.875rem;
  color: #9ca3af;
  margin-top: 0.25rem;
  white-space: nowrap;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  color: #d1d5db;
  text-decoration: none;
  transition: all 0.2s;
  white-space: nowrap;
}

.nav-link:hover {
  background: #374151;
  color: white;
}

.nav-link.active {
  background: #374151;
  color: white;
  border-left: 4px solid #667eea;
}

.nav-icon {
  margin-right: 0.75rem;
  font-size: 1.2rem;
  width: 1.5rem;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #374151;
}

.logout-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.75rem;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  font-size: 1rem;
}

.logout-btn:hover {
  color: white;
}
</style>
