<template>
  <div class="salary-view">
    <div class="header-section">
      <div class="title-with-badge">
        <h1>Моя зарплата</h1>
        <span class="status-badge live">Обновлено в реальном времени</span>
      </div>
      <p class="subtitle">Детализация ваших начислений, выплат и текущего баланса</p>
    </div>

    <!-- Stats Dashboard -->
    <div v-if="stats" class="stats-grid">
      <div 
        class="stat-card primary" 
        :class="{ 'debt-mode': stats.current_balance < 0 }"
      >
        <div class="stat-icon"><i :class="stats.current_balance < 0 ? 'ri-error-warning-line' : 'ri-wallet-3-line'"></i></div>
        <div class="stat-content">
          <span class="stat-label">{{ stats.current_balance < 0 ? 'Долг по авансу' : 'К выплате' }}</span>
          <span class="stat-value">{{ formatMoney(Math.abs(stats.current_balance)) }}</span>
        </div>
        <div class="stat-footer">
          {{ stats.current_balance < 0 ? 'Вы получили больше, чем заработали' : 'Ваш текущий остаток' }}
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon earned"><i class="ri-coins-line"></i></div>
        <div class="stat-content">
          <span class="stat-label">Заработано всего</span>
          <span class="stat-value small">{{ formatMoney(stats.total_earned) }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon paid"><i class="ri-hand-coin-line"></i></div>
        <div class="stat-content">
          <span class="stat-label">Выплачено</span>
          <span class="stat-value small">{{ formatMoney(stats.total_paid) }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon advance"><i class="ri-history-line"></i></div>
        <div class="stat-content">
          <span class="stat-label">Получено авансов</span>
          <span class="stat-value small">{{ formatMoney(stats.total_advances) }}</span>
        </div>
      </div>
    </div>

    <!-- Tabs Content -->
    <div class="content-card">
      <div class="tabs-header">
        <button 
          :class="{ active: activeTab === 'logs' }" 
          @click="activeTab = 'logs'"
        >
          <i class="ri-list-check-2"></i> Мои начисления
        </button>
        <button 
          :class="{ active: activeTab === 'payments' }" 
          @click="activeTab = 'payments'"
        >
          <i class="ri-history-line"></i> История выплат
        </button>
      </div>

      <div class="tab-panel">
        <!-- Work Logs Tab -->
        <div v-show="activeTab === 'logs'" class="table-container fade-in">
          <div v-if="loadingLogs" class="loading-state">
            <div class="spinner"></div>
            <p>Загрузка начислений...</p>
          </div>
          <div v-else-if="logs.length === 0" class="empty-state">
            <i class="ri-inbox-line"></i>
            <p>Начислений пока нет. Выполните работу, чтобы увидеть её здесь.</p>
          </div>
          <div v-else class="table-scroll-wrapper">
            <table class="modern-table">
              <thead>
                <tr>
                  <th>Дата</th>
                  <th>Изделие</th>
                  <th>Этап</th>
                  <th>Плата</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in sortedLogs" :key="log.id">
                  <td class="cell-date">
                    <span class="date">{{ formatDate(log.completed_at) }}</span>
                    <span class="time">{{ formatTime(log.completed_at) }}</span>
                  </td>
                  <td class="cell-product">{{ log.product_name }}</td>
                  <td>
                    <span class="stage-tag">{{ log.stage_name }}</span>
                    <div class="table-qty-hint">{{ log.quantity }} шт.</div>
                  </td>
                  <td class="text-right bold">{{ formatMoney(log.payment) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Payments History Tab -->
        <div v-show="activeTab === 'payments'" class="table-container fade-in">
          <div v-if="loadingHistory" class="loading-state">
            <div class="spinner"></div>
            <p>Загрузка истории...</p>
          </div>
          <div v-else-if="history.length === 0" class="empty-state">
            <i class="ri-bank-card-line"></i>
            <p>Выплат пока не было.</p>
          </div>
          <div v-else class="table-scroll-wrapper">
            <table class="modern-table">
              <thead>
                <tr>
                  <th>Дата</th>
                  <th>Тип</th>
                  <th class="text-right">Сумма</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="pay in history" :key="pay.id">
                  <td class="cell-date">
                    <span class="date">{{ formatDate(pay.created_at) }}</span>
                    <span class="time">{{ formatTime(pay.created_at) }}</span>
                  </td>
                  <td>
                    <span :class="['type-badge', pay.payment_type]">
                      {{ pay.payment_type === 'advance' ? 'Аванс' : 'Зарплата' }}
                    </span>
                    <div class="payment-comment-small">{{ pay.comment }}</div>
                  </td>
                  <td class="text-right bold amount">{{ formatMoney(pay.amount) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { workLogsAPI, salariesAPI } from '@/api'

const stats = ref(null)
const logs = ref([])
const history = ref([])
const activeTab = ref('logs')
const loadingLogs = ref(false)
const loadingHistory = ref(false)

const formatMoney = (val) => new Intl.NumberFormat('ru-RU').format(val || 0) + ' ₸'

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('ru-RU', { 
    day: '2-digit', month: 'short' 
  })
}

const formatTime = (dateStr) => {
  return new Date(dateStr).toLocaleTimeString('ru-RU', { 
    hour: '2-digit', minute: '2-digit' 
  })
}

const sortedLogs = computed(() => {
  return [...logs.value].sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))
})

const loadData = async () => {
  try {
    const { data } = await workLogsAPI.getMySalary()
    stats.value = data
    
    // Initial logs load
    await loadLogs()
    await loadHistory()
  } catch (e) {
    console.error('Error loading salary stats', e)
  }
}

const loadLogs = async () => {
  loadingLogs.value = true
  try {
    const { data } = await workLogsAPI.getAll()
    logs.value = data
  } catch (e) {
    console.error('Error loading logs', e)
  } finally {
    loadingLogs.value = false
  }
}

const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const { data } = await salariesAPI.getMyHistory()
    history.value = data
  } catch (e) {
    console.error('Error loading history', e)
  } finally {
    loadingHistory.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.salary-view {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Inter', sans-serif;
  background: #f8fafc;
  min-height: 100vh;
}

.header-section { margin-bottom: 2rem; }
.title-with-badge { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem; }
.header-section h1 { font-size: 1.875rem; font-weight: 800; color: #1e293b; margin: 0; }
.status-badge.live {
  background: #dcfce7;
  color: #166534;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 99px;
  text-transform: uppercase;
}
.subtitle { color: #64748b; margin: 0; }

.stats-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
  gap: 1.25rem; 
  margin-bottom: 2rem; 
}

.stat-card {
  background: #fff;
  padding: 1.5rem;
  border-radius: 1.25rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.stat-card.primary { background: #3b82f6; color: white; border: none; }
.stat-card.primary .stat-label { color: rgba(255,255,255,0.8); }
.stat-card.primary .stat-icon { background: rgba(255,255,255,0.2); color: white; }
.stat-card.primary.debt-mode { background: #f97316; }
.stat-card.primary.debt-mode .stat-icon { background: rgba(255,255,255,0.3); animation: pulse 2s infinite; }

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  margin-bottom: 1rem;
}

.stat-icon.earned { background: #eff6ff; color: #2563eb; }
.stat-icon.paid { background: #ecfdf5; color: #059669; }
.stat-icon.advance { background: #fffbeb; color: #d97706; }

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-label { 
  font-size: 0.85rem; 
  font-weight: 700; 
  color: #64748b; 
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-card.primary .stat-label { color: rgba(255,255,255,0.9); }

.stat-value { 
  font-size: 1.75rem; 
  font-weight: 800; 
  color: #1e293b;
  line-height: 1.1;
}

.stat-card.primary .stat-value { color: white; }

.stat-value.small { font-size: 1.4rem; }

.stat-footer { 
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
  font-size: 0.85rem;
  font-weight: 500;
  color: #94a3b8;
}

.stat-card.primary .stat-footer { 
  border-top-color: rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.85); 
}

/* Content Card */
.content-card {
  background: white;
  border-radius: 1.25rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  border: 1px solid #f1f5f9;
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

.tabs-header {
  display: flex;
  padding: 0.75rem;
  gap: 0.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.tabs-header button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: transparent;
  border-radius: 0.75rem;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.tabs-header button:hover { background: #f8fafc; color: #1e293b; }
.tabs-header button.active { background: #eff6ff; color: #3b82f6; }

.tab-panel { flex: 1; padding: 1rem; }

.table-container { height: 100%; }

.modern-table { width: 100%; border-collapse: collapse; }
.modern-table th {
  text-align: left;
  padding: 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #f1f5f9;
}

.modern-table td { padding: 1.25rem 1rem; border-bottom: 1px solid #f8fafc; font-size: 0.9375rem; }

.cell-date { display: flex; flex-direction: column; }
.cell-date .date { font-weight: 700; color: #1e293b; }
.cell-date .time { font-size: 0.8rem; color: #94a3b8; }

.cell-product { font-weight: 700; color: #1e293b; }
.stage-tag { background: #f1f5f9; color: #475569; padding: 0.25rem 0.5rem; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }

.status-pill {
  padding: 0.35rem 0.75rem;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 700;
}
.status-pill.paid { background: #dcfce7; color: #166534; }
.status-pill.pending { background: #fee2e2; color: #991b1b; }

.type-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.75rem;
}
.type-badge.salary { background: #dbeafe; color: #1e40af; }
.type-badge.advance { background: #fef9c3; color: #854d0e; }

.comment-cell { color: #64748b; font-style: italic; max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.payment-comment-small { font-size: 0.75rem; color: #94a3b8; font-style: italic; margin-top: 2px; }
.table-qty-hint { font-size: 0.75rem; color: #94a3b8; margin-top: 2px; }
.table-scroll-wrapper { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }

.text-right { text-align: right; }
.text-center { text-align: center; }
.bold { font-weight: 800; }
.amount { color: #1e293b; }

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
  color: #94a3b8;
}

.empty-state i { font-size: 4rem; margin-bottom: 1rem; opacity: 0.3; }

.spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid #f1f5f9;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.3s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

@media (max-width: 768px) {
  .salary-view { padding: 1rem; }
  .header-section h1 { font-size: 1.5rem; }
  .stats-grid { grid-template-columns: 1fr; gap: 1rem; }
  .stat-card { padding: 1.25rem; }
  .stat-value { font-size: 1.5rem; }
  .tabs-header { padding: 0.25rem; }
  .tabs-header button { font-size: 0.85rem; padding: 0.6rem; }
  .tab-panel { padding: 0.5rem; }
  .modern-table th, .modern-table td { padding: 0.75rem 0.5rem; }
}

@media (max-width: 375px) {
    .salary-view { padding: 0.75rem; }
    .stat-value { font-size: 1.35rem; }
}
</style>
