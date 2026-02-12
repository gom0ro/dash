<template>
  <div class="production-tasks">
    <div class="page-header">
      <div class="header-main">
        <h1>Производство</h1>
        <p class="subtitle">Отслеживайте этапы и отмечайте выполнение</p>
      </div>
      
      <div class="header-actions">
        <div v-if="quickStats" class="quick-balance-card" @click="router.push('/employee/salary')">
          <div class="qb-icon"><i class="ri-wallet-3-line"></i></div>
          <div class="qb-info">
            <span class="qb-label">Баланс:</span>
            <span class="qb-value">{{ formatPrice(quickStats.current_balance) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка данных о производстве...</p>
    </div>

    <div v-else-if="pipelines.length === 0" class="empty-state">
      <div class="empty-icon">🏗️</div>
      <h3>На производстве пока пусто</h3>
      <p>Запустите новый товар в работу или примите заказ, чтобы здесь появились данные</p>
    </div>

    <div v-else class="pipelines-grid">
      <div v-for="product in pipelines" :key="product.id" class="product-pipeline-card">
        <div class="product-info">
          <h2 class="product-name">{{ product.name }}</h2>
          <div class="total-stats">
            В производстве: {{ getTotalInWip(product) }} шт.
          </div>
        </div>

        <div class="pipeline-flow">
          <div 
            v-for="(stage, index) in product.pipeline" 
            :key="stage.stage_id"
            class="pipeline-step"
            :class="{ 
              'has-items': stage.quantity > 0,
              'can-execute': canExecute(product.pipeline, index),
              'start-step': stage.stage_id === 0
            }"
          >
            <!-- Line Connector -->
            <div v-if="index > 0" class="connector"></div>

            <div class="step-content">
              <div class="step-header">
                <span class="step-num">{{ stage.stage_id === 0 ? '📦' : stage.order_num }}</span>
                <span class="step-name">{{ stage.stage_name }}</span>
              </div>

              <div class="step-body">
                <div class="quantity-badge" :class="{ 'qty-ready': stage.quantity > 0 }">
                  {{ stage.quantity }} шт.
                </div>
                
                <div v-if="stage.stage_id !== 0" class="payment-hint">
                  Оплата: {{ formatPrice(stage.payment) }}
                </div>
              </div>

              <div class="step-footer">
                <AppButton 
                  v-if="canExecute(product.pipeline, index)"
                  size="sm"
                  variant="success"
                  @click="openReportModal(product, stage, index)"
                >
                  🔨 В работу
                </AppButton>
                <div v-else-if="stage.stage_id !== 0" class="wait-hint">
                  {{ index > 0 && product.pipeline[index-1].quantity === 0 ? 'Ждем заготовки' : '' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal for reporting work -->
    <AppModal v-model="showReportModal" :title="`Выполнение этапа: ${selectedStage?.stage_name}`">
      <div v-if="selectedProduct && selectedStage" class="report-form">
        <div class="report-summary">
          <p>Товар: <strong>{{ selectedProduct.name }}</strong></p>
          <p>Доступно для этого этапа: <strong>{{ prevStageQuantity }} шт.</strong></p>
        </div>

        <div class="form-group">
          <label class="label">Сколько штук вы выполнили?</label>
          <div class="input-with-max">
            <input 
              v-model.number="reportForm.quantity" 
              type="number" 
              min="1" 
              :max="prevStageQuantity"
              class="input-qty"
            />
            <button class="btn-max" @click="reportForm.quantity = prevStageQuantity">МАКС</button>
          </div>
          <div class="payment-calculation">
            К выплате: <strong>{{ formatPrice(reportForm.quantity * selectedStage.payment) }}</strong>
          </div>
        </div>
      </div>

      <template #footer>
        <AppButton variant="secondary" @click="showReportModal = false">Отмена</AppButton>
        <AppButton 
          variant="primary" 
          :loading="submitting"
          @click="submitReport"
        >
          Зафиксировать работу
        </AppButton>
      </template>
    </AppModal>

    <!-- Success Feedback Overlay -->
    <Transition name="slide-up">
      <div v-if="showSuccess" class="success-alert">
        <span class="check">✅</span>
        Работа сохранена! Зачислено {{ formatPrice(lastEarned) }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { productionAPI } from '@/api/production'
import { workLogsAPI } from '@/api/work_logs'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const pipelines = ref([])
const showReportModal = ref(false)
const showSuccess = ref(false)
const quickStats = ref(null)

const selectedProduct = ref(null)
const selectedStage = ref(null)
const selectedIndex = ref(-1)
const lastEarned = ref(0)

const reportForm = ref({
  quantity: 1
})

const loadData = async () => {
  loading.value = true
  try {
    const [wipRes, statsRes] = await Promise.all([
      productionAPI.getWipPipeline(),
      workLogsAPI.getMySalary()
    ])
    pipelines.value = wipRes.data
    quickStats.value = statsRes.data
  } catch (e) {
    console.error('Failed to load data', e)
  } finally {
    loading.value = false
  }
}

const getTotalInWip = (product) => {
  return product.pipeline.reduce((acc, stage) => acc + stage.quantity, 0)
}

const canExecute = (pipeline, index) => {
  if (index === 0) return false // Нулевой этап нельзя "выполнить", он - источник заготовок
  // Можно выполнить текущий этап, если на ПРЕДЫДУЩЕМ этапе есть хотя бы 1 единица
  const prevStage = pipeline[index - 1]
  return prevStage && prevStage.quantity > 0
}

const prevStageQuantity = computed(() => {
  if (!selectedProduct.value || selectedIndex.value <= 0) return 0
  return selectedProduct.value.pipeline[selectedIndex.value - 1].quantity
})

const openReportModal = (product, stage, index) => {
  selectedProduct.value = product
  selectedStage.value = stage
  selectedIndex.value = index
  reportForm.value.quantity = 1 // default to 1
  if (prevStageQuantity.value > 0 && prevStageQuantity.value < 10) {
      reportForm.value.quantity = prevStageQuantity.value
  }
  showReportModal.value = true
}

const submitReport = async () => {
  if (reportForm.value.quantity <= 0 || reportForm.value.quantity > prevStageQuantity.value) {
    alert('Некорректное количество')
    return
  }

  submitting.value = true
  try {
    const payload = {
      product_id: selectedProduct.value.id,
      stage_id: selectedStage.value.stage_id,
      quantity: reportForm.value.quantity
    }
    
    const { data } = await workLogsAPI.create(payload)
    
    lastEarned.value = data.payment
    showReportModal.value = false
    showSuccess.value = true
    setTimeout(() => showSuccess.value = false, 3000)
    
    await loadData()
  } catch (e) {
    alert('Ошибка: ' + (e.response?.data?.detail || e.message))
  } finally {
    submitting.value = false
  }
}

const formatPrice = (val) => {
  return new Intl.NumberFormat('ru-RU').format(val || 0) + ' ₸'
}

onMounted(loadData)
</script>

<style scoped>
.production-tasks {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; gap: 1rem; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.quick-balance-card {
  background: white;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  border: 1px solid #edf2f7;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-balance-card:hover {
  transform: translateY(-2px);
  border-color: #3182ce;
}

.qb-icon {
  width: 32px;
  height: 32px;
  background: #ebf8ff;
  color: #3182ce;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.qb-info { display: flex; flex-direction: column; }
.qb-label { font-size: 0.7rem; color: #718096; font-weight: 700; text-transform: uppercase; }
.qb-value { font-size: 1rem; font-weight: 800; color: #2d3748; }

.refresh-btn { height: 44px; width: 44px; display: flex; align-items: center; justify-content: center; padding: 0 !important; }

.page-header h1 {
  font-size: 2rem;
  font-weight: 800;
  margin: 0 0 0.5rem;
  color: #1a202c;
}

.subtitle {
  color: #718096;
  margin: 0;
}

.pipelines-grid {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.product-pipeline-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 25px rgba(0,0,0,0.05);
  border: 1px solid #edf2f7;
}

.product-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 2px solid #f7fafc;
  padding-bottom: 1rem;
}

.product-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0;
}

.total-stats {
  background: #ebf8ff;
  color: #3182ce;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  font-weight: 600;
}

.pipeline-flow {
  display: flex;
  align-items: flex-start;
  gap: 0;
  overflow-x: auto;
  padding: 1rem 0;
}

.pipeline-step {
  flex: 1;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  position: relative;
}

.connector {
  position: absolute;
  top: 30px;
  left: -50%;
  width: 100%;
  height: 3px;
  background: #e2e8f0;
  z-index: 1;
}

.pipeline-step.has-items .connector {
  background: #cbd5e0;
}

.step-content {
  position: relative;
  z-index: 2;
  background: #f8fafc;
  border: 2px solid #edf2f7;
  border-radius: 16px;
  padding: 1.25rem;
  margin: 0 0.75rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.pipeline-step.can-execute .step-content {
  border-color: #bee3f8;
  background: #fff;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.pipeline-step.has-items .step-content {
  border-color: #3182ce;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.step-num {
  width: 32px;
  height: 32px;
  background: #cbd5e0;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  transition: background 0.3s;
}

.pipeline-step.has-items .step-num {
  background: #3182ce;
}

.step-name {
  font-weight: 700;
  color: #4a5568;
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-body {
  margin-bottom: 1.25rem;
}

.quantity-badge {
  font-size: 1.25rem;
  font-weight: 800;
  color: #a0aec0;
  margin-bottom: 0.25rem;
}

.quantity-badge.qty-ready {
  color: #2d3748;
}

.payment-hint {
  font-size: 0.8rem;
  color: #48bb78;
  font-weight: 600;
}

.step-footer {
  min-height: 40px;
  display: flex;
  align-items: center;
}

.wait-hint {
  font-size: 0.75rem;
  color: #a0aec0;
  font-style: italic;
}

/* Modal Styles */
.report-form {
  padding: 0.5rem;
}

.report-summary {
  background: #f7fafc;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1.5rem;
}

.report-summary p {
  margin: 0.25rem 0;
  color: #4a5568;
}

.input-with-max {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.input-qty {
  flex: 1;
  padding: 0.75rem;
  font-size: 1.25rem;
  font-weight: 700;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  text-align: center;
}

.btn-max {
  background: #edf2f7;
  border: none;
  padding: 0 1rem;
  border-radius: 10px;
  font-weight: 700;
  color: #4a5568;
  cursor: pointer;
}

.btn-max:hover {
  background: #e2e8f0;
}

.payment-calculation {
  margin-top: 1rem;
  font-size: 1.1rem;
  color: #2d3748;
}

.payment-calculation strong {
  color: #38a169;
}

/* Toast */
.success-alert {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: #2f855a;
  color: white;
  padding: 1rem 2rem;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 1rem;
  font-weight: 700;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  z-index: 9999;
}

/* Transitions */
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.4s ease; }
.slide-up-enter-from { opacity: 0; transform: translateY(50px); }
.slide-up-leave-to { opacity: 0; transform: scale(0.9); }

.loading-state, .empty-state {
  text-align: center;
  padding: 6rem 2rem;
  background: white;
  border-radius: 30px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.empty-icon { font-size: 5rem; margin-bottom: 1rem; }

.spinner {
  width: 4rem;
  height: 4rem;
  border: 5px solid #edf2f7;
  border-top-color: #3182ce;
  border-radius: 50%;
  animation: spin 1s infinite linear;
  margin: 0 auto 1.5rem;
}

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .production-tasks { padding: 1rem; }
  .page-header { flex-direction: column; align-items: stretch; margin-bottom: 1.5rem; }
  .header-main h1 { font-size: 1.75rem; }
  .quick-balance-card { width: 100%; justify-content: center; }
  .pipeline-flow { flex-direction: column; gap: 1rem; padding: 0.5rem 0; }
  .pipeline-step { width: 100%; min-width: 0; }
  .connector { display: none; }
  .step-content { margin: 0; padding: 1rem; }
  .step-header { margin-bottom: 0.75rem; }
  .quantity-badge { font-size: 1.1rem; }
  .product-info { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
}

@media (max-width: 375px) {
    .production-tasks { padding: 0.75rem; }
    .page-header h1 { font-size: 1.5rem; }
}
</style>
