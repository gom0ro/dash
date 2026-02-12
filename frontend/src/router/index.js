import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/views/auth/Login.vue'), meta: { public: true } },
  {
    path: '/admin',
    component: () => import('@/views/layouts/MainLayout.vue'),
    meta: { roles: ['admin'] },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'products', name: 'AdminProducts', component: () => import('@/views/admin/Products.vue') },
      { path: 'warehouse', name: 'AdminWarehouse', component: () => import('@/views/admin/WarehouseView.vue') },
      { path: 'staff', name: 'AdminStaff', component: () => import('@/views/admin/StaffManagement.vue') },
      { path: 'finance', name: 'AdminFinance', component: () => import('@/views/admin/Finance.vue') },
      { path: 'expenses', name: 'AdminExpenses', component: () => import('@/views/admin/Expenses.vue') },
      { path: 'reports', name: 'AdminReports', component: () => import('@/views/admin/Reports.vue') },
      { path: 'wip', name: 'WipWarehouse', component: () => import('@/views/admin/WipWarehouse.vue') },
      { path: 'salaries', name: 'AdminSalaries', component: () => import('@/views/admin/SalariesView.vue') },
    ]
  },
  {
    path: '/manager',
    component: () => import('@/views/layouts/MainLayout.vue'),
    meta: { roles: ['manager', 'admin'] },
    children: [
      { path: '', redirect: '/manager/orders' },
      { path: 'orders', name: 'ManagerOrders', component: () => import('@/views/manager/OrderList.vue') },
      { path: 'orders/create', name: 'OrderCreate', component: () => import('@/views/manager/OrderCreate.vue') },
      { path: 'orders/:id', name: 'OrderDetails', component: () => import('@/views/manager/OrderDetails.vue') },
    ]
  },
  {
    path: '/employee',
    component: () => import('@/views/layouts/MainLayout.vue'),
    meta: { roles: ['worker', 'admin'] },
    children: [
      { path: '', redirect: '/employee/tasks' },
      { path: 'tasks', name: 'WorkerTasks', component: () => import('@/views/employee/Tasks.vue') },
      { path: 'orders-today', name: 'OrdersToday', component: () => import('@/views/employee/OrdersToday.vue') },
      { path: 'salary', name: 'WorkerSalary', component: () => import('@/views/employee/Salary.vue') },
    ]
  },
  {
    path: '/wholesaler',
    component: () => import('@/views/layouts/MainLayout.vue'),
    meta: { roles: ['wholesaler', 'admin'] },
    children: [
      { path: '', redirect: '/wholesaler/catalog' },
      { path: 'catalog', name: 'WholesalerCatalog', component: () => import('@/views/wholesaler/Catalog.vue') },
      { path: 'my-orders', name: 'WholesalerOrders', component: () => import('@/views/wholesaler/MyOrders.vue') },
      { path: 'profile', name: 'WholesalerProfile', component: () => import('@/views/wholesaler/Profile.vue') },
    ]
  },
  {
    path: '/',
    redirect: '/login'
  },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFound.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guard
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.public) {
    if (userStore.isAuthenticated && userStore.user?.role) {
      next(userStore.roleHome[userStore.user.role])
    } else {
      next()
    }
    return
  }

  if (!userStore.isAuthenticated) {
    next('/login')
    return
  }

  if (to.path === '/') {
    const home = userStore.user?.role ? userStore.roleHome[userStore.user.role] : '/login'
    next(home || '/login')
    return
  }

  const allowedRoles = to.matched.flatMap(r => r.meta.roles || [])
  const userRole = userStore.user?.role
  if (allowedRoles.length && (!userRole || !allowedRoles.includes(userRole))) {
    const home = userRole ? userStore.roleHome[userRole] : '/login'
    next(home || '/login')
    return
  }

  next()
})

export default router
