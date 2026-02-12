import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
// ОШИБКА БЫЛА ТУТ: router обычно лежит внутри src, путь должен быть './router'
import router from './router' 

// ОШИБКА БЫЛА ТУТ: используйте относительный путь './assets/main.css'
// Vite не поймет путь 'new/src/main.css'
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

// Настройка Axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

app.use(pinia)
app.use(router)
app.mount('#app')