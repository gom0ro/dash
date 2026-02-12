<template>
  <div class="order-details">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          ← Назад
        </button>
        <div>
          <h1>Заказ #{{ orderId }}</h1>
          <p class="subtitle">Детальная информация о заказе</p>
        </div>
      </div>
      <div class="header-actions">
        <StatusBadge v-if="order" :status="order.status" />
        <AppButton
          v-if="userStore.canManageOrders && order"
          variant="danger"
          @click="confirmDelete"
        >
          Удалить заказ
        </AppButton>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка заказа...</p>
    </div>

    <div v-else-if="!order" class="error">
      <div class="error-icon">❌</div>
      <h3>Заказ не найден</h3>
      <p>Заказ #{{ orderId }} не существует или был удален</p>
      <AppButton @click="goBack">
        Вернуться назад
      </AppButton>
    </div>

    <div v-else class="content-grid">
      <!-- Основная информация -->
      <div class="main-content">
        <!-- Данные клиента -->
        <div class="card">
          <div class="card-header">
            <h3>Данные клиента</h3>
          </div>
          <div class="card-body">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Имя клиента:</span>
                <span class="info-value">{{ order.customer_name || '—' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Телефон:</span>
                <span class="info-value">{{ order.customer_phone || '—' }}</span>
              </div>
              <div class="info-item full-width">
                <span class="info-label">Адрес доставки:</span>
                <span class="info-value">{{ order.customer_address || '—' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>Состав заказа</h3>
          </div>
          <div class="card-body">
            <div class="items-table-wrapper">
                <table class="items-table">
                    <thead>
                        <tr>
                            <th>Товар</th>
                            <th class="text-right">Кол-во</th>
                            <th class="text-right">Цена</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in displayItems" :key="item.id">
                            <td>
                                <div class="item-name">{{ getProductNameById(item.product_id) }}</div>
                            </td>
                            <td class="text-right"><strong>{{ item.quantity }} шт.</strong></td>
                            <td class="text-right">{{ formatMoney(getProductPriceById(item.product_id)) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div v-if="order" class="info-grid mt-4">
              <div class="info-item">
                <span class="info-label">Дедлайн:</span>
                <span class="info-value" :class="{ overdue: isOverdue }">
                  {{ formatDate(order.deadline) }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">Создан:</span>
                <span class="info-value">{{ formatDate(order.created_at) }}</span>
              </div>
            </div>

            <div v-if="product" class="pricing-info">
              <div class="pricing-row total">
                <span>Итоговая сумма:</span>
                <strong>{{ formatMoney(order.total_price) }}</strong>
              </div>
              <div class="pricing-row">
                <span>Метод оплаты:</span>
                <strong style="text-transform: capitalize;">{{ order.payment_method }}</strong>
              </div>
              <div class="pricing-divider"></div>
              <div class="pricing-row">
                <span>Предоплата:</span>
                <strong class="profit">{{ formatMoney(order.prepayment) }}</strong>
              </div>
              <div class="pricing-row">
                <span>Остаток к оплате:</span>
                <strong :class="{ 'red': (order.total_price - order.prepayment) > 0 }">
                  {{ formatMoney(order.total_price - order.prepayment) }}
                </strong>
              </div>
              <div class="pricing-divider"></div>
              <div class="pricing-divider"></div>
              <div class="pricing-row" v-if="product">
                 <span>Ожидаемая прибыль:</span>
                 <strong :class="['profit', { 'red': (order.total_price - ((product.cost + totalStagesCost) * order.quantity)) < 0 }]">
                   {{ formatMoney(order.total_price - ((product.cost + totalStagesCost) * order.quantity)) }}
                 </strong>
              </div>
              <div class="profit-hint" v-if="product">
                 (Цена - (Себ-сть: {{ formatMoney(product.cost) }} + Работа: {{ formatMoney(totalStagesCost) }})) × {{ order.quantity }} шт.
              </div>
            </div>
          </div>
        </div>

        <!-- Управление статусом -->
        <div v-if="userStore.canManageOrders" class="card">
          <div class="card-header">
            <h3>Управление заказом</h3>
          </div>
          <div class="card-body">
            <div class="status-control">
              <label class="label">Изменить статус:</label>
              <div class="status-buttons">
                <button
                  v-for="status in statuses"
                  :key="status.value"
                  :class="['status-button', { active: order.status === status.value }]"
                  :disabled="updatingStatus"
                  @click="updateStatus(status.value)"
                >
                  <span class="status-icon">{{ status.icon }}</span>
                  <span>{{ status.label }}</span>
                </button>
              </div>
            </div>

            <div v-if="order.status === 'delivered'" class="delivery-info">
              <div class="info-message success">
                ✅ Заказ сдан. Продажа учтена в кассе.
              </div>
            </div>
            <div v-else-if="order.status === 'pending'" class="delivery-info">
              <div class="info-message warning">
                ⏳ Заказ ожидает подтверждения
              </div>
            </div>
          </div>
        </div>

        <!-- История работы -->
        <div v-if="workLogs.length > 0" class="card">
          <div class="card-header">
            <h3>История выполнения</h3>
            <span class="work-count">{{ workLogs.length }} записей</span>
          </div>
          <div class="card-body">
            <div class="work-logs-list">
              <div
                v-for="log in workLogs"
                :key="log.id"
                class="work-log-item"
              >
                <div class="work-log-header">
                  <div class="worker-info">
                    <span class="worker-icon">👤</span>
                    <span class="worker-name">{{ getWorkerName(log.worker_id) }}</span>
                  </div>
                  <div class="work-log-time">
                    {{ formatDateTime(log.completed_at) }}
                  </div>
                </div>
                <div class="work-log-body">
                  <div class="stage-name">{{ getStageName(log.stage_id) }}</div>
                  <div class="work-log-payment">
                    <span class="payment-label">Начислено:</span>
                    <span class="payment-value">{{ formatMoney(log.payment) }}</span>
                    <span :class="['payment-status', log.is_paid ? 'paid' : 'unpaid']">
                      {{ log.is_paid ? '✓ Выплачено' : '⏳ Ожидает' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Боковая панель -->
      <div class="sidebar">
        <!-- Этапы производства -->
        <div class="card">
          <div class="card-header">
            <h3>Этапы производства</h3>
          </div>
          <div class="card-body">
            <div v-if="!productStages.length" class="no-stages">
              Этапы не настроены
            </div>
            <div v-else class="stages-list">
              <div
                v-for="stage in productStages"
                :key="stage.id"
                :class="['stage-item', { completed: isStageCompleted(stage.id) }]"
              >
                <div class="stage-number">
                  <span v-if="isStageCompleted(stage.id)">✓</span>
                  <span v-else>{{ stage.order_num }}</span>
                </div>
                <div class="stage-info">
                  <div class="stage-name">{{ stage.name }}</div>
                  <div class="stage-payment">{{ formatMoney(stage.payment) }}</div>
                </div>
              </div>
            </div>

            <div v-if="productStages.length" class="stages-summary">
              <div class="summary-row">
                <span>Всего этапов:</span>
                <strong>{{ productStages.length }}</strong>
              </div>
              <div class="summary-row">
                <span>Выполнено:</span>
                <strong>{{ completedStagesCount }}</strong>
              </div>
              <div class="summary-divider"></div>
              <div class="summary-row">
                <span>Стоимость работы:</span>
                <strong>{{ formatMoney(totalStagesCost) }}</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- Прогресс -->
        <div class="card">
          <div class="card-header">
            <h3>Прогресс</h3>
          </div>
          <div class="card-body">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
            <div class="progress-text">
              {{ progressPercent }}% выполнено
            </div>

            <div class="timeline">
              <div :class="['timeline-item', { active: order.status === 'pending' || isPast('pending') }]">
                <div class="timeline-dot"></div>
                <div class="timeline-label">Создан</div>
              </div>
              <div :class="['timeline-item', { active: isPast('accepted') }]">
                <div class="timeline-dot"></div>
                <div class="timeline-label">Принят</div>
              </div>
              <div :class="['timeline-item', { active: isPast('in_progress') }]">
                <div class="timeline-dot"></div>
                <div class="timeline-label">В работе</div>
              </div>
              <div :class="['timeline-item', { active: isPast('done') }]">
                <div class="timeline-dot"></div>
                <div class="timeline-label">Готов</div>
              </div>
              <div :class="['timeline-item', { active: order.status === 'delivered' }]">
                <div class="timeline-dot"></div>
                <div class="timeline-label">Сдан</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка удаления -->
    <AppModal
      v-model="showDeleteModal"
      title="Удаление заказа"
      size="sm"
    >
      <p>Вы уверены, что хотите удалить заказ #{{ orderId }}?</p>
      <p class="warning">Это действие нельзя отменить. Все связанные записи о выполнении будут также удалены.</p>

      <template #footer>
        <AppButton variant="secondary" @click="showDeleteModal = false">
          Отмена
        </AppButton>
        <AppButton variant="danger" :loading="deleting" @click="handleDelete">
          Удалить
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import { useWarehouseStore } from '@/stores/warehouse'
import { useUserStore } from '@/stores/user'
import { ordersAPI, workLogsAPI, usersAPI } from '@/api'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'
import StatusBadge from '@/components/UI/StatusBadge.vue'

const route = useRoute()
const router = useRouter()
const ordersStore = useOrdersStore()
const warehouseStore = useWarehouseStore()
const userStore = useUserStore()

const orderId = ref(parseInt(route.params.id))
const loading = ref(false)
const updatingStatus = ref(false)
const deleting = ref(false)

const order = ref(null)
const product = ref(null)
const workLogs = ref([])
const users = ref([])
const showDeleteModal = ref(false)

const statuses = [
  { value: 'pending', label: 'Ожидает', icon: '⏳' },
  { value: 'accepted', label: 'Принят', icon: '✓' },
  { value: 'in_progress', label: 'В работе', icon: '🔨' },
  { value: 'done', label: 'Готов', icon: '✅' },
  { value: 'delivered', label: 'Сдан', icon: '📦' }
]

const statusOrder = ['pending', 'accepted', 'in_progress', 'done', 'delivered']

const productName = computed(() => product.value?.name || 'Неизвестный товар')

const creatorName = computed(() => {
  if (!order.value) return '—'
  const creator = users.value.find(u => u.id === order.value.created_by)
  return creator?.full_name || '—'
})

const wholesalerName = computed(() => {
  if (!order.value?.wholesaler_id) return '—'
  const wholesaler = users.value.find(u => u.id === order.value.wholesaler_id)
  return wholesaler?.full_name || '—'
})

const productStages = computed(() => {
  if (!product.value?.stages) return []
  return [...product.value.stages].sort((a, b) => a.order_num - b.order_num)
})

const totalPrice = computed(() => {
  if (!product.value || !order.value) return 0
  return product.value.price * order.value.quantity
})

const totalProfit = computed(() => {
  if (!product.value || !order.value) return 0
  return (product.value.price - product.value.cost) * order.value.quantity
})

const displayItems = computed(() => {
    if (order.value?.items && order.value.items.length > 0) return order.value.items
    if (order.value?.product_id) return [{ product_id: order.value.product_id, quantity: order.value.quantity }]
    return []
})

const getProductNameById = (id) => {
    return warehouseStore.getProductById(id)?.name || 'Неизвестный товар'
}

const getProductPriceById = (id) => {
    return warehouseStore.getProductById(id)?.price || 0
}

const totalStagesCost = computed(() => {
  // Расчет стоимости работ (берем сумму всех этапов по всем товарам в заказе)
  return displayItems.value.reduce((total, item) => {
      const prod = warehouseStore.getProductById(item.product_id)
      const stagesSum = prod?.stages?.reduce((s, st) => s + st.payment, 0) || 0
      return total + (stagesSum * item.quantity)
  }, 0)
})

const completedStagesCount = computed(() => {
  return productStages.value.filter(stage => isStageCompleted(stage.id)).length
})

const progressPercent = computed(() => {
  if (!productStages.value.length) return 0
  return Math.round((completedStagesCount.value / productStages.value.length) * 100)
})

const isOverdue = computed(() => {
  if (!order.value || order.value.status === 'delivered') return false
  return new Date(order.value.deadline) < new Date()
})

const isStageCompleted = (stageId) => {
  return workLogs.value.some(log => log.stage_id === stageId)
}

const getStageName = (stageId) => {
  const stage = productStages.value.find(s => s.id === stageId)
  return stage?.name || 'Неизвестный этап'
}

const getWorkerName = (workerId) => {
  const worker = users.value.find(u => u.id === workerId)
  return worker?.full_name || 'Неизвестный сотрудник'
}

const isPast = (status) => {
  if (!order.value) return false
  const currentIndex = statusOrder.indexOf(order.value.status)
  const checkIndex = statusOrder.indexOf(status)
  return currentIndex >= checkIndex
}

const formatMoney = (amount) => {
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount || 0) + ' тг'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goBack = () => {
  router.back()
}

const updateStatus = async (newStatus) => {
  if (order.value.status === newStatus) return

  try {
    updatingStatus.value = true
    await ordersStore.updateOrderStatus(orderId.value, newStatus)
    order.value.status = newStatus
    if (newStatus === 'delivered') {
      order.value.delivered_at = new Date().toISOString()
    }
  } catch (error) {
    alert('Ошибка обновления статуса: ' + (error.response?.data?.detail || error.message))
  } finally {
    updatingStatus.value = false
  }
}

const confirmDelete = () => {
  showDeleteModal.value = true
}

const handleDelete = async () => {
  try {
    deleting.value = true
    await ordersStore.deleteOrder(orderId.value)
    router.push('/manager/orders')
  } catch (error) {
    alert('Ошибка удаления: ' + (error.response?.data?.detail || error.message))
  } finally {
    deleting.value = false
  }
}

const loadOrderDetails = async () => {
  try {
    const { data } = await ordersAPI.getById(orderId.value)
    order.value = data
  } catch (error) {
    console.error('Ошибка загрузки заказа:', error)
    order.value = null
  }
}

const loadProduct = async () => {
  if (!order.value) return
  product.value = warehouseStore.getProductById(order.value.product_id)
  if (!product.value) {
    await warehouseStore.fetchProducts()
    product.value = warehouseStore.getProductById(order.value.product_id)
  }
}

const loadWorkLogs = async () => {
  try {
    const { data } = await workLogsAPI.getAll()
    workLogs.value = data.filter(log => log.order_id === orderId.value)
      .sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))
  } catch (error) {
    console.error('Ошибка загрузки логов:', error)
  }
}

const loadUsers = async () => {
  try {
    const { data } = await usersAPI.getAll()
    users.value = data
  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await loadOrderDetails()
    if (order.value) {
      await Promise.all([
        loadProduct(),
        loadWorkLogs(),
        loadUsers()
      ])
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.order-details {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 1.5rem;
}

.header-left {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.back-btn {
  padding: 0.75rem 1.25rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #374151;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f9fafb;
  border-color: #667eea;
  color: #667eea;
}

.page-header h1 {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
}

.items-table-wrapper { margin-bottom: 1.5rem; border: 1.5px solid #f1f5f9; border-radius: 12px; overflow: hidden; }
.items-table { width: 100%; border-collapse: collapse; }
.items-table th { background: #f8fafc; padding: 1rem; text-align: left; font-size: 0.75rem; text-transform: uppercase; color: #64748b; font-weight: 800; border-bottom: 1.5px solid #f1f5f9; }
.items-table td { padding: 1rem; border-bottom: 1px solid #f8fafc; font-size: 0.95rem; }
.text-right { text-align: right !important; }
.item-name { font-weight: 700; color: #1e293b; }
.mt-4 { margin-top: 1rem; }

.subtitle {
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.loading,
.error {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
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

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error h3 {
  margin: 0 0 0.5rem;
  color: #111827;
}

.error p {
  margin: 0 0 1.5rem;
  color: #6b7280;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 1.5rem;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: #111827;
}

.work-count {
  background: #f3f4f6;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #6b7280;
}

.card-body {
  padding: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.info-value {
  font-size: 0.9375rem;
  color: #111827;
  font-weight: 500;
}

.info-value.overdue {
  color: #e74c3c;
  font-weight: 600;
}

.pricing-info {
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
}

.pricing-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.pricing-row span {
  color: #6b7280;
  font-size: 0.9375rem;
}

.pricing-row strong {
  color: #111827;
  font-size: 0.9375rem;
  font-weight: 600;
}

.pricing-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 0.5rem 0;
}

.pricing-row.total {
  padding-top: 1rem;
}

.pricing-row.total span,
.pricing-row.total strong {
  font-size: 1.125rem;
  font-weight: 700;
}

.pricing-row strong.profit {
  color: #27ae60;
}

.pricing-row strong.profit.red {
  color: #e74c3c;
}

.profit-hint {
  font-size: 0.75rem;
  color: #9ca3af;
  text-align: right;
  margin-top: 0.25rem;
}

strong.red {
  color: #e74c3c;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.status-control {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.status-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.status-button {
  flex: 1;
  min-width: 120px;
  padding: 0.875rem 1rem;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.status-button:hover:not(:disabled) {
  border-color: #667eea;
  background: #f3f4f6;
}

.status-button.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.status-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-icon {
  font-size: 1.25rem;
}

.delivery-info {
  margin-top: 1.5rem;
}

.info-message {
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 500;
}

.info-message.success {
  background: #dcfce7;
  color: #065f46;
}

.info-message.warning {
  background: #fef3c7;
  color: #92400e;
}

.work-logs-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.work-log-item {
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.work-log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.worker-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.worker-icon {
  font-size: 1.125rem;
}

.worker-name {
  font-weight: 600;
  color: #111827;
  font-size: 0.9375rem;
}

.work-log-time {
  color: #6b7280;
  font-size: 0.875rem;
}

.work-log-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stage-name {
  color: #374151;
  font-weight: 500;
}

.work-log-payment {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.payment-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.payment-value {
  color: #27ae60;
  font-weight: 700;
}

.payment-status {
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.payment-status.paid {
  background: #dcfce7;
  color: #065f46;
}

.payment-status.unpaid {
  background: #fef3c7;
  color: #92400e;
}

.no-stages {
  text-align: center;
  padding: 2rem;
  color: #9ca3af;
  font-size: 0.875rem;
}

.stages-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.stage-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  transition: all 0.2s;
}

.stage-item.completed {
  background: #dcfce7;
  border-color: #27ae60;
}

.stage-number {
  width: 2rem;
  height: 2rem;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.stage-item.completed .stage-number {
  background: #27ae60;
}

.stage-info {
  flex: 1;
}

.stage-name {
  font-weight: 500;
  color: #111827;
  font-size: 0.9375rem;
}

.stage-payment {
  color: #6b7280;
  font-size: 0.875rem;
}

.stages-summary {
  padding: 1rem;
  background: #f3f4f6;
  border-radius: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.summary-row span {
  color: #6b7280;
  font-size: 0.875rem;
}

.summary-row strong {
  color: #111827;
  font-weight: 600;
}

.summary-divider {
  height: 1px;
  background: #d1d5db;
  margin: 0.5rem 0;
}

.progress-bar {
  width: 100%;
  height: 0.75rem;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
  padding-left: 1.5rem;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: 0.375rem;
  top: 1.5rem;
  width: 2px;
  height: calc(100% + 1rem);
  background: #e5e7eb;
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-dot {
  width: 0.75rem;
  height: 0.75rem;
  background: #e5e7eb;
  border-radius: 50%;
  flex-shrink: 0;
  position: absolute;
  left: 0;
}

.timeline-item.active .timeline-dot {
  background: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
}

.timeline-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.timeline-item.active .timeline-label {
  color: #111827;
  font-weight: 600;
}

.warning {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .sidebar {
    order: -1;
  }
}

@media (max-width: 768px) {
  .order-details {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
  }

  .header-left {
    flex-direction: column;
    gap: 1rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .status-buttons {
    flex-direction: column;
  }

  .status-button {
    min-width: 100%;
  }
}
</style>