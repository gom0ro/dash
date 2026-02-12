<template>
  <div class="salaries-view fade-in">
    <div class="page-header">
      <div class="header-content">
        <h1>Выплата зарплаты</h1>
        <p class="subtitle">Управление начислениями, авансами и расчетами с персоналом</p>
      </div>
      <div class="header-actions-global" v-if="selectedWorker">
          <AppButton variant="primary" @click="openAdvanceModal" class="action-btn-main">
            <i class="ri-hand-coin-line"></i> <span>Выдать аванс</span>
          </AppButton>
          <AppButton 
            variant="success" 
            :disabled="selectedIds.length === 0"
            @click="paySelected"
            :loading="paying"
            class="action-btn-main"
          >
            <i class="ri-money-dollar-circle-line"></i> 
            <span>Выплатить ({{ formatMoney(selectedAmount) }})</span>
          </AppButton>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка данных о сотрудниках...</p>
    </div>

    <div v-else class="salaries-layout">
      <!-- Left: Workers List -->
      <aside class="workers-sidebar" :class="{ 'hidden-mobile': selectedWorker }">
        <div class="sidebar-header">
            <div class="search-wrapper">
                <i class="ri-search-line"></i>
                <input v-model="searchQuery" type="text" placeholder="Поиск по имени..." />
            </div>
            <div class="date-filters">
                <input v-model="filters.startDate" type="date" @change="loadWorkers" title="Начало периода" />
                <input v-model="filters.endDate" type="date" @change="loadWorkers" title="Конец периода" />
            </div>
        </div>

        <div class="workers-list">
          <div 
            v-for="worker in filteredWorkers" 
            :key="worker.worker_id"
            class="worker-card-mini"
            :class="{ active: selectedWorker?.worker_id === worker.worker_id }"
            @click="selectWorker(worker)"
          >
            <div class="mini-avatar" :style="avatarStyle(worker.worker_name)">
              {{ worker.worker_name.charAt(0) }}
            </div>
            <div class="mini-info">
              <span class="name">{{ worker.worker_name }}</span>
              <span class="balance" :class="getBalanceClass(worker.current_balance)">
                {{ worker.current_balance > 0 ? 'Долг: ' : 'Аванс: ' }}
                {{ formatMoney(Math.abs(worker.current_balance)) }}
              </span>
            </div>
            <div v-if="worker.total_unpaid > 0" class="pending-indicator"></div>
            <i class="ri-arrow-right-s-line chevron"></i>
          </div>
        </div>
      </aside>

      <!-- Right: Worker Details -->
      <main class="worker-details" :class="{ 'visible-mobile': selectedWorker }">
        <div v-if="!selectedWorker" class="welcome-screen">
          <div class="welcome-icon"><i class="ri-wallet-line"></i></div>
          <h2>Финансовый кабинет сотрудника</h2>
          <p>Выберите сотрудника из списка слева для просмотра детализации выработки, истории платежей и выплаты заработной платы.</p>
        </div>
        
        <div v-else class="details-pane">
          <!-- Back button for mobile -->
          <button class="back-link" @click="selectedWorker = null">
            <i class="ri-arrow-left-line"></i> Назад к списку
          </button>

          <header class="worker-header-card">
              <div class="profile-main">
                <div class="avatar-large" :style="avatarStyle(selectedWorker.worker_name)">
                    {{ selectedWorker.worker_name.charAt(0) }}
                </div>
                <div class="profile-text">
                    <h2>{{ selectedWorker.worker_name }}</h2>
                    <div class="contact-pill" v-if="selectedWorker.worker_phone">
                        <i class="ri-phone-fill"></i>
                        <a :href="'tel:' + selectedWorker.worker_phone">{{ selectedWorker.worker_phone }}</a>
                    </div>
                </div>
              </div>
          </header>

          <div class="stats-grid-salaries">
            <div class="salary-stat-card">
              <span class="lbl">Заработано (все)</span>
              <span class="val">{{ formatMoney(selectedWorker.total_earned) }}</span>
              <div class="icon bill"><i class="ri-bank-card-line"></i></div>
            </div>
            <div class="salary-stat-card">
              <span class="lbl">Выплачено</span>
              <span class="val">{{ formatMoney(selectedWorker.total_paid) }}</span>
              <div class="icon check"><i class="ri-checkbox-circle-line"></i></div>
            </div>
            <div class="salary-stat-card">
              <span class="lbl">Авансы</span>
              <span class="val">{{ formatMoney(selectedWorker.total_advances) }}</span>
              <div class="icon advance"><i class="ri-hand-coin-line"></i></div>
            </div>
            <div class="salary-stat-card balance" :class="getBalanceClass(selectedWorker.current_balance)">
              <span class="lbl">{{ selectedWorker.current_balance < 0 ? 'Долг (аванс)' : 'К выплате' }}</span>
              <span class="val">{{ formatMoney(Math.abs(selectedWorker.current_balance)) }}</span>
            </div>
          </div>

          <div class="tabs-nav">
            <button :class="{ active: activeTab === 'unpaid' }" @click="activeTab = 'unpaid'">
              К выплате <span v-if="unpaidLogs.length">({{ unpaidLogs.length }})</span>
            </button>
            <button :class="{ active: activeTab === 'all_work' }" @click="activeTab = 'all_work'">
              Выработка
            </button>
            <button :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">
              Транзакции
            </button>
          </div>

          <!-- Unpaid Tab -->
          <div v-show="activeTab === 'unpaid'" class="tab-content-pane">
            <div class="pane-header">
              <h3>Ожидает оплаты</h3>
              <button class="select-all-btn" v-if="unpaidLogs.length" @click="toggleSelectAll">
                {{ isAllSelected ? 'Снять все' : 'Выбрать все' }}
              </button>
            </div>
            
            <div v-if="unpaidLogs.length === 0" class="empty-tab">
              <i class="ri-emotion-happy-line"></i>
              <p>Все работы оплачены!</p>
            </div>
            
            <div v-else class="logs-list">
              <div 
                v-for="log in unpaidLogs" 
                :key="log.id" 
                class="log-row"
                :class="{ 'selected': selectedIds.includes(log.id) }"
                @click="toggleLogSelection(log.id)"
              >
                <div class="log-check">
                   <div class="check-box"><i class="ri-check-line"></i></div>
                </div>
                <div class="log-main">
                    <span class="log-product">{{ log.product_name }}</span>
                    <span class="log-stage">{{ log.stage_name }} • {{ log.quantity }} шт.</span>
                </div>
                <div class="log-right">
                    <span class="log-price">{{ formatMoney(log.payment) }}</span>
                    <span class="log-date">{{ formatDateShort(log.completed_at) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- All Work Tab -->
          <div v-show="activeTab === 'all_work'" class="tab-content-pane">
            <div v-if="allWorkLogs.length === 0" class="empty-tab">
              <i class="ri-inbox-line"></i>
              <p>Нет записей за период</p>
            </div>
            <div class="table-responsive" v-else>
              <table class="compact-table">
                <thead>
                  <tr>
                    <th>Дата</th>
                    <th>Изделие</th>
                    <th>Этап</th>
                    <th>Сумма</th>
                    <th>Статус</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="log in allWorkLogs" :key="log.id">
                    <td class="small">{{ formatDateShort(log.completed_at) }}</td>
                    <td class="bold">{{ log.product_name }}</td>
                    <td><span class="stage-tag-small">{{ log.stage_name }}</span></td>
                    <td class="bold">{{ formatMoney(log.payment) }}</td>
                    <td>
                      <span class="stat-badge-mini" :class="log.is_paid ? 'paid' : 'pending'">
                        {{ log.is_paid ? 'Оплачен' : 'Ожидает' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- History Tab -->
          <div v-show="activeTab === 'history'" class="tab-content-pane">
            <div v-if="paymentHistory.length === 0" class="empty-tab">
              <i class="ri-history-line"></i>
              <p>История пуста</p>
            </div>
            <div class="history-list" v-else>
                <div v-for="pay in paymentHistory" :key="pay.id" class="history-item">
                    <div class="hist-icon" :class="pay.payment_type">
                        <i :class="pay.payment_type === 'advance' ? 'ri-hand-coin-fill' : 'ri-wallet-3-fill'"></i>
                    </div>
                    <div class="hist-info">
                        <span class="type">{{ pay.payment_type === 'advance' ? 'Аванс' : 'Выплата з/п' }}</span>
                        <span class="comment">{{ pay.comment || 'Без комментария' }}</span>
                        <span class="date">{{ formatDate(pay.created_at) }}</span>
                    </div>
                    <div class="hist-amount">{{ formatMoney(pay.amount) }}</div>
                </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Advance Modal -->
    <AppModal v-model="showAdvanceModal" title="Выдача аванса">
      <div class="modal-inner-form">
        <div class="f-group">
          <label>Сумма выплаты</label>
          <div class="huge-input">
            <input v-model.number="advanceForm.amount" type="number" placeholder="0" />
            <span class="curr">₸</span>
          </div>
        </div>
        <div class="f-group">
          <label>Комментарий</label>
          <textarea v-model="advanceForm.comment" rows="3" placeholder="Укажите причину..."></textarea>
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
  startDate: '',
  endDate: ''
})

const advanceForm = ref({
  amount: 0,
  comment: ''
})

const formatMoney = (v) => new Intl.NumberFormat('ru-RU').format(v || 0) + ' ₸'
const formatDate = (d) => new Date(d).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
const formatDateShort = (d) => new Date(d).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })

