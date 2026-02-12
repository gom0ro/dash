<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <div class="header-left">
        <h1>{{ greeting }}</h1>
        <p class="subtitle">{{ roleDescription }}</p>
      </div>
      <div class="header-right" v-if="userStore.isAdmin">
        <div class="date-chip">{{ currentDate }}</div>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка аналитики...</p>
    </div>

    <div v-else class="dashboard-content">
      <!-- Admin/Manager Quick Actions -->
      <div v-if="userStore.isAdmin || userStore.isManager" class="quick-actions-bar">
        <AppButton @click="openTaskModal" variant="primary">
          <i class="ri-edit-2-line btn-icon"></i> Дать поручение
        </AppButton>
        <AppButton v-if="userStore.isManager" variant="outline" @click="$router.push('/manager/orders/create')">
          <i class="ri-add-line btn-icon"></i> Новый заказ
        </AppButton>
      </div>

      <!-- ADMIN DASHBOARD -->
      <div v-if="userStore.isAdmin" class="admin-section">
        <!-- Stats Cards Grid -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e0f2fe; color: #0369a1;"><i class="ri-box-3-line"></i></div>
            <div class="stat-main">
              <div class="stat-label">Заказы (общ)</div>
              <div class="stat-value">{{ stats.totalOrders }}</div>
              <div class="stat-sub">{{ stats.pendingOrders }} в ожидании</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: #fef3c7; color: #92400e;"><i class="ri-time-line"></i></div>
            <div class="stat-main">
              <div class="stat-label">В работе</div>
              <div class="stat-value">{{ stats.inProgressOrders }}</div>
              <div class="stat-sub">{{ stats.doneOrders }} сделано</div>
            </div>
          </div>
          <div class="stat-card" :class="{ 'alert-card': stats.overdueOrders > 0 }">
            <div class="stat-icon" style="background: #fee2e2; color: #991b1b;"><i class="ri-error-warning-line"></i></div>
            <div class="stat-main">
              <div class="stat-label">Просрочено</div>
              <div class="stat-value">{{ stats.overdueOrders }}</div>
              <div class="stat-sub urgent">Требуют внимания!</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: #dcfce7; color: #166534;"><i class="ri-money-dollar-circle-line"></i></div>
            <div class="stat-main">
              <div class="stat-label">Касса</div>
              <div class="stat-value">{{ formatMoney(stats.cash) }}</div>
              <div class="stat-sub positive">Продаж: {{ formatMoney(stats.sales) }}</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: #ede9fe; color: #5b21b6;"><i class="ri-hotel-line"></i></div>
            <div class="stat-main">
              <div class="stat-label">Склад</div>
              <div class="stat-value">{{ stats.totalProducts }}</div>
              <div class="stat-sub" :class="{ warning: stats.lowStock > 0 }">
                {{ stats.lowStock }} тов. заканчивается
              </div>
            </div>
          </div>
        </div>

        <!-- CHARTS SECTION -->
        <div class="charts-section">
          <div class="chart-card main-chart">
            <div class="chart-header">
              <h3>Динамика продаж (30 дней)</h3>
              <div class="chart-legend">Общий доход за период</div>
            </div>
            <div class="chart-container">
              <Line v-if="chartData.sales" :data="chartData.sales" :options="chartOptions.line" />
            </div>
          </div>

          <div class="charts-side">
            <div class="chart-card">
              <h3>Топ товаров (шт)</h3>
              <div class="chart-container-sm">
                <Doughnut v-if="chartData.products" :data="chartData.products" :options="chartOptions.doughnut" />
              </div>
            </div>
            <div class="chart-card">
              <h3>Производительность (логи)</h3>
              <div class="chart-container-sm">
                <Bar v-if="chartData.workers" :data="chartData.workers" :options="chartOptions.bar" />
              </div>
            </div>
          </div>
        </div>

        <div class="dashboard-tables">
          <div class="table-card">
            <div class="card-title">Последние заказы</div>
            <div class="simple-list">
              <div v-for="order in recentOrders" :key="order.id" class="list-item">
                <div class="item-info">
                  <span class="id">#{{ order.id }}</span>
                  <span class="name">{{ getProductName(order.product_id) }}</span>
                </div>
                <StatusBadge :status="order.status" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- MANAGER DASHBOARD -->
      <div v-else-if="userStore.isManager" class="manager-section">
         <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e0f2fe; color: #0369a1;"><i class="ri-file-list-3-line"></i></div>
            <div class="stat-main">
              <div class="stat-label">Активные заказы</div>
              <div class="stat-value">{{ stats.activeOrders }}</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: #fee2e2; color: #991b1b;"><i class="ri-error-warning-line"></i></div>
            <div class="stat-main">
              <div class="stat-label">Просрочено</div>
              <div class="stat-value">{{ stats.overdueOrders }}</div>
            </div>
          </div>
        </div>
        
        <div class="card" style="margin-top: 2rem;">
          <div class="card-header"><h3>Срочные заказы</h3></div>
          <div class="card-body">
            <div v-for="order in urgentOrders" :key="order.id" class="list-item border">
              <div class="info">
                <strong>#{{ order.id }}</strong> - {{ getProductName(order.product_id) }}
                <div class="date">Дедлайн: {{ formatDate(order.deadline) }}</div>
              </div>
              <StatusBadge :status="order.status" />
            </div>
          </div>
        </div>
      </div>

      <!-- WORKER DASHBOARD -->
      <div v-else-if="userStore.isWorker" class="worker-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon" style="background: #dcfce7; color: #166534;"><i class="ri-medal-line"></i></div>
            <div class="stat-main">
              <div class="stat-label">Начислено всего</div>
              <div class="stat-value">{{ formatMoney(salary.total_earned) }}</div>
              <div class="stat-sub warning">Не выплачено: {{ formatMoney(salary.total_unpaid) }}</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background: #e0f2fe; color: #0369a1;"><i class="ri-tools-line"></i></div>
            <div class="stat-main">
              <div class="stat-label">План на сегодня</div>
              <div class="stat-value">{{ todayOrders.length }}</div>
            </div>
          </div>
        </div>

        <div class="worker-actions">
           <AppButton @click="$router.push('/employee/tasks')"><i class="ri-factory-line btn-icon"></i> Перейти к задачам</AppButton>
           <AppButton variant="outline" @click="$router.push('/employee/salary')"><i class="ri-wallet-3-line btn-icon"></i> Моя зарплата</AppButton>
        </div>
      </div>

      <!-- WHOLESALER CRM DASHBOARD -->
      <div v-else-if="userStore.isWholesaler" class="wholesaler-section">
        <div class="welcome-box">
          <div class="box-content">
            <h2>Добро пожаловать в кабинет партнёра!</h2>
            <p>Здесь вы можете отслеживать статус ваших заказов и заказывать новые партии товара по оптовым ценам.</p>
            <AppButton @click="$router.push('/wholesaler/catalog')" size="lg">Перейти к каталогу <i class="ri-arrow-right-line"></i></AppButton>
          </div>
          <div class="box-stats">
            <div class="mini-stat">
              <div class="num">{{ stats.myOrders }}</div>
              <div class="lab">Всего заказов</div>
            </div>
            <div class="mini-stat">
              <div class="num">{{ stats.pendingOrders }}</div>
              <div class="lab">В обработке</div>
            </div>
          </div>
        </div>

        <div class="wholesaler-grid">
           <div class="card">
             <div class="card-header"><h3>Мои последние заказы</h3></div>
             <div class="card-body">
                <div v-if="myOrders.length === 0" class="empty">У вас пока нет заказов</div>
                <div v-for="order in myOrders" :key="order.id" class="order-strip">
                   <div class="strip-id">#{{ order.id }}</div>
                   <div class="strip-product">{{ getProductName(order.product_id) }}</div>
                   <div class="strip-qty">{{ order.quantity }} шт.</div>
                   <StatusBadge :status="order.status" />
                </div>
                <div class="strip-footer">
                   <router-link to="/wholesaler/my-orders" class="link">Все заказы →</router-link>
                </div>
             </div>
           </div>
        </div>
      </div>
    </div>

    <!-- Task Modal -->
    <AppModal v-model="showTaskModal" title="Новое поручение">
       <div class="form-group">
          <label>Заголовок</label>
          <input v-model="taskForm.title" class="input" placeholder="Напр: Срочная упаковка">
       </div>
       <div class="form-group">
          <label>Сотрудник</label>
          <select v-model="taskForm.worker_id" class="select">
             <option v-for="w in workers" :key="w.id" :value="w.id">{{ w.full_name }}</option>
          </select>
       </div>
       <template #footer>
          <AppButton @click="handleCreateTask" :loading="submittingTask">Назначить</AppButton>
       </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useOrdersStore } from '@/stores/orders'
