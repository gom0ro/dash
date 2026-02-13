<template>
  <div class="my-orders-view">
    <div class="page-header">
      <div>
        <h1>История заказов</h1>
        <p class="subtitle">Отслеживайте статус ваших закупок в реальном времени</p>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="stats-grid">
      <div class="stat-card blue">
        <div class="stat-icon"><i class="ri-box-3-line"></i></div>
        <div class="stat-info">
          <span class="stat-label">Всего заказов</span>
          <span class="stat-value">{{ myOrders.length }}</span>
        </div>
      </div>
      <div class="stat-card orange">
        <div class="stat-icon"><i class="ri-settings-3-line"></i></div>
        <div class="stat-info">
          <span class="stat-label">В работе</span>
          <span class="stat-value">{{ inWorkCount }}</span>
        </div>
      </div>
      <div class="stat-card green">
        <div class="stat-icon"><i class="ri-checkbox-circle-line"></i></div>
        <div class="stat-info">
          <span class="stat-label">Доставлено</span>
          <span class="stat-value">{{ deliveredCount }}</span>
        </div>
      </div>
    </div>

    <!-- Filters & Search -->
    <div class="filters-bar">
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.value"
          :class="['tab-btn', { active: currentTab === tab.value }]"
          @click="currentTab = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Поиск по ID или товару..."
          class="search-input"
        >
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загружаем вашу историю заказов...</p>
    </div>

    <div v-else-if="filteredOrders.length === 0" class="empty-state">
      <div class="empty-icon"><i class="ri-folder-open-line"></i></div>
      <h3>Заказы не найдены</h3>
      <p>По вашему запросу ничего не нашлось или вы еще не совершали заказов.</p>
      <AppButton variant="primary" @click="$router.push('/wholesaler/catalog')">
        Перейти в каталог
      </AppButton>
    </div>

    <div v-else class="orders-grid">
      <div 
        v-for="order in filteredOrders" 
        :key="order.id" 
        class="order-premium-card"
      >
        <div class="card-top">
          <div class="order-id">Заказ #{{ order.id }}</div>
          <StatusBadge :status="order.status" />
        </div>
        
        <div class="card-content">
          <h3 class="product-name">{{ getProductName(order.product_id) }}</h3>
          <div class="info-row">
            <span class="label">Количество:</span>
            <span class="value">{{ order.quantity }} шт.</span>
          </div>
          <div class="info-row">
            <span class="label">Сумма:</span>
            <span class="value price">{{ formatMoney(order.total_price) }}</span>
          </div>
          <div class="info-row">
            <span class="label">Создан:</span>
            <span class="value">{{ formatDate(order.created_at) }}</span>
          </div>
          <div class="info-row" v-if="order.deadline">
            <span class="label">Ожидаем к:</span>
            <span class="value">{{ formatDate(order.deadline) }}</span>
          </div>
        </div>

        <div class="card-footer">
           <div class="payment-status" :class="order.prepayment >= order.total_price ? 'paid' : 'pending'">
             <i :class="order.prepayment >= order.total_price ? 'ri-checkbox-circle-fill' : 'ri-time-line'"></i>
             {{ order.prepayment >= order.total_price ? ' Оплачен' : ' Ожидает оплаты' }}
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useOrdersStore } from '@/stores/orders'
import { useUserStore } from '@/stores/user'
import { useWarehouseStore } from '@/stores/warehouse'
import StatusBadge from '@/components/UI/StatusBadge.vue'
import AppButton from '@/components/UI/AppButton.vue'

const ordersStore = useOrdersStore()
const userStore = useUserStore()
const warehouseStore = useWarehouseStore()

const loading = ref(false)
const searchQuery = ref('')
const currentTab = ref('all')

const tabs = [
  { label: 'Все', value: 'all' },
  { label: 'В работе', value: 'work' },
  { label: 'Выполнены', value: 'done' },
  { label: 'Доставлены', value: 'delivered' }
]

