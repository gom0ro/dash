<template>
  <div class="catalog-view">
    <div class="page-header">
      <div class="header-content">
        <h1>Каталог продукции</h1>
        <p class="subtitle">Оптовые цены напрямую от производителя</p>
      </div>
      <div class="header-actions">
        <div class="search-box">
          <i class="ri-search-line"></i>
          <input v-model="search" type="text" placeholder="Поиск товара..." class="search-input" />
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка каталога товаров...</p>
    </div>

    <div v-else class="catalog-container">
      <div v-for="product in filteredProducts" :key="product.id" class="product-premium-card">
        <div class="product-visual">
          <div class="product-icon">📦</div>
        </div>
        
        <div class="product-body">
          <div class="product-main">
            <h3 class="product-title">{{ product.name }}</h3>
            <p class="product-desc">{{ product.description || 'Высококачественное изделие собственного производства.' }}</p>
          </div>

          <div class="product-footer">
            <div class="price-box">
              <span class="price-label">Оптовая цена</span>
              <span class="price-value">{{ formatMoney(product.price) }}</span>
            </div>

            <div class="order-controls">
              <div class="qty-selector">
                <button class="qty-btn" @click="adjustQty(product.id, -1)">-</button>
                <input v-model.number="orderForm[product.id]" type="number" min="1" class="qty-field" />
                <button class="qty-btn" @click="adjustQty(product.id, 1)">+</button>
              </div>
              <AppButton 
                variant="primary" 
                @click="createOrder(product.id)" 
                :loading="ordering === product.id"
                block
              >
                Оформить заказ
              </AppButton>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Feedback -->
    <Transition name="toast">
      <div v-if="showSuccess" class="success-toast">
        <div class="toast-icon">✅</div>
        <div class="toast-msg">Заказ успешно оформлен! Следите за статусом в личном кабинете.</div>
      </div>
    </Transition>

    <!-- Confirmation Modal -->
    <AppModal 
      v-model="showConfirmModal" 
      title="Подтверждение заказа"
      size="md"
    >
      <div v-if="selectedProduct" class="confirm-modal-content">
        <div class="order-summary-box">
          <div class="summary-item">
            <span class="label">Товар:</span>
            <span class="value">{{ selectedProduct.name }}</span>
          </div>
          <div class="summary-item">
            <span class="label">Количество:</span>
            <span class="value">{{ confirmForm.quantity }} шт.</span>
          </div>
          <div class="summary-item total">
            <span class="label">К оплате:</span>
            <span class="value">{{ formatMoney(selectedProduct.price * confirmForm.quantity) }}</span>
          </div>
        </div>

        <div class="confirm-form">
          <h4>Проверьте контактные данные</h4>
          <p class="hint">Эти данные будут использованы для доставки и связи</p>
          
          <div class="form-group">
            <label>Ваше имя / Компания</label>
            <input v-model="confirmForm.customer_name" class="input" type="text" placeholder="ФИО">
          </div>
          <div class="form-group">
            <label>Телефон</label>
            <input v-model="confirmForm.customer_phone" class="input" type="tel" placeholder="Номер телефона">
          </div>
          <div class="form-group">
            <label>Адрес доставки</label>
            <textarea v-model="confirmForm.customer_address" class="textarea" rows="2" placeholder="Адрес"></textarea>
          </div>
        </div>
      </div>

      <template #footer>
        <AppButton variant="secondary" @click="showConfirmModal = false">Отмена</AppButton>
        <AppButton 
          variant="primary" 
          @click="confirmAndSendOrder" 
          :loading="submittingOrder"
        >
          Заказать
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { productionAPI, ordersAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'

const userStore = useUserStore()

const products = ref([])
const loading = ref(false)
const search = ref('')
const showSuccess = ref(false)
const orderForm = ref({})

// Modal states
const showConfirmModal = ref(false)
const submittingOrder = ref(false)
const selectedProduct = ref(null)
const confirmForm = ref({
  quantity: 0,
  customer_name: '',
  customer_phone: '',
  customer_address: ''
})

const formatMoney = (v) => new Intl.NumberFormat('ru-RU').format(v || 0) + ' ₸'

const filteredProducts = computed(() => {
  return products.value.filter(p => p.name.toLowerCase().includes(search.value.toLowerCase()))
})

const loadProducts = async () => {
  loading.value = true
  try {
    const { data } = await productionAPI.getProducts()
    products.value = data
    data.forEach(p => orderForm.value[p.id] = 5) // По умолчанию опт от 5 шт
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const adjustQty = (id, delta) => {
  const current = orderForm.value[id] || 0
  orderForm.value[id] = Math.max(1, current + delta)
}

const createOrder = (productId) => {
  const quantity = orderForm.value[productId]
  if (quantity < 1) return
  
  const product = products.value.find(p => p.id === productId)
  if (!product) return

  selectedProduct.value = product
  confirmForm.value = {
    quantity,
    customer_name: userStore.user?.full_name || '',
    customer_phone: userStore.user?.phone || '',
    customer_address: userStore.user?.address || ''
  }
  showConfirmModal.value = true
}

const confirmAndSendOrder = async () => {
  if (!selectedProduct.value) return
  
  submittingOrder.value = true
  try {
    const deadline = new Date()
    deadline.setDate(deadline.getDate() + 10) 
    
    await ordersAPI.createOrder({
      product_id: selectedProduct.value.id,
      quantity: confirmForm.value.quantity,
      deadline: deadline.toISOString(),
      customer_name: confirmForm.value.customer_name,
      customer_phone: confirmForm.value.customer_phone,
      customer_address: confirmForm.value.customer_address,
      total_price: selectedProduct.value.price * confirmForm.value.quantity,
      prepayment: 0,
      payment_method: 'безнал'
    })
    
    showConfirmModal.value = false
    showSuccess.value = true
    setTimeout(() => showSuccess.value = false, 4000)
  } catch (err) {
    alert('Ошибка при оформлении: ' + (err.response?.data?.detail || err.message))
  } finally {
    submittingOrder.value = false
  }
}

onMounted(loadProducts)
</script>

<style scoped>
.catalog-view { padding: 2rem; max-width: 1400px; margin: 0 auto; background: #f8fafc; min-height: 100vh; }

.page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 3rem; }
.header-content h1 { font-size: 2.5rem; font-weight: 800; color: #1e293b; margin: 0; letter-spacing: -0.025em; }
.subtitle { color: #64748b; font-size: 1.1rem; margin-top: 0.5rem; }

.search-box { position: relative; width: 100%; max-width: 400px; }
.search-box i { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.search-input { padding: 0.75rem 1rem 0.75rem 2.8rem; border-radius: 14px; border: 1.5px solid #e2e8f0; width: 100%; font-size: 0.95rem; transition: all 0.2s; background: white; }
.search-input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 4px rgba(59,130,246,0.1); }

.catalog-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }

.product-premium-card { background: white; border-radius: 24px; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.product-premium-card:hover { transform: translateY(-8px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }

.product-visual { height: 120px; background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); display: flex; align-items: center; justify-content: center; font-size: 3rem; }

.product-body { padding: 1.5rem; flex: 1; display: flex; flex-direction: column; }
.product-main { flex: 1; }
.product-title { font-size: 1.5rem; font-weight: 800; color: #1e293b; margin: 0 0 0.5rem; }
.product-desc { color: #64748b; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.5rem; }

.product-footer { border-top: 1px solid #f1f5f9; padding-top: 1.5rem; }
.price-box { margin-bottom: 1.5rem; }
.price-label { display: block; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem; }
.price-value { font-size: 2rem; font-weight: 800; color: #3b82f6; }

.order-controls { display: flex; flex-direction: column; gap: 1rem; }
.qty-selector { display: flex; align-items: center; background: #f1f5f9; border-radius: 12px; padding: 0.25rem; }
.qty-btn { width: 40px; height: 40px; border: none; background: white; border-radius: 10px; font-size: 1.25rem; font-weight: 700; color: #1e293b; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.qty-btn:hover { background: #3b82f6; color: white; }
.qty-field { flex: 1; background: transparent; border: none; text-align: center; font-size: 1.1rem; font-weight: 800; color: #1e293b; pointer-events: none; }

/* Toast Notification */
.success-toast { position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%); background: #1e293b; color: white; padding: 1rem 2rem; border-radius: 16px; display: flex; align-items: center; gap: 1rem; z-index: 1000; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2); }
.toast-icon { font-size: 1.5rem; }
.toast-msg { font-weight: 600; font-size: 0.95rem; }

.toast-enter-active, .toast-leave-active { transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.toast-enter-from { opacity: 0; transform: translate(-50%, 20px); }
.toast-leave-to { opacity: 0; transform: translate(-50%, 20px) scale(0.9); }

/* Confirm Modal Styles */
.confirm-modal-content {
  padding: 1rem 0;
}

.order-summary-box {
  background: #f8fafc;
  padding: 1.25rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  border: 1px solid #e2e8f0;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.summary-item .label {
  color: #64748b;
  font-size: 0.9rem;
}

.summary-item .value {
  font-weight: 700;
  color: #1e293b;
}

.summary-item.total {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 2px dashed #e2e8f0;
}

.summary-item.total .value {
  font-size: 1.25rem;
  color: #3b82f6;
}

.confirm-form h4 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
}

.confirm-form .hint {
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
}

.input {
  padding: 0.75rem;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
}

.loading-state { height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.spinner { width: 3.5rem; height: 3.5rem; border: 4px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 1.5rem; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .catalog-view { padding: 1rem; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 1.5rem; margin-bottom: 2rem; }
  .header-content h1 { font-size: 1.8rem; }
  .search-box { max-width: 100%; }
  .catalog-container { grid-template-columns: 1fr; gap: 1rem; }
  .product-premium-card { border-radius: 20px; }
  .product-main h3 { font-size: 1.25rem; }
  .price-value { font-size: 1.6rem; }
}

@media (max-width: 375px) {
    .catalog-view { padding: 0.75rem; }
    .product-body { padding: 1.25rem; }
}
</style>
