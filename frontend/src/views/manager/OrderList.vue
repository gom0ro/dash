<template>
  <div class="orders-view fade-in">
    <div class="page-header">
      <div class="header-content">
        <h1>Управление заказами</h1>
        <p class="subtitle">Отслеживание и обработка клиентских заказов</p>
      </div>
      <AppButton @click="router.push('/manager/orders/create')" class="create-order-btn">
        <i class="ri-add-line"></i> <span>Новый заказ</span>
      </AppButton>
    </div>

    <!-- Filters Section -->
    <div class="filters-container">
      <div class="status-scroll">
        <button 
          v-for="status in statuses" 
          :key="status.value"
          :class="['status-chip', { active: currentFilter === status.value }]"
          @click="setFilter(status.value)"
        >
          {{ status.label }}
          <span class="count-badge" v-if="getCount(status.value) > 0">
            {{ getCount(status.value) }}
          </span>
        </button>
      </div>
    </div>

    <div v-if="orderStore.loading && !orderStore.orders.length" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка заказов...</p>
    </div>
    
    <div v-else-if="orderStore.error" class="error-state">
      <i class="ri-error-warning-line"></i>
      <p>{{ orderStore.error }}</p>
      <AppButton size="sm" @click="orderStore.fetchOrders()">Попробовать снова</AppButton>
    </div>

    <div v-else class="orders-content">
      <div v-if="filteredOrders.length === 0" class="empty-state">
        <i class="ri-inbox-line"></i>
        <h3>Заказов пока нет</h3>
        <p>Попробуйте изменить фильтры или создайте новый заказ.</p>
      </div>

      <div v-else class="orders-grid">
        <div 
          v-for="order in filteredOrders" 
          :key="order.id" 
          class="order-card"
          :class="{ 'card-overdue': isOverdue(order) }"
          @click="openOrder(order.id)"
        >
          <div class="order-card-header">
            <div class="order-id-track">
                <span class="id-pill">#{{ order.id }}</span>
                <span v-if="isOverdue(order)" class="overdue-tag">
                    <i class="ri-alarm-warning-line"></i> Просрочен
                </span>
            </div>
            <StatusBadge :status="order.status" />
          </div>

          <div class="order-card-body">
            <div class="customer-info">
                <h3>{{ order.customer_name || 'Частный клиент' }}</h3>
                <span class="customer-phone" v-if="order.customer_phone">{{ order.customer_phone }}</span>
            </div>

            <div class="order-meta-grid">
                <div class="meta-item">
                    <span class="label">Дедлайн:</span>
                    <span class="value" :class="{ 'warning': isDueSoon(order), 'danger': isOverdue(order) }">
                        <i class="ri-calendar-event-line"></i> {{ formatDate(order.deadline) }}
                    </span>
                </div>
                <div class="meta-item">
                    <span class="label">Сумма:</span>
                    <span class="value price">{{ formatPrice(order.total_price) }}</span>
                </div>
            </div>
          </div>

          <div class="order-card-footer" @click.stop>
            <div class="actions-group" v-if="order.status === 'pending'">
                <button class="btn-action approve" @click="approveOrder(order.id)">
                    <i class="ri-check-line"></i> Принять
                </button>
                <button class="btn-action reject" @click="rejectOrder(order.id)">
                    <i class="ri-close-line"></i> Отклонить
                </button>
            </div>
            <div class="actions-group" v-else>
                <button class="btn-action view" @click="openOrder(order.id)">
                    Подробнее <i class="ri-arrow-right-line"></i>
                </button>
            </div>
          </div>
        </div>
      </div>
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
  { label: 'Новые', value: 'pending' },
  { label: 'В работе', value: 'accepted' },
  { label: 'Активные', value: 'in_progress' },
  { label: 'Готовы', value: 'done' },
  { label: 'Сданы', value: 'delivered' }
]

const filteredOrders = computed(() => {
  let orders = orderStore.orders
  if (currentFilter.value !== 'all') {
    orders = orders.filter(order => order.status === currentFilter.value)
  } else {
    // 'Все' now shows only non-delivered orders as per user request
    orders = orders.filter(order => order.status !== 'delivered')
  }
  return orders.sort((a, b) => b.id - a.id)
})