const filteredWorkers = computed(() => {
  return workers.value.filter(w => 
    w.worker_name.toLowerCase().includes(searchQuery.value.toLowerCase())
  ).sort((a, b) => b.current_balance - a.current_balance)
})

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
    const [resUnpaid, resAll, resHistory] = await Promise.all([
      workLogsAPI.getAll({ ...params, is_paid: false }),
      workLogsAPI.getAll(params),
      salariesAPI.getHistory(worker.worker_id)
    ])
    unpaidLogs.value = resUnpaid.data
    allWorkLogs.value = resAll.data.sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))
    paymentHistory.value = resHistory.data
  } catch (e) {
    console.error(e)
  }
}

const toggleLogSelection = (id) => {
  const index = selectedIds.value.indexOf(id)
  index > -1 ? selectedIds.value.splice(index, 1) : selectedIds.value.push(id)
}

const isAllSelected = computed(() => unpaidLogs.value.length > 0 && selectedIds.value.length === unpaidLogs.value.length)
const toggleSelectAll = () => selectedIds.value = isAllSelected.value ? [] : unpaidLogs.value.map(l => l.id)
const selectedAmount = computed(() => unpaidLogs.value.filter(l => selectedIds.value.includes(l.id)).reduce((sum, l) => sum + l.payment, 0))

