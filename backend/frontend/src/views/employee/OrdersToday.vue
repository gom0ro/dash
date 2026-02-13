<template>
  <div class="orders-today">
    <div class="page-header">
      <div>
        <h1>Задачи на сегодня</h1>
        <p class="subtitle">Выберите заказ и этап для выполнения</p>
      </div>
      <div class="header-stats">
        <div class="stat-badge">
          <span class="badge-label">Заказов:</span>
          <span class="badge-value">{{ todayOrders.length }}</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка заказов...</p>
    </div>

    <div v-else-if="todayOrders.length === 0" class="empty">
      <div class="empty-icon">✅</div>
      <h3>Все заказы выполнены!</h3>
      <p>На сегодня заказов в работе нет</p>
    </div>

    <div v-else class="orders-grid">
      <div
        v-for="order in todayOrders"
        :key="order.id"
        class="order-card"
      >
        <div class="order-header">
          <div class="order-title">
            <div class="order-id">#{{ order.id }}</div>
            <StatusBadge :status="order.status" />
          </div>
          <div class="order-deadline" :class="{ overdue: isOverdue(order) }">
            <span class="deadline-icon">⏰</span>
            {{ formatDeadline(order.deadline) }}
          </div>
        </div>

        <div class="order-body">
          <div class="product-info">
            <h4>{{ getProductName(order.product_id) }}</h4>
            <div class="product-meta">
              Количество: <strong>{{ order.quantity }} шт.</strong>
            </div>
          </div>

          <div class="stages-section">
            <h5>Этапы производства:</h5>
            
            <div v-if="!getProductStages(order.product_id).length" class="no-stages">
              Этапы не настроены для этого товара
            </div>

            <div v-else class="stages-list">
              <button
                v-for="stage in getProductStages(order.product_id)"
                :key="stage.id"
                class="stage-btn"
                :disabled="completingStage === `${order.id}-${stage.id}`"
                @click="completeStage(order, stage.id, stage.payment)"
              >
                <div class="stage-info">
                  <span class="stage-number">{{ stage.order_num }}</span>
                  <span class="stage-name">{{ stage.name }}</span>
                </div>
                <div class="stage-payment">
                  +{{ formatMoney(stage.payment) }}
                </div>
                <div v-if="completingStage === `${order.id}-${stage.id}`" class="stage-loader">
                  <div class="mini-spinner"></div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <AppModal
      v-model="showSuccessModal"
      title="Этап выполнен!"
      size="sm"
    >
      <div class="success-content">
        <div class="success-icon">✅</div>
        <p class="success-message">Этап успешно завершен</p>
        <div class="earned-amount">
          <span>Начислено:</span>
          <strong>{{ formatMoney(earnedAmount) }}</strong>
        </div>
      </div>
      <template #footer>
        <AppButton @click="showSuccessModal = false">
          Продолжить работу
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useOrdersStore } from '@/stores/orders'
import { useWarehouseStore } from '@/stores/warehouse'
import { useUserStore } from '@/stores/user'
import { workLogsAPI } from '@/api'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'
import StatusBadge from '@/components/UI/StatusBadge.vue'

const ordersStore = useOrdersStore()
const warehouseStore = useWarehouseStore()
const userStore = useUserStore()

const loading = ref(false)
const completingStage = ref(null)
const showSuccessModal = ref(false)
const earnedAmount = ref(0)

const todayOrders = computed(() => {
  return ordersStore.inProgressOrders.filter(order => {
    const deadline = new Date(order.deadline)
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    
    return deadline >= today && deadline <= tomorrow
  })
})

const getProductName = (productId) => {
  const product = warehouseStore.getProductById(productId)
  return product?.name || 'Неизвестный товар'
}

const getProductStages = (productId) => {
  const product = warehouseStore.products.find(p => p.id === productId)
  if (!product || !product.stages) return []
  return product.stages.sort((a, b) => a.order_num - b.order_num)
}

const formatDeadline = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffHours = Math.floor((date - now) / (1000 * 60 * 60))
  
  if (diffHours < 0) {
    return 'Просрочено'
  } else if (diffHours < 24) {
    return `Через ${diffHours} ч.`
  } else {
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

const isOverdue = (order) => {
  return new Date(order.deadline) < new Date()
}

const formatMoney = (amount) => {
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount || 0) + ' тг'
}

const completeStage = async (order, stageId, payment) => {
  const key = `${order.id}-${stageId}`
  
  if (completingStage.value === key) return
  
  if (!confirm('Подтвердить выполнение этапа?')) return
  
  try {
    completingStage.value = key
    
    const { data } = await workLogsAPI.create({
      order_id: order.id,
      product_id: order.product_id,
      quantity: order.quantity,
      stage_id: stageId
    })
    
    earnedAmount.value = data.payment || payment
    showSuccessModal.value = true
    
    await ordersStore.fetchOrders()
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Произошла ошибка'
    alert('Ошибка: ' + errorMsg)
  } finally {
    completingStage.value = null
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      ordersStore.fetchOrders(),
      warehouseStore.fetchProducts()
    ])
  } catch (error) {
    console.error('Ошибка загрузки:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.orders-today {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.header-stats {
  display: flex;
  gap: 1rem;
}

.stat-badge {
  background: white;
  padding: 0.75rem 1.25rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.badge-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.badge-value {
  color: #667eea;
  font-size: 1.25rem;
  font-weight: 700;
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
  margin: 0;
  color: #6b7280;
}

.orders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.order-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border-left: 4px solid #667eea;
  transition: transform 0.2s, box-shadow 0.2s;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.order-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  background: #f9fafb;
}

.order-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.order-id {
  font-size: 1.125rem;
  font-weight: 700;
  color: #667eea;
}

.order-deadline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.deadline-icon {
  font-size: 1rem;
}

.order-deadline.overdue {
  color: #e74c3c;
  font-weight: 600;
}

.order-body {
  padding: 1.5rem;
}

.product-info {
  margin-bottom: 1.5rem;
}

.product-info h4 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
  color: #111827;
}

.product-meta {
  color: #6b7280;
  font-size: 0.875rem;
}

.product-meta strong {
  color: #111827;
}

.stages-section h5 {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6b7280;
  margin: 0 0 1rem;
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
}

.stage-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.stage-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #667eea;
  transform: translateX(4px);
}

.stage-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.stage-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
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

.stage-name {
  color: #111827;
  font-weight: 500;
}

.stage-payment {
  color: #27ae60;
  font-weight: 700;
  font-size: 1rem;
  flex-shrink: 0;
}

.stage-loader {
  position: absolute;
  right: 1rem;
}

.mini-spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.success-content {
  text-align: center;
  padding: 1rem;
}

.success-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.success-message {
  font-size: 1.125rem;
  color: #111827;
  margin: 0 0 1.5rem;
}

.earned-amount {
  background: #dcfce7;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.earned-amount span {
  color: #065f46;
  font-size: 0.875rem;
}

.earned-amount strong {
  color: #065f46;
  font-size: 1.5rem;
  font-weight: 700;
}

@media (max-width: 1024px) {
  .orders-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .orders-today {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    gap: 1rem;
  }

  .orders-grid {
    grid-template-columns: 1fr;
  }
}
</style>