<template>
  <div class="warehouse-view">
    <div class="page-header">
      <div>
        <h1>Готовый склад</h1>
        <p class="subtitle">Отгрузка готовой продукции клиентам и оптовикам</p>
      </div>
    </div>

    <div class="filters-bar">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Найти готовый товар..."
          class="search-input"
        />
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка остатков...</p>
    </div>

    <div v-else class="inventory-container">
      <div v-if="readyProducts.length === 0" class="empty">
        <div class="empty-icon">📭</div>
        <h3>На складе пусто</h3>
        <p>Дождитесь завершения производства товаров.</p>
      </div>

      <div v-else class="stock-table-card">
        <table class="stock-table">
          <thead>
            <tr>
              <th>Товар</th>
              <th>Описание</th>
              <th>В наличии</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in readyProducts" :key="product.id">
              <td>
                <div class="product-info">
                  <div class="product-name">{{ product.name }}</div>
                </div>
              </td>
              <td>
                <div class="product-desc-tiny">{{ product.description || '—' }}</div>
              </td>
              <td>
                <div class="stock-count" :class="{ low: product.stock < 5 }">
                  {{ product.stock }} шт.
                </div>
              </td>
              <td class="actions-cell">
                <AppButton size="sm" variant="success" @click="openIssueModal(product)">
                  📦 Выдать
                </AppButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Модалка выдачи товара -->
    <AppModal v-model="showIssueModal" title="Выдача товара со склада">
      <div v-if="selectedProduct" class="issue-modal-body">
        <div class="issue-info">
          <h3>{{ selectedProduct.name }}</h3>
          <p>Доступно для выдачи: <strong>{{ selectedProduct.stock }} шт.</strong></p>
        </div>
        
        <div class="form-group" style="margin-bottom: 1.5rem;">
          <label class="label-bold">Выдуть под заказ?</label>
          <div class="orders-selection">
            <div 
              class="order-option" 
              :class="{ active: selectedOrderId === null }"
              @click="selectedOrderId = null"
            >
              <div class="option-title">Без привязки к заказу</div>
              <div class="option-desc">Просто списать со склада</div>
            </div>
            
            <div 
              v-for="order in activeProductOrders" 
              :key="order.id"
              class="order-option"
              :class="{ active: selectedOrderId === order.id }"
              @click="selectOrder(order)"
            >
              <div class="option-header">
                <span class="order-id">Заказ #{{ order.id }}</span>
                <span class="order-qty">{{ order.quantity }} шт.</span>
              </div>
              <div class="option-client">
                {{ order.customer_name || 'Оптовик' }} 
                <span v-if="order.customer_phone" class="phone">({{ order.customer_phone }})</span>
              </div>
              <div class="option-finance">
                Итого: {{ order.total_price }} ₸ | Оплата: {{ order.payment_method }}
              </div>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label class="label-bold">Количество для выдачи</label>
          <div class="qty-control">
             <input 
              v-model.number="issueQty" 
              type="number" 
              class="input qty-input-large" 
              min="1" 
              :max="selectedProduct.stock"
            />
            <span class="qty-suffix">из {{ selectedProduct.stock }} доступных</span>
          </div>
          <p class="hint">Это количество будет окончательно списано со склада</p>
        </div>
      </div>
      
      <template #footer>
        <AppButton variant="secondary" @click="showIssueModal = false">Отмена</AppButton>
        <AppButton :loading="issuing" @click="handleIssue">Подтвердить выдачу</AppButton>
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
    o.status !== 'pending'
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
      // КЕЙС 1: Выдача под конкретный заказ. 
      // Бэкенд сам спишет товар со склада при переходе в статус 'delivered'
      await ordersStore.updateOrderStatus(selectedOrderId.value, 'delivered')
    } else {
      // КЕЙС 2: Прямое списание со склада (без заказа)
      const newStock = selectedProduct.value.stock - issueQty.value
      await warehouseStore.updateStock(selectedProduct.value.id, newStock)
    }
    
    showIssueModal.value = false
    alert(selectedOrderId.value ? 'Заказ успешно выдан и закрыт!' : 'Товар успешно списан со склада!')
    
    // Обновляем данные на странице
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
.warehouse-view { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.page-header { margin-bottom: 2rem; }
.subtitle { color: #64748b; margin: 0; }

.filters-bar { margin-bottom: 2rem; background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.search-input { width: 100%; padding: 0.75rem 1rem; border: 1.5px solid #e2e8f0; border-radius: 10px; }

.stock-table-card { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; }
.stock-table { width: 100%; border-collapse: collapse; text-align: left; }
.stock-table th { background: #f8fafc; padding: 1.25rem 1.5rem; color: #64748b; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.stock-table td { padding: 1.25rem 1.5rem; border-top: 1px solid #f1f5f9; }

.product-name { font-weight: 700; color: #1e293b; font-size: 1.05rem; }
.product-desc-tiny { color: #94a3b8; font-size: 0.85rem; max-width: 300px; }

.stock-count { font-weight: 800; color: #10b981; font-size: 1.1rem; }
.stock-count.low { color: #f59e0b; }

.issue-modal-body { padding: 1rem 0; }
.issue-info { background: #f8fafc; padding: 1.25rem; border-radius: 12px; margin-bottom: 1.5rem; }
.issue-info h3 { margin: 0 0 0.5rem; color: #1e293b; }
.issue-info p { color: #64748b; margin: 0; }

.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.label-bold { font-weight: 700; color: #1e293b; font-size: 0.95rem; margin-bottom: 0.25rem; }
.input { padding: 0.75rem; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 1.1rem; font-weight: 700; }
.qty-control { display: flex; align-items: center; gap: 1rem; }
.qty-input-large { width: 120px; }
.qty-suffix { color: #64748b; font-size: 0.9rem; }

.orders-selection { display: flex; flex-direction: column; gap: 0.75rem; max-height: 300px; overflow-y: auto; padding: 2px; }
.order-option { background: #f8fafc; border: 1.5px solid #e2e8f0; padding: 1rem; border-radius: 12px; cursor: pointer; transition: all 0.2s; }
.order-option:hover { border-color: #3b82f6; background: #eff6ff; }
.order-option.active { border-color: #3b82f6; background: #eff6ff; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }

.option-title { font-weight: 700; color: #1e293b; }
.option-desc { font-size: 0.85rem; color: #64748b; }

.option-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.order-id { font-weight: 800; color: #3b82f6; }
.order-qty { font-weight: 800; background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 6px; font-size: 0.85rem; }
.option-client { font-weight: 600; font-size: 0.9rem; color: #1e293b; }
.option-client .phone { color: #64748b; font-weight: 400; font-size: 0.8rem; }
.option-finance { font-size: 0.8rem; color: #64748b; margin-top: 0.25rem; }

.hint { font-size: 0.85rem; color: #94a3b8; margin: 0; }

.loading { text-align: center; padding: 4rem; }
.spinner { width: 3rem; height: 3rem; border: 3px solid #f3f4f6; border-top-color: #3b82f6; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }

.empty { text-align: center; padding: 5rem; background: white; border-radius: 20px; color: #94a3b8; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
</style>