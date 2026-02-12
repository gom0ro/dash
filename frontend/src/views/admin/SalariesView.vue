<template>
  <div class="salaries-management">
    <div class="page-header">
      <div>
        <h1>Выплата зарплаты</h1>
        <p class="subtitle">Управление начислениями и выплатами сотрудникам</p>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка данных о сотрудниках...</p>
    </div>

    <div v-else class="salaries-grid">
      <!-- Список сотрудников -->
      <div class="workers-list-card card">
        <div class="card-header-flex">
          <h3>Сотрудники</h3>
          <span class="count-badge">{{ filteredWorkers.length }}</span>
        </div>
        
        <div class="filters-container">
          <div class="search-box">
            <i class="ri-search-line"></i>
            <input v-model="searchQuery" type="text" placeholder="Поиск сотрудника..." class="input-minimal" />
          </div>
          
          <div class="date-range-filter">
            <div class="date-input-group">
              <label>Период с:</label>
              <input v-model="filters.startDate" type="date" class="input-small" @change="loadWorkers" />
            </div>
            <div class="date-input-group">
              <label>по:</label>
              <input v-model="filters.endDate" type="date" class="input-small" @change="loadWorkers" />
            </div>
          </div>
        </div>

        <div class="workers-scroll">
          <div 
            v-for="worker in filteredWorkers" 
            :key="worker.worker_id"
            class="worker-item"
            :class="{ active: selectedWorker?.worker_id === worker.worker_id }"
            @click="selectWorker(worker)"
          >
            <div class="worker-avatar" :style="{ background: getAvatarColor(worker.worker_name) }">
              {{ worker.worker_name.charAt(0) }}
            </div>
            <div class="worker-info">
              <div class="worker-name">{{ worker.worker_name }}</div>
              <div class="worker-balance" :class="getBalanceClass(worker.current_balance)">
                {{ worker.current_balance > 0 ? 'Долг: ' : 'Аванс: ' }}
                {{ formatMoney(Math.abs(worker.current_balance)) }}
              </div>
            </div>
            <div v-if="worker.total_unpaid > 0" class="alert-dot"></div>
            <div class="worker-chevron">
              <i class="ri-arrow-right-s-line"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Детализация по выбранному сотруднику -->
      <div class="worker-details-card card">
        <div v-if="!selectedWorker" class="no-selection">
          <div class="empty-state-illustration">
            <i class="ri-wallet-3-line"></i>
          </div>
          <h2>Управление финансами персонала</h2>
          <p>Выберите сотрудника из списка слева, чтобы посмотреть детализацию начислений, выдать аванс или произвести выплату зарплаты.</p>
        </div>
        
        <div v-else class="details-content">
          <div class="details-header">
            <div class="worker-profile">
              <div class="worker-avatar-large" :style="{ background: getAvatarColor(selectedWorker.worker_name) }">
                {{ selectedWorker.worker_name.charAt(0) }}
              </div>
              <div class="worker-profile-info">
                <h2>{{ selectedWorker.worker_name }}</h2>
                <div class="worker-contact" v-if="selectedWorker.worker_phone">
                  <i class="ri-phone-line"></i>
                  <a :href="'tel:' + selectedWorker.worker_phone">{{ selectedWorker.worker_phone }}</a>
                </div>
              </div>
            </div>
            
            <div class="header-actions">
              <AppButton 
                variant="primary" 
                @click="openAdvanceModal"
              >
                <i class="ri-hand-coin-line"></i> Выдать аванс
              </AppButton>
              <AppButton 
                variant="success" 
                :disabled="selectedIds.length === 0"
                @click="paySelected"
                :loading="paying"
              >
                <i class="ri-money-dollar-circle-line"></i> 
                {{ selectedIds.length > 0 ? `Выплатить выбранное (${formatMoney(selectedAmount)})` : 'Выплатить' }}
              </AppButton>
            </div>
          </div>

          <!-- Stats Dashboard -->
          <div class="stats-dashboard">
            <div class="dashboard-card">
              <div class="dash-icon blue"><i class="ri-funds-line"></i></div>
              <div class="dash-data">
                <span class="dash-label">Заработано (всего)</span>
                <span class="dash-value">{{ formatMoney(selectedWorker.total_earned) }}</span>
              </div>
            </div>
            <div class="dashboard-card">
              <div class="dash-icon green"><i class="ri-checkbox-circle-line"></i></div>
              <div class="dash-data">
                <span class="dash-label">Выплачено</span>
                <span class="dash-value">{{ formatMoney(selectedWorker.total_paid) }}</span>
              </div>
            </div>
            <div class="dashboard-card">
              <div class="dash-icon yellow"><i class="ri-exchange-funds-line"></i></div>
              <div class="dash-data">
                <span class="dash-label">Авансы</span>
                <span class="dash-value">{{ formatMoney(selectedWorker.total_advances) }}</span>
              </div>
            </div>
            <div class="dashboard-card highlight-card" :class="getBalanceClass(selectedWorker.current_balance)">
              <div class="dash-icon"><i class="ri-scales-3-line"></i></div>
              <div class="dash-data">
                <span class="dash-label">Текущий баланс</span>
                <span class="dash-value">{{ formatMoney(selectedWorker.current_balance) }}</span>
              </div>
            </div>
          </div>

          <!-- Performance Row -->
          <div class="stats-dashboard performance-row">
            <div class="dashboard-card small">
              <div class="dash-icon primary"><i class="ri-focus-3-line"></i></div>
              <div class="dash-data">
                <span class="dash-label">Специализация</span>
                <span class="dash-value">{{ selectedWorker.top_product || '—' }}</span>
              </div>
            </div>
            <div class="dashboard-card small">
              <div class="dash-icon primary"><i class="ri-speed-up-line"></i></div>
              <div class="dash-data">
                <span class="dash-label">Средний доход (в день)</span>
                <span class="dash-value">{{ formatMoney(selectedWorker.avg_daily) }}</span>
              </div>
            </div>
            <div class="dashboard-card small">
              <div class="dash-icon primary"><i class="ri-medal-2-line"></i></div>
              <div class="dash-data">
                <span class="dash-label">Выполнено стадий</span>
                <span class="dash-value">{{ selectedWorker.stages_completed }}</span>
              </div>
            </div>
          </div>

          <div class="details-tabs">
            <button :class="{ active: activeTab === 'unpaid' }" @click="activeTab = 'unpaid'">
              <i class="ri-time-line"></i> Ожидает оплаты ({{ unpaidLogs.length }})
            </button>
            <button :class="{ active: activeTab === 'all_work' }" @click="activeTab = 'all_work'">
              <i class="ri-history-line"></i> Все этапы
            </button>
            <button :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">
              <i class="ri-file-list-3-line"></i> История транзакций
            </button>
          </div>

          <!-- Unpaid Logs Section -->
          <div v-show="activeTab === 'unpaid'" class="tab-panel">
            <div class="panel-header">
              <h3>Начисления к выплате</h3>
              <div class="panel-actions" v-if="unpaidLogs.length > 0">
                <label class="checkbox-container">
                  <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" />
                  <span class="checkmark"></span>
                  Выбрать все
                </label>
              </div>
            </div>
            
            <div v-if="unpaidLogs.length === 0" class="empty-panel">
              <i class="ri-checkbox-circle-fill"></i>
              <p>Все работы оплачены. Нет начислений в ожидании.</p>
            </div>
            
            <div v-else class="table-container">
              <table class="modern-table">
                <thead>
                  <tr>
                    <th width="40"></th>
                    <th>Дата</th>
                    <th>Изделие</th>
                    <th>Этап производства</th>
                    <th>Кол-во</th>
                    <th class="text-right">Сумма</th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="log in unpaidLogs" 
                    :key="log.id" 
                    :class="{ 'selected-row': selectedIds.includes(log.id) }"
                    @click="toggleLogSelection(log.id)"
                  >
                    <td>
                      <label class="checkbox-container" @click.stop>
                        <input type="checkbox" :value="log.id" v-model="selectedIds" />
                        <span class="checkmark"></span>
                      </label>
                    </td>
                    <td class="cell-date">{{ formatDate(log.completed_at) }}</td>
                    <td class="cell-product">{{ log.product_name }}</td>
                    <td>
                      <span class="stage-tag">{{ log.stage_name }}</span>
                    </td>
                    <td class="text-center">{{ log.quantity }} шт.</td>
                    <td class="text-right bold">{{ formatMoney(log.payment) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- All Work Section -->
          <div v-show="activeTab === 'all_work'" class="tab-panel">
            <div class="panel-header">
              <h3>Полная история работ</h3>
            </div>
            
            <div v-if="allWorkLogs.length === 0" class="empty-panel">
              <i class="ri-survey-line"></i>
              <p>Нет записей о выполненной работе за выбранный период.</p>
            </div>
            
            <div v-else class="table-container">
              <table class="modern-table">
                <thead>
                  <tr>
                    <th>Дата</th>
                    <th>Изделие</th>
                    <th>Этап</th>
                    <th>Кол-во</th>
                    <th>Начислено</th>
                    <th>Статус</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="log in allWorkLogs" :key="log.id">
                    <td class="cell-date">{{ formatDate(log.completed_at) }}</td>
                    <td class="cell-product">{{ log.product_name }}</td>
                    <td><span class="stage-tag">{{ log.stage_name }}</span></td>
                    <td class="text-center">{{ log.quantity }} шт.</td>
                    <td class="bold">{{ formatMoney(log.payment) }}</td>
                    <td>
                      <span class="status-badge" :class="log.is_paid ? 'paid' : 'unpaid'">
                        <i :class="log.is_paid ? 'ri-checkbox-circle-line' : 'ri-time-line'"></i>
                        {{ log.is_paid ? 'Оплачено' : 'Ожидает' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- History Section -->
          <div v-show="activeTab === 'history'" class="tab-panel">
            <div class="panel-header">
              <h3>История платежей и авансов</h3>
            </div>
            
            <div v-if="paymentHistory.length === 0" class="empty-panel">
              <i class="ri-history-line"></i>
              <p>История финансовых операций пуста.</p>
            </div>
            
            <div v-else class="table-container">
              <table class="modern-table">
                <thead>
                  <tr>
                    <th>Дата и время</th>
                    <th>Тип операции</th>
                    <th>Сумма</th>
                    <th>Примечание</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="pay in paymentHistory" :key="pay.id">
                    <td class="cell-date">{{ formatDate(pay.created_at) }}</td>
                    <td>
                      <span class="payment-badge" :class="pay.payment_type">
                        <i :class="pay.payment_type === 'advance' ? 'ri-hand-coin-line' : 'ri-money-dollar-box-line'"></i>
                        {{ pay.payment_type === 'advance' ? 'АГАНС' : 'ЗАРПЛАТА' }}
                      </span>
                    </td>
                    <td class="bold text-lg">{{ formatMoney(pay.amount) }}</td>
                    <td class="text-muted italic">{{ pay.comment || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal for Advance -->
    <AppModal v-model="showAdvanceModal" title="Выдача аванса сотруднику">
      <div class="modal-form">
        <div class="form-group-fancy">
          <label>Сумма аванса (₸)</label>
          <div class="input-with-icon">
            <i class="ri-money-tenge-circle-line"></i>
            <input v-model.number="advanceForm.amount" type="number" class="input-big" placeholder="0" />
          </div>
        </div>
        <div class="form-group-fancy">
          <label>Примечание к авансу</label>
          <textarea v-model="advanceForm.comment" class="textarea-fancy" rows="3" placeholder="Например: Семейные обстоятельства, по просьбе сотрудника..."></textarea>
        </div>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showAdvanceModal = false">Отмена</AppButton>
        <AppButton variant="primary" :loading="savingAdvance" @click="submitAdvance">Подтвердить выдачу</AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { reportsAPI, workLogsAPI, salariesAPI } from '@/api'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'

const loading = ref(false)
const paying = ref(false)
const savingAdvance = ref(false)
const workers = ref([])
const searchQuery = ref('')
const selectedWorker = ref(null)
const unpaidLogs = ref([])
const allWorkLogs = ref([])
const paymentHistory = ref([])
const activeTab = ref('unpaid')
const showAdvanceModal = ref(false)
const selectedIds = ref([])

const filters = ref({
  startDate: '', // Default to current month could be better, but start empty
  endDate: ''
})

const advanceForm = ref({
  amount: 0,
  comment: ''
})

const filteredWorkers = computed(() => {
  return workers.value.filter(w => 
    w.worker_name.toLowerCase().includes(searchQuery.value.toLowerCase())
  ).sort((a, b) => b.current_balance - a.current_balance)
})

const formatMoney = (v) => new Intl.NumberFormat('ru-RU').format(v || 0) + ' ₸'
const formatDate = (d) => {
  if (!d) return '—'
  return new Date(d).toLocaleString('ru-RU', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric',
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const loadWorkers = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.startDate) params.start_date = filters.value.startDate
    if (filters.value.endDate) params.end_date = filters.value.endDate
    
    const { data } = await reportsAPI.getWorkersReport(params)
    workers.value = data.workers
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const selectWorker = async (worker) => {
  selectedWorker.value = worker
  unpaidLogs.value = []
  allWorkLogs.value = []
  paymentHistory.value = []
  selectedIds.value = []
  try {
    const params = { worker_id: worker.worker_id }
    if (filters.value.startDate) params.start_date = filters.value.startDate
    if (filters.value.endDate) params.end_date = filters.value.endDate

    // Неоплаченные
    const resUnpaid = await workLogsAPI.getAll({ ...params, is_paid: false })
    unpaidLogs.value = resUnpaid.data
    
    // Все за период
    const resAll = await workLogsAPI.getAll(params)
    allWorkLogs.value = resAll.data.sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))
    
    // История выплат
    const resHistory = await salariesAPI.getHistory(worker.worker_id)
    paymentHistory.value = resHistory.data
  } catch (e) {
    console.error(e)
  }
}

// Logic for selection
const toggleLogSelection = (id) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const isAllSelected = computed(() => {
  return unpaidLogs.value.length > 0 && selectedIds.value.length === unpaidLogs.value.length
})

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = unpaidLogs.value.map(l => l.id)
  }
}

const selectedAmount = computed(() => {
  return unpaidLogs.value
    .filter(l => selectedIds.value.includes(l.id))
    .reduce((sum, l) => sum + l.payment, 0)
})

const paySelected = async () => {
  if (selectedIds.value.length === 0) return
  
  if (!confirm(`Вы подтверждаете выплату на сумму ${formatMoney(selectedAmount.value)}?`)) return

  paying.value = true
  try {
    await workLogsAPI.markAsPaid({ work_log_ids: selectedIds.value })
    
    // Refresh data
    await loadWorkers()
    if (selectedWorker.value) {
      const updated = workers.value.find(w => w.worker_id === selectedWorker.value.worker_id)
      if (updated) await selectWorker(updated)
    }
  } catch (e) {
    alert('Ошибка при выполнении выплаты')
  } finally {
    paying.value = false
  }
}

const openAdvanceModal = () => {
    advanceForm.value = { amount: 0, comment: '' }
    showAdvanceModal.value = true
}

const submitAdvance = async () => {
    if (advanceForm.value.amount <= 0) return alert('Введите корректную сумму')
    savingAdvance.value = true
    try {
        await salariesAPI.createPayment({
            worker_id: selectedWorker.value.worker_id,
            amount: advanceForm.value.amount,
            payment_type: 'advance',
            comment: advanceForm.value.comment
        })
        showAdvanceModal.value = false
        await loadWorkers()
        const updated = workers.value.find(w => w.worker_id === selectedWorker.value.worker_id)
        if (updated) await selectWorker(updated)
    } catch (e) {
        alert('Ошибка при сохранении операции')
    } finally {
        savingAdvance.value = false
    }
}

// Helpers
const getAvatarColor = (name) => {
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

const getBalanceClass = (val) => {
  if (val > 0) return 'warning'
  if (val < 0) return 'success'
  return ''
}

onMounted(loadWorkers)
</script>

<style scoped>
.salaries-management { padding: 1.5rem; max-width: 1600px; margin: 0 auto; background: #f1f5f9; min-height: 100vh; font-family: 'Inter', sans-serif; }
.card { background: white; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; overflow: hidden; }

.salaries-grid { display: grid; grid-template-columns: 350px 1fr; gap: 1.5rem; align-items: flex-start; }

/* Left Column */
.workers-list-card { height: calc(100vh - 120px); display: flex; flex-direction: column; padding: 1.25rem; }
.card-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
.count-badge { background: #e2e8f0; color: #475569; padding: 0.2rem 0.6rem; border-radius: 99px; font-size: 0.75rem; font-weight: 700; }

.filters-container { margin-bottom: 1rem; border-bottom: 1px solid #f1f5f9; padding-bottom: 1rem; }
.search-box { position: relative; margin-bottom: 0.75rem; }
.search-box i { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.input-minimal { width: 100%; padding: 0.6rem 0.75rem 0.6rem 2.5rem; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 0.9rem; transition: all 0.2s; }
.input-minimal:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }

.date-range-filter { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
.date-input-group label { display: block; font-size: 0.7rem; color: #64748b; margin-bottom: 2px; text-transform: uppercase; font-weight: 600; }
.input-small { width: 100%; border: 1px solid #e2e8f0; border-radius: 6px; padding: 0.25rem 0.4rem; font-size: 0.8rem; }

.workers-scroll { overflow-y: auto; flex: 1; padding-right: 4px; }
.worker-item { display: flex; align-items: center; gap: 0.85rem; padding: 0.85rem; border-radius: 12px; cursor: pointer; transition: all 0.2s; margin-bottom: 0.4rem; border: 1.5px solid transparent; position: relative; }
.worker-item:hover { background: #f8fafc; }
.worker-item.active { background: #eff6ff; border-color: #3b82f6; }

.worker-avatar { width: 40px; height: 40px; color: white; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1rem; }
.worker-info { flex: 1; }
.worker-name { font-weight: 600; color: #1e293b; font-size: 0.95rem; }
.worker-balance { font-size: 0.8rem; font-weight: 500; }
.worker-balance.warning { color: #f59e0b; }
.worker-balance.success { color: #10b981; }

.alert-dot { width: 8px; height: 8px; background: #ef4444; border-radius: 50%; margin-right: 0.5rem; }
.worker-chevron { color: #cbd5e1; font-size: 1.2rem; }

/* Right Column */
.worker-details-card { min-height: 800px; display: flex; flex-direction: column; }
.no-selection { height: 100%; flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 4rem; color: #64748b; }
.empty-state-illustration { font-size: 5rem; color: #cbd5e1; margin-bottom: 1.5rem; }
.no-selection h2 { color: #1e293b; margin-bottom: 1rem; }
.no-selection p { max-width: 450px; line-height: 1.6; }

.details-content { padding: 1.5rem; }
.details-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #f1f5f9; }

.worker-profile { display: flex; align-items: center; gap: 1.25rem; }
.worker-avatar-large { width: 64px; height: 64px; border-radius: 16px; color: white; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 800; }
.worker-profile-info h2 { margin: 0; font-size: 1.5rem; font-weight: 800; color: #1e293b; }
.worker-contact { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.35rem; color: #64748b; font-size: 0.9rem; }
.worker-contact a { color: #3b82f6; text-decoration: none; font-weight: 600; }

.header-actions { display: flex; gap: 0.75rem; }

/* Stats Dashboard */
.stats-dashboard { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
.dashboard-card { background: #f8fafc; padding: 1rem; border-radius: 12px; display: flex; align-items: center; gap: 1rem; border: 1px solid #f1f5f9; }
.dash-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }
.dash-icon.blue { background: #dbeafe; color: #2563eb; }
.dash-icon.green { background: #dcfce7; color: #166534; }
.dash-icon.yellow { background: #fef9c3; color: #854d0e; }
.dash-data { display: flex; flex-direction: column; }
.dash-label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
.dash-value { font-size: 1.1rem; font-weight: 800; color: #1e293b; }

.highlight-card.warning { background: #fff7ed; border-color: #fed7aa; }
.highlight-card.warning .dash-icon { background: #ffedd5; color: #ea580c; }
.highlight-card.success { background: #f0fdf4; border-color: #bbf7d0; }
.dashboard-card.small { padding: 0.75rem; background: #fff; border-style: dashed; }
.dashboard-card.small .dash-icon { width: 36px; height: 36px; font-size: 1.1rem; }
.dashboard-card.small .dash-icon.primary { background: #f0f7ff; color: #3b82f6; }
.dashboard-card.small .dash-value { font-size: 0.95rem; }

.performance-row { grid-template-columns: repeat(3, 1fr); margin-bottom: 1.5rem; }

/* Tabs */
.details-tabs { display: flex; gap: 0.5rem; background: #f1f5f9; padding: 0.4rem; border-radius: 10px; margin-bottom: 1.5rem; }
.details-tabs button { flex: 1; padding: 0.6rem; border: none; background: none; border-radius: 8px; cursor: pointer; font-weight: 700; color: #64748b; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem; transition: all 0.2s; }
.details-tabs button:hover { background: rgba(255,255,255,0.5); }
.details-tabs button.active { background: white; color: #3b82f6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }

/* Table Section */
.tab-panel { animation: slideUp 0.3s ease-out; }
@keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.panel-header h3 { font-size: 1.1rem; font-weight: 700; color: #1e293b; margin: 0; }

.modern-table { width: 100%; border-collapse: separate; border-spacing: 0; }
.modern-table th { background: #f8fafc; padding: 1rem; text-align: left; font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #e2e8f0; }
.modern-table td { padding: 1rem; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; vertical-align: middle; transition: all 0.2s; }
.modern-table tr:hover td { background: #f8fafc; }
.selected-row td { background: #eff6ff !important; }

.cell-date { color: #64748b; font-variant-numeric: tabular-nums; width: 150px; }
.cell-product { font-weight: 700; color: #1e293b; }
.stage-tag { background: #f1f5f9; color: #475569; padding: 0.25rem 0.5rem; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }

.status-badge { padding: 0.35rem 0.75rem; border-radius: 8px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.35rem; }
.status-badge.paid { background: #dcfce7; color: #166534; }
.status-badge.unpaid { background: #fee2e2; color: #991b1b; }

.payment-badge { padding: 0.4rem 0.75rem; border-radius: 8px; font-size: 0.8rem; font-weight: 800; display: inline-flex; align-items: center; gap: 0.4rem; }
.payment-badge.salary { background: #eff6ff; color: #2563eb; }
.payment-badge.advance { background: #fef9c3; color: #854d0e; }

.text-lg { font-size: 1.1rem; }
.italic { font-style: italic; }

/* Checkbox Styling */
.checkbox-container { display: block; position: relative; padding-left: 25px; cursor: pointer; font-size: 0.85rem; font-weight: 600; color: #64748b; user-select: none; }
.checkbox-container input { position: absolute; opacity: 0; cursor: pointer; height: 0; width: 0; }
.checkmark { position: absolute; top: 50%; left: 0; transform: translateY(-50%); height: 18px; width: 18px; background-color: #e2e8f0; border-radius: 4px; transition: all 0.2s; }
.checkbox-container:hover input ~ .checkmark { background-color: #cbd5e1; }
.checkbox-container input:checked ~ .checkmark { background-color: #3b82f6; }
.checkmark:after { content: ""; position: absolute; display: none; }
.checkbox-container input:checked ~ .checkmark:after { display: block; }
.checkbox-container .checkmark:after { left: 6px; top: 2px; width: 4px; height: 9px; border: solid white; border-width: 0 2px 2px 0; transform: rotate(45deg); }

.empty-panel { text-align: center; padding: 5rem 2rem; color: #94a3b8; }
.empty-panel i { font-size: 3rem; margin-bottom: 1rem; opacity: 0.4; }

/* Modal Fancy */
.modal-form { padding: 0.5rem; }
.form-group-fancy { margin-bottom: 1.5rem; }
.form-group-fancy label { display: block; font-size: 0.9rem; font-weight: 700; color: #1e293b; margin-bottom: 0.75rem; }
.input-with-icon { position: relative; }
.input-with-icon i { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); font-size: 1.5rem; color: #3b82f6; }
.input-big { width: 100%; border: 2px solid #e2e8f0; border-radius: 12px; padding: 1rem 1rem 1rem 3.5rem; font-size: 1.5rem; font-weight: 800; transition: all 0.2s; }
.input-big:focus { border-color: #3b82f6; outline: none; }
.textarea-fancy { width: 100%; border: 2px solid #e2e8f0; border-radius: 12px; padding: 1rem; font-size: 0.95rem; resize: none; transition: all 0.2s; }
.textarea-fancy:focus { border-color: #3b82f6; outline: none; }

.text-right { text-align: right; }
.text-center { text-align: center; }
.bold { font-weight: 800; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

@media (max-width: 1200px) {
  .salaries-grid { grid-template-columns: 1fr; }
  .workers-list-card { height: auto; }
  .stats-dashboard { grid-template-columns: repeat(2, 1fr); }
}
</style>
