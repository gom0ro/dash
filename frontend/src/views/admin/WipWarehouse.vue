<template>
  <div class="wip-warehouse fade-in">
    <div class="page-header">
      <div class="header-content">
        <h1>Временный склад (WIP)</h1>
        <p class="subtitle">Отслеживание незавершенного производства по этапам</p>
      </div>
      <div class="header-stats" v-if="!loading && groupedInventory.length > 0">
        <div class="stat-pill">
          <span class="label">Всего изделий:</span>
          <span class="value">{{ totalInProcess }}</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка данных склада...</p>
    </div>

    <div v-else-if="groupedInventory.length === 0" class="empty-state">
      <div class="empty-icon">🏗️</div>
      <h3>Склад пуст</h3>
      <p>На данный момент активные производственные процессы отсутствуют.</p>
    </div>

    <div v-else class="inventory-grid">
      <div v-for="product in groupedInventory" :key="product.id" class="product-card">
        <div class="product-card-header">
          <div class="product-title">
            <div class="product-icon"><i class="ri-hammer-line"></i></div>
            <h3>{{ product.name }}</h3>
          </div>
          <span class="total-qty-badge">{{ product.total }} ед.</span>
        </div>
        
        <div class="stages-container">
          <div v-for="stage in product.stages" :key="stage.stage_id" class="stage-card">
            <div class="stage-info">
              <span class="stage-name">{{ stage.stage_name }}</span>
              <span class="stage-qty">{{ stage.quantity }} <small>шт.</small></span>
            </div>
            <div class="progress-wrapper">
              <div class="progress-bg">
                <div 
                  class="progress-fill" 
                  :style="{ width: (stage.quantity / product.total * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { productionAPI } from '@/api/production'

const inventory = ref([])
const loading = ref(false)

const loadInventory = async () => {
  loading.value = true
  try {
    const { data } = await productionAPI.getWipInventory()
    inventory.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const totalInProcess = computed(() => {
  return inventory.value.reduce((acc, item) => acc + item.quantity, 0)
})

const groupedInventory = computed(() => {
  const groups = {}
  inventory.value.forEach(item => {
    if (!groups[item.product_id]) {
      groups[item.product_id] = {
        id: item.product_id,
        name: item.product_name,
        total: 0,
        stages: []
      }
    }
    groups[item.product_id].total += item.quantity
    groups[item.product_id].stages.push(item)
  })
  return Object.values(groups)
})

onMounted(loadInventory)
</script>

<style scoped>
.wip-warehouse {
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

.subtitle {
  color: #64748b;
  font-weight: 500;
  margin: 0;
}

.stat-pill {
  background: white;
  padding: 0.6rem 1.25rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  border: 1px solid #f1f5f9;
}

.stat-pill .label { font-size: 0.875rem; color: #64748b; font-weight: 600; }
.stat-pill .value { font-size: 1.125rem; color: #3b82f6; font-weight: 800; }

.inventory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 1.5rem;
}

.product-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.04);
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.08);
}

.product-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #f8fafc;
}

.product-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-icon {
  width: 40px;
  height: 40px;
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.product-card-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.total-qty-badge {
  background: #f1f5f9;
  color: #475569;
  font-weight: 700;
  font-size: 0.875rem;
  padding: 0.4rem 0.8rem;
  border-radius: 99px;
}

.stages-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stage-card {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
}

.stage-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.stage-name {
  font-weight: 600;
  color: #475569;
  font-size: 0.9375rem;
}

.stage-qty {
  font-weight: 800;
  color: #1e293b;
  font-size: 1.125rem;
}

.stage-qty small {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-left: 2px;
}

.progress-wrapper {
  height: 6px;
  width: 100%;
}

.progress-bg {
  height: 100%;
  background: #e2e8f0;
  border-radius: 99px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
  border-radius: 99px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.loading-state, .empty-state {
  text-align: center;
  padding: 5rem 2rem;
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

.empty-icon { font-size: 4.5rem; margin-bottom: 1.5rem; opacity: 0.8; }
.empty-state h3 { font-size: 1.5rem; color: #1e293b; margin-bottom: 0.5rem; }
.empty-state p { color: #64748b; }

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
  .inventory-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
}

@media (max-width: 768px) {
  .wip-warehouse { padding: 1rem; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .header-stats { width: 100%; }
  .stat-pill { width: 100%; justify-content: center; }
  .inventory-grid { grid-template-columns: 1fr; }
  .product-card { padding: 1.25rem; }
  .header-content h1 { font-size: 1.5rem; }
}
</style>
