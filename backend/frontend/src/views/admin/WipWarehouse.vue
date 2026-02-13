<template>
  <div class="wip-warehouse">
    <div class="page-header">
      <div>
        <h1>Временный склад (WIP)</h1>
        <p class="subtitle">Незавершенное производство по этапам</p>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка данных склада...</p>
    </div>

    <div v-else-if="groupedInventory.length === 0" class="empty">
      <div class="empty-icon">📦</div>
      <h3>Склад пуст</h3>
      <p>Нет активных процессов производства</p>
    </div>

    <div v-else class="inventory-grid">
      <div v-for="product in groupedInventory" :key="product.id" class="product-card">
        <div class="product-header">
          <h3>{{ product.name }}</h3>
          <span class="total-qty">{{ product.total }} ед. в процессе</span>
        </div>
        
        <div class="stages-list">
          <div v-for="stage in product.stages" :key="stage.stage_id" class="stage-item">
            <div class="stage-info">
              <span class="stage-name">{{ stage.stage_name }}</span>
              <span class="stage-qty">{{ stage.quantity }} ед.</span>
            </div>
            <div class="stage-bar">
              <div class="bar-fill" :style="{ width: (stage.quantity / product.total * 100) + '%' }"></div>
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
.wip-warehouse { padding: 2rem; }
.page-header { margin-bottom: 2rem; }
.inventory-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 1.5rem; }

.product-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 1rem;
}

.product-header h3 { margin: 0; font-size: 1.25rem; color: #111827; }
.total-qty { font-size: 0.875rem; color: #6b7280; background: #f3f4f6; padding: 0.25rem 0.75rem; border-radius: 999px; }

.stages-list { display: flex; flex-direction: column; gap: 1rem; }

.stage-item { display: flex; flex-direction: column; gap: 0.5rem; }
.stage-info { display: flex; justify-content: space-between; font-size: 0.95rem; }
.stage-name { color: #374151; font-weight: 500; }
.stage-qty { color: #667eea; font-weight: 700; }

.stage-bar { height: 8px; background: #f3f4f6; border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; background: #667eea; transition: width 0.3s ease; }

.empty { text-align: center; padding: 4rem; background: white; border-radius: 12px; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
