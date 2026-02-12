<template>
  <div class="staff-management fade-in">
    <div class="page-header">
      <div class="header-content">
        <h1>Управление персоналом</h1>
        <p class="subtitle">Учетные записи и права доступа в системе</p>
      </div>
      <AppButton @click="openCreateModal" class="add-user-btn">
        <i class="ri-user-add-line"></i> <span>Добавить пользователя</span>
      </AppButton>
    </div>

    <!-- Search and Filter (Bonus for premium feel) -->
    <div class="list-filters">
        <div class="search-box">
            <i class="ri-search-line"></i>
            <input v-model="searchQuery" placeholder="Поиск по имени или username..." />
        </div>
        <div class="filter-chips">
            <button 
              v-for="role in ['all', 'admin', 'manager', 'worker', 'wholesaler']" 
              :key="role"
              :class="{ active: activeFilter === role }"
              @click="activeFilter = role"
            >
                {{ role === 'all' ? 'Все' : roleLabels[role] }}
            </button>
        </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка списка персонала...</p>
    </div>

    <div v-else class="staff-grid">
      <div v-for="staff in filteredUsers" :key="staff.id" class="staff-card">
        <div class="staff-main-info">
            <div class="staff-avatar" :style="avatarStyle(staff.full_name)">
                {{ getInitials(staff.full_name) }}
            </div>
            <div class="staff-details">
                <h3>{{ staff.full_name }}</h3>
                <span class="staff-username">@{{ staff.username }}</span>
                <div class="role-badge" :class="staff.role">
                    {{ roleLabels[staff.role] }}
                </div>
            </div>
        </div>

        <div class="staff-contact" v-if="staff.phone">
            <i class="ri-phone-line"></i> {{ staff.phone }}
        </div>

        <div class="staff-actions">
          <button @click="openEditModal(staff)" class="action-btn edit" title="Редактировать">
            <i class="ri-edit-line"></i>
          </button>
          <button 
            v-if="staff.id !== currentUserId" 
            @click="confirmDelete(staff)" 
            class="action-btn delete" 
            title="Удалить"
          >
            <i class="ri-delete-bin-line"></i>
          </button>
        </div>
      </div>
    </div>

    <div v-if="!loading && filteredUsers.length === 0" class="empty-results">
        <i class="ri-user-search-line"></i>
        <p>Пользователи не найдены</p>
    </div>

    <!-- Modal for Create/Edit -->
    <AppModal v-model="showModal" :title="editingUser ? 'Редактировать пользователя' : 'Новый пользователь'">
      <div class="user-form-container">
          <form @submit.prevent="saveUser" id="userForm">
            <div class="form-grid">
                <div class="form-group full">
                  <label>Полное имя</label>
                  <input v-model="form.full_name" type="text" required class="modern-input" placeholder="Иван Иванов" />
                </div>
                
                <div class="form-group">
                  <label>Username</label>
                  <input v-model="form.username" type="text" required class="modern-input" placeholder="ivan_i" />
                </div>
                
                <div class="form-group">
                  <label>Роль</label>
                  <select v-model="form.role" class="modern-select">
                    <option value="admin">Администратор</option>
                    <option value="manager">Менеджер</option>
                    <option value="worker">Сотрудник</option>
                    <option value="wholesaler">Оптовик</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Email</label>
                  <input v-model="form.email" type="email" required class="modern-input" placeholder="mail@example.com" />
                </div>
                
                <div class="form-group" v-if="!editingUser">
                  <label>Пароль</label>
                  <input v-model="form.password" type="password" required class="modern-input" placeholder="••••••••" />
                </div>

                <div class="form-group">
                  <label>Номер телефона <span v-if="form.role === 'wholesaler'" class="required">*</span></label>
                  <input v-model="form.phone" type="text" class="modern-input" placeholder="+7 (___) ___ __ __" />
                </div>

                <div class="form-group" v-if="form.role === 'wholesaler'">
                  <label>Адрес <span class="required">*</span></label>
                  <input v-model="form.address" type="text" class="modern-input" placeholder="Город, улица..." />
                </div>
            </div>
          </form>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showModal = false">Отмена</AppButton>
        <AppButton @click="saveUser" class="save-user-btn">{{ editingUser ? 'Сохранить изменения' : 'Создать аккаунт' }}</AppButton>
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
const searchQuery = ref('')
const activeFilter = ref('all')

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

