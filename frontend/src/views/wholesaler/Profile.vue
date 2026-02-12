<template>
  <div class="profile-view">
    <div class="page-header">
      <h1>Мой профиль</h1>
      <p class="subtitle">Управляйте своими контактными данными для оформления заказов</p>
    </div>

    <div class="profile-container">
      <div class="profile-card card">
        <div class="card-header">
          <h3>Контактная информация</h3>
        </div>
        <div class="card-body">
          <form @submit.prevent="handleUpdateProfile" class="profile-form">
            <div class="form-grid">
              <div class="form-group">
                <label class="label">ФИО / Название компании</label>
                <input 
                  v-model="form.full_name" 
                  type="text" 
                  class="input" 
                  placeholder="Введите полное имя"
                  required
                >
              </div>

              <div class="form-group">
                <label class="label">Email</label>
                <input 
                  v-model="form.email" 
                  type="email" 
                  class="input" 
                  placeholder="email@example.com"
                  required
                >
              </div>

              <div class="form-group">
                <label class="label">Номер телефона</label>
                <input 
                  v-model="form.phone" 
                  type="tel" 
                  class="input" 
                  placeholder="+7 (___) ___-__-__"
                >
              </div>

              <div class="form-group full-width">
                <label class="label">Адрес доставки (по умолчанию)</label>
                <textarea 
                  v-model="form.address" 
                  class="textarea" 
                  rows="3" 
                  placeholder="Укажите город, улицу, дом..."
                ></textarea>
              </div>
            </div>

            <div v-if="message" :class="['message', messageType]">
              {{ message }}
            </div>

            <div class="form-actions">
              <AppButton 
                type="submit" 
                variant="primary" 
                :loading="loading"
                full-width
              >
                Сохранить изменения
              </AppButton>
            </div>
          </form>
        </div>
      </div>

      <div class="stats-sidebar">
        <div class="stat-card card pink-gradient">
          <div class="stat-icon"><i class="ri-box-3-line"></i></div>
          <div class="stat-content">
            <div class="stat-label">Всего заказов</div>
            <div class="stat-value">{{ orderCount }}</div>
          </div>
        </div>
        <div class="stat-card card blue-gradient">
          <div class="stat-icon"><i class="ri-vip-diamond-line"></i></div>
          <div class="stat-content">
            <div class="stat-label">Статус</div>
            <div class="stat-value">Оптовик</div>
          </div>
        </div>
      </div>

      <div class="profile-card card security-card">
        <div class="card-header">
          <h3>Безопасность</h3>
        </div>
        <div class="card-body">
          <form @submit.prevent="handleChangePassword" class="password-form">
            <div class="form-grid">
              <div class="form-group">
                <label class="label">Новый пароль</label>
                <input 
                  v-model="passwordForm.password" 
                  type="password" 
                  class="input" 
                  placeholder="••••••••"
                  required
                >
              </div>
              <div class="form-group">
                <label class="label">Подтвердите пароль</label>
                <input 
                  v-model="passwordForm.confirm" 
                  type="password" 
                  class="input" 
                  placeholder="••••••••"
                  required
                >
              </div>
            </div>

            <div v-if="passwordMessage" :class="['message', passwordMessageType]">
              {{ passwordMessage }}
            </div>

            <div class="form-actions">
              <AppButton 
                type="submit" 
                variant="outline" 
                :loading="changingPassword"
                full-width
              >
                Обновить пароль
              </AppButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useOrdersStore } from '@/stores/orders'
import { usersAPI } from '@/api'
import AppButton from '@/components/UI/AppButton.vue'

const userStore = useUserStore()
const ordersStore = useOrdersStore()

const loading = ref(false)
const message = ref('')
const messageType = ref('success')

const form = ref({
  full_name: '',
  email: '',
  phone: '',
  address: ''
})

const passwordForm = ref({
  password: '',
  confirm: ''
})

const changingPassword = ref(false)
const passwordMessage = ref('')
const passwordMessageType = ref('success')

const orderCount = computed(() => {
  return ordersStore.orders.filter(o => o.wholesaler_id === userStore.user?.id).length
})

const loadProfile = () => {
  if (userStore.user) {
    form.value = {
      full_name: userStore.user.full_name || '',
      email: userStore.user.email || '',
      phone: userStore.user.phone || '',
      address: userStore.user.address || ''
    }
  }
}

const handleUpdateProfile = async () => {
  loading.value = true
  message.value = ''
  
  try {
    if (!userStore.user?.id) throw new Error('Пользователь не авторизован')
    
    const { data } = await usersAPI.update(userStore.user.id, form.value)
    // Синхронизируем данные во всем приложении
    await userStore.fetchUserData()
    message.value = 'Профиль успешно обновлен!'
    messageType.value = 'success'
  } catch (err) {
    console.error('Update error:', err)
    message.value = err.response?.data?.detail || err.message || 'Ошибка при обновлении профиля'
    messageType.value = 'error'
  } finally {
    loading.value = false
    setTimeout(() => message.value = '', 5000)
  }
}

const handleChangePassword = async () => {
  if (passwordForm.value.password !== passwordForm.value.confirm) {
    passwordMessage.value = 'Пароли не совпадают'
    passwordMessageType.value = 'error'
    return
  }

  if (passwordForm.value.password.length < 6) {
    passwordMessage.value = 'Пароль должен быть не менее 6 символов'
    passwordMessageType.value = 'error'
    return
  }

  changingPassword.value = true
  passwordMessage.value = ''
  
  try {
    await usersAPI.update(userStore.user.id, { password: passwordForm.value.password })
    passwordMessage.value = 'Пароль успешно изменен!'
    passwordMessageType.value = 'success'
    passwordForm.value.password = ''
    passwordForm.value.confirm = ''
  } catch (err) {
    passwordMessage.value = err.response?.data?.detail || 'Ошибка при смене пароля'
    passwordMessageType.value = 'error'
  } finally {
    changingPassword.value = false
    setTimeout(() => passwordMessage.value = '', 5000)
  }
}

onMounted(() => {
  loadProfile()
  ordersStore.fetchOrders()
})
</script>

<style scoped>
.profile-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.subtitle {
  color: #6b7280;
  margin-top: 0.5rem;
}

.profile-container {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
}

.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f3f4f6;
}

.card-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.card-body {
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.full-width {
  grid-column: 1 / -1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.input, .textarea {
  padding: 0.75rem 1rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.2s;
}

.input:focus, .textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.form-actions {
  margin-top: 2rem;
}

.security-card {
  margin-top: 2rem;
}

.stats-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stat-card {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  color: white;
}

.pink-gradient {
  background: linear-gradient(135deg, #ec4899 0%, #d946ef 100%);
}

.blue-gradient {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-icon {
  font-size: 2rem;
  background: rgba(255, 255, 255, 0.2);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.9;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
}

.message {
  padding: 1rem;
  border-radius: 10px;
  margin-top: 1.5rem;
  font-weight: 600;
  text-align: center;
}

.message.success {
  background: #dcfce7;
  color: #166534;
}

.message.error {
  background: #fee2e2;
  color: #991b1b;
}

@media (max-width: 900px) {
  .profile-container {
    grid-template-columns: 1fr;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
