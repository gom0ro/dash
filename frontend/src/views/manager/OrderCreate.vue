<template>
  <div class="order-create">
    <div class="page-header">
      <div>
        <h1>Создание заказа</h1>
        <p class="subtitle">Заполните форму для создания нового заказа</p>
      </div>
    </div>

    <div class="form-container">
      <form @submit.prevent="handleSubmit">
        <div class="form-section">
          <h3>Основная информация</h3>

          <div class="form-group">
            <label class="label">
              Товар <span class="required">*</span>
            </label>
            <select
              v-model="form.product_id"
              class="select"
              required
              :disabled="loadingProducts"
            >
              <option value="">Выберите товар</option>
              <option
                v-for="product in availableProducts"
                :key="product.id"
                :value="product.id"
              >
                {{ product.name }} (остаток: {{ product.stock }} шт.)
              </option>
            </select>
            <span v-if="selectedProduct" class="hint">
              Цена: {{ selectedProduct.price }} тг | 
              Себестоимость: {{ selectedProduct.cost }} тг
            </span>
          </div>

          <div class="form-group">
            <label for="quantity" class="label">
              Количество <span class="required">*</span>
            </label>
            <input
              id="quantity"
              v-model.number="form.quantity"
              type="number"
              min="1"
              class="input"
              placeholder="Введите количество"
              required
            />
            <span v-if="selectedProduct && form.quantity" class="hint">
              Стоимость: {{ totalPrice }} тг
            </span>
          </div>

          <div class="form-group">
            <label for="deadline" class="label">
              Дедлайн <span class="required">*</span>
            </label>
            <input
              id="deadline"
              v-model="form.deadline"
              type="datetime-local"
              class="input"
              :min="minDeadline"
              required
            />
          </div>
        </div>

        <div class="form-section">
          <h3>Данные клиента</h3>
          <div class="form-grid">
            <div class="form-group">
              <label class="label">Имя клиента</label>
              <input v-model="form.customer_name" type="text" class="input" placeholder="ФИО клиента" />
            </div>
            <div class="form-group">
              <label class="label">Телефон</label>
              <input v-model="form.customer_phone" type="text" class="input" placeholder="+7 (___) ___ __ __" />
            </div>
          </div>
          <div class="form-group">
            <label class="label">Адрес доставки</label>
            <input v-model="form.customer_address" type="text" class="input" placeholder="Город, улица, дом..." />
          </div>
        </div>

        <div class="form-section">
          <h3>Финансы</h3>
          <div class="form-grid">
            <div class="form-group">
              <label class="label">Сумма заказа (₸)</label>
              <input v-model.number="form.total_price" type="number" class="input" />
              <span class="hint">Рекомендуемая: {{ totalPriceRecommendation }} ₸</span>
            </div>
            <div class="form-group">
              <label class="label">Предоплата (₸)</label>
              <input v-model.number="form.prepayment" type="number" class="input" />
            </div>
            <div class="form-group">
              <label class="label">Способ оплаты</label>
              <select v-model="form.payment_method" class="select">
                <option value="cash">Наличные</option>
                <option value="card">Карта / Kaspi</option>
                <option value="transfer">Безналичный расчет</option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="userStore.isAdmin" class="form-section">
          <h3>Оптовый заказ</h3>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="isWholesalerOrder"
                type="checkbox"
                class="checkbox"
              />
              Это заказ от зарегистрированного оптовика
            </label>
          </div>

          <div v-if="isWholesalerOrder" class="form-group">
            <label for="wholesaler" class="label">
              Выберите оптовика
            </label>
            <select
              id="wholesaler"
              v-model="form.wholesaler_id"
              class="select"
            >
              <option value="">Выберите оптовика</option>
              <option
                v-for="wholesaler in wholesalers"
                :key="wholesaler.id"
                :value="wholesaler.id"
              >
                {{ wholesaler.full_name }} ({{ wholesaler.username }})
              </option>
            </select>
          </div>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="form-actions">
          <AppButton
            type="button"
            variant="secondary"
            @click="handleCancel"
            :disabled="submitting"
          >
            Отмена
          </AppButton>
          <AppButton
            type="submit"
            :loading="submitting"
          >
            Создать заказ
          </AppButton>
        </div>
      </form>

      <div v-if="selectedProduct" class="order-summary">
        <h3>Сводка заказа</h3>
        <div class="summary-item">
          <span>Товар:</span>
          <strong>{{ selectedProduct.name }}</strong>
        </div>
        <div class="summary-item">
          <span>Количество:</span>
          <strong>{{ form.quantity || 0 }} шт.</strong>
        </div>
        <div class="summary-item">
          <span>Дедлайн:</span>
          <strong>{{ formatDeadline }}</strong>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-item total">
          <span>Итого:</span>
          <strong>{{ totalPrice }} тг</strong>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import { useWarehouseStore } from '@/stores/warehouse'
import { useUserStore } from '@/stores/user'
import { usersAPI } from '@/api'
import AppButton from '@/components/UI/AppButton.vue'

const router = useRouter()
const ordersStore = useOrdersStore()
const warehouseStore = useWarehouseStore()
const userStore = useUserStore()

const loadingProducts = ref(false)
const submitting = ref(false)
const error = ref('')
const isWholesalerOrder = ref(false)
const wholesalers = ref([])