import { useWarehouseStore } from '@/stores/warehouse'
import { reportsAPI, workLogsAPI, tasksAPI, usersAPI } from '@/api'
import AppButton from '@/components/UI/AppButton.vue'
import AppModal from '@/components/UI/AppModal.vue'
import StatusBadge from '@/components/UI/StatusBadge.vue'

// Charts
import { Line, Doughnut, Bar } from 'vue-chartjs'
import { 
  Chart as ChartJS, 
  Title, Tooltip, Legend, 
  LineElement, LinearScale, PointElement, CategoryScale,
  ArcElement, BarElement
} from 'chart.js'

ChartJS.register(
  Title, Tooltip, Legend, 
  LineElement, LinearScale, PointElement, CategoryScale,
  ArcElement, BarElement
)

const userStore = useUserStore()
const ordersStore = useOrdersStore()
const warehouseStore = useWarehouseStore()

const loading = ref(true)
const cashReport = ref(null)
const salary = ref({ total_earned: 0, total_paid: 0, total_unpaid: 0 })
const dashboardStats = ref(null)

const showTaskModal = ref(false)
const submittingTask = ref(false)
const workers = ref([])
const taskForm = ref({ title: '', worker_id: '' })

// Charts Data
const chartData = ref({ sales: null, products: null, workers: null })
const chartOptions = {
  line: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } }
  },
  doughnut: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'bottom' } }
  },
  bar: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } }
  }
}

