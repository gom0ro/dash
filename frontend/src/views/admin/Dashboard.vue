<template>
  <div class="dashboard fade-in">
    <header class="dashboard-header">
      <div class="header-main">
        <h1>{{ greeting }}</h1>
        <p class="subtitle">{{ roleDescription }}</p>
      </div>
      <div class="header-meta">
        <div class="time-pill">
            <i class="ri-calendar-event-line"></i>
            <span>{{ currentDate }}</span>
        </div>
      </div>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Сбор аналитики...</p>
    </div>

    <div v-else class="dashboard-content">
      <!-- Admin / Manager Quick Controls -->
      <div v-if="userStore.isAdmin || userStore.isManager" class="action-grid">
        <button class="control-btn primary" @click="openTaskModal">
            <div class="btn-icon"><i class="ri-edit-2-fill"></i></div>
            <div class="btn-text">
                <span class="t-main">Дать поручение</span>
                <span class="t-sub">Сотруднику на сегодня</span>
            </div>
        </button>
        <button v-if="userStore.isManager" class="control-btn outline" @click="$router.push('/manager/orders/create')">
            <div class="btn-icon"><i class="ri-add-circle-fill"></i></div>
            <div class="btn-text">
                <span class="t-main">Создать заказ</span>
                <span class="t-sub">Опт или розница</span>
            </div>
        </button>
      </div>

      <!-- ADMIN VIEW -->
      <div v-if="userStore.isAdmin" class="view-section">
        <!-- Main Stats Strip -->
        <div class="stats-ribbon">
          <div class="glass-stat">
            <div class="g-icon orders"><i class="ri-shopping-cart-2-line"></i></div>
            <div class="g-data">
              <span class="g-label">Заказы (общ)</span>
              <span class="g-value">{{ stats.totalOrders }}</span>
              <span class="g-sub">{{ stats.pendingOrders }} новых</span>
            </div>
          </div>
          <div class="glass-stat">
            <div class="g-icon work"><i class="ri-hammer-line"></i></div>
            <div class="g-data">
              <span class="g-label">В производстве</span>
              <span class="g-value">{{ stats.inProgressOrders }}</span>
              <span class="g-sub">{{ stats.doneOrders }} завершено</span>
            </div>
          </div>
          <div class="glass-stat" :class="{ 'warning-pulse': stats.overdueOrders > 0 }">
            <div class="g-icon alert"><i class="ri-alarm-warning-line"></i></div>
            <div class="g-data">
              <span class="g-label">Просрочено</span>
              <span class="g-value">{{ stats.overdueOrders }}</span>
              <span class="g-sub urgent">Срочно!</span>
            </div>
          </div>
          <div class="glass-stat highlight">
            <div class="g-icon cash"><i class="ri-wallet-3-line"></i></div>
            <div class="g-data">
              <span class="g-label">Остаток в кассе</span>
              <span class="g-value">{{ formatMoney(stats.cash) }}</span>
              <span class="g-sub sales">Продаж: {{ formatMoney(stats.sales) }}</span>
            </div>
          </div>
        </div>

        <!-- Analytics Visuals -->
        <div class="analytics-layout">
          <div class="main-chart-card panel">
            <div class="panel-header">
                <h3>Динамика выручки</h3>
                <span class="period-label">Последние 30 дней</span>
            </div>
            <div class="chart-box">
              <Line v-if="chartData.sales" :data="chartData.sales" :options="chartOptions.line" />
            </div>
          </div>

          <div class="side-charts">
            <div class="panel half">
              <h3>Топ товаров</h3>
              <div class="chart-box-sm">
                <Doughnut v-if="chartData.products" :data="chartData.products" :options="chartOptions.doughnut" />
              </div>
            </div>
            <div class="panel half">
              <h3>Производительность</h3>
              <div class="chart-box-sm">
                <Bar v-if="chartData.workers" :data="chartData.workers" :options="chartOptions.bar" />
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="activity-section">
            <div class="panel">
                <div class="panel-header">
                    <h3>Последние заказы</h3>
                    <button class="link-btn" @click="$router.push('/manager/orders')">Все заказы <i class="ri-arrow-right-s-line"></i></button>
                </div>
                <div class="orders-list-simple">
                  <div v-for="order in recentOrders" :key="order.id" class="simple-order-row" @click="$router.push(`/manager/orders/${order.id}`)">
                    <div class="order-id-track">
                        <span class="id">#{{ order.id }}</span>
                        <span class="p-name">{{ getProductName(order.product_id) }}</span>
                    </div>
                    <StatusBadge :status="order.status" />
                  </div>
                </div>
            </div>
        </div>
      </div>

      <!-- MANAGER VIEW -->
      <div v-else-if="userStore.isManager" class="view-section">
         <div class="stats-ribbon">
          <div class="glass-stat">
            <div class="g-icon orders"><i class="ri-file-list-3-line"></i></div>
            <div class="g-data">
              <span class="g-label">Активные заказы</span>
              <span class="g-value">{{ stats.activeOrders }}</span>
            </div>
          </div>
          <div class="glass-stat warning-pulse">
            <div class="g-icon alert"><i class="ri-error-warning-line"></i></div>
            <div class="g-data">
              <span class="g-label">Просрочено</span>
              <span class="g-value">{{ stats.overdueOrders }}</span>
            </div>
          </div>
        </div>
        
        <div class="panel mt-gap">
          <div class="panel-header"><h3>Срочные задачи</h3></div>
          <div class="urgent-orders-list">
            <div v-for="order in urgentOrders" :key="order.id" class="urgent-item">
              <div class="u-info">
                <span class="u-title">#{{ order.id }} • {{ getProductName(order.product_id) }}</span>
                <span class="u-date" :class="{ 'danger': isOverdue(order) }">Дедлайн: {{ formatDate(order.deadline) }}</span>
              </div>
              <StatusBadge :status="order.status" />
            </div>
          </div>
        </div>
      </div>

      <!-- WORKER VIEW -->
      <div v-else-if="userStore.isWorker" class="view-section">
        <div class="worker-welcome">
            <div class="w-card income">
                <div class="w-icon"><i class="ri-medal-fill"></i></div>
                <div class="w-data">
                    <span class="w-lbl">Вы заработали</span>
                    <span class="w-val">{{ formatMoney(salary.total_earned) }}</span>
                    <span class="w-sub" v-if="salary.total_unpaid > 0">К выплате: {{ formatMoney(salary.total_unpaid) }}</span>
                </div>
            </div>
            <div class="w-card work">
                <div class="w-icon"><i class="ri-flashlight-fill"></i></div>
                <div class="w-data">
                    <span class="w-lbl">Задач на сегодня</span>
                    <span class="w-val">{{ todayOrders.length }}</span>
                </div>
            </div>
        </div>

        <div class="worker-nav">
           <button class="nav-tile" @click="$router.push('/employee/tasks')">
               <i class="ri-factory-line"></i>
               <span>Задачи в цеху</span>
           </button>
           <button class="nav-tile secondary" @click="$router.push('/employee/salary')">
               <i class="ri-money-tenge-box-line"></i>
               <span>Моя выработка</span>
           </button>
        </div>
      </div>

      <!-- WHOLESALER VIEW -->
      <div v-else-if="userStore.isWholesaler" class="view-section">
        <div class="partner-hero">
          <div class="hero-content">
            <h2>Добро пожаловать, партнёр!</h2>
            <p>Управляйте своими оптовыми заказами и следите за статусом поставок в реальном времени.</p>
            <AppButton variant="primary" size="lg" @click="$router.push('/wholesaler/catalog')">
                Перейти в каталог <i class="ri-arrow-right-line"></i>
            </AppButton>
          </div>
          <div class="partner-stats">
              <div class="p-stat">
                  <span class="val">{{ stats.myOrders }}</span>
                  <span class="lbl">Заказов всего</span>
              </div>
              <div class="p-stat">
                  <span class="val">{{ stats.pendingOrders }}</span>
                  <span class="lbl">В обработке</span>
              </div>
          </div>
        </div>

        <div class="panel mt-gap">
            <div class="panel-header">
                <h3>Активные заказы</h3>
                <button class="link-btn" @click="$router.push('/wholesaler/my-orders')">История →</button>
            </div>
            <div class="order-strips-container">
                <div v-if="myOrders.length === 0" class="empty-notif">У вас пока нет активных заказов</div>
                <div v-for="order in myOrders" :key="order.id" class="order-strip">
                   <div class="s-id">#{{ order.id }}</div>
                   <div class="s-product">{{ getProductName(order.product_id) }}</div>
                   <div class="s-qty">{{ order.quantity }} шт.</div>
                   <StatusBadge :status="order.status" />
                </div>
            </div>
        </div>
      </div>
    </div>

    <!-- Task Modal -->
    <AppModal v-model="showTaskModal" title="Создать поручение">
       <div class="modern-form">
          <div class="f-group">
             <label>Опишите задачу</label>
             <input v-model="taskForm.title" class="modern-input" placeholder="Напр: Срочная упаковка товара">
          </div>
          <div class="f-group">
             <label>Исполнитель</label>
             <select v-model="taskForm.worker_id" class="modern-select">
                <option value="" disabled>Выберите сотрудника</option>
                <option v-for="w in workers" :key="w.id" :value="w.id">{{ w.full_name }}</option>
             </select>
          </div>
       </div>
       <template #footer>
          <AppButton @click="handleCreateTask" :loading="submittingTask" variant="primary" class="full-btn">Назначить задачу</AppButton>
       </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
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
  Chart as ChartJS, Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale, ArcElement, BarElement, Filler 
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale, ArcElement, BarElement, Filler)

