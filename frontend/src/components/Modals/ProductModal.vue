<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ editingProduct ? 'Редактировать продукт' : 'Создать продукт' }}</h2>
        <button @click="$emit('close')" class="close-btn">×</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="name">Название продукта *</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            required
            placeholder="Введите название"
          />
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="category">Категория *</label>
            <select id="category" v-model="form.category" required>
              <option value="">Выберите категорию</option>
              <option value="Электроника">Электроника</option>
              <option value="Мебель">Мебель</option>
              <option value="Одежда">Одежда</option>
              <option value="Книги">Книги</option>
              <option value="Продукты">Продукты</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="price">Цена (₽) *</label>
            <input
              id="price"
              v-model.number="form.price"
              type="number"
              min="0"
              step="0.01"
              required
              placeholder="0.00"
            />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="stock">Количество на складе *</label>
            <input
              id="stock"
              v-model.number="form.stock"
              type="number"
              min="0"
              required
              placeholder="0"
            />
          </div>
          
          <div class="form-group">
            <label for="sales">Продажи</label>
            <input
              id="sales"
              v-model.number="form.sales"
              type="number"
              min="0"
              placeholder="0"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="revenue">Доход (₽)</label>
          <input
            id="revenue"
            v-model.number="form.revenue"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
          />
        </div>
        
        <div class="modal-actions">
          <button type="button" @click="$emit('close')" class="btn-secondary">
            Отмена
          </button>
          <button type="submit" class="btn-primary">
            {{ editingProduct ? 'Сохранить' : 'Создать' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

interface Product {
  id?: number
  name: string
  category: string
  price: number
  stock: number
  sales: number
  revenue: number
}

const props = defineProps<{
  product: Product | null
}>()

const emit = defineEmits<{
  (e: 'save', product: Product): void
  (e: 'close'): void
}>()

const editingProduct = computed(() => !!props.product?.id)

const form = ref<Product>({
  name: '',
  category: '',
  price: 0,
  stock: 0,
  sales: 0,
  revenue: 0
})

watch(() => props.product, (newProduct) => {
  if (newProduct) {
    form.value = { ...newProduct }
  } else {
    resetForm()
  }
}, { immediate: true })

const resetForm = () => {
  form.value = {
    name: '',
    category: '',
    price: 0,
    stock: 0,
    sales: 0,
    revenue: 0
  }
}

const handleSubmit = () => {
  emit('save', { ...form.value })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
    margin: 0;
    font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #666;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

input, select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

input:focus, select:focus {
  outline: none;
  border-color: #3498db;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

.btn-secondary {
  background: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
  padding: 0.7rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary:hover {
  background: #e9ecef;
}

.btn-primary {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.7rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-primary:hover {
  background: #2980b9;
}
</style>