const greeting = computed(() => {
  const h = new Date().getHours()
  const name = userStore.user?.full_name?.split(' ')[0] || 'Пользователь'
  if (h < 12) return `Доброе утро, ${name}!`
  if (h < 18) return `Добрый день, ${name}!`
  return `Добрый вечер, ${name}!`
})

const roleDescription = computed(() => {
  const map = { admin: 'Управление производством и бизнесом', manager: 'Контроль заказов и клиентов', worker: 'Задачи и выработка', wholesaler: 'Личный кабинет партнёра' }
  return map[userStore.user?.role] || ''
})

const currentDate = computed(() => new Date().toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' }))

const formatMoney = (v) => new Intl.NumberFormat('ru-RU').format(v || 0) + ' ₸'
const formatDate = (d) => new Date(d).toLocaleDateString('ru-RU')
const getProductName = (id) => warehouseStore.getProductById(id)?.name || '...'

const stats = computed(() => ({
  totalOrders: ordersStore.orders.length,
  pendingOrders: ordersStore.pendingOrders.length,
  inProgressOrders: ordersStore.inProgressOrders.length,
  doneOrders: ordersStore.doneOrders.length,
  totalProducts: warehouseStore.products.length,
  lowStock: warehouseStore.lowStockProducts.length,
  cash: cashReport.value?.cash_balance || 0,
  sales: cashReport.value?.sales || 0,
  activeOrders: ordersStore.orders.filter(o => o.status !== 'delivered').length,
  overdueOrders: ordersStore.overdueOrders.length,
  myOrders: ordersStore.orders.filter(o => o.wholesaler_id === userStore.user?.id).length
}))

const recentOrders = computed(() => ordersStore.orders.slice(0, 8))
const urgentOrders = computed(() => ordersStore.orders.filter(o => o.status !== 'delivered').slice(0, 5))
const todayOrders = computed(() => ordersStore.todayOrders)
const myOrders = computed(() => ordersStore.orders.filter(o => o.wholesaler_id === userStore.user?.id).slice(0, 10))

const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([
      ordersStore.fetchOrders(),
      warehouseStore.fetchProducts()
    ])

    if (userStore.isAdmin) {
      const [cash, dStats] = await Promise.all([
        reportsAPI.getCashReport(),
        reportsAPI.getDashboardStats()
      ])
      cashReport.value = cash.data
      dashboardStats.value = dStats.data
      initCharts(dStats.data)
    }

    if (userStore.isWorker) {
      const { data } = await workLogsAPI.getMySalary()
      salary.value = data
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const initCharts = (data) => {
  chartData.value.sales = {
    labels: data.daily_sales.map(s => s.date),
    datasets: [{
      label: 'Продажи',
      data: data.daily_sales.map(s => s.amount),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 2
    }]
  }

  chartData.value.products = {
    labels: data.top_products.map(p => p.name),
    datasets: [{
      data: data.top_products.map(p => p.value),
      backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    }]
  }

  chartData.value.workers = {
    labels: data.worker_performance.map(w => w.name),
    datasets: [{
      data: data.worker_performance.map(w => w.value),
      backgroundColor: '#6366f1'
    }]
  }
}

const openTaskModal = async () => {
  showTaskModal.value = true
  if (workers.value.length === 0) {
    const { data } = await usersAPI.getAll()
    workers.value = data.filter(u => u.role === 'worker')
  }
}

const handleCreateTask = async () => {
  submittingTask.value = true
  try {
    await tasksAPI.create(taskForm.value)
    showTaskModal.value = false
    alert('Готово!')
  } catch (e) {
    alert('Ошибка')
  } finally {
    submittingTask.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.dashboard { padding: 2rem; max-width: 1400px; margin: 0 auto; background: #f8fafc; min-height: 100vh; }
.dashboard-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; }
.dashboard-header h1 { font-size: 2.25rem; font-weight: 800; color: #1e293b; margin: 0; letter-spacing: -0.025em; }
.subtitle { color: #64748b; font-size: 1.1rem; margin-top: 0.25rem; }
.date-chip { background: white; padding: 0.5rem 1rem; border-radius: 99px; font-weight: 600; color: #475569; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

.quick-actions-bar { display: flex; gap: 1rem; margin-bottom: 2rem; }
.btn-icon { margin-right: 0.5rem; font-size: 1.1rem; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
.stat-card { background: white; padding: 1.5rem; border-radius: 16px; display: flex; gap: 1.25rem; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; }
.stat-icon { width: 3.5rem; height: 3.5rem; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0; }
.stat-label { color: #64748b; font-size: 0.875rem; font-weight: 600; }
.stat-value { font-size: 1.875rem; font-weight: 800; color: #1e293b; margin: 0.1rem 0; }
.stat-sub { font-size: 0.8rem; color: #94a3b8; font-weight: 500; }
.stat-sub.positive { color: #10b981; }
.stat-sub.warning { color: #f59e0b; }

.charts-section { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; margin-bottom: 2.5rem; }
.chart-card { background: white; padding: 1.5rem; border-radius: 16px; border: 1px solid #f1f5f9; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.chart-card h3 { font-size: 1.1rem; font-weight: 700; color: #1e293b; margin: 0 0 1.25rem; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.chart-legend { font-size: 0.85rem; color: #64748b; }
.chart-container { height: 320px; position: relative; }
.chart-container-sm { height: 230px; position: relative; }
.charts-side { display: flex; flex-direction: column; gap: 1.5rem; }

.dashboard-tables { display: grid; grid-template-columns: 1fr; }
.table-card { background: white; padding: 1.5rem; border-radius: 16px; border: 1px solid #f1f5f9; }
.card-title { font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-bottom: 1rem; }
.simple-list { display: flex; flex-direction: column; }
.list-item { display: flex; justify-content: space-between; align-items: center; padding: 0.85rem 0; border-bottom: 1px solid #f1f5f9; }
.list-item:last-child { border-bottom: none; }
.item-info .id { font-weight: 700; color: #3b82f6; margin-right: 0.75rem; }
.item-info .name { font-weight: 500; color: #334155; }

/* Wholesaler Specific */
.welcome-box { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; padding: 2.5rem; border-radius: 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.box-content { max-width: 60%; }
.box-content h2 { font-size: 1.875rem; margin: 0 0 1rem; font-weight: 800; }
.box-content p { font-size: 1.1rem; opacity: 0.9; margin-bottom: 1.5rem; color: #cbd5e1; }
.box-stats { display: flex; gap: 2rem; }
.mini-stat { text-align: center; background: rgba(255,255,255,0.1); padding: 1.5rem 2rem; border-radius: 16px; backdrop-filter: blur(4px); }
.mini-stat .num { font-size: 2rem; font-weight: 800; color: white; }
.mini-stat .lab { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }
.order-strip { display: flex; align-items: center; padding: 1rem; background: white; border-radius: 12px; margin-bottom: 0.75rem; border: 1px solid #f1f5f9; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.strip-id { font-weight: 800; color: #3b82f6; width: 60px; }
.strip-product { flex: 1; font-weight: 600; color: #1e293b; }
.strip-qty { margin-right: 2rem; color: #64748b; font-weight: 500; }
.strip-footer { text-align: right; margin-top: 1rem; }

.worker-actions { display: flex; gap: 1rem; margin: 2rem 0; }

.loading { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 50vh; }
.spinner { width: 3rem; height: 3rem; border: 4px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1200px) {
  .charts-section { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .dashboard-header { flex-direction: column; }
  .welcome-box { flex-direction: column; align-items: flex-start; gap: 2rem; }
  .box-content { max-width: 100%; }
}
.stat-sub.urgent { color: #dc2626; font-weight: 700; }

.stat-card.alert-card {
  border: 2px solid #fee2e2;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { border-color: #fee2e2; }
  50% { border-color: #dc2626; }
}
</style>