<template>
  <div class="order-create fade-in">
    <div class="page-header">
      <div class="header-content">
        <h1>Создание заказа</h1>
        <p class="subtitle">Оформление нового заказа (розница или опт)</p>
      </div>
      <AppButton variant="secondary" @click="router.back()">
        <i class="ri-arrow-left-line"></i> Назад
      </AppButton>
    </div>

    <div class="form-layout">
      <div class="form-main">
        <form @submit.prevent="handleSubmit">
          <!-- Products Section -->
          <div class="form-card">
            <div class="card-header">
              <h3><i class="ri-shopping-bag-line"></i> Состав заказа</h3>
              <AppButton type="button" size="sm" variant="outline" @click="addItem">
                <i class="ri-add-line"></i> Добавить товар
              </AppButton>
            </div>
            
            <div class="items-list">
              <div v-for="(item, index) in form.items" :key="index" class="item-row">
                <div class="item-qty">
                  <label v-if="index === 0">Кол-во</label>
                  <input v-model.number="item.quantity" type="number" min="1" class="modern-input" required />
                </div>
                <div class="item-product">
                  <label v-if="index === 0">Товар</label>
                  <select v-model="item.product_id" class="modern-select" required @change="updateRecommendedPrice">
                    <option value="" disabled>Выберите товар</option>
                    <option v-for="p in warehouseStore.products" :key="p.id" :value="p.id">
                      {{ p.name }} ({{ formatPrice(p.price) }})
                    </option>
                  </select>
                </div>
                <div class="item-remove">
                  <button v-if="form.items.length > 1" type="button" class="remove-btn" @click="removeItem(index)">
                    <i class="ri-delete-bin-line"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Client Section -->
          <div class="form-card">
            <div class="card-header">
              <h3><i class="ri-user-smile-line"></i> Данные клиента</h3>
              <div class="wholesaler-toggle" v-if="userStore.isAdmin">
                  <input type="checkbox" id="w-check" v-model="isWholesalerOrder" @change="handleWholesalerToggle" />
                  <label for="w-check">Оптовый заказ</label>
              </div>
            </div>
            
            <div v-if="isWholesalerOrder" class="form-group w-full mb-4">
                <label>Выберите оптовика</label>
                <select v-model="form.wholesaler_id" class="modern-select" @change="fillWholesalerData">
                    <option value="" disabled>Список оптовиков</option>
                    <option v-for="w in wholesalers" :key="w.id" :value="w.id">{{ w.full_name }}</option>
                </select>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>Имя клиента</label>
                <input v-model="form.customer_name" type="text" class="modern-input" placeholder="Введите имя" required />
              </div>
              <div class="form-group">
                <label>Телефон</label>
                <input v-model="form.customer_phone" type="text" class="modern-input" placeholder="+7..." />
              </div>
              <div class="form-group full">
                <label>Адрес доставки</label>
                <input v-model="form.customer_address" type="text" class="modern-input" placeholder="Город, улица, дом..." />
              </div>
            </div>
          </div>

          <!-- Finance & Deadline -->
          <div class="form-card">
            <div class="card-header">
              <h3><i class="ri-money-dollar-circle-line"></i> Условия и оплата</h3>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Дедлайн</label>
                <input v-model="form.deadline" type="datetime-local" class="modern-input" required />
              </div>
              <div class="form-group">
                <label>Способ оплаты</label>
                <select v-model="form.payment_method" class="modern-select">
                  <option value="cash">Наличные</option>
                  <option value="card">Карта / Kaspi</option>
                  <option value="transfer">Перевод</option>
                </select>
              </div>
              <div class="form-group">
                <label>Общая сумма (₸)</label>
                <input v-model.number="form.total_price" type="number" class="modern-input price-input" />
                <span class="hint">Рекомендовано: {{ formatPrice(calcRecommendedPrice) }}</span>
              </div>
              <div class="form-group">
                <label>Предоплата (₸)</label>
                <input v-model.number="form.prepayment" type="number" class="modern-input" />
              </div>
            </div>
          </div>

          <div v-if="error" class="error-shelf">{{ error }}</div>

          <div class="form-actions">
            <AppButton type="submit" :loading="submitting" size="lg" class="submit-btn" :disabled="!isFormValid">
              Создать и запустить в производство
            </AppButton>
          </div>
        </form>
      </div>

      <div class="summary-sidebar">
          <div class="summary-card">
              <h3>Сводка</h3>
              <div class="summary-items">
                  <div v-for="(item, i) in form.items" :key="i" class="summary-line">
                      <span v-if="item.product_id" class="s-name">
                          {{ i + 1 }}. {{ getProductName(item.product_id) }} x {{ item.quantity }}
                      </span>
                      <span v-if="item.product_id" class="s-price">
                          {{ formatPrice(getProductPrice(item.product_id) * item.quantity) }}
                      </span>
                  </div>
              </div>
              <div class="summary-total">
                  <span>К оплате:</span>
                  <span class="total-big">{{ formatPrice(form.total_price) }}</span>
              </div>
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

