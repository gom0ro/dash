<template>
  <div class="warehouse-view fade-in">
    <div class="page-header">
      <div class="header-content">
        <h1>Готовый склад</h1>
        <p class="subtitle">Управление отгрузкой готовой продукции клиентам</p>
      </div>
      <div class="header-stats" v-if="!loading && readyProducts.length > 0">
        <div class="stat-badge">
          <i class="ri-checkbox-circle-line"></i>
          <span>{{ readyProducts.length }} позиций в наличии</span>
        </div>
      </div>
    </div>

    <div class="filters-bar">
      <div class="search-box">
        <i class="ri-search-line"></i>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск по названию товара..."
          class="modern-search-input"
        />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка остатков склада...</p>
    </div>

    <div v-else class="inventory-container">
      <div v-if="readyProducts.length === 0" class="empty-state">
        <div class="empty-icon">📦</div>
        <h3>Склад пуст</h3>
        <p>На данный момент готовой продукции нет. Ожидайте завершения производства.</p>
      </div>

      <div v-else class="stock-grid">
        <div v-for="product in readyProducts" :key="product.id" class="stock-card">
          <div class="stock-card-main">
            <div class="product-visual">
              <div class="product-icon"><i class="ri-box-3-line"></i></div>
            </div>
            <div class="product-details">
              <h3>{{ product.name }}</h3>
              <p class="product-desc">{{ product.description || 'Нет описания' }}</p>
            </div>
          </div>
          
          <div class="stock-info-row">
            <div class="stock-status">
              <span class="label">В наличии:</span>
              <div class="stock-badge" :class="{ 'low': product.stock < 5 }">
                <span class="value">{{ product.stock }}</span>
                <span class="unit">шт.</span>
              </div>
            </div>
            <AppButton size="md" variant="success" class="issue-btn" @click="openIssueModal(product)">
              <i class="ri-send-plane-fill"></i> Выдать
            </AppButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка выдачи товара -->
    <AppModal v-model="showIssueModal" title="Выдача товара со склада">
      <div v-if="selectedProduct" class="issue-modal-content">
        <div class="selected-product-banner">
          <div class="banner-icon"><i class="ri-archive-line"></i></div>
          <div class="banner-text">
            <h3>{{ selectedProduct.name }}</h3>
            <p>Текущий остаток: <strong>{{ selectedProduct.stock }} шт.</strong></p>
          </div>
        </div>
        
        <div class="form-section">
          <label class="section-label">Цель выдачи</label>
          <div class="orders-list-custom">
            <div 
              class="order-item simple" 
              :class="{ active: selectedOrderId === null }"
              @click="selectedOrderId = null"
            >
              <div class="order-radio"><div class="dot"></div></div>
              <div class="order-text">
                <span class="title">Прямое списание</span>
                <span class="desc">Выдача без привязки к конкретному заказу</span>
              </div>
            </div>
            
            <div 
              v-for="order in activeProductOrders" 
              :key="order.id"
              class="order-item"
              :class="{ active: selectedOrderId === order.id }"
              @click="selectOrder(order)"
            >
              <div class="order-radio"><div class="dot"></div></div>
              <div class="order-details-box">
                <div class="order-top">
                  <span class="order-number">Заказ #{{ order.id }}</span>
                  <span class="order-qty-pill">{{ order.quantity }} шт.</span>
                </div>
                <div class="order-client">
                  <i class="ri-user-line"></i> {{ order.customer_name || 'Клиент' }}
                  <span v-if="order.customer_phone" class="phone-small">{{ order.customer_phone }}</span>
                </div>
                <div class="order-footer-meta">
                  {{ order.total_price }} ₸ • {{ order.payment_method }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="form-section">
          <label class="section-label">Количество к выдаче</label>
          <div class="qty-input-box">
             <input 
              v-model.number="issueQty" 
              type="number" 
              class="modern-input-qty" 
              min="1" 
              :max="selectedProduct.stock"
            />
            <div class="qty-info">
                <span>из {{ selectedProduct.stock }} доступных</span>
                <div class="qty-bar"><div class="qty-bar-fill" :style="{ width: (issueQty / selectedProduct.stock * 100) + '%' }"></div></div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <AppButton variant="secondary" @click="showIssueModal = false">Отмена</AppButton>
        <AppButton variant="success" :loading="issuing" @click="handleIssue" class="confirm-issue">
          Подтвердить отгрузку
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWarehouseStore } from '@/stores/warehouse'
import { useOrdersStore } from '@/stores/orders'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'