const paySelected = async () => {
  if (selectedIds.value.length === 0) return
  if (!confirm(`Вы подтверждаете выплату на сумму ${formatMoney(selectedAmount.value)}?`)) return
  paying.value = true
  try {
    await workLogsAPI.markAsPaid({ work_log_ids: selectedIds.value })
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

const avatarStyle = (name) => {
    const hues = [210, 160, 40, 10, 280, 25]
    const idx = (name || '').length % hues.length
    return { background: `hsl(${hues[idx]}, 65%, 60%)`, color: 'white' }
}

const getBalanceClass = (val) => val > 0 ? 'warning' : val < 0 ? 'success' : ''

onMounted(loadWorkers)
</script>

<style scoped>
.salaries-view { padding: 1.5rem; max-width: 1500px; margin: 0 auto; height: calc(100vh - 100px); display: flex; flex-direction: column; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.header-content h1 { font-size: 2rem; font-weight: 800; color: #1e293b; margin: 0 0 0.5rem; }
.subtitle { color: #64748b; font-weight: 500; }
.header-actions-global { display: flex; gap: 1rem; }
.action-btn-main { padding: 0.75rem 1.5rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem; }

.salaries-layout { display: grid; grid-template-columns: 360px 1fr; gap: 2rem; flex: 1; min-height: 0; }

/* Sidebar */
.workers-sidebar { background: white; border-radius: 24px; display: flex; flex-direction: column; border: 1px solid #f1f5f9; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); overflow: hidden; }
.sidebar-header { padding: 1.25rem; border-bottom: 1px solid #f8fafc; background: #fafafa; }
.search-wrapper { position: relative; margin-bottom: 1rem; }
.search-wrapper i { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.search-wrapper input { width: 100%; padding: 0.75rem 1rem 0.75rem 2.75rem; border: 1.5px solid #edf2f7; border-radius: 12px; font-size: 0.95rem; }
.date-filters { display: flex; gap: 0.5rem; }
.date-filters input { flex: 1; padding: 0.5rem; border: 1px solid #edf2f7; border-radius: 8px; font-size: 0.8rem; }

.workers-list { flex: 1; overflow-y: auto; padding: 1rem; }
.worker-card-mini { display: flex; align-items: center; gap: 1rem; padding: 1rem; border-radius: 16px; cursor: pointer; transition: all 0.2s; position: relative; border: 2px solid transparent; }
.worker-card-mini:hover { background: #f8fafc; }
.worker-card-mini.active { background: #eff6ff; border-color: #3b82f6; }

.mini-avatar { width: 44px; height: 44px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.2rem; }
.mini-info { display: flex; flex-direction: column; overflow: hidden; }
.mini-info .name { font-weight: 700; color: #1e293b; font-size: 0.95rem; }
.mini-info .balance { font-size: 0.8rem; font-weight: 800; }
.mini-info .balance.warning { color: #d97706; }
.mini-info .balance.success { color: #059669; }

.pending-indicator { width: 8px; height: 8px; background: #ef4444; border-radius: 50%; margin-left: auto; }
.chevron { margin-left: auto; color: #cbd5e1; }

/* Details Pane */
.worker-details { background: white; border-radius: 24px; border: 1px solid #f1f5f9; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); display: flex; flex-direction: column; overflow: hidden; }
.welcome-screen { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem; text-align: center; }
.welcome-icon { font-size: 5rem; color: #e2e8f0; margin-bottom: 2rem; }
.welcome-screen h2 { color: #1e293b; margin-bottom: 1rem; }
.welcome-screen p { color: #64748b; max-width: 400px; line-height: 1.6; }

.details-pane { padding: 2rem; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 2rem; }
.back-link { display: none; padding: 0.5rem 0; background: none; border: none; font-weight: 700; color: #3b82f6; cursor: pointer; align-items: center; gap: 0.5rem; }

.worker-header-card { display: flex; justify-content: space-between; align-items: center; }
.profile-main { display: flex; align-items: center; gap: 1.5rem; }
.avatar-large { width: 72px; height: 72px; border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; font-weight: 900; }
.profile-text h2 { margin: 0; font-size: 1.8rem; font-weight: 900; color: #1e293b; }
.contact-pill { display: flex; align-items: center; gap: 0.5rem; font-weight: 700; color: #3b82f6; font-size: 0.9rem; margin-top: 0.4rem; }
.contact-pill a { color: inherit; text-decoration: none; }

.stats-grid-salaries { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.25rem; }
.salary-stat-card { background: #f8fafc; padding: 1.25rem; border-radius: 20px; position: relative; overflow: hidden; display: flex; flex-direction: column; border: 1px solid #f1f5f9; }
.salary-stat-card .lbl { font-size: 0.75rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
.salary-stat-card .val { font-size: 1.25rem; font-weight: 900; color: #1e293b; }
.salary-stat-card .icon { position: absolute; right: -10px; bottom: -10px; font-size: 4rem; opacity: 0.03; transform: rotate(-15deg); }
.salary-stat-card.balance.warning { background: #fffbeb; border-color: #fef3c7; }
.salary-stat-card.balance.warning .val { color: #d97706; }
.salary-stat-card.balance.success { background: #f0fdf4; border-color: #dcfce7; }
.salary-stat-card.balance.success .val { color: #059669; }

.tabs-nav { display: flex; background: #f1f5f9; padding: 0.4rem; border-radius: 14px; gap: 0.25rem; }
.tabs-nav button { flex: 1; padding: 0.75rem; border: none; border-radius: 10px; font-weight: 800; color: #64748b; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; }
.tabs-nav button.active { background: white; color: #3b82f6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }

.tab-content-pane { flex: 1; }
.pane-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
.pane-header h3 { font-size: 1.2rem; font-weight: 800; color: #1e293b; margin: 0; }
.select-all-btn { background: #f1f5f9; border: none; padding: 0.4rem 0.8rem; border-radius: 8px; font-weight: 700; color: #475569; font-size: 0.8rem; cursor: pointer; }

.logs-list { display: flex; flex-direction: column; gap: 0.75rem; }
.log-row { display: flex; align-items: center; gap: 1rem; padding: 1rem; background: #f8fafc; border-radius: 16px; border: 2px solid transparent; cursor: pointer; transition: all 0.2s; }
.log-row:hover { background: #f1f5f9; }
.log-row.selected { background: white; border-color: #3b82f6; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08); }

.log-check { width: 24px; height: 24px; border: 2px solid #cbd5e1; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.check-box { font-size: 1.2rem; color: white; transition: all 0.2s; opacity: 0; transform: scale(0.5); }
.log-row.selected .log-check { border-color: #3b82f6; background: #3b82f6; }
.log-row.selected .check-box { opacity: 1; transform: scale(1); }

.log-main { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.log-product { font-weight: 800; color: #1e293b; }
.log-stage { font-size: 0.85rem; color: #64748b; font-weight: 600; }
.log-right { text-align: right; display: flex; flex-direction: column; gap: 2px; }
.log-price { font-weight: 900; color: #3b82f6; font-size: 1.1rem; }
.log-date { font-size: 0.75rem; color: #94a3b8; font-weight: 600; }

.empty-tab { text-align: center; padding: 4rem; color: #cbd5e1; }
.empty-tab i { font-size: 4rem; margin-bottom: 1rem; }

.history-list { display: flex; flex-direction: column; gap: 1rem; }
.history-item { display: flex; align-items: center; gap: 1.25rem; padding: 1.25rem; background: #f8fafc; border-radius: 18px; }
.hist-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0; }
.hist-icon.advance { background: #fff7ed; color: #ea580c; }
.hist-icon.salary { background: #eff6ff; color: #3b82f6; }
.hist-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.hist-info .type { font-weight: 800; color: #1e293b; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }
.hist-info .comment { font-size: 0.95rem; color: #475569; font-weight: 600; }
.hist-info .date { font-size: 0.75rem; color: #94a3b8; font-weight: 500; }
.hist-amount { font-size: 1.25rem; font-weight: 900; color: #1e293b; }

.modal-inner-form { display: flex; flex-direction: column; gap: 1.5rem; padding: 0.5rem 0; }
.huge-input { position: relative; }
.huge-input input { width: 100%; border: 2px solid #f1f5f9; background: #f8fafc; padding: 1.25rem; padding-right: 3rem; border-radius: 16px; font-size: 2rem; font-weight: 900; color: #1e293b; text-align: center; }
.huge-input .curr { position: absolute; right: 1.5rem; top: 50%; transform: translateY(-50%); font-size: 1.5rem; font-weight: 900; color: #94a3b8; }
.f-group label { display: block; font-weight: 800; color: #1e293b; margin-bottom: 0.75rem; font-size: 0.9rem; text-transform: uppercase; }
.f-group textarea { width: 100%; border: 2px solid #f1f5f9; background: #f8fafc; padding: 1rem; border-radius: 14px; resize: none; font-size: 1rem; }

.loading-state { text-align: center; padding: 5rem; }
.spinner { width: 3.5rem; height: 3.5rem; border: 4px solid #f1f5f9; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1.5rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1200px) {
    .salaries-layout { grid-template-columns: 320px 1fr; }
    .stats-grid-salaries { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 900px) {
    .salaries-layout { display: block; position: relative; height: auto; }
    .workers-sidebar.hidden-mobile { display: none; }
    .worker-details { display: none; }
    .worker-details.visible-mobile { display: flex; position: fixed; inset: 0; z-index: 1000; border-radius: 0; padding-top: 2rem; }
    .back-link { display: flex; }
    .page-header { flex-direction: column; align-items: flex-start; gap: 1rem; }
    .header-actions-global { width: 100%; flex-direction: column; }
    .action-btn-main { justify-content: center; }
}

/* Compact Table fallback */
.table-responsive { overflow-x: auto; }
.compact-table { width: 100%; border-collapse: collapse; }
.compact-table th { text-align: left; padding: 1rem; color: #94a3b8; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; border-bottom: 1px solid #f8fafc; }
.compact-table td { padding: 1rem; border-bottom: 1px solid #f8fafc; font-size: 0.95rem; }
.bold { font-weight: 800; }
.small { font-size: 0.8rem; color: #94a3b8; }
.stage-tag-small { background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; }
.stat-badge-mini { padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; }
.stat-badge-mini.paid { background: #dcfce7; color: #059669; }
.stat-badge-mini.pending { background: #fff7ed; color: #d97706; }
</style>
