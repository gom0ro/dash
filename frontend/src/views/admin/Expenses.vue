<template>
  <div class="expenses-view">
    <div class="page-header">
      <div>
        <h1>Расходы</h1>
        <p class="subtitle">Учет всех расходов компании</p>
      </div>
      <AppButton @click="openCreateModal">
        + Добавить расход
      </AppButton>
    </div>

    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-icon" style="background: #fee2e2;"><i class="ri-bank-card-line" style="color: #991b1b;"></i></div>
        <div class="stat-content">
          <div class="stat-label">Всего расходов</div>
          <div class="stat-value">{{ formatMoney(totalExpenses) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fef3c7;"><i class="ri-archive-line" style="color: #92400e;"></i></div>
        <div class="stat-content">
          <div class="stat-label">В себестоимость</div>
          <div class="stat-value">{{ formatMoney(costExpenses) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #dbeafe;"><i class="ri-file-list-3-line" style="color: #1e40af;"></i></div>
        <div class="stat-content">
          <div class="stat-label">Прочие расходы</div>
          <div class="stat-value">{{ formatMoney(otherExpenses) }}</div>
        </div>
      </div>
    </div>

    <div class="filters-bar">
      <div class="filter-buttons">
        <button
          :class="['filter-btn', { active: typeFilter === 'all' }]"
          @click="typeFilter = 'all'"
        >
          Все ({{ expenses.length }})
        </button>
        <button
          :class="['filter-btn', { active: typeFilter === 'cost' }]"
          @click="typeFilter = 'cost'"
        >
          Себестоимость ({{ costExpensesList.length }})
        </button>
        <button
          :class="['filter-btn', { active: typeFilter === 'other' }]"
          @click="typeFilter = 'other'"
        >
          Прочие ({{ otherExpensesList.length }})
        </button>
      </div>
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск расходов..."
          class="search-input"
        />
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка расходов...</p>
    </div>

    <div v-else-if="filteredExpenses.length === 0" class="empty">
      <div class="empty-icon"><i class="ri-money-dollar-circle-line"></i></div>
      <h3>Расходов не найдено</h3>
      <p v-if="searchQuery">Попробуйте изменить поисковый запрос</p>
      <AppButton v-else @click="openCreateModal">
        Добавить первый расход
      </AppButton>
    </div>

    <div v-else class="expenses-table">
      <table>
        <thead>
          <tr>
            <th>Дата</th>
            <th>Название</th>
            <th>Описание</th>
            <th>Тип</th>
            <th>Товар</th>
            <th>Сумма</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="expense in filteredExpenses" :key="expense.id">
            <td class="date-cell">{{ formatDate(expense.created_at) }}</td>
            <td class="name-cell">{{ expense.name }}</td>
            <td class="description-cell">
              {{ expense.description || '—' }}
            </td>
            <td>
              <span :class="['type-badge', expense.expense_type]">
                {{ expenseTypeLabels[expense.expense_type] }}
              </span>
            </td>
            <td class="product-cell">
              {{ getProductName(expense.product_id) }}
            </td>
            <td class="amount-cell">
              {{ formatMoney(expense.amount) }}
            </td>
            <td class="actions-cell">
              <button
                class="action-btn edit"
                @click="openEditModal(expense)"
                title="Редактировать"
              >
                <i class="ri-edit-line"></i>
              </button>
              <button
                class="action-btn delete"
                @click="confirmDelete(expense)"
                title="Удалить"
              >
                <i class="ri-delete-bin-line"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Модалка создания/редактирования расхода -->
    <AppModal
      v-model="showExpenseModal"
      :title="editingExpense ? 'Редактирование расхода' : 'Новый расход'"
      size="md"
    >
      <form @submit.prevent="handleSaveExpense">
        <div class="form-group">
          <label class="label">
            Название <span class="required">*</span>
          </label>
          <input
            v-model="expenseForm.name"
            type="text"
            class="input"
            placeholder="Например: Аренда офиса"
            required
          />
        </div>

        <div class="form-group">
          <label class="label">Описание</label>
          <textarea
            v-model="expenseForm.description"
            class="textarea"
            rows="3"
            placeholder="Дополнительная информация о расходе"
          ></textarea>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label class="label">
              Сумма <span class="required">*</span>
            </label>
            <input
              v-model.number="expenseForm.amount"
              type="number"
              min="0"
              step="0.01"
              class="input"
              placeholder="0.00"
              required
            />
          </div>

          <div class="form-group">
            <label class="label">
              Тип расхода <span class="required">*</span>
            </label>
            <select
              v-model="expenseForm.expense_type"
              class="select"
              required
            >
              <option value="">Выберите тип</option>
              <option value="cost">Входит в себестоимость</option>
              <option value="other">Прочие расходы</option>
            </select>
          </div>
        </div>

        <div v-if="expenseForm.expense_type === 'cost'" class="form-group">
          <label class="label">Товар</label>
          <select
            v-model="expenseForm.product_id"
            class="select"
          >
            <option :value="null">Не привязан к товару</option>
            <option
              v-for="product in products"
              :key="product.id"
              :value="product.id"
            >
              {{ product.name }}
            </option>
          </select>
          <span class="hint">
            Выберите товар, если расход относится к конкретному товару
          </span>
        </div>

        <div v-if="expenseError" class="error-message">
          {{ expenseError }}
        </div>
      </form>

      <template #footer>
        <AppButton variant="secondary" @click="showExpenseModal = false">
          Отмена
        </AppButton>
        <AppButton :loading="saving" @click="handleSaveExpense">
          {{ editingExpense ? 'Сохранить' : 'Добавить' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- Модалка удаления -->
    <AppModal
      v-model="showDeleteModal"
      title="Удаление расхода"
      size="sm"
    >
      <p>Вы уверены, что хотите удалить расход <strong>{{ expenseToDelete?.name }}</strong>?</p>
      <p class="amount-info">Сумма: {{ formatMoney(expenseToDelete?.amount) }}</p>
      <p class="warning">Это действие нельзя отменить.</p>

      <template #footer>
        <AppButton variant="secondary" @click="showDeleteModal = false">
          Отмена
        </AppButton>
        <AppButton variant="danger" :loading="deleting" @click="handleDelete">
          Удалить
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { expensesAPI, productsAPI } from '@/api'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)

const expenses = ref([])
const products = ref([])

const searchQuery = ref('')
const typeFilter = ref('all')

const showExpenseModal = ref(false)
const showDeleteModal = ref(false)

const editingExpense = ref(null)
const expenseToDelete = ref(null)
const expenseError = ref('')

const expenseForm = ref({
  name: '',
  description: '',
  amount: 0,
  expense_type: '',
  product_id: null
})

const expenseTypeLabels = {
  cost: 'Себестоимость',
  other: 'Прочие'
}

const totalExpenses = computed(() => {
  return expenses.value.reduce((sum, exp) => sum + exp.amount, 0)
})

const costExpenses = computed(() => {
  return expenses.value
    .filter(exp => exp.expense_type === 'cost')
    .reduce((sum, exp) => sum + exp.amount, 0)
})

const otherExpenses = computed(() => {
  return expenses.value
    .filter(exp => exp.expense_type === 'other')
    .reduce((sum, exp) => sum + exp.amount, 0)
})

const costExpensesList = computed(() => {
  return expenses.value.filter(exp => exp.expense_type === 'cost')
})

const otherExpensesList = computed(() => {
  return expenses.value.filter(exp => exp.expense_type === 'other')
})

const filteredExpenses = computed(() => {
  let filtered = expenses.value

  if (typeFilter.value !== 'all') {
    filtered = filtered.filter(exp => exp.expense_type === typeFilter.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(exp =>
      exp.name.toLowerCase().includes(query) ||
      exp.description?.toLowerCase().includes(query)
    )
  }

  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const getProductName = (productId) => {
  if (!productId) return '—'
  const product = products.value.find(p => p.id === productId)
  return product?.name || '—'
}

const formatMoney = (amount) => {
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(amount || 0) + ' тг'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const resetForm = () => {
  expenseForm.value = {
    name: '',
    description: '',
    amount: 0,
    expense_type: '',
    product_id: null
  }
  editingExpense.value = null
  expenseError.value = ''
}

const openCreateModal = () => {
  resetForm()
  showExpenseModal.value = true
}

const openEditModal = (expense) => {
  editingExpense.value = expense
  expenseForm.value = {
    name: expense.name,
    description: expense.description || '',
    amount: expense.amount,
    expense_type: expense.expense_type,
    product_id: expense.product_id
  }
  showExpenseModal.value = true
}

const confirmDelete = (expense) => {
  expenseToDelete.value = expense
  showDeleteModal.value = true
}

const handleSaveExpense = async () => {
  expenseError.value = ''

  if (!expenseForm.value.name.trim()) {
    expenseError.value = 'Введите название расхода'
    return
  }

  if (expenseForm.value.amount <= 0) {
    expenseError.value = 'Сумма должна быть больше 0'
    return
  }

  if (!expenseForm.value.expense_type) {
    expenseError.value = 'Выберите тип расхода'
    return
  }

  try {
    saving.value = true

    const data = { ...expenseForm.value }
    if (data.expense_type === 'other') {
      data.product_id = null
    }

    if (editingExpense.value) {
      await expensesAPI.update(editingExpense.value.id, data)
    } else {
      await expensesAPI.create(data)
    }

    await loadExpenses()
    showExpenseModal.value = false
    resetForm()
  } catch (error) {
    expenseError.value = error.response?.data?.detail || 'Ошибка сохранения расхода'
  } finally {
    saving.value = false
  }
}

const handleDelete = async () => {
  try {
    deleting.value = true
    await expensesAPI.delete(expenseToDelete.value.id)
    await loadExpenses()
    showDeleteModal.value = false
    expenseToDelete.value = null
  } catch (error) {
    alert('Ошибка удаления: ' + (error.response?.data?.detail || error.message))
  } finally {
    deleting.value = false
  }
}

const loadExpenses = async () => {
  try {
    const { data } = await expensesAPI.getAll()
    expenses.value = data
  } catch (error) {
    console.error('Ошибка загрузки расходов:', error)
  }
}

const loadProducts = async () => {
  try {
    const { data } = await productsAPI.getAll()
    products.value = data
  } catch (error) {
    console.error('Ошибка загрузки товаров:', error)
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      loadExpenses(),
      loadProducts()
    ])
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.expenses-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
}

.subtitle {
  color: #6b7280;
  margin: 0;
}

.stats-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 1rem;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.filters-bar {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-buttons {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  padding: 0.75rem 1.25rem;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9375rem;
  color: #6b7280;
  transition: all 0.2s;
  font-weight: 500;
}

.filter-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.filter-btn.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.loading {
  text-align: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty h3 {
  margin: 0 0 0.5rem;
  color: #111827;
}

.empty p {
  margin: 0 0 1.5rem;
  color: #6b7280;
}

.expenses-table {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f9fafb;
}

th {
  padding: 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: 1rem;
  border-top: 1px solid #f3f4f6;
}

.date-cell {
  color: #6b7280;
  font-size: 0.875rem;
  white-space: nowrap;
}

.name-cell {
  font-weight: 600;
  color: #111827;
}

.description-cell {
  color: #6b7280;
  font-size: 0.875rem;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 600;
}

.type-badge.cost {
  background: #fef3c7;
  color: #92400e;
}

.type-badge.other {
  background: #dbeafe;
  color: #1e40af;
}

.product-cell {
  color: #6b7280;
  font-size: 0.875rem;
}

.amount-cell {
  font-weight: 700;
  color: #e74c3c;
  white-space: nowrap;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0.25rem;
  opacity: 0.6;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  opacity: 1;
}

.form-group {
  margin-bottom: 1.5rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.required {
  color: #e74c3c;
}

.input,
.textarea,
.select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.textarea {
  resize: vertical;
  font-family: inherit;
}

.input:focus,
.textarea:focus,
.select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.hint {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.error-message {
  padding: 1rem;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 8px;
  margin-top: 1.5rem;
  font-size: 0.9375rem;
}

.amount-info {
  margin: 0.5rem 0;
  color: #6b7280;
  font-size: 0.9375rem;
}

.warning {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

@media (max-width: 1024px) {
  .expenses-table {
    overflow-x: auto;
  }

  table {
    min-width: 900px;
  }
}

@media (max-width: 768px) {
  .expenses-view {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    gap: 1rem;
  }

  .filters-bar {
    flex-direction: column;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>