const getCount = (status) => {
    if (status === 'all') return orderStore.orders.filter(o => o.status !== 'delivered').length
    return orderStore.orders.filter(o => o.status === status).length
}

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
  return new Date(dateString).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
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
.orders-view {
  padding: 1.5rem;
  max-width: 1400px;
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

.subtitle { color: #64748b; font-weight: 500; }

.create-order-btn {
    padding: 0.75rem 1.5rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.filters-container {
    margin-bottom: 2rem;
    overflow: hidden;
}

.status-scroll {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding: 0.25rem 0.25rem 0.75rem;
    -webkit-overflow-scrolling: touch;
}

.status-scroll::-webkit-scrollbar { display: none; }

.status-chip {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1.25rem;
    background: white;
    border: 1px solid #f1f5f9;
    border-radius: 14px;
    color: #64748b;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
}

.status-chip:hover {
    color: #1e293b;
    background: #f8fafc;
}

.status-chip.active {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
    box-shadow: 0 8px 15px rgba(59, 130, 246, 0.2);
}

.count-badge {
    background: rgba(255,255,255,0.2);
    color: inherit;
    font-size: 0.75rem;
    padding: 2px 6px;
    border-radius: 6px;
    font-weight: 800;
}

.status-chip.active .count-badge {
    background: white;
    color: #3b82f6;
}

.orders-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
}

.order-card {
    background: white;
    border-radius: 20px;
    padding: 1.5rem;
    border: 1px solid #f1f5f9;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.03);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.order-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.06);
}

.order-card.card-overdue {
    border-left: 4px solid #ef4444;
}

.order-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.id-pill {
    background: #f1f5f9;
    color: #475569;
    font-weight: 800;
    font-size: 0.75rem;
    padding: 4px 10px;
    border-radius: 8px;
}

.overdue-tag {
    margin-left: 8px;
    color: #ef4444;
    font-weight: 800;
    font-size: 0.75rem;
    text-transform: uppercase;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.customer-info h3 {
    margin: 0 0 4px;
    font-size: 1.2rem;
    font-weight: 800;
    color: #1e293b;
}

.customer-phone {
    font-size: 0.9rem;
    color: #94a3b8;
    font-weight: 500;
}

.order-meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    padding: 1.25rem;
    background: #f8fafc;
    border-radius: 16px;
    border: 1px solid #f1f5f9;
}

.meta-item { display: flex; flex-direction: column; gap: 4px; }
.meta-item .label { font-size: 0.7rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.meta-item .value { font-weight: 700; color: #1e293b; font-size: 0.95rem; display: flex; align-items: center; gap: 6px; }
.meta-item .value.price { color: #3b82f6; font-weight: 900; font-size: 1.1rem; }
.meta-item .value.warning { color: #d97706; }
.meta-item .value.danger { color: #ef4444; }

.order-card-footer {
    padding-top: 1rem;
    border-top: 1px solid #f8fafc;
}

.actions-group {
    display: flex;
    gap: 0.75rem;
}

.btn-action {
    flex: 1;
    padding: 0.7rem;
    border-radius: 12px;
    border: none;
    font-weight: 800;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}

.btn-action.approve { background: #dcfce7; color: #166534; }
.btn-action.approve:hover { background: #bbf7d0; }

.btn-action.reject { background: #fee2e2; color: #991b1b; }
.btn-action.reject:hover { background: #fecaca; }

.btn-action.view { background: #f1f5f9; color: #475569; }
.btn-action.view:hover { background: #e2e8f0; color: #1e293b; }

.loading-state, .error-state, .empty-state {
    text-align: center;
    padding: 5rem 2rem;
    background: white;
    border-radius: 24px;
}

.loading-state i, .empty-state i { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; color: #94a3b8; }

.spinner {
    width: 3rem;
    height: 3rem;
    border: 4px solid #f1f5f9;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1.5rem;
}

@keyframes spin { to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1024px) {
    .orders-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
}

@media (max-width: 768px) {
    .orders-view { padding: 1rem; }
    .page-header { flex-direction: column; align-items: stretch; gap: 1.25rem; margin-bottom: 2rem; }
    .header-content h1 { font-size: 1.6rem; }
    .create-order-btn { width: 100%; justify-content: center; padding: 1rem; }
    .status-chip { padding: 0.5rem 1rem; font-size: 0.85rem; }
    .orders-grid { grid-template-columns: 1fr; gap: 1rem; }
    .order-card { padding: 1.25rem; border-radius: 16px; }
    .order-meta-grid { padding: 1rem; gap: 0.75rem; }
    .meta-item .value { font-size: 0.85rem; }
    .meta-item .value.price { font-size: 1rem; }
}

@media (max-width: 375px) {
    .orders-view { padding: 0.75rem; }
    .order-card { padding: 1rem; }
}
</style>