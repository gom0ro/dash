<template>
  <div class="finance-view fade-in">
    <div class="page-header">
      <div class="header-content">
        <h1>Управление финансами</h1>
        <p class="subtitle">Контроль наличности, прибыли и расходов</p>
      </div>
      <AppButton variant="danger" class="withdraw-btn" @click="showWithdrawModal = true">
        <i class="ri-money-dollar-circle-line"></i> Изъятие из кассы
      </AppButton>
    </div>

    <div class="finance-grid">
      <!-- Cash Balance Card -->
      <div class="finance-card main-balance">
        <div class="card-icon"><i class="ri-wallet-3-line"></i></div>
        <div class="card-info">
          <span class="card-label">Текущий остаток в кассе</span>
          <div class="big-value">{{ formatMoney(cashData.cash_balance) }}</div>
          <div class="balance-indicator" :class="{ 'warning': cashData.cash_balance < 10000 }">
            <i class="ri-information-line"></i>
            {{ cashData.cash_balance < 10000 ? 'Низкий баланс наличности' : 'Средства доступны для изъятия' }}
          </div>
        </div>
      </div>

      <!-- Profitability Stats -->
      <div class="finance-card stats-card">
        <div class="stats-header">
          <h3>Финансовые показатели</h3>
          <span class="period-badge">За все время</span>
        </div>
        
        <div class="stats-list">
          <div class="stat-item highlight success">
            <div class="stat-meta">
              <span class="label">Чистая прибыль</span>
              <div class="info-tooltip" title="Доход после вычета всех расходов и зарплат">?</div>
            </div>
            <span class="value">{{ formatMoney(cashData.net_profit) }}</span>
          </div>

          <div class="stat-item">
            <span class="label">Валовая прибыль</span>
            <span class="value">{{ formatMoney(cashData.gross_profit) }}</span>
          </div>

          <div class="stats-divider"></div>

          <div class="stat-item danger-text">
            <span class="label">Общие расходы</span>
            <span class="value">-{{ formatMoney(cashData.total_expenses) }}</span>
          </div>

          <div class="stat-item danger-text">
            <span class="label">Выплачено зарплат</span>
            <span class="value">-{{ formatMoney(cashData.total_salaries) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Withdraw Modal -->
    <AppModal v-model="showWithdrawModal" title="Изъятие денег из кассы">
      <div class="withdraw-modal-body">
        <div class="available-info">
          <span>Доступно в кассе:</span>
          <strong>{{ formatMoney(cashData.cash_balance) }}</strong>
        </div>

        <form @submit.prevent="handleWithdraw" id="withdrawForm">
          <div class="form-group">
            <label>Сумма изъятия</label>
            <div class="input-wrapper">
              <input 
                v-model.number="withdrawForm.amount" 
                type="number" 
                required 
                class="modern-input" 
                :max="cashData.cash_balance"
                placeholder="0.00"
              />
              <span class="currency-label">₸</span>
            </div>
          </div>
          <div class="form-group">
            <label>Примечание к операции</label>
            <textarea 
              v-model="withdrawForm.note" 
              class="modern-textarea" 
              rows="3" 
              placeholder="Например: Покупка канцелярии или хозяйственные нужды"
            ></textarea>
          </div>
        </form>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showWithdrawModal = false">Отмена</AppButton>
        <AppButton variant="danger" form="withdrawForm" :loading="withdrawing" @click="handleWithdraw" class="confirm-btn">
          Подтвердить изъятие
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { reportsAPI } from '@/api'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'

const loading = ref(false)
const withdrawing = ref(false)
const cashData = ref({})
const showWithdrawModal = ref(false)

const withdrawForm = ref({
  amount: 0,
  note: ''
})

const formatMoney = (amount) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'KZT',
    minimumFractionDigits: 0
  }).format(amount || 0)
}

const loadData = async () => {
  loading.value = true
  try {
    const { data } = await reportsAPI.getCashReport()
    cashData.value = data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleWithdraw = async () => {
  if (withdrawForm.value.amount <= 0) return alert('Сумма должна быть больше 0')
  if (withdrawForm.value.amount > cashData.value.cash_balance) return alert('Недостаточно средств в кассе')

  withdrawing.value = true
  try {
    await reportsAPI.withdrawCash(withdrawForm.value)
    showWithdrawModal.value = false
    withdrawForm.value = { amount: 0, note: '' }
    await loadData()
  } catch (err) {
    alert('Ошибка при изъятии')
  } finally {
    withdrawing.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.finance-view {
  padding: 1.5rem;
  max-width: 1200px;
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

.subtitle {
  color: #64748b;
  font-weight: 500;
  margin: 0;
}

.withdraw-btn {
  padding: 0.75rem 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.finance-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.finance-card {
  background: white;
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid #f1f5f9;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.04);
}

.main-balance {
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.card-icon {
  position: absolute;
  top: -20px;
  right: -20px;
  font-size: 8rem;
  opacity: 0.03;
  color: #1e293b;
  transform: rotate(-15deg);
}

.card-label {
  font-size: 0.875rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}

.big-value {
  font-size: 3.5rem;
  font-weight: 900;
  color: #1e293b;
  margin-bottom: 1.5rem;
  letter-spacing: -0.04em;
}

.balance-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #059669;
  font-weight: 600;
  background: #ecfdf5;
  padding: 0.5rem 1rem;
  border-radius: 99px;
  align-self: flex-start;
}

.balance-indicator.warning {
  color: #d97706;
  background: #fffbeb;
}

.stats-card .stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.stats-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: #1e293b;
}

.period-badge {
  background: #f1f5f9;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  text-transform: uppercase;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item .label {
  font-size: 1rem;
  color: #475569;
  font-weight: 500;
}

.stat-item .value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.stat-item.highlight {
  background: #f8fafc;
  padding: 1.25rem;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
}

.stat-item.highlight.success .value {
  color: #059669;
  font-size: 1.5rem;
}

.stat-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-tooltip {
  width: 18px;
  height: 18px;
  background: #e2e8f0;
  color: #64748b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 800;
  cursor: help;
}

.stats-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 0.5rem 0;
}

.danger-text .value {
  color: #ef4444;
}

/* Modal Improvements */
.withdraw-modal-body {
  padding: 0.5rem 0;
}

.available-info {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.available-info span { color: #64748b; font-weight: 500; }
.available-info strong { color: #1e293b; font-size: 1.1rem; }

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.modern-input {
  width: 100%;
  padding: 1rem 1rem 1rem 1.25rem;
  border: 2px solid #f1f5f9;
  background: #f8fafc;
  border-radius: 12px;
  font-size: 1.25rem;
  font-weight: 700;
  transition: all 0.2s;
}

.modern-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.currency-label {
  position: absolute;
  right: 1.25rem;
  font-weight: 800;
  color: #94a3b8;
  font-size: 1.25rem;
}

.modern-textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #f1f5f9;
  background: #f8fafc;
  border-radius: 12px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s;
}

.modern-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
}

.confirm-btn {
  padding: 0.75rem 1.5rem;
  font-weight: 700;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in { animation: fadeIn 0.4s ease; }

@media (max-width: 1024px) {
  .finance-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.25rem;
  }
  
  .withdraw-btn {
    width: 100%;
    justify-content: center;
  }
  
  .big-value {
    font-size: 2.5rem;
  }
  
  .finance-card {
    padding: 1.5rem;
  }
  
  .stat-item.highlight.success .value {
    font-size: 1.25rem;
  }
}
</style>