const router = useRouter()
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
    scales: { 
        y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { font: { weight: '600' } } },
        x: { grid: { display: false } }
    }
  },
  doughnut: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, padding: 20, font: { weight: '600' } } } },
    cutout: '70%'
  },
  bar: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { 
        y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
        x: { grid: { display: false } }
    }
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
  const map = { admin: 'Панель управления бизнесом', manager: 'Операционный контроль', worker: 'Мой рабочий цех', wholesaler: 'Кабинет оптовика' }
  return map[userStore.user?.role] || ''
})

const currentDate = computed(() => {
    return new Date().toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', weekday: 'long' })
})

const formatMoney = (v) => new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(v || 0) + ' ₸'
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

const isOverdue = (order) => {
  if (order.status === 'delivered') return false
  return new Date(order.deadline) < new Date()
}

const recentOrders = computed(() => ordersStore.orders.filter(o => o.status !== 'delivered').sort((a,b) => b.id - a.id).slice(0, 8))
const urgentOrders = computed(() => ordersStore.orders.filter(o => o.status !== 'delivered').sort((a,b) => new Date(a.deadline) - new Date(b.deadline)).slice(0, 5))
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
    labels: data.daily_sales.map(s => s.date.split('-').slice(1).reverse().join('.')),
    datasets: [{
      label: 'Продажи',
      data: data.daily_sales.map(s => s.amount),
      borderColor: '#3b82f6',
      backgroundColor: (context) => {
          const bg = context.chart.ctx.createLinearGradient(0, 0, 0, 400);
          bg.addColorStop(0, 'rgba(59, 130, 246, 0.2)');
          bg.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
          return bg;
      },
      fill: true,
      tension: 0.45,
      pointRadius: 4,
      pointBackgroundColor: '#fff',
      pointBorderWidth: 2,
      borderWidth: 4
    }]
  }

  chartData.value.products = {
    labels: data.top_products.map(p => p.name),
    datasets: [{
      data: data.top_products.map(p => p.value),
      backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'],
      hoverOffset: 10,
      borderWidth: 0
    }]
  }

  chartData.value.workers = {
    labels: data.worker_performance.map(w => w.name.split(' ')[0]),
    datasets: [{
      data: data.worker_performance.map(w => w.value),
      backgroundColor: '#6366f1',
      borderRadius: 8,
      barThickness: 30
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
  if (!taskForm.value.title || !taskForm.value.worker_id) return
  submittingTask.value = true
  try {
    await tasksAPI.create(taskForm.value)
    showTaskModal.value = false
    taskForm.value = { title: '', worker_id: '' }
    alert('Поручение создано!')
  } catch (e) {
    alert('Ошибка при создании')
  } finally {
    submittingTask.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.dashboard { padding: 1.5rem; max-width: 1400px; margin: 0 auto; overflow-x: hidden; }
.dashboard-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2.5rem; gap: 1rem; }
.dashboard-header h1 { font-size: 2.5rem; font-weight: 900; color: #1e293b; margin: 0; letter-spacing: -0.02em; line-height: 1.2; }
.subtitle { color: #64748b; font-size: 1.1rem; font-weight: 500; margin-top: 0.25rem; }
.time-pill { background: white; padding: 0.6rem 1.25rem; border-radius: 14px; display: flex; align-items: center; gap: 0.75rem; color: #475569; font-weight: 700; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; }
.time-pill i { color: #3b82f6; font-size: 1.2rem; }

.action-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem; }
.control-btn { display: flex; align-items: center; gap: 1.25rem; padding: 1.25rem; border-radius: 20px; border: none; cursor: pointer; transition: all 0.2s; text-align: left; }
.control-btn.primary { background: #3b82f6; color: white; box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.25); }
.control-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 15px 20px -5px rgba(59, 130, 246, 0.3); }
.control-btn.outline { background: white; border: 2px solid #f1f5f9; color: #1e293b; }
.control-btn.outline:hover { border-color: #3b82f6; background: #eff6ff; }

.btn-icon { width: 50px; height: 50px; border-radius: 14px; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
.control-btn.outline .btn-icon { background: #f1f5f9; color: #3b82f6; }
.btn-text { display: flex; flex-direction: column; }
.t-main { font-weight: 800; font-size: 1.1rem; }
.t-sub { font-size: 0.85rem; opacity: 0.8; font-weight: 500; }

/* Stats Ribbon */
.stats-ribbon { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem; }
.glass-stat { background: white; padding: 1.5rem; border-radius: 24px; display: flex; align-items: center; gap: 1.25rem; border: 1px solid #f1f5f9; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.02); }
.g-icon { width: 60px; height: 60px; border-radius: 18px; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; flex-shrink: 0; }
.g-icon.orders { background: #e0f2fe; color: #0369a1; }
.g-icon.work { background: #fef3c7; color: #92400e; }
.g-icon.alert { background: #fee2e2; color: #b91c1c; }
.g-icon.cash { background: #dcfce7; color: #15803d; }

.g-data { display: flex; flex-direction: column; }
.g-label { font-size: 0.8rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
.g-value { font-size: 1.8rem; font-weight: 900; color: #1e293b; line-height: 1; margin: 4px 0; }
.g-sub { font-size: 0.85rem; color: #64748b; font-weight: 600; }
.g-sub.urgent { color: #ef4444; }
.glass-stat.highlight { background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border-color: #3b82f6; border-width: 1.5px; }

.warning-pulse { animation: shadowPulse 2s infinite; border-color: #fecaca; }
@keyframes shadowPulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.1); } 50% { box-shadow: 0 0 20px 5px rgba(239, 68, 68, 0.15); } }

/* Analytics Panel */
.analytics-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; margin-bottom: 2.5rem; min-width: 0; }
.panel { background: white; border-radius: 26px; border: 1px solid #f1f5f9; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.02); padding: 2rem; min-width: 0; }
.panel-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; gap: 0.5rem; }
.panel-header h3 { font-size: 1.25rem; font-weight: 800; color: #1e293b; margin: 0; }
.period-label { font-size: 0.85rem; font-weight: 700; color: #3b82f6; background: #eff6ff; padding: 4px 12px; border-radius: 8px; }

.chart-box { height: 350px; position: relative; }
.chart-box-sm { height: 260px; position: relative; }
.side-charts { display: flex; flex-direction: column; gap: 1.5rem; }
.panel.half { padding: 1.5rem; flex: 1; }

/* Orders List */
.orders-list-simple { display: flex; flex-direction: column; gap: 0.75rem; }
.simple-order-row { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.25rem; background: #f8fafc; border-radius: 16px; border: 1.5px solid transparent; cursor: pointer; transition: all 0.2s; }
.simple-order-row:hover { background: white; border-color: #3b82f6; transform: translateX(8px); }
.order-id-track { display: flex; align-items: center; gap: 1rem; }
.order-id-track .id { font-weight: 900; color: #3b82f6; font-size: 1rem; }
.order-id-track .p-name { font-weight: 700; color: #1e293b; font-size: 1rem; }

/* Worker Cards */
.worker-welcome { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }
.w-card { padding: 2.5rem; border-radius: 28px; display: flex; align-items: center; gap: 2rem; color: white; }
.w-card.income { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); }
.w-card.work { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
.w-icon { font-size: 3.5rem; opacity: 0.3; }
.w-data { display: flex; flex-direction: column; }
.w-lbl { font-size: 0.9rem; font-weight: 700; opacity: 0.8; text-transform: uppercase; letter-spacing: 0.1em; }
.w-val { font-size: 2.8rem; font-weight: 900; line-height: 1; margin: 10px 0; }
.w-sub { font-size: 1.1rem; font-weight: 600; opacity: 0.9; }

.worker-nav { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.nav-tile { padding: 2.5rem; border-radius: 24px; border: none; background: white; display: flex; flex-direction: column; align-items: center; gap: 1rem; cursor: pointer; border: 2px solid #f1f5f9; transition: all 0.2s; }
.nav-tile i { font-size: 3rem; color: #3b82f6; }
.nav-tile span { font-size: 1.25rem; font-weight: 800; color: #1e293b; }
.nav-tile:hover { border-color: #3b82f6; transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05); }

/* Partner Hero */
.partner-hero { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 28px; padding: 3.5rem; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.5rem; }
.hero-content { max-width: 60%; }
.hero-content h2 { font-size: 2.5rem; font-weight: 900; margin: 0 0 1rem; }
.hero-content p { font-size: 1.25rem; opacity: 0.8; margin-bottom: 2rem; line-height: 1.6; }
.partner-stats { display: flex; gap: 2rem; }
.p-stat { background: rgba(255,255,255,0.08); padding: 1.5rem 2.5rem; border-radius: 20px; backdrop-filter: blur(10px); text-align: center; }
.p-stat .val { font-size: 2.5rem; font-weight: 900; display: block; }
.p-stat .lbl { font-size: 0.8rem; opacity: 0.7; font-weight: 800; text-transform: uppercase; }

.order-strip { display: flex; align-items: center; padding: 1.25rem; background: #f8fafc; border-radius: 18px; border: 1px solid #f1f5f9; margin-bottom: 0.75rem; }
.s-id { font-weight: 900; color: #3b82f6; width: 70px; }
.s-product { flex: 1; font-weight: 800; color: #1e293b; font-size: 1.1rem; }
.s-qty { margin-right: 2rem; font-weight: 600; color: #64748b; }

.link-btn { background: none; border: none; font-weight: 800; color: #3b82f6; cursor: pointer; display: flex; align-items: center; gap: 4px; }

/* Form Elements */
.modern-form { display: flex; flex-direction: column; gap: 1.5rem; padding: 0.5rem 0; }
.f-group label { display: block; font-weight: 800; color: #1e293b; margin-bottom: 0.75rem; font-size: 0.9rem; text-transform: uppercase; }
.modern-input, .modern-select { width: 100%; padding: 1rem; border: 2px solid #f1f5f9; background: #f8fafc; border-radius: 14px; font-size: 1rem; font-weight: 600; outline: none; transition: all 0.2s; }
.modern-input:focus, .modern-select:focus { border-color: #3b82f6; background: white; }
.full-btn { padding: 1rem; font-weight: 800; width: 100%; border-radius: 14px; }

.loading-state { height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.spinner { width: 4rem; height: 4rem; border: 5px solid #f1f5f9; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1.5rem; }

@keyframes spin { to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1200px) {
    .analytics-layout { grid-template-columns: 1fr; }
    .side-charts { flex-direction: row; }
}

@media (max-width: 768px) {
    .dashboard { padding: 0.75rem; }
    .dashboard-header { flex-direction: column; gap: 1rem; }
    .dashboard-header h1 { font-size: 1.8rem; }
    .stats-ribbon { grid-template-columns: 1fr; gap: 1rem; }
    .glass-stat { padding: 1.25rem; }
    .worker-welcome, .worker-nav { grid-template-columns: 1fr; gap: 1rem; }
    .w-card { padding: 1.5rem; gap: 1rem; }
    .w-val { font-size: 2.2rem; }
    .side-charts { flex-direction: column; }
    .partner-hero { flex-direction: column; padding: 2rem 1.5rem; gap: 2rem; text-align: center; }
    .partner-hero .hero-content { max-width: 100%; }
    .hero-content h2 { font-size: 1.8rem; }
    .p-stat { padding: 1rem; }
    .panel { padding: 1.25rem; }
    .action-grid { gap: 1rem; }
    .chart-box { height: 280px; }
}

@media (max-width: 480px) {
    .dashboard { padding: 0.5rem; }
    .panel { padding: 1rem; border-radius: 18px; }
    .chart-box { height: 220px; }
    .chart-box-sm { height: 200px; }
    .g-value { font-size: 1.5rem; }
}

.mt-gap { margin-top: 2.5rem; }
.u-info { display: flex; flex-direction: column; }
.u-title { font-weight: 800; color: #1e293b; }
.u-date { font-size: 0.85rem; color: #64748b; font-weight: 600; }
.u-date.danger { color: #ef4444; }
.urgent-item { display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: #f8fafc; border-radius: 14px; margin-bottom: 0.75rem; }
</style>