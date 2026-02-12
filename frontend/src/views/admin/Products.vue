<template>
  <div class="products-view">
    <div class="page-header">
      <div>
        <h1>Управление товарами</h1>
        <p class="subtitle">Создание продукции, настройка этапов и запуск в производство</p>
      </div>
      <AppButton 
        v-if="userStore.canManageProducts" 
        @click="openCreateModal"
      >
        + Добавить товар
      </AppButton>
    </div>

    <div class="filters-bar">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск товаров..."
          class="search-input"
        />
      </div>
      <div class="filter-buttons">
        <button
          :class="['filter-btn', { active: stockFilter === 'all' }]"
          @click="stockFilter = 'all'"
        >
          Все ({{ warehouseStore.products.length }})
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка товаров...</p>
    </div>

    <div v-else-if="filteredProducts.length === 0" class="empty">
      <div class="empty-icon"><i class="ri-archive-line"></i></div>
      <h3>Товаров не найдено</h3>
      <p v-if="searchQuery">Попробуйте изменить поисковый запрос</p>
      <AppButton v-else @click="openCreateModal">
        Добавить первый товар
      </AppButton>
    </div>

    <div v-else class="products-grid">
      <div
        v-for="product in filteredProducts"
        :key="product.id"
        class="product-card"
      >
        <div class="product-header">
          <h3>{{ product.name }}</h3>
          <div class="stock-badge ok">
            На складе: {{ product.stock }} шт.
          </div>
        </div>

        <div class="product-body">
          <p class="product-description">{{ product.description || 'Без описания' }}</p>

          <div class="product-pricing">
            <div class="price-item">
              <span class="price-label">Цена продажи:</span>
              <span class="price-value">{{ formatMoney(product.price) }}</span>
            </div>
            <div class="price-item">
              <span class="price-label">Себестоимость:</span>
              <span class="price-value">{{ formatMoney(product.cost) }}</span>
            </div>
          </div>

          <div v-if="product.stages && product.stages.length" class="stages-info">
            <div class="stages-header">
              <span>Этапов производства:</span>
              <strong>{{ product.stages.length }}</strong>
            </div>
            <div class="stages-summary">
              Стоимость работы: {{ formatMoney(getTotalStagesCost(product.stages)) }}
            </div>
          </div>
        </div>

        <div class="product-actions">
          <div class="actions-row">
            <button
              class="action-btn"
              @click="openStockModal(product)"
            >
              <i class="ri-bar-chart-box-line"></i> Остаток
            </button>
            <button
              class="action-btn produce"
              @click="openProduceModal(product)"
            >
              <i class="ri-hammer-line"></i> В работу
            </button>
          </div>
          <div class="actions-row">
            <button
              v-if="userStore.canManageProducts"
              class="action-btn edit"
              @click="openEditModal(product)"
            >
              <i class="ri-edit-line"></i> Изменить
            </button>
            <button
              v-if="userStore.canManageProducts"
              class="action-btn delete"
              @click="confirmDelete(product)"
            >
              <i class="ri-delete-bin-line"></i> Удалить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка создания/редактирования товара -->
    <AppModal
      v-model="showProductModal"
      :title="editingProduct ? 'Редактирование товара' : 'Новый товар'"
      size="lg"
    >
      <form @submit.prevent="handleSaveProduct">
        <div class="form-grid">
          <div class="form-group">
            <label class="label">Название <span class="required">*</span></label>
            <input
              v-model="productForm.name"
              type="text"
              class="input"
              placeholder="Название товара"
              required
            />
          </div>

          <div class="form-group">
            <label class="label">Остаток <span class="required">*</span></label>
            <input
              v-model.number="productForm.stock"
              type="number"
              min="0"
              class="input"
              required
            />
          </div>

          <div class="form-group" v-if="!editingProduct">
            <label class="label">Запустить в производство (шт.)</label>
            <input
              v-model.number="productForm.to_produce"
              type="number"
              min="0"
              class="input"
              placeholder="Количество заготовок"
            />
          </div>

          <div class="form-group full-width">
            <label class="label">Описание</label>
            <textarea
              v-model="productForm.description"
              class="textarea"
              rows="3"
              placeholder="Описание товара"
            ></textarea>
          </div>

          <div class="form-group">
            <label class="label">Цена продажи <span class="required">*</span></label>
            <input
              v-model.number="productForm.price"
              type="number"
              min="0"
              step="0.01"
              class="input"
              placeholder="0.00"
              required
            />
          </div>

          <div class="form-group">
            <label class="label">Себестоимость <span class="required">*</span></label>
            <input
              v-model.number="productForm.cost"
              type="number"
              min="0"
              step="0.01"
              class="input"
              placeholder="0.00"
              required
            />
          </div>
        </div>

        <div class="stages-section">
          <div class="stages-header-row">
            <h4>Этапы производства</h4>
            <button type="button" class="btn-add-stage" @click="addStage">
              + Добавить этап
            </button>
          </div>

          <div v-if="productForm.stages.length === 0" class="no-stages-msg">
            Этапы производства не добавлены
          </div>

          <div v-else class="stages-list">
            <div
              v-for="(stage, index) in productForm.stages"
              :key="index"
              class="stage-row"
            >
              <div class="stage-number">{{ index + 1 }}</div>
              <input
                v-model="stage.name"
                type="text"
                class="input"
                placeholder="Название этапа"
                required
              />
              <input
                v-model.number="stage.payment"
                type="number"
                min="0"
                class="input"
                placeholder="Оплата"
                required
              />
              <button
                type="button"
                class="btn-remove-stage"
                @click="removeStage(index)"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

        <div v-if="productError" class="error-message">
          {{ productError }}
        </div>
      </form>

      <template #footer>
        <AppButton variant="secondary" @click="showProductModal = false">
          Отмена
        </AppButton>
        <AppButton :loading="saving" @click="handleSaveProduct">
          {{ editingProduct ? 'Сохранить' : 'Создать' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- Модалка изменения остатка -->
    <AppModal
      v-model="showStockModal"
      title="Изменить остаток"
      size="sm"
    >
      <div v-if="selectedProduct" class="stock-modal-content">
        <h4>{{ selectedProduct.name }}</h4>
        <p class="current-stock">Текущий остаток: <strong>{{ selectedProduct.stock }} шт.</strong></p>
        
        <div class="form-group">
          <label class="label">Новый остаток</label>
          <input
            v-model.number="newStock"
            type="number"
            min="0"
            class="input"
            placeholder="Введите количество"
          />
        </div>
      </div>

      <template #footer>
        <AppButton variant="secondary" @click="showStockModal = false">
          Отмена
        </AppButton>
        <AppButton :loading="updatingStock" @click="handleUpdateStock">
          Обновить
        </AppButton>
      </template>
    </AppModal>

    <!-- Модалка удаления -->
    <AppModal
      v-model="showDeleteModal"
      title="Удаление товара"
      size="sm"
    >
      <div class="delete-confirm-content">
        <p>Вы уверены, что хотите полностью удалить товар <strong>{{ productToDelete?.name }}</strong>?</p>
        <p class="warning">Это действие удалит всю историю, заказы и остатки этого товара. Его нельзя отменить.</p>
        
        <div class="captcha-box">
          <label class="label">Для подтверждения введите: <strong>Подтверждаю</strong></label>
          <input 
            v-model="deleteConfirmText" 
            type="text" 
            class="input" 
            placeholder="Введите слово..."
          />
        </div>
      </div>

      <template #footer>
        <AppButton variant="secondary" @click="showDeleteModal = false">
          Отмена
        </AppButton>
        <AppButton 
          variant="danger" 
          :loading="deleting" 
          :disabled="deleteConfirmText !== 'Подтверждаю'"
          @click="handleDelete"
        >
          Удалить навсегда
        </AppButton>
      </template>
    </AppModal>
    
    <!-- Модалка запуска в производство -->
    <AppModal
      v-model="showProduceModal"
      title="Запуск в производство"
      size="sm"
    >
      <div v-if="selectedProduct" class="produce-modal-content">
        <h4>{{ selectedProduct.name }}</h4>
        <p class="hint">Введите количество единиц для запуска (поступят на временный склад)</p>
        
        <div class="form-group" style="margin-top: 1rem;">
          <label class="label">Количество заготовок</label>
          <input
            v-model.number="produceQuantity"
            type="number"
            min="1"
            class="input"
            placeholder="Напр. 50"
          />
        </div>
      </div>

      <template #footer>
        <AppButton variant="secondary" @click="showProduceModal = false">
          Отмена
        </AppButton>
        <AppButton :loading="startingProduction" @click="handleLaunchProduction">
          Запустить
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWarehouseStore } from '@/stores/warehouse'
import { useUserStore } from '@/stores/user'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'

const warehouseStore = useWarehouseStore()
const userStore = useUserStore()

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const updatingStock = ref(false)

const searchQuery = ref('')
const stockFilter = ref('all')

const showProductModal = ref(false)
const showStockModal = ref(false)
const showDeleteModal = ref(false)
const showProduceModal = ref(false)

const startingProduction = ref(false)
const produceQuantity = ref(10)
const deleteConfirmText = ref('')

const editingProduct = ref(null)
const selectedProduct = ref(null)
const productToDelete = ref(null)
const productError = ref('')
const newStock = ref(0)

const productForm = ref({
  name: '',
  description: '',
  price: 0,
  cost: 0,
  stock: 0,
  to_produce: 0,
  stages: []
})

const filteredProducts = computed(() => {
  let products = warehouseStore.products

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    products = products.filter(p => 
      p.name.toLowerCase().includes(query) ||
      p.description?.toLowerCase().includes(query)
    )
  }

  return products
})

