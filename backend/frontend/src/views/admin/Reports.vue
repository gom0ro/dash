<template>
  <div class="reports-view">
    <div class="page-header">
      <div>
        <h1>Аналитика и отчеты</h1>
        <p class="subtitle">Детальная статистика деятельности предприятия</p>
      </div>
    </div>

    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Сбор данных...</p>
    </div>

    <div v-else class="report-content">
      <!-- Cash Report Tab -->
      <div v-if="activeTab === 'cash'" class="cash-report">
        <div class="stats-grid">
          <div class="stat-card">
            <span class="label">Продажи</span>
            <span class="value positive">{{ formatMoney(cashData.sales) }}</span>
          </div>
          <div class="stat-card">
            <span class="label">Всего расходов</span>
            <span class="value negative">{{ formatMoney(cashData.total_expenses) }}</span>
          </div>
          <div class="stat-card">
            <span class="label">Зарплаты (всего)</span>
            <span class="value negative">{{ formatMoney(cashData.total_salaries) }}</span>
          </div>
          <div class="stat-card primary">
            <span class="label">Остаток в кассе</span>
            <span class="value">{{ formatMoney(cashData.cash_balance) }}</span>
          </div>
        </div>
      </div>

      <!-- Sales Report Tab -->
      <div v-if="activeTab === 'sales'" class="sales-report">
        <div class="summary-card">
          <h3>Всего заказов: {{ salesData.total_orders }}</h3>
          <h2>Общая выручка: {{ formatMoney(salesData.total_revenue) }}</h2>
        </div>
        
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Товар</th>
                <th>Продано</th>
                <th>Выручка</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in salesData.sales_by_product" :key="item.product_id">
                <td>{{ item.product_name }}</td>
                <td>{{ item.quantity_sold }} шт.</td>
                <td>{{ formatMoney(item.revenue) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Workers Report Tab -->
      <div v-if="activeTab === 'workers'" class="workers-report">
        <div class="workers-grid">
          <div v-for="worker in workersData.workers" :key="worker.worker_id" class="worker-stat-card">
            <h4>{{ worker.worker_name }}</h4>
            <div class="worker-details">
              <div class="detail">
                <span>Этапов выполнено:</span>
                <strong>{{ worker.stages_completed }}</strong>
              </div>
              <div class="detail">
                <span>Заработано:</span>
                <strong>{{ formatMoney(worker.total_earned) }}</strong>
              </div>
              <div class="detail">
                <span>Выплачено:</span>
                <strong class="positive">{{ formatMoney(worker.total_paid) }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { reportsAPI } from '@/api'

const activeTab = ref('cash')
const loading = ref(false)
const cashData = ref({})
const salesData = ref({ workers: [], total_orders: 0, total_revenue: 0, sales_by_product: [] })
const workersData = ref({ workers: [] })

const tabs = [
  { id: 'cash', label: 'Касса' },
  { id: 'sales', label: 'Продажи' },
  { id: 'workers', label: 'Сотрудники' }
]

const formatMoney = (amount) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'KZT',
    minimumFractionDigits: 0
  }).format(amount || 0)
}

const loadReport = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'cash') {
      const { data } = await reportsAPI.getCashReport()
      cashData.value = data
    } else if (activeTab.value === 'sales') {
      const { data } = await reportsAPI.getSalesReport()
      salesData.value = data
    } else if (activeTab.value === 'workers') {
      const { data } = await reportsAPI.getWorkersReport()
      workersData.value = data
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

watch(activeTab, loadReport)
onMounted(loadReport)
</script>

<style scoped>
.reports-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #f3f4f6;
}

.tab-btn.active {
  background: #667eea;
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.stat-card.primary {
  background: #667eea;
  color: white;
}

.stat-card .label { font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem; }
.stat-card.primary .label { color: #e0e7ff; }

.stat-card .value { font-size: 1.75rem; font-weight: 700; }
.stat-card .value.positive { color: #10b981; }
.stat-card .value.negative { color: #ef4444; }

.summary-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  text-align: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 1rem; background: #f9fafb; color: #374151; }
td { padding: 1rem; border-top: 1px solid #f3f4f6; }

.workers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.worker-stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.worker-details { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1rem; }
.detail { display: flex; justify-content: space-between; }
</style>