const submitting = ref(false)
const error = ref('')
const isWholesalerOrder = ref(false)
const wholesalers = ref([])

const form = ref({
  items: [
    { product_id: '', quantity: 1 }
  ],
  deadline: '',
  wholesaler_id: null,
  customer_name: '',
  customer_phone: '',
  customer_address: '',
  total_price: 0,
  prepayment: 0,
  payment_method: 'cash'
})

const calcRecommendedPrice = computed(() => {
    return form.value.items.reduce((sum, item) => {
        const prod = warehouseStore.getProductById(item.product_id)
        return sum + (prod ? prod.price * item.quantity : 0)
    }, 0)
})

const getProductName = (id) => warehouseStore.getProductById(id)?.name || '—'
const getProductPrice = (id) => warehouseStore.getProductById(id)?.price || 0
const formatPrice = (v) => new Intl.NumberFormat('ru-RU').format(v || 0) + ' ₸'

const isFormValid = computed(() => {
    return form.value.items.every(i => i.product_id && i.quantity > 0) && form.value.deadline && form.value.customer_name
})

const addItem = () => {
    form.value.items.push({ product_id: '', quantity: 1 })
}

const removeItem = (index) => {
    form.value.items.splice(index, 1)
}

const updateRecommendedPrice = () => {
    form.value.total_price = calcRecommendedPrice.value
}

const handleWholesalerToggle = async () => {
    if (isWholesalerOrder.value && wholesalers.value.length === 0) {
        const { data } = await usersAPI.getAll()
        wholesalers.value = data.filter(u => u.role === 'wholesaler')
    }
    if (!isWholesalerOrder.value) {
        form.value.wholesaler_id = null
    }
}

const fillWholesalerData = () => {
    const w = wholesalers.value.find(u => u.id === form.value.wholesaler_id)
    if (w) {
        form.value.customer_name = w.full_name
        form.value.customer_phone = w.phone || ''
        form.value.customer_address = w.address || ''
    }
}

const handleSubmit = async () => {
  error.value = ''
  submitting.value = true
  try {
    const payload = { ...form.value }
    if (!isWholesalerOrder.value) payload.wholesaler_id = null
    
    await ordersStore.createOrder(payload)
    router.push('/manager/orders')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка создания заказа'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await warehouseStore.fetchProducts()
  
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 2)
  tomorrow.setHours(18, 0, 0, 0)
  form.value.deadline = tomorrow.toISOString().slice(0, 16)
})

watch(calcRecommendedPrice, (newVal) => {
    form.value.total_price = newVal
})
</script>

