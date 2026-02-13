import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ordersAPI } from '@/api/orders'

export const useOrdersStore = defineStore('orders', () => {
    const orders = ref([])
    const currentOrder = ref(null)
    const loading = ref(false)
    const error = ref(null)

    const pendingOrders = computed(() => orders.value.filter(o => o.status === 'pending'))
    const acceptedOrders = computed(() => orders.value.filter(o => o.status === 'accepted'))
    const inProgressOrders = computed(() => orders.value.filter(o => o.status === 'in_progress'))
    const doneOrders = computed(() => orders.value.filter(o => o.status === 'done'))
    const deliveredOrders = computed(() => orders.value.filter(o => o.status === 'delivered'))

    const overdueOrders = computed(() => {
        const now = new Date()
        return orders.value.filter(o =>
            o.status !== 'delivered' &&
            new Date(o.deadline) < now
        )
    })

    const todayOrders = computed(() => {
        const today = new Date().toISOString().split('T')[0]
        return orders.value.filter(o => o.deadline.startsWith(today))
    })

    async function fetchOrders(params) {
        loading.value = true
        error.value = null
        try {
            const { data } = await ordersAPI.getOrders(params)
            orders.value = Array.isArray(data) ? data : (data.items || [])
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to fetch orders'
            console.error(err)
        } finally {
            loading.value = false
        }
    }

    async function fetchOrder(id) {
        loading.value = true
        try {
            const { data } = await ordersAPI.getOrder(id)
            currentOrder.value = data
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to fetch order'
        } finally {
            loading.value = false
        }
    }

    async function createOrder(orderData) {
        loading.value = true
        try {
            const { data } = await ordersAPI.createOrder(orderData)
            orders.value.unshift(data)
            return data
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to create order'
            throw err
        } finally {
            loading.value = false
        }
    }

    async function updateOrderStatus(id, status) {
        try {
            await ordersAPI.updateStatus(id, status)
            const order = orders.value.find(o => o.id === id)
            if (order) order.status = status
        } catch (err) {
            console.error(err)
            throw err
        }
    }

    async function deleteOrder(id) {
        try {
            await ordersAPI.deleteOrder(id)
            orders.value = orders.value.filter(o => o.id !== id)
        } catch (err) {
            console.error(err)
            throw err
        }
    }

    return {
        orders,
        currentOrder,
        loading,
        error,
        pendingOrders,
        acceptedOrders,
        inProgressOrders,
        doneOrders,
        deliveredOrders,
        overdueOrders,
        todayOrders,
        fetchOrders,
        fetchOrder,
        createOrder,
        updateOrderStatus,
        deleteOrder
    }
})