const formatMoney = (amount) => {
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(amount || 0) + ' тг'
}

const getTotalStagesCost = (stages) => {
  return stages.reduce((sum, stage) => sum + (stage.payment || 0), 0)
}

const resetForm = () => {
  productForm.value = {
    name: '',
    description: '',
    price: 0,
    cost: 0,
    stock: 0,
    to_produce: 0,
    stages: []
  }
  editingProduct.value = null
  productError.value = ''
}

const openCreateModal = () => {
  resetForm()
  showProductModal.value = true
}

const openEditModal = (product) => {
  editingProduct.value = product
  productForm.value = {
    name: product.name,
    description: product.description || '',
    price: product.price,
    cost: product.cost,
    stock: product.stock,
    to_produce: 0,
    stages: product.stages?.map(s => ({
      name: s.name,
      payment: s.payment,
      order_num: s.order_num
    })) || []
  }
  showProductModal.value = true
}

const openStockModal = (product) => {
  selectedProduct.value = product
  newStock.value = product.stock
  showStockModal.value = true
}

const confirmDelete = (product) => {
  productToDelete.value = product
  deleteConfirmText.value = ''
  showDeleteModal.value = true
}

const openProduceModal = (product) => {
  selectedProduct.value = product
  produceQuantity.value = 10
  showProduceModal.value = true
}

