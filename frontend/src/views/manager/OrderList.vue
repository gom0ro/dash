<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Список заказов</h1>
      <AppButton @click="router.push('/manager/orders/create')">
        Создать заказ
      </AppButton>
    </div>

    <div class="filters">
      <div class="status-filters">
        <button 
          v-for="status in statuses" 
          :key="status.value"
          :class="['filter-chip', { active: currentFilter === status.value }]"
          @click="setFilter(status.value)"
        >
          {{ status.label }}
        </button>
      </div>
    </div>

    <div class="orders-table-container">
      <div v-if="orderStore.loading && !orderStore.orders.length" class="loading-state">
        Загрузка...
      </div>
      
      <div v-else-if="orderStore.error" class="error-state">
        {{ orderStore.error }}
      </div>
      
      <table v-else class="orders-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Клиент</th>
            <th>Дедлайн</th>
            <th>Сумма</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="order in filteredOrders" 
            :key="order.id" 
            :class="['order-row', { overdue: isOverdue(order) }]" 
            @click="openOrder(order.id)"
          >
            <td>#{{ order.id }}</td>
            <td>
              <div class="customer-cell">
                {{ order.customer_name || 'Частный клиент' }}
                <span v-if="isOverdue(order)" class="overdue-badge">⚠️ Просрочен</span>
              </div>
            </td>
            <td :class="{ 'deadline-warning': isDueSoon(order), 'deadline-overdue': isOverdue(order) }">
              {{ formatDate(order.deadline) }}
            </td>
            <td>{{ formatPrice(order.total_price) }}</td>
            <td>
              <StatusBadge :status="order.status" />
            </td>
            <td>
              <div class="action-buttons">
                <AppButton 
                  v-if="order.status === 'pending'" 
                  size="sm" 
                  variant="success" 
                  @click.stop="approveOrder(order.id)"
                  class="mr-2"
                >
                  ✓ Принять
                </AppButton>
                <AppButton 
                  v-if="order.status === 'pending'" 
                  size="sm" 
                  variant="danger" 
                  @click.stop="rejectOrder(order.id)"
                  class="mr-2"
                >
                  ✗ Отклонить
                </AppButton>
                <AppButton 
                  size="sm" 
                  variant="outline" 
                  @click.stop="openOrder(order.id)"
                >
                  Просмотр
                </AppButton>
              </div>
            </td>
          </tr>
          <tr v-if="filteredOrders.length === 0">
            <td colspan="6" class="empty-state">
              Заказы не найдены
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import AppButton from '@/components/UI/AppButton.vue'
import StatusBadge from '@/components/UI/StatusBadge.vue'

const router = useRouter()
const orderStore = useOrdersStore()

const currentFilter = ref('all')

const statuses = [
  { label: 'Все', value: 'all' },
  { label: 'Ожидает', value: 'pending' },
  { label: 'Принят', value: 'accepted' },
  { label: 'В работе', value: 'in_progress' },
  { label: 'Готов', value: 'done' },
  { label: 'Сдан', value: 'delivered' },
  { label: 'Отменен', value: 'cancelled' }
]

const filteredOrders = computed(() => {
  if (currentFilter.value === 'all') {
    return orderStore.orders
  }
  return orderStore.orders.filter(order => order.status === currentFilter.value)
})

onMounted(() => {
  orderStore.fetchOrders()
})

const setFilter = (status) => {
  currentFilter.value = status
}

const openOrder = (id) => {
  router.push(`/manager/orders/${id}`)
}

const approveOrder = async (id) => {
  if (!confirm('Принять этот заказ в производство?')) return
  
  try {
    await orderStore.updateOrderStatus(id, 'accepted')
    await orderStore.fetchOrders()
  } catch (err) {
    alert('Ошибка при принятии заказа')
  }
}

const rejectOrder = async (id) => {
  if (!confirm('Отклонить этот заказ? Действие необратимо.')) return
  
  try {
    await orderStore.deleteOrder(id)
    await orderStore.fetchOrders()
  } catch (err) {
    alert('Ошибка при отклонении заказа')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('ru-RU')
}

const formatPrice = (price) => {
  if (price === null || price === undefined) return '-'
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'KZT', maximumFractionDigits: 0 }).format(price)
}

const isOverdue = (order) => {
  if (order.status === 'delivered') return false
  return new Date(order.deadline) < new Date()
}

const isDueSoon = (order) => {
  if (order.status === 'delivered') return false
  const deadline = new Date(order.deadline)
  const now = new Date()
  const hoursUntilDeadline = (deadline - now) / (1000 * 60 * 60)
  return hoursUntilDeadline > 0 && hoursUntilDeadline <= 24
}
</script>

<style scoped>
.page-container {
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

.page-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #111827;
}

.filters {
  margin-bottom: 2rem;
}

.status-filters {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-chip {
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  background: white;
  border: 1px solid #d1d5db;
  color: #4b5563;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-chip:hover {
  background: #f3f4f6;
}

.filter-chip.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.orders-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table th {
  background: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #6b7280;
  letter-spacing: 0.05em;
}

.orders-table td {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  color: #111827;
  font-size: 0.875rem;
}

.order-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.order-row:hover {
  background-color: #f9fafb;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.loading-state, .error-state {
  padding: 2rem;
  text-align: center;
}

.error-state {
  color: #ef4444;
}

.order-row.overdue {
  background-color: #fee2e2;
}

.order-row.overdue:hover {
  background-color: #fecaca;
}

.customer-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.overdue-badge {
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
  background: #dc2626;
  color: white;
  border-radius: 4px;
  font-weight: 600;
}

.deadline-warning {
  color: #f59e0b;
  font-weight: 600;
}

.deadline-overdue {
  color: #dc2626;
  font-weight: 700;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.mr-2 {
  margin-right: 0.5rem;
}
</style>