<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header (Optional) -->
      <header class="bg-white shadow-sm z-10 p-4 flex justify-between items-center">
        <h2 class="text-xl font-semibold text-gray-800">{{ currentRouteName }}</h2>
        <div class="flex items-center space-x-4">
           <!-- User Info / Logout could go here -->
           <span>Администратор</span>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'

const route = useRoute()
const currentRouteName = computed(() => {
  // Map route names to display titles if needed
  const titles = {
    'AdminDashboard': 'Дашборд',
    'Finance': 'Финансы',
    'StaffManagement': 'Персонал',
    'AdminProducts': 'Склад и Товары',
    'Expenses': 'Расходы',
    'Reports': 'Отчеты'
  }
  return titles[route.name] || 'Админ-панель'
})
</script>
