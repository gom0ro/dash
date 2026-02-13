<!-- frontend/src/views/NotFound.vue -->
<template>
  <div class="not-found">
    <div class="content">
      <div class="icon">404</div>
      <h1>Страница не найдена</h1>
      <p>Запрашиваемая страница не существует</p>
      <AppButton @click="goHome">
        Вернуться на главную
      </AppButton>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AppButton from '@/components/UI/AppButton.vue'

const router = useRouter()
const userStore = useUserStore()

const goHome = () => {
  const defaultRoutes = {
    admin: '/admin/dashboard',
    manager: '/manager/orders',
    worker: '/employee/tasks',
    wholesaler: '/wholesaler/catalog'
  }
  router.push(defaultRoutes[userStore.user?.role] || '/')
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.content {
  text-align: center;
  background: white;
  padding: 4rem 3rem;
  border-radius: 12px;
  max-width: 500px;
}

.icon {
  font-size: 6rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 1.5rem;
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 1rem;
  color: #111827;
}

p {
  margin: 0 0 2rem;
  color: #6b7280;
  font-size: 1.125rem;
}
</style>