<style scoped>
.order-create { padding: 1.5rem; max-width: 1400px; margin: 0 auto; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.5rem; }
.header-content h1 { font-size: 2.2rem; font-weight: 900; color: #1e293b; margin: 0; letter-spacing: -0.04em; }
.subtitle { color: #64748b; font-size: 1.1rem; font-weight: 500; }

.form-layout { display: grid; grid-template-columns: 1fr 350px; gap: 2rem; }

.form-card { background: white; border-radius: 24px; padding: 2rem; border: 1.5px solid #f1f5f9; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.02); margin-bottom: 2rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; border-bottom: 1.5px solid #f8fafc; padding-bottom: 1rem; }
.card-header h3 { font-size: 1.25rem; font-weight: 800; color: #1e293b; display: flex; align-items: center; gap: 10px; margin: 0; }
.card-header i { color: #3b82f6; }

.items-list { display: flex; flex-direction: column; gap: 1rem; }
.item-row { display: flex; gap: 1rem; align-items: flex-end; animation: slideIn 0.3s ease; }
.item-qty { width: 100px; }
.item-product { flex: 1; }
.remove-btn { height: 48px; width: 48px; border-radius: 12px; border: none; background: #fee2e2; color: #ef4444; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
.remove-btn:hover { background: #ef4444; color: white; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group.full { grid-column: span 2; }
.form-group label { font-size: 0.85rem; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }

.modern-input, .modern-select { width: 100%; padding: 0.85rem 1rem; border: 2.1px solid #f1f5f9; background: #f8fafc; border-radius: 14px; font-size: 1rem; font-weight: 600; outline: none; transition: all 0.2s; }
.modern-input:focus, .modern-select:focus { border-color: #3b82f6; background: white; }
.price-input { font-size: 1.5rem; color: #3b82f6; font-weight: 900; }

.hint { font-size: 0.8rem; color: #94a3b8; font-weight: 600; }
.error-shelf { padding: 1rem; background: #fee2e2; color: #b91c1c; border-radius: 14px; margin-bottom: 1.5rem; font-weight: 700; text-align: center; }

.wholesaler-toggle { display: flex; align-items: center; gap: 8px; font-weight: 800; color: #3b82f6; cursor: pointer; }
.wholesaler-toggle input { width: 18px; height: 18px; cursor: pointer; }

.form-actions { display: flex; justify-content: center; margin-top: 2rem; }
.submit-btn { padding: 1.25rem 3rem; font-weight: 900; font-size: 1.1rem; border-radius: 18px; width: 100%; box-shadow: 0 15px 30px rgba(59, 130, 246, 0.3); }

.summary-sidebar { position: sticky; top: 2rem; height: fit-content; }
.summary-card { background: #1e293b; color: white; border-radius: 24px; padding: 2rem; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.summary-card h3 { font-size: 1.5rem; font-weight: 900; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1rem; }
.summary-items { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem; }
.summary-line { display: flex; justify-content: space-between; gap: 1rem; font-size: 0.9rem; }
.s-name { opacity: 0.8; font-weight: 600; }
.s-price { font-weight: 800; color: #60a5fa; }
.summary-total { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1.5rem; display: flex; flex-direction: column; gap: 5px; }
.summary-total span:first-child { font-size: 0.9rem; opacity: 0.6; font-weight: 800; text-transform: uppercase; }
.total-big { font-size: 2.2rem; font-weight: 900; color: #fff; }

@keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1024px) {
    .form-layout { grid-template-columns: 1fr; }
    .summary-sidebar { position: static; }
}

@media (max-width: 768px) {
    .item-row { flex-direction: column; align-items: stretch; gap: 0.5rem; background: #f8fafc; padding: 1rem; border-radius: 16px; position: relative; }
    .item-qty { width: 100%; }
    .remove-btn { position: absolute; top: 0.5rem; right: 0.5rem; height: 32px; width: 32px; }
    .form-grid { grid-template-columns: 1fr; }
    .submit-btn { padding: 1rem; }
}
@media (max-width: 375px) {
    .order-create { padding: 0.75rem; }
    .header-content h1 { font-size: 1.75rem; }
    .form-card { padding: 1.25rem; }
}
</style>