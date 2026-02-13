<template>
  <div class="salary-report">
    <div class="page-header">
      <div>
        <h1>Моя зарплата</h1>
        <p class="subtitle">История начислений и выплат</p>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card total">
        <div class="stat-icon">💰</div>
        <div class="stat-content">
          <div class="stat-label">Всего заработано</div>
          <div class="stat-value">{{ formatMoney(salary.total_earned) }}</div>
        </div>
      </div>

      <div class="stat-card paid">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-label">Выплачено</div>
          <div class="stat-value">{{ formatMoney(salary.total_paid) }}</div>
        </div>
      </div>

      <div class="stat-card unpaid">
        <div class="stat-icon">⏳</div>
        <div class="stat-content">
          <div class="stat-label">Ожидает выплаты</div>
          <div class="stat-value">{{ formatMoney(salary.total_unpaid) }}</div>
          <div class="stat-meta">{{ salary.unpaid_count }} начислений</div>
        </div>
      </div>
    </div>

    <div class="filters-bar">
      <div class="period-filters">
        <button
          v-for="period in periods"
          :key="period.value"
          :class="['period-btn', { active: selectedPeriod === period.value }]"
          @click="selectPeriod(period.value)"
        >
          {{ period.label }}
        </button>
      </div>

      <div class="status-filters">
        <button
          :class="['status-btn', { active: statusFilter === 'all' }]"
          @click="statusFilter = 'all'"
        >
          Все
        </button>
        <button
          :class="['status-btn', { active: statusFilter === 'paid' }]"
          @click="statusFilter = 'paid'"
        >
          Выплачено
        </button>
        <button
          :class="['status-btn', { active: statusFilter === 'unpaid' }]"
          @click="statusFilter = 'unpaid'"
        >
          Не выплачено
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка данных...</p>
    </div>

    <div v-else-if="filteredWorkLogs.length === 0" class="empty">
      <div class="empty-icon">📝</div>
      <h3>Начислений не найдено</h3>
      <p v-if="statusFilter !== 'all'">
        Попробуйте выбрать другой фильтр
      </p>
      <p v-else>
        Начните работать над заказами, чтобы получать начисления
      </p>
      <AppButton @click="$router.push('/employee/tasks')">
        Перейти к задачам
      </AppButton>
    </div>

    <div v-else class="work-logs-container">
      <div class="summary-card">
        <div class="summary-row">
          <span>Период:</span>
          <strong>{{ periodLabel }}</strong>
        </div>
        <div class="summary-row">
          <span>Начислений:</span>
          <strong>{{ filteredWorkLogs.length }}</strong>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-row total">
          <span>Итого:</span>
          <strong>{{ formatMoney(periodTotal) }}</strong>
        </div>
      </div>

      <div class="work-logs-table">
        <table>
          <thead>
            <tr>
              <th>Дата</th>
              <th>Заказ</th>
              <th>Этап</th>
              <th>Сумма</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(group, date) in groupedWorkLogs" :key="date">
              <tr class="date-row">
                <td colspan="5" class="date-header">
                  {{ formatGroupDate(date) }}
                  <span class="date-total">{{ formatMoney(getGroupTotal(group)) }}</span>
                </td>
              </tr>
              <tr v-for="log in group" :key="log.id" class="log-row">
                <td class="time-cell">{{ formatTime(log.completed_at) }}</td>
                <td class="order-cell">
                  <span class="order-id">#{{ log.order_id }}</span>
                </td>
                <td class="stage-cell">
                  {{ getStageName(log) }}
                </td>
                <td class="amount-cell">
                  {{ formatMoney(log.payment) }}
                </td>
                <td class="status-cell">
                  <span :class="['status-badge', log.is_paid ? 'paid' : 'unpaid']">
                    {{ log.is_paid ? '✓ Выплачено' : '⏳ Ожидает' }}
                  </span>
                  <span v-if="log.is_paid && log.paid_at" class="paid-date">
                    {{ formatShortDate(log.paid_at) }}
                  </span>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { workLogsAPI } from '@/api'
import AppButton from '@/components/UI/AppButton.vue'

const router = useRouter()

const loading = ref(false)
const salary = ref({
  total_earned: 0,
  total_paid: 0,
  total_unpaid: 0,
  unpaid_count: 0
})
const workLogs = ref([])
const selectedPeriod = ref('month')
const statusFilter = ref('all')

const periods = [
  { value: 'today', label: 'Сегодня' },
  { value: 'week', label: 'Неделя' },
  { value: 'month', label: 'Месяц' },
  { value: 'all', label: 'Все время' }
]

const periodLabel = computed(() => {
  const period = periods.find(p => p.value === selectedPeriod.value)
  return period?.label || 'Все время'
})

