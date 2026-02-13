<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-box">
        <h2 class="login-title">Вход в систему</h2>
        
        <div class="login-tabs">
          <button
            :class="['tab', { active: loginMode === 'password' }]"
            @click="loginMode = 'password'"
          >
            Логин/Пароль
          </button>
          <button
            :class="['tab', { active: loginMode === 'qr' }]"
            @click="loginMode = 'qr'"
          >
            QR-код
          </button>
        </div>
        
        <!-- Форма логин/пароль -->
        <form v-if="loginMode === 'password'" @submit.prevent="handlePasswordLogin" class="login-form">
          <AppInput
            v-model="credentials.username"
            type="text"
            label="Логин"
            placeholder="Введите логин"
            required
            :error="errors.username"
          />
          
          <AppInput
            v-model="credentials.password"
            type="password"
            label="Пароль"
            placeholder="Введите пароль"
            required
            :error="errors.password"
          />
          
          <div v-if="loginError" class="error-message">
            {{ loginError }}
          </div>
          
          <AppButton
            type="submit"
            :loading="userStore.loading"
            full-width
          >
            Войти
          </AppButton>
        </form>
        
        <!-- QR-сканер -->
        <div v-else class="qr-scanner">
          <p class="qr-hint">Отсканируйте ваш QR-код для входа</p>
          <div class="qr-input">
            <AppInput
              v-model="qrData"
              type="text"
              label="Или введите код вручную"
              placeholder="worker:123"
            />
            <AppButton
              :loading="userStore.loading"
              :disabled="!qrData"
              @click="handleQRLogin"
            >
              Войти по QR
            </AppButton>
          </div>
          
          <div v-if="loginError" class="error-message">
            {{ loginError }}
          </div>
        </div>
        
        <div class="login-footer">
          <p>Тестовый доступ: admin / admin123</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AppInput from '@/components/UI/AppInput.vue'
import AppButton from '@/components/UI/AppButton.vue'

const router = useRouter()
const userStore = useUserStore()

const loginMode = ref('password') // 'password' or 'qr'
const loginError = ref('')

const credentials = reactive({
  username: '',
  password: ''
})

const errors = reactive({
  username: '',
  password: ''
})

const qrData = ref('')

watch(loginMode, () => {
  loginError.value = ''
  errors.username = ''
  errors.password = ''
})

const validateForm = () => {
  errors.username = credentials.username ? '' : 'Введите логин'
  errors.password = credentials.password ? '' : 'Введите пароль'
  
  return !errors.username && !errors.password
}

const handlePasswordLogin = async () => {
  loginError.value = ''
  
  if (!validateForm()) return
  
  const success = await userStore.login(credentials.username, credentials.password)
  
  if (success) {
    const redirectPath = userStore.roleHome[userStore.user?.role] || '/'
    router.push(redirectPath)
  } else {
    loginError.value = userStore.error
  }
}

const handleQRLogin = async () => {
  loginError.value = ''
  
  if (!qrData.value) {
    loginError.value = 'Введите QR-код'
    return
  }
  
  const success = await userStore.loginQR(qrData.value)
  
  if (success) {
    const redirectPath = userStore.roleHome[userStore.user?.role] || '/'
    router.push(redirectPath)
  } else {
    loginError.value = userStore.error
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.login-container {
  width: 100%;
  max-width: 450px;
}

.login-box {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 2.5rem;
}

.login-title {
  font-size: 1.75rem;
  font-weight: 700;
  text-align: center;
  margin: 0 0 2rem;
  color: #111827;
}

.login-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.tab {
  flex: 1;
  padding: 0.75rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  color: #6b7280;
  transition: all 0.2s;
  margin-bottom: -2px;
}

.tab:hover {
  color: #111827;
}

.tab.active {
  color: #667eea;
  border-bottom-color: #667eea;
  font-weight: 600;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.qr-scanner {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.qr-hint {
  text-align: center;
  color: #6b7280;
  margin: 0;
}

.qr-input {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.error-message {
  padding: 0.75rem;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 6px;
  font-size: 0.875rem;
  text-align: center;
}

.login-footer {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
  text-align: center;
}

.login-footer p {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}
</style>