const warehouseStore = useWarehouseStore()
const ordersStore = useOrdersStore()
const loading = ref(false)
const issuing = ref(false)
const searchQuery = ref('')

const showIssueModal = ref(false)
const selectedProduct = ref(null)
const selectedOrderId = ref(null)
const issueQty = ref(1)

const activeProductOrders = computed(() => {
  if (!selectedProduct.value) return []
  return ordersStore.orders.filter(o => 
    o.product_id === selectedProduct.value.id && 
    o.status !== 'delivered' &&
    o.status !== 'pending' &&
    o.status !== 'cancelled'
  )
})

const openIssueModal = async (product) => {
  selectedProduct.value = product
  issueQty.value = 1
  selectedOrderId.value = null
  showIssueModal.value = true
}

const selectOrder = (order) => {
  selectedOrderId.value = order.id
  issueQty.value = order.quantity
}

const handleIssue = async () => {
  if (issueQty.value < 1 || issueQty.value > selectedProduct.value.stock) {
    alert('Некорректное количество')
    return
  }
  
  issuing.value = true
  try {
    if (selectedOrderId.value) {
      await ordersStore.updateOrderStatus(selectedOrderId.value, 'delivered')
    } else {
      const newStock = selectedProduct.value.stock - issueQty.value
      await warehouseStore.updateStock(selectedProduct.value.id, newStock)
    }
    
    showIssueModal.value = false
    alert(selectedOrderId.value ? 'Заказ успешно выдан и закрыт!' : 'Товар успешно списан со склада!')
    
    await Promise.all([
      warehouseStore.fetchProducts(),
      ordersStore.fetchOrders()
    ])
  } catch (err) {
    alert('Ошибка при выдаче: ' + (err.response?.data?.detail || err.message))
  } finally {
    issuing.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      warehouseStore.fetchProducts(),
      ordersStore.fetchOrders()
    ])
  } finally {
    loading.value = false
  }
})

const readyProducts = computed(() => {
  let products = warehouseStore.products.filter(p => p.stock > 0)
  if (searchQuery.value) {
    products = products.filter(p => p.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }
  return products
})
</script>

<style scoped>
.warehouse-view {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
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

.stat-badge {
    background: #dcfce7;
    color: #166534;
    padding: 0.6rem 1.25rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 700;
    font-size: 0.9rem;
}

.filters-bar {
    margin-bottom: 2rem;
}

.search-box {
    position: relative;
    max-width: 500px;
}

.search-box i {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
    font-size: 1.2rem;
}

.modern-search-input {
    width: 100%;
    padding: 0.85rem 1rem 0.85rem 3rem;
    border: 1px solid #f1f5f9;
    background: white;
    border-radius: 14px;
    font-size: 0.95rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    transition: all 0.2s;
}

.modern-search-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.05);
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.stock-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  border: 1px solid #f1f5f9;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  transition: all 0.2s;
}

.stock-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.06);
}

.stock-card-main {
    display: flex;
    gap: 1.25rem;
}

.product-visual {
    flex-shrink: 0;
}

.product-icon {
    width: 56px;
    height: 56px;
    background: #f8fafc;
    color: #3b82f6;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    border: 1px solid #f1f5f9;
}

.product-details h3 {
    margin: 0 0 0.25rem;
    font-size: 1.2rem;
    font-weight: 800;
    color: #1e293b;
}