const myOrders = computed(() => {
  return ordersStore.orders.filter(o => o.wholesaler_id === userStore.user?.id)
})

const inWorkCount = computed(() => {
  return myOrders.value.filter(o => ['accepted', 'in_progress', 'done'].includes(o.status)).length
})

const deliveredCount = computed(() => {
  return myOrders.value.filter(o => o.status === 'delivered').length
})

const filteredOrders = computed(() => {
  let list = myOrders.value

  // Tab Filtering
  if (currentTab.value === 'work') {
    list = list.filter(o => ['pending', 'accepted', 'in_progress', 'done'].includes(o.status))
  } else if (currentTab.value === 'done') {
    list = list.filter(o => o.status === 'done')
  } else if (currentTab.value === 'delivered') {
    list = list.filter(o => o.status === 'delivered')
  }

  // Search filtering
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(o => 
      o.id.toString().includes(q) || 
      getProductName(o.product_id).toLowerCase().includes(q)
    )
  }

  return list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const getProductName = (id) => {
  const p = warehouseStore.getProductById(id)
  return p ? p.name : `Товар #${id}`
}

const formatMoney = (v) => new Intl.NumberFormat('ru-RU').format(v || 0) + ' ₸'
const formatDate = (d) => new Date(d).toLocaleDateString('ru-RU', { day: '2-digit', month: 'long' })

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      ordersStore.fetchOrders(),
      warehouseStore.fetchProducts()
    ])
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.my-orders-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.subtitle {
  color: #6b7280;
  margin-top: 0.5rem;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-card.blue .stat-icon { background: #eff6ff; color: #3b82f6; }
.stat-card.orange .stat-icon { background: #fff7ed; color: #f97316; }
.stat-card.green .stat-icon { background: #f0fdf4; color: #22c55e; }

.stat-info { display: flex; flex-direction: column; }
.stat-label { font-size: 0.875rem; color: #6b7280; font-weight: 500; }
.stat-value { font-size: 1.5rem; font-weight: 800; color: #111827; }

/* Filters */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: white;
  padding: 0.75rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.tabs { display: flex; gap: 0.5rem; }
.tab-btn {
  padding: 0.6rem 1.25rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover { background: #f9fafb; color: #374151; }
.tab-btn.active { background: #667eea; color: white; }

.search-input {
  padding: 0.6rem 1rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  width: 300px;
}

/* Grid */
.orders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.order-premium-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #f3f4f6;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.order-premium-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.card-top {
  padding: 1.25rem;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fdfdfd;
}

.order-id { font-weight: 700; color: #111827; font-size: 0.95rem; }

.card-content { padding: 1.5rem; flex: 1; }
.product-name { margin: 0 0 1rem; font-size: 1.15rem; font-weight: 700; color: #1e293b; }

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.6rem;
  font-size: 0.9rem;
}

.info-row .label { color: #64748b; }
.info-row .value { font-weight: 600; color: #1e293b; }
.info-row .value.price { color: #3b82f6; font-weight: 700; }

.card-footer {
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #f1f5f9;
}

.payment-status {
  font-size: 0.875rem;
  font-weight: 700;
  text-align: center;
  padding: 0.4rem;
  border-radius: 8px;
}

.payment-status.paid {
  background: #dcfce7;
  color: #166534;
}

.payment-status.pending {
  background: #fff7ed;
  color: #9a3412;
}

/* States */
.loading-state, .empty-state {
  padding: 5rem 2rem;
  text-align: center;
  background: white;
  border-radius: 20px;
}

.empty-icon { font-size: 4rem; opacity: 0.3; margin-bottom: 1rem; }
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f4f6;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .filters-bar { flex-direction: column; gap: 1rem; align-items: stretch; }
  .search-input { width: 100%; }
  .tabs { overflow-x: auto; padding-bottom: 0.5rem; }
}
</style>
