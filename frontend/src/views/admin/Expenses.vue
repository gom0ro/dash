<template>
  <div class="expenses-view fade-in">
    <div class="page-header">
      <div class="header-content">
        <h1>Расходы компании</h1>
        <p class="subtitle">Учет операционных затрат и производственной себестоимости</p>
      </div>
      <AppButton @click="openCreateModal" class="add-expense-btn">
        <i class="ri-add-line"></i> <span>Добавить расход</span>
      </AppButton>
    </div>

    <!-- Stats Ribbon -->
    <div class="stats-ribbon">
      <div class="glass-stat total">
        <div class="g-icon"><i class="ri-money-dollar-circle-line"></i></div>
        <div class="g-data">
          <span class="g-label">Общая сумма</span>
          <span class="g-value">{{ formatPrice(totalExpenses) }}</span>
        </div>
      </div>
      <div class="glass-stat cost">
        <div class="g-icon"><i class="ri-tools-line"></i></div>
        <div class="g-data">
          <span class="g-label">Себестоимость</span>
          <span class="g-value">{{ formatPrice(costExpenses) }}</span>
        </div>
      </div>
      <div class="glass-stat other">
        <div class="g-icon"><i class="ri-pie-chart-line"></i></div>
        <div class="g-data">
          <span class="g-label">Прочие нужды</span>
          <span class="g-value">{{ formatPrice(otherExpenses) }}</span>
        </div>
      </div>
    </div>

    <!-- Filters Section -->
    <div class="filters-container">
      <div class="search-box">
        <i class="ri-search-line"></i>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск по названию или описанию..."
          class="modern-search-input"
        />
      </div>
      
      <div class="type-chips">
        <button
          v-for="type in filterTypes"
          :key="type.value"
          :class="['chip', { active: typeFilter === type.value }]"
          @click="typeFilter = type.value"
        >
          {{ type.label }} <span v-if="getCount(type.value) > 0" class="badge">{{ getCount(type.value) }}</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка данных...</p>
    </div>

    <div v-else-if="filteredExpenses.length === 0" class="empty-state">
      <div class="empty-icon"><i class="ri-coins-line"></i></div>
      <h3>Расходы не найдены</h3>
      <p>Добавьте новый расход или измените параметры поиска.</p>
      <AppButton v-if="!searchQuery && typeFilter === 'all'" @click="openCreateModal">
        Добавить первый расход
      </AppButton>
    </div>

    <!-- Expenses Grid -->
    <div v-else class="expenses-grid">
      <div v-for="expense in filteredExpenses" :key="expense.id" class="expense-card">
        <div class="card-top">
          <div class="expense-main">
            <span class="expense-date">{{ formatDateShort(expense.created_at) }}</span>
            <h3>{{ expense.name }}</h3>
          </div>
          <div class="expense-type-tag" :class="expense.expense_type">
            {{ expenseTypeLabels[expense.expense_type] }}
          </div>
        </div>

        <div class="card-middle">
          <p class="expense-desc">{{ expense.description || 'Нет описания' }}</p>
          <div class="product-link" v-if="expense.product_id">
              <i class="ri-links-line"></i> {{ getProductName(expense.product_id) }}
          </div>
        </div>

        <div class="card-bottom">
          <div class="expense-price">{{ formatPrice(expense.amount) }}</div>
          <div class="expense-actions">
            <button class="icon-btn edit" @click="openEditModal(expense)">
              <i class="ri-pencil-line"></i>
            </button>
            <button class="icon-btn delete" @click="confirmDelete(expense)">
              <i class="ri-delete-bin-line"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Expense Modal -->
    <AppModal
      v-model="showExpenseModal"
      :title="editingExpense ? 'Редактировать расход' : 'Новый расход'"
      size="md"
    >
      <div class="modal-form-container">
        <form @submit.prevent="handleSaveExpense" id="expenseForm">
          <div class="form-group full">
            <label>Название расхода</label>
            <input
              v-model="expenseForm.name"
              type="text"
              class="modern-input"
              placeholder="Например: Аренда помещений"
              required
            />
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label>Сумма (₸)</label>
              <input
                v-model.number="expenseForm.amount"
                type="number"
                min="0"
                step="0.01"
                class="modern-input"
                placeholder="0.00"
                required
              />
            </div>

            <div class="form-group">
              <label>Категория</label>
              <select v-model="expenseForm.expense_type" class="modern-select" required>
                <option value="" disabled>Выберите тип</option>
                <option value="cost">Себестоимость</option>
                <option value="other">Прочие расходы</option>
              </select>
            </div>
          </div>

          <div class="form-group" v-if="expenseForm.expense_type === 'cost'">
            <label>Привязка к товару</label>
            <select v-model="expenseForm.product_id" class="modern-select">
              <option :value="null">Без привязки</option>
              <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>

          <div class="form-group">
            <label>Комментарий</label>
            <textarea
              v-model="expenseForm.description"
              class="modern-textarea"
              rows="3"
              placeholder="Опционально..."
            ></textarea>
          </div>
        </form>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showExpenseModal = false">Отмена</AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleSaveExpense">
          {{ editingExpense ? 'Сохранить изменения' : 'Добавить расход' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- Delete Modal -->
    <AppModal v-model="showDeleteModal" title="Удалить запись?" size="sm">
      <div class="confirm-content">
          <p>Вы действительно хотите удалить расход <strong>{{ expenseToDelete?.name }}</strong> на сумму <strong>{{ formatPrice(expenseToDelete?.amount) }}</strong>?</p>
          <p class="warning-txt">Это действие нельзя отменить.</p>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showDeleteModal = false">Отмена</AppButton>
        <AppButton variant="danger" :loading="deleting" @click="handleDelete">Удалить</AppButton>
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

const expenseForm = ref({
  name: '',
  description: '',
  amount: 0,
  expense_type: '',
  product_id: null
})

const filterTypes = [
    { label: 'Все', value: 'all' },
    { label: 'Себестоимость', value: 'cost' },
    { label: 'Прочие', value: 'other' }
]

const expenseTypeLabels = {
  cost: 'Себестоимость',
  other: 'Прочие'
}

const totalExpenses = computed(() => expenses.value.reduce((sum, exp) => sum + exp.amount, 0))
const costExpenses = computed(() => expenses.value.filter(exp => exp.expense_type === 'cost').reduce((sum, exp) => sum + exp.amount, 0))
const otherExpenses = computed(() => expenses.value.filter(exp => exp.expense_type === 'other').reduce((sum, exp) => sum + exp.amount, 0))

const getCount = (val) => {
    if (val === 'all') return expenses.value.length
    return expenses.value.filter(e => e.expense_type === val).length
}

const filteredExpenses = computed(() => {
  let filtered = expenses.value
  if (typeFilter.value !== 'all') filtered = filtered.filter(exp => exp.expense_type === typeFilter.value)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(exp => exp.name.toLowerCase().includes(q) || exp.description?.toLowerCase().includes(q))
  }
  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const getProductName = (id) => products.value.find(p => p.id === id)?.name || '—'
const formatPrice = (v) => new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(v || 0) + ' ₸'
const formatDateShort = (d) => new Date(d).toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' })

const resetForm = () => {
  expenseForm.value = { name: '', description: '', amount: 0, expense_type: '', product_id: null }
  editingExpense.value = null
}

const openCreateModal = () => { resetForm(); showExpenseModal.value = true }
const openEditModal = (expense) => {
  editingExpense.value = expense
  expenseForm.value = { ...expense, description: expense.description || '' }
  showExpenseModal.value = true
}

const confirmDelete = (expense) => { expenseToDelete.value = expense; showDeleteModal.value = true }

const handleSaveExpense = async () => {
  if (!expenseForm.value.name || expenseForm.value.amount <= 0 || !expenseForm.value.expense_type) return
  saving.value = true
  try {
    const data = { ...expenseForm.value }
    if (data.expense_type === 'other') data.product_id = null
    if (editingExpense.value) await expensesAPI.update(editingExpense.value.id, data)
    else await expensesAPI.create(data)
    await loadExpenses()
    showExpenseModal.value = false
  } catch (error) {
    alert('Ошибка при сохранении')
  } finally { saving.value = false }
}

const handleDelete = async () => {
  deleting.value = true
  try {
    await expensesAPI.delete(expenseToDelete.value.id)
    await loadExpenses()
    showDeleteModal.value = false
  } catch (error) { alert('Ошибка при удалении') }
  finally { deleting.value = false }
}

const loadExpenses = async () => {
    const { data } = await expensesAPI.getAll()
    expenses.value = data
}

const loadProducts = async () => {
    const { data } = await productsAPI.getAll()
    products.value = data
}

onMounted(async () => {
  loading.value = true
  try { await Promise.all([loadExpenses(), loadProducts()]) } finally { loading.value = false }
})
</script>

<style scoped>
.expenses-view { padding: 1.5rem; max-width: 1400px; margin: 0 auto; }

.page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2.5rem; }
.header-content h1 { font-size: 2rem; font-weight: 900; color: #1e293b; margin: 0 0 0.5rem; }
.subtitle { color: #64748b; font-weight: 500; }
.add-expense-btn { padding: 0.75rem 1.5rem; font-weight: 800; display: flex; align-items: center; gap: 0.5rem; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2); }

.stats-ribbon { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem; }
.glass-stat { background: white; padding: 1.5rem; border-radius: 24px; border: 1px solid #f1f5f9; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.02); display: flex; align-items: center; gap: 1.25rem; }
.g-icon { width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
.total .g-icon { background: #fee2e2; color: #ef4444; }
.cost .g-icon { background: #fef3c7; color: #d97706; }
.other .g-icon { background: #eff6ff; color: #3b82f6; }

.g-data { display: flex; flex-direction: column; }
.g-label { font-size: 0.75rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
.g-value { font-size: 1.6rem; font-weight: 900; color: #1e293b; }

.filters-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; gap: 1.5rem; flex-wrap: wrap; }
.search-box { position: relative; flex: 1; min-width: 300px; }
.search-box i { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 1.2rem; }
.modern-search-input { width: 100%; padding: 0.85rem 1rem 0.85rem 3rem; border: 1.5px solid #f1f5f9; background: white; border-radius: 14px; font-size: 0.95rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
.modern-search-input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.05); }

.type-chips { display: flex; gap: 0.5rem; }
.chip { padding: 0.65rem 1.25rem; background: white; border: 1.5px solid #f1f5f9; border-radius: 12px; color: #64748b; font-weight: 800; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }
.chip:hover { border-color: #3b82f6; color: #3b82f6; }
.chip.active { background: #3b82f6; color: white; border-color: #3b82f6; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2); }
.badge { background: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 6px; font-size: 0.75rem; }
.chip.active .badge { background: rgba(255,255,255,0.2); }

.expenses-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 1.5rem; }
.expense-card { background: white; border-radius: 20px; padding: 1.5rem; border: 1.5px solid #f1f5f9; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.03); display: flex; flex-direction: column; gap: 1rem; transition: all 0.2s; }
.expense-card:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.06); }

.card-top { display: flex; justify-content: space-between; align-items: flex-start; }
.expense-main { display: flex; flex-direction: column; }
.expense-date { font-size: 0.75rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.expense-main h3 { margin: 4px 0 0; font-size: 1.2rem; font-weight: 800; color: #1e293b; }

.expense-type-tag { font-size: 0.7rem; font-weight: 800; padding: 4px 8px; border-radius: 8px; text-transform: uppercase; }
.expense-type-tag.cost { background: #fffbeb; color: #d97706; }
.expense-type-tag.other { background: #eff6ff; color: #3b82f6; }

.card-middle { flex: 1; }
.expense-desc { font-size: 0.9rem; color: #64748b; margin: 0; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.product-link { margin-top: 0.75rem; font-size: 0.85rem; font-weight: 700; color: #3b82f6; display: flex; align-items: center; gap: 4px; }

.card-bottom { display: flex; justify-content: space-between; align-items: center; padding-top: 1rem; border-top: 1px solid #f8fafc; }
.expense-price { font-size: 1.5rem; font-weight: 900; color: #ef4444; }
.expense-actions { display: flex; gap: 8px; }
.icon-btn { width: 36px; height: 36px; border-radius: 10px; border: none; background: #f8fafc; color: #94a3b8; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }
.icon-btn:hover { color: white; }
.icon-btn.edit:hover { background: #3b82f6; }
.icon-btn.delete:hover { background: #ef4444; }

.modal-form-container { padding: 0.5rem 0; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { margin-bottom: 1.25rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 800; color: #1e293b; text-transform: uppercase; margin-bottom: 0.5rem; }
.modern-input, .modern-select, .modern-textarea { width: 100%; padding: 0.85rem; border: 2px solid #f1f5f9; background: #f8fafc; border-radius: 12px; font-size: 1rem; font-weight: 600; outline: none; }
.modern-input:focus, .modern-select:focus, .modern-textarea:focus { border-color: #3b82f6; background: white; }

.confirm-content { text-align: center; padding: 1rem 0; }
.warning-txt { color: #ef4444; font-weight: 700; font-size: 0.85rem; margin-top: 1rem; }

.loading-state, .empty-state { text-align: center; padding: 5rem 2rem; background: white; border-radius: 24px; }
.spinner { width: 3.5rem; height: 3.5rem; border: 4px solid #f1f5f9; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1.5rem; }

@keyframes spin { to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1024px) {
    .expenses-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
}

@media (max-width: 768px) {
    .expenses-view { padding: 1rem; }
    .page-header { flex-direction: column; align-items: flex-start; gap: 1.5rem; }
    .add-expense-btn { width: 100%; justify-content: center; }
    .type-chips { width: 100%; overflow-x: auto; padding-bottom: 0.5rem; }
    .stats-ribbon { grid-template-columns: 1fr; }
    .expenses-grid { grid-template-columns: 1fr; }
    .form-grid { grid-template-columns: 1fr; }
}
</style>