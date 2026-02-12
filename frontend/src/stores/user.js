import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  const isAdmin = computed(() => user.value?.role === 'admin')
  const isManager = computed(() => user.value?.role === 'manager')
  const isWorker = computed(() => user.value?.role === 'worker')
  const isWholesaler = computed(() => user.value?.role === 'wholesaler')

  const canManageStaff = computed(() => user.value?.role === 'admin')
  const canManageProducts = computed(() => ['admin', 'manager'].includes(user.value?.role))
  const canManageFinance = computed(() => user.value?.role === 'admin')

  const roleHome = {
    admin: '/admin/dashboard',
    manager: '/manager/orders',
    worker: '/employee/tasks',
    wholesaler: '/wholesaler/catalog'
  }

  async function login(email, password) {
    try {
      loading.value = true
      error.value = null
      const { data } = await authAPI.login(email, password)

      token.value = data.access_token
      localStorage.setItem('token', data.access_token)

      await fetchUserData()

      return true
    } catch (err) {
      console.error('Ошибка авторизации:', err)
      error.value = err.response?.data?.detail || 'Ошибка входа'
      return false
    } finally {
      loading.value = false
    }
  }

  async function loginQR(qrData) {
    try {
      loading.value = true
      error.value = null
      const { data } = await authAPI.loginQR(qrData)

      token.value = data.access_token
      localStorage.setItem('token', data.access_token)

      await fetchUserData()

      return true
    } catch (err) {
      console.error('Ошибка QR-авторизации:', err)
      error.value = err.response?.data?.detail || 'Ошибка QR-входа'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(payload) {
    try {
      loading.value = true
      error.value = null
      await authAPI.register(payload) // POST /auth/register
      // Авто-login после регистрации
      return await login(payload.email, payload.password)
    } catch (err) {
      console.error('Ошибка регистрации:', err)
      error.value = err.response?.data?.detail || 'Ошибка регистрации'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUserData() {
    try {
      const { data } = await authAPI.getMe()
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
    } catch (err) {
      logout()
      throw err
    }
  }

  function logout() {
    token.value = null
    user.value = null
    error.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isManager,
    isWorker,
    isWholesaler,
    canManageStaff,
    canManageProducts,
    canManageFinance,
    roleHome,
    login,
    loginQR,
    register,
    fetchUserData,
    logout
  }
})