const filteredWorkLogs = computed(() => {
  let filtered = workLogs.value

  // Фильтр по периоду
  if (selectedPeriod.value !== 'all') {
    const now = new Date()
    const startDate = new Date()

    if (selectedPeriod.value === 'today') {
      startDate.setHours(0, 0, 0, 0)
    } else if (selectedPeriod.value === 'week') {
      startDate.setDate(now.getDate() - 7)
    } else if (selectedPeriod.value === 'month') {
      startDate.setMonth(now.getMonth() - 1)
    }

    filtered = filtered.filter(log => {
      const logDate = new Date(log.completed_at)
      return logDate >= startDate
    })
  }

  // Фильтр по статусу
  if (statusFilter.value === 'paid') {
    filtered = filtered.filter(log => log.is_paid)
  } else if (statusFilter.value === 'unpaid') {
    filtered = filtered.filter(log => !log.is_paid)
  }

  return filtered.sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))
})

const groupedWorkLogs = computed(() => {
  const groups = {}
  
  filteredWorkLogs.value.forEach(log => {
    const date = new Date(log.completed_at).toLocaleDateString('ru-RU')
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(log)
  })

  return groups
})

const periodTotal = computed(() => {
  return filteredWorkLogs.value.reduce((sum, log) => sum + log.payment, 0)
})

const formatMoney = (amount) => {
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount || 0) + ' тг'
}

const formatGroupDate = (dateStr) => {
  const date = new Date(dateStr.split('.').reverse().join('-'))
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const logDate = new Date(date)
  logDate.setHours(0, 0, 0, 0)

  if (logDate.getTime() === today.getTime()) {
    return 'Сегодня'
  } else if (logDate.getTime() === yesterday.getTime()) {
    return 'Вчера'
  } else {
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    })
  }
}

const formatTime = (dateString) => {
  return new Date(dateString).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatShortDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit'
  })
}

const getStageName = (log) => {
  return log.stage?.name || 'Этап не указан'
}

const getGroupTotal = (group) => {
  return group.reduce((sum, log) => sum + log.payment, 0)
}

const selectPeriod = (period) => {
  selectedPeriod.value = period
}

const loadSalaryData = async () => {
  try {
    const { data } = await workLogsAPI.getMySalary()
    salary.value = data
  } catch (error) {
    console.error('Ошибка загрузки зарплаты:', error)
  }
}

const loadWorkLogs = async () => {
  try {
    const { data } = await workLogsAPI.getAll()
    workLogs.value = data
  } catch (error) {
    console.error('Ошибка загрузки логов:', error)
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      loadSalaryData(),
      loadWorkLogs()
    ])
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.salary-report {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
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
  border-left: 4px solid transparent;
}

.stat-card.total {
  border-left-color: #667eea;
}

.stat-card.paid {
  border-left-color: #27ae60;
}

.stat-card.unpaid {
  border-left-color: #f39c12;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  background: #f3f4f6;
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
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.25rem;
}

.stat-meta {
  font-size: 0.875rem;
  color: #6b7280;
}

.filters-bar {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.period-filters,
.status-filters {
  display: flex;
  gap: 0.5rem;
}

.period-btn,
.status-btn {
  padding: 0.625rem 1.125rem;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9375rem;
  color: #6b7280;
  transition: all 0.2s;
  font-weight: 500;
}

.period-btn:hover,
.status-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.period-btn.active,
.status-btn.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
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

.work-logs-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1.5rem;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  height: fit-content;
  position: sticky;
  top: 2rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.summary-row span {
  color: #6b7280;
  font-size: 0.9375rem;
}

.summary-row strong {
  color: #111827;
  font-size: 0.9375rem;
}

.summary-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 0.75rem 0;
}

.summary-row.total {
  padding-top: 1rem;
}

.summary-row.total span,
.summary-row.total strong {
  font-size: 1.125rem;
  font-weight: 600;
}

.summary-row.total strong {
  color: #667eea;
}

.work-logs-table {
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

.date-row {
  background: #f3f4f6;
}

.date-header {
  padding: 0.75rem 1rem;
  font-weight: 600;
  color: #111827;
  font-size: 0.9375rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date-total {
  color: #667eea;
  font-weight: 700;
}

.log-row td {
  padding: 1rem;
  border-top: 1px solid #f3f4f6;
}

.time-cell {
  color: #6b7280;
  font-size: 0.875rem;
  white-space: nowrap;
}

.order-cell {
  font-size: 0.875rem;
}

.order-id {
  color: #667eea;
  font-weight: 600;
}

.stage-cell {
  color: #111827;
  font-weight: 500;
}

.amount-cell {
  font-weight: 700;
  color: #27ae60;
  white-space: nowrap;
}

.status-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 600;
  width: fit-content;
}

.status-badge.paid {
  background: #dcfce7;
  color: #065f46;
}

.status-badge.unpaid {
  background: #fef3c7;
  color: #92400e;
}

.paid-date {
  font-size: 0.75rem;
  color: #9ca3af;
}

@media (max-width: 1024px) {
  .work-logs-container {
    grid-template-columns: 1fr;
  }

  .summary-card {
    position: static;
  }
}

@media (max-width: 768px) {
  .salary-report {
    padding: 1rem;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .period-filters,
  .status-filters {
    flex-wrap: wrap;
  }

  .work-logs-table {
    overflow-x: auto;
  }

  table {
    min-width: 600px;
  }
}
</style>