const filteredUsers = computed(() => {
    return users.value.filter(u => {
        const matchesSearch = u.full_name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                             u.username.toLowerCase().includes(searchQuery.value.toLowerCase())
        const matchesRole = activeFilter.value === 'all' || u.role === activeFilter.value
        return matchesSearch && matchesRole
    })
})

const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const avatarStyle = (name) => {
    const hues = [210, 250, 150, 20, 320, 180]
    const idx = name.length % hues.length
    return {
        background: `hsl(${hues[idx]}, 70%, 60%)`,
        color: 'white',
        fontWeight: 'bold'
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
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  gap: 1.5rem;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}

.subtitle { color: #64748b; font-weight: 500; }

.add-user-btn {
    padding: 0.75rem 1.5rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.list-filters {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.search-box {
    position: relative;
    flex: 1;
    min-width: 300px;
}

.search-box i {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
    font-size: 1.2rem;
}

.search-box input {
    width: 100%;
    padding: 0.85rem 1rem 0.85rem 3rem;
    border: 1px solid #f1f5f9;
    background: white;
    border-radius: 14px;
    font-size: 0.95rem;
    transition: all 0.2s;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
}

.search-box input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.05);
}

.filter-chips {
    display: flex;
    gap: 0.5rem;
}

.filter-chips button {
    padding: 0.6rem 1rem;
    border-radius: 10px;
    border: 1px solid #f1f5f9;
    background: white;
    color: #64748b;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
}

.filter-chips button:hover {
    background: #f8fafc;
    color: #1e293b;
}

.filter-chips button.active {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2);
}

.staff-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
}

.staff-card {
  background: white;
  padding: 1.5rem;
  border-radius: 20px;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.03);
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  transition: all 0.2s;
}

.staff-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.06);
}

.staff-main-info {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.staff-avatar {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.4rem;
}

.staff-details { flex: 1; }
.staff-details h3 { margin: 0; font-size: 1.15rem; color: #1e293b; font-weight: 800; }
.staff-username { color: #94a3b8; font-size: 0.875rem; font-weight: 500; }

.role-badge {
  display: inline-block;
  font-size: 0.7rem;
  padding: 0.25rem 0.6rem;
  border-radius: 8px;
  margin-top: 0.5rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.role-badge.admin { background: #fee2e2; color: #991b1b; }
.role-badge.manager { background: #dbeafe; color: #1e40af; }
.role-badge.worker { background: #dcfce7; color: #065f46; }
.role-badge.wholesaler { background: #fef3c7; color: #92400e; }

.staff-contact {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    color: #64748b;
    padding: 0.75rem;
    background: #f8fafc;
    border-radius: 10px;
    font-weight: 600;
}

.staff-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: auto;
  padding-top: 0.5rem;
}

.action-btn {
  width: 38px;
  height: 38px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  border-radius: 10px;
  transition: all 0.2s;
  background: #f1f5f9;
  color: #64748b;
}

.action-btn.edit:hover { background: #eff6ff; color: #3b82f6; }
.action-btn.delete:hover { background: #fef2f2; color: #ef4444; }

/* Form Elements */
.user-form-container { padding: 0.5rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
.form-group.full { grid-column: span 2; }

.form-group label {
  display: block;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.modern-input, .modern-select {
  width: 100%;
  padding: 0.85rem 1rem;
  border: 2px solid #f1f5f9;
  background: #f8fafc;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s;
}

.modern-input:focus, .modern-select:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
}

.required { color: #ef4444; }
.loading-state, .empty-results { text-align: center; padding: 5rem 0; color: #94a3b8; }
.empty-results i { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }

.spinner {
  width: 3rem;
  height: 3rem;
  border: 4px solid #f1f5f9;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin { to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1024px) {
  .staff-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
}

@media (max-width: 768px) {
    .page-header { flex-direction: column; align-items: flex-start; gap: 1.25rem; }
    .add-user-btn { width: 100%; justify-content: center; }
    .search-box { min-width: 100%; }
    .filter-chips { width: 100%; overflow-x: auto; padding-bottom: 0.5rem; }
    .filter-chips button { white-space: nowrap; }
    .staff-grid { grid-template-columns: 1fr; }
    .form-grid { grid-template-columns: 1fr; }
    .form-group.full { grid-column: auto; }
}
</style>