const form = ref({
  product_id: '',
  quantity: 1,
  deadline: '',
  wholesaler_id: null,
  customer_name: '',
  customer_phone: '',
  customer_address: '',
  total_price: 0,
  prepayment: 0,
  payment_method: 'cash'
})

const totalPriceRecommendation = computed(() => {
  if (!selectedProduct.value || !form.value.quantity) return 0
  return selectedProduct.value.price * form.value.quantity
})

const availableProducts = computed(() => {
  return warehouseStore.products.filter(p => p.stock > 0)
})

const selectedProduct = computed(() => {
  if (!form.value.product_id) return null
  return warehouseStore.getProductById(form.value.product_id)
})

const totalPrice = computed(() => {
  if (!selectedProduct.value || !form.value.quantity) return 0
  return (selectedProduct.value.price * form.value.quantity).toFixed(2)
})

const minDeadline = computed(() => {
  const now = new Date()
  now.setHours(now.getHours() + 1)
  return now.toISOString().slice(0, 16)
})

const formatDeadline = computed(() => {
  if (!form.value.deadline) return '—'
  return new Date(form.value.deadline).toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const loadWholesalers = async () => {
  try {
    const { data } = await usersAPI.getAll()
    wholesalers.value = data.filter(u => u.role === 'wholesaler')
  } catch (err) {
    console.error('Ошибка загрузки оптовиков:', err)
  }
}

const handleSubmit = async () => {
  error.value = ''

  if (!form.value.product_id) {
    error.value = 'Выберите товар'
    return
  }

  if (form.value.quantity < 1) {
    error.value = 'Количество должно быть больше 0'
    return
  }

  if (!form.value.deadline) {
    error.value = 'Укажите дедлайн'
    return
  }

  const deadline = new Date(form.value.deadline)
  if (deadline < new Date()) {
    error.value = 'Дедлайн не может быть в прошлом'
    return
  }

  try {
    submitting.value = true

    const orderData = {
      product_id: form.value.product_id,
      quantity: form.value.quantity,
      deadline: form.value.deadline,
      wholesaler_id: isWholesalerOrder.value ? form.value.wholesaler_id : null,
      customer_name: form.value.customer_name,
      customer_phone: form.value.customer_phone,
      customer_address: form.value.customer_address,
      total_price: form.value.total_price || totalPriceRecommendation.value,
      prepayment: form.value.prepayment,
      payment_method: form.value.payment_method
    }

    await ordersStore.createOrder(orderData)

    router.push('/manager/orders')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка создания заказа'
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  if (confirm('Отменить создание заказа?')) {
    router.back()
  }
}

onMounted(async () => {
  loadingProducts.value = true
  try {
    await warehouseStore.fetchProducts()
    if (userStore.isAdmin) {
      await loadWholesalers()
    }

    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(12, 0, 0, 0)
    form.value.deadline = tomorrow.toISOString().slice(0, 16)
    
    // Watch for product change to update recommended price
    watch(() => form.value.product_id, (newId) => {
      if (newId) {
        setTimeout(() => {
           form.value.total_price = totalPriceRecommendation.value
        }, 100)
      }
    })
    watch(() => form.value.quantity, () => {
       form.value.total_price = totalPriceRecommendation.value
    })

    // Watch for wholesaler selection to auto-fill data
    watch(() => form.value.wholesaler_id, (newId) => {
      if (newId && isWholesalerOrder.value) {
        const selectedWholesaler = wholesalers.value.find(w => w.id === newId)
        if (selectedWholesaler) {
          form.value.customer_name = selectedWholesaler.full_name
          form.value.customer_phone = selectedWholesaler.phone || ''
          form.value.customer_address = selectedWholesaler.address || ''
        }
      }
    })
  } catch (err) {
    error.value = 'Ошибка загрузки данных'
  } finally {
    loadingProducts.value = false
  }
})
</script>

<style scoped>
.order-create {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
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

.form-container {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 2rem;
}

form {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2rem;
}

.form-section:last-of-type {
  margin-bottom: 0;
}

.form-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1.5rem;
  color: #111827;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
  display: inline-block;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
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
.select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.input:focus,
.select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input:disabled,
.select:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

.hint {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9375rem;
  color: #374151;
}

.checkbox {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.error-message {
  padding: 1rem;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.9375rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.order-summary {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  height: fit-content;
  position: sticky;
  top: 2rem;
}

.order-summary h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1.5rem;
  color: #111827;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.summary-item span {
  color: #6b7280;
  font-size: 0.9375rem;
}

.summary-item strong {
  color: #111827;
  font-size: 0.9375rem;
}

.summary-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 1rem 0;
}

.summary-item.total {
  padding-top: 1rem;
}

.summary-item.total span,
.summary-item.total strong {
  font-size: 1.125rem;
  font-weight: 600;
}

.summary-item.total strong {
  color: #667eea;
}

@media (max-width: 1024px) {
  .form-container {
    grid-template-columns: 1fr;
  }

  .order-summary {
    position: static;
  }
}

@media (max-width: 768px) {
  .order-create {
    padding: 1rem;
  }

  form,
  .order-summary {
    padding: 1.5rem;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .form-actions button {
    width: 100%;
  }
}
</style>