.product-desc {
    font-size: 0.875rem;
    color: #94a3b8;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.stock-info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1.25rem;
    border-top: 1px solid #f8fafc;
}

.stock-status {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.stock-status .label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stock-badge {
    display: flex;
    align-items: flex-end;
    gap: 4px;
    color: #059669;
}

.stock-badge .value {
    font-size: 1.5rem;
    font-weight: 900;
    line-height: 1;
}

.stock-badge .unit {
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 2px;
}

.stock-badge.low {
    color: #d97706;
}

.issue-btn {
    padding: 0.6rem 1.25rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Modal Styling */
.issue-modal-content { padding: 0.5rem 0; }

.selected-product-banner {
    background: #f8fafc;
    padding: 1.25rem;
    border-radius: 16px;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    margin-bottom: 2rem;
    border: 1px solid #f1f5f9;
}

.banner-icon {
    width: 48px;
    height: 48px;
    background: white;
    color: #3b82f6;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

.banner-text h3 { margin: 0; font-size: 1.1rem; font-weight: 800; color: #1e293b; }
.banner-text p { margin: 2px 0 0; font-size: 0.875rem; color: #64748b; }

.section-label {
    display: block;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.form-section { margin-bottom: 2rem; }

.orders-list-custom {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    max-height: 300px;
    overflow-y: auto;
    padding-right: 0.5rem;
}

.order-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f8fafc;
    border: 2px solid #f1f5f9;
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.2s;
}

.order-radio {
    width: 20px;
    height: 20px;
    border: 2px solid #cbd5e1;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.order-radio .dot {
    width: 10px;
    height: 10px;
    background: #3b82f6;
    border-radius: 50%;
    opacity: 0;
    transform: scale(0.5);
    transition: all 0.2s;
}

.order-item.active {
    background: white;
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
}

.order-item.active .order-radio { border-color: #3b82f6; }
.order-item.active .order-radio .dot { opacity: 1; transform: scale(1); }

.order-details-box { flex: 1; }
.order-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.order-number { font-weight: 800; color: #1e293b; font-size: 0.95rem; }
.order-qty-pill { background: #dcfce7; color: #166534; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 6px; }
.order-client { font-size: 0.85rem; color: #475569; font-weight: 600; display: flex; align-items: center; gap: 4px; }
.phone-small { color: #94a3b8; font-weight: 400; }
.order-footer-meta { font-size: 0.75rem; color: #94a3b8; margin-top: 4px; font-weight: 500; }

.order-item.simple .title { font-weight: 700; color: #1e293b; display: block; }
.order-item.simple .desc { font-size: 0.8rem; color: #94a3b8; font-weight: 500; }

.qty-input-box {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.modern-input-qty {
    width: 120px;
    padding: 1rem;
    border: 2px solid #f1f5f9;
    background: #f8fafc;
    border-radius: 14px;
    font-size: 1.5rem;
    font-weight: 900;
    color: #1e293b;
    text-align: center;
}

.qty-info { flex: 1; }
.qty-info span { font-size: 0.9rem; color: #64748b; font-weight: 600; display: block; margin-bottom: 8px; }
.qty-bar { height: 8px; background: #f1f5f9; border-radius: 99px; overflow: hidden; }
.qty-bar-fill { height: 100%; background: #3b82f6; border-radius: 99px; transition: width 0.3s ease; }

.confirm-issue { padding: 0.75rem 1.5rem; font-weight: 700; }

.loading-state, .empty-state {
    text-align: center;
    padding: 5rem 2rem;
    background: white;
    border-radius: 24px;
}

.spinner {
    width: 3.5rem;
    height: 3.5rem;
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
    .stock-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
}

@media (max-width: 768px) {
    .warehouse-view { padding: 1rem; }
    .page-header { flex-direction: column; align-items: flex-start; gap: 1.25rem; }
    .header-stats { width: 100%; }
    .stat-badge { width: 100%; justify-content: center; }
    .stock-grid { grid-template-columns: 1fr; }
    .header-content h1 { font-size: 1.6rem; }
}
</style>