const handleLaunchProduction = async () => {
  if (produceQuantity.value < 1) return
  try {
    startingProduction.value = true
    await warehouseStore.launchProduction(selectedProduct.value.id, produceQuantity.value)
    showProduceModal.value = false
    alert('Товар успешно запущен в производство!')
  } catch (error) {
    alert('Ошибка запуска: ' + (error.response?.data?.detail || error.message))
  } finally {
    startingProduction.value = false
  }
}

const addStage = () => {
  productForm.value.stages.push({
    name: '',
    payment: 0,
    order_num: productForm.value.stages.length + 1
  })
}

const removeStage = (index) => {
  productForm.value.stages.splice(index, 1)
  productForm.value.stages.forEach((stage, idx) => {
    stage.order_num = idx + 1
  })
}

const handleSaveProduct = async () => {
  productError.value = ''

  if (!productForm.value.name.trim()) {
    productError.value = 'Введите название товара'
    return
  }

  if (productForm.value.price <= 0) {
    productError.value = 'Цена должна быть больше 0'
    return
  }

  if (productForm.value.cost < 0) {
    productError.value = 'Себестоимость не может быть отрицательной'
    return
  }

  try {
    saving.value = true

    if (editingProduct.value) {
      await warehouseStore.updateProduct(editingProduct.value.id, productForm.value)
    } else {
      await warehouseStore.createProduct(productForm.value)
    }

    showProductModal.value = false
    resetForm()
  } catch (error) {
    productError.value = error.response?.data?.detail || 'Ошибка сохранения товара'
  } finally {
    saving.value = false
  }
}

const handleUpdateStock = async () => {
  if (newStock.value < 0) {
    alert('Остаток не может быть отрицательным')
    return
  }

  try {
    updatingStock.value = true
    await warehouseStore.updateStock(selectedProduct.value.id, newStock.value)
    showStockModal.value = false
  } catch (error) {
    alert('Ошибка обновления остатка: ' + (error.response?.data?.detail || error.message))
  } finally {
    updatingStock.value = false
  }
}

