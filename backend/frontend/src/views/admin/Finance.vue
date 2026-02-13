<template>
  <div class="finance-view">
    <div class="page-header">
      <div>
        <h1>Управление финансами</h1>
        <p class="subtitle">Контроль наличности и прибыли</p>
      </div>
      <AppButton variant="danger" @click="showWithdrawModal = true">
        💸 Изъятие из кассы
      </AppButton>
    </div>

    <div class="finance-grid">
      <!-- Cash Balance Card -->
      <div class="card cash-balance">
        <h3>Текущий остаток</h3>
        <div class="big-value">{{ formatMoney(cashData.cash_balance) }}</div>
        <p class="hint">Доступно для изъятия</p>
      </div>

      <!-- Profitability Card -->
      <div class="card stats">
        <div class="stat-row">
          <span>Валовая прибыль:</span>
          <strong>{{ formatMoney(cashData.gross_profit) }}</strong>
        </div>
        <div class="stat-row">
          <span>Чистая прибыль:</span>
          <strong>{{ formatMoney(cashData.net_profit) }}</strong>
        </div>
        <hr />
        <div class="stat-row">
          <span>Общие расходы:</span>
          <span class="negative">{{ formatMoney(cashData.total_expenses) }}</span>
        </div>
        <div class="stat-row">
          <span>Общие зарплаты:</span>
          <span class="negative">{{ formatMoney(cashData.total_salaries) }}</span>
        </div>
      </div>
    </div>

    <!-- Withdraw Modal -->
    <AppModal v-model="showWithdrawModal" title="Изъятие денег из кассы">
      <form @submit.prevent="handleWithdraw">
        <div class="form-group">
          <label>Сумма изъятия</label>
          <input v-model.number="withdrawForm.amount" type="number" required class="input" :max="cashData.cash_balance" />
        </div>
        <div class="form-group">
          <label>Примечание</label>
          <textarea v-model="withdrawForm.note" class="textarea" rows="3" placeholder="Например: Покупка канцелярии или личные нужды"></textarea>
        </div>
      </form>
      <template #footer>
        <AppButton variant="secondary" @click="showWithdrawModal = false">Отмена</AppButton>
        <AppButton variant="danger" @click="handleWithdraw" :loading="withdrawing">Изъять</AppButton>
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

.finance-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.cash-balance {
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.big-value {
  font-size: 3rem;
  font-weight: 800;
  color: #111827;
  margin: 1rem 0;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
}

.stat-row strong { font-size: 1.1rem; }
.stat-row .negative { color: #e74c3c; font-weight: 600; }

.input, .textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  margin-top: 0.5rem;
}

hr { border: 0; border-top: 1px solid #f3f4f6; margin: 1rem 0; }
</style>
