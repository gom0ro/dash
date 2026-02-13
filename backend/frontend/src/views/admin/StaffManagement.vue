<template>
  <div class="staff-management">
    <div class="page-header">
      <div>
        <h1>Управление персоналом</h1>
        <p class="subtitle">Управление учетными записями и правами доступа</p>
      </div>
      <AppButton @click="openCreateModal">
        + Создать пользователя
      </AppButton>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка персонала...</p>
    </div>

    <div v-else class="staff-list">
      <div v-for="staff in users" :key="staff.id" class="staff-card">
        <div class="staff-avatar">
          {{ staff.full_name.split(' ').map(n => n[0]).join('').toUpperCase() || '?' }}
        </div>
        <div class="staff-info">
          <h3>{{ staff.full_name }}</h3>
          <p class="username">@{{ staff.username }}</p>
          <div class="role-badge" :class="staff.role">
            {{ roleLabels[staff.role] }}
          </div>
        </div>
        <div class="staff-actions">
          <button @click="openEditModal(staff)" class="action-btn">✏️</button>
          <button v-if="staff.id !== currentUserId" @click="confirmDelete(staff)" class="action-btn delete">🗑️</button>
        </div>
      </div>
    </div>

    <!-- Modal for Create/Edit -->
    <AppModal v-model="showModal" :title="editingUser ? 'Редактировать пользователя' : 'Новый пользователь'">
      <form @submit.prevent="saveUser">
        <div class="form-group">
          <label>Полное имя</label>
          <input v-model="form.full_name" type="text" required class="input" />
        </div>
        <div class="form-group">
          <label>Username</label>
          <input v-model="form.username" type="text" required class="input" />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="form.email" type="email" required class="input" />
        </div>
        <div class="form-group" v-if="!editingUser">
          <label>Пароль</label>
          <input v-model="form.password" type="password" required class="input" />
        </div>
        <div class="form-group">
          <label>Роль</label>
          <select v-model="form.role" class="input">
            <option value="admin">Администратор</option>
            <option value="manager">Менеджер</option>
            <option value="worker">Сотрудник</option>
            <option value="wholesaler">Оптовик</option>
          </select>
        </div>
        <div class="form-group">
          <label>Номер телефона <span v-if="form.role === 'wholesaler'" class="required">*</span></label>
          <input v-model="form.phone" type="text" class="input" placeholder="+7 (___) ___ __ __" />
        </div>
        <div class="form-group">
          <label>Адрес <span v-if="form.role === 'wholesaler'" class="required">*</span></label>
          <input v-model="form.address" type="text" class="input" placeholder="Город, улица..." />
        </div>
      </form>
      <template #footer>
        <AppButton variant="secondary" @click="showModal = false">Отмена</AppButton>
        <AppButton @click="saveUser">{{ editingUser ? 'Сохранить' : 'Создать' }}</AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { usersAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.user?.id)

const users = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingUser = ref(null)

const form = ref({
  full_name: '',
  username: '',
  email: '',
  password: '',
  role: 'worker',
  phone: '',
  address: ''
})

const roleLabels = {
  admin: 'Администратор',
  manager: 'Менеджер',
  worker: 'Сотрудник',
  wholesaler: 'Оптовик'
}

const loadUsers = async () => {
  loading.value = true
  try {
    const { data } = await usersAPI.getAll()
    users.value = data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingUser.value = null
  form.value = { 
    full_name: '', 
    username: '', 
    email: '', 
    password: '', 
    role: 'worker',
    phone: '',
    address: ''
  }
  showModal.value = true
}

const openEditModal = (user) => {
  editingUser.value = user
  form.value = { 
    ...user,
    phone: user.phone || '',
    address: user.address || ''
  }
  showModal.value = true
}

const saveUser = async () => {
  if (form.value.role === 'wholesaler') {
    if (!form.value.phone || !form.value.address) {
      alert('Для оптовика обязательны номер телефона и адрес!')
      return
    }
  }

  try {
    if (editingUser.value) {
      await usersAPI.update(editingUser.value.id, form.value)
    } else {
      await usersAPI.create(form.value)
    }
    showModal.value = false
    loadUsers()
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка при сохранении')
  }
}

const confirmDelete = async (user) => {
  if (confirm(`Удалить пользователя ${user.full_name}?`)) {
    try {
      await usersAPI.delete(user.id)
      loadUsers()
    } catch (err) {
      alert('Ошибка при удалении')
    }
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.staff-management {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.staff-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.staff-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.staff-avatar {
  width: 50px;
  height: 50px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.25rem;
}

.staff-info {
  flex: 1;
}

.staff-info h3 {
  margin: 0;
  font-size: 1.1rem;
}

.username {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0;
}

.role-badge {
  display: inline-block;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  margin-top: 0.5rem;
  font-weight: 600;
}

.role-badge.admin { background: #fee2e2; color: #991b1b; }
.role-badge.manager { background: #dbeafe; color: #1e40af; }
.role-badge.worker { background: #dcfce7; color: #065f46; }
.role-badge.wholesaler { background: #fef3c7; color: #92400e; }

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  font-size: 1.1rem;
  border-radius: 6px;
  transition: background 0.2s;
}

.action-btn:hover { background: #f3f4f6; }
.action-btn.delete { color: #e74c3c; }

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}
</style>