const handleDelete = async () => {
  try {
    deleting.value = true
    await warehouseStore.deleteProduct(productToDelete.value.id)
    showDeleteModal.value = false
    productToDelete.value = null
  } catch (error) {
    alert('Ошибка удаления: ' + (error.response?.data?.detail || error.message))
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await warehouseStore.fetchProducts()
  } catch (error) {
    console.error('Ошибка загрузки:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.products-view {
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

.filters-bar {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-buttons {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  padding: 0.75rem 1.25rem;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9375rem;
  color: #6b7280;
  transition: all 0.2s;
  font-weight: 500;
}

.filter-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.filter-btn.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
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
  margin: 0 0 1.5rem;
  color: #6b7280;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.product-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.product-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.product-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: #111827;
  flex: 1;
}

.stock-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
}

.stock-badge.ok {
  background: #dcfce7;
  color: #065f46;
}

.product-body {
  padding: 1.5rem;
}

.product-description {
  color: #6b7280;
  font-size: 0.9375rem;
  margin: 0 0 1.5rem;
  line-height: 1.5;
}

.product-pricing {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.price-value {
  color: #111827;
  font-weight: 600;
  font-size: 0.9375rem;
}

.stages-info {
  padding: 1rem;
  background: #f3f4f6;
  border-radius: 8px;
}

.stages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.stages-header span {
  color: #6b7280;
  font-size: 0.875rem;
}

.stages-header strong {
  color: #111827;
}

.stages-summary {
  color: #667eea;
  font-size: 0.875rem;
  font-weight: 600;
}

.product-actions {
  padding: 1rem 1.5rem;
  border-top: 1px solid #f3f4f6;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: #fdfdfd;
}

.actions-row {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  flex: 1;
  padding: 0.75rem 0.5rem;
  background: #fff;
  border: 1.5px solid #edf2f7;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  color: #4a5568;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}

.action-btn:hover {
  background: #f8fafc;
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-1px);
}

.action-btn.produce:hover {
  border-color: #48bb78;
  color: #48bb78;
  background: #f0fff4;
}

.action-btn.edit:hover {
  border-color: #ecc94b;
  color: #b7791f;
  background: #fffff0;
}

.action-btn.delete:hover {
  border-color: #f56565;
  color: #c53030;
  background: #fff5f5;
}

.captcha-box {
  margin-top: 1.5rem;
  padding: 1.25rem;
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 12px;
}

.captcha-box .label {
  color: #c53030;
  margin-bottom: 0.75rem;
}

.captcha-box .input {
  border-color: #feb2b2;
}

.captcha-box .input:focus {
  border-color: #f56565;
  box-shadow: 0 0 0 3px rgba(245, 101, 101, 0.2);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.required {
  color: #e74c3c;
}

.input,
.textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.textarea {
  resize: vertical;
  font-family: inherit;
}

.input:focus,
.textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.stages-section {
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.stages-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stages-header-row h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.btn-add-stage {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-add-stage:hover {
  background: #5568d3;
}

.no-stages-msg {
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

.stage-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
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

.stage-row .input {
  flex: 1;
}

.stage-row .input:last-of-type {
  max-width: 150px;
}

.btn-remove-stage {
  width: 2rem;
  height: 2rem;
  background: #fee2e2;
  color: #991b1b;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  flex-shrink: 0;
  transition: all 0.2s;
}

.btn-remove-stage:hover {
  background: #fecaca;
}

.error-message {
  padding: 1rem;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 8px;
  font-size: 0.9375rem;
}

.stock-modal-content h4 {
  margin: 0 0 1rem;
  color: #111827;
}

.current-stock {
  margin: 0 0 1.5rem;
  color: #6b7280;
}

.current-stock strong {
  color: #111827;
}

.warning {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.hint {
  color: #6b7280;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.produce-modal-content h4 {
  margin: 0 0 0.5rem;
  color: #111827;
}

@media (max-width: 768px) {
  .products-view {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    gap: 1rem;
  }

  .filters-bar {
    flex-direction: column;
  }

  .products-grid {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .stage-row {
    flex-wrap: wrap;
  }

  .stage-row .input:last-of-type {
    max-width: none;
  }
}
</style>
