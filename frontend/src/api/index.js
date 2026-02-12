// src/api/index.js
import axios from 'axios'

// Создаем базовый экземпляр Axios
const api = axios.create({
  baseURL: '/api/v1'
})

// Добавляем токен Authorization автоматически
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401 && !error.config.url.includes('/auth/login')) {
      // Auto logout if 401 (token expired) and not a login attempt
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export * from './auth'
export * from './orders'
export * from './production'
export { productionAPI as productsAPI } from './production'
export * from './finance'
export * from './reports'
export * from './work_logs'
export * from './expenses'
export * from './users'
export * from './tasks'
export * from './salaries'

export default api
