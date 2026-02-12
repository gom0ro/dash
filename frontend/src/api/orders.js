import api from './index'

export const ordersAPI = {
    // Get all orders (with filters)
    getOrders(params = { skip: 0, limit: 100 }) {
        return api.get('/orders/', { params })
    },

    // Get single order by ID
    getOrder(id) {
        return api.get(`/orders/${id}`)
    },

    // Create new order
    createOrder(data) {
        return api.post('/orders/', data)
    },

    // Update order (status or details)
    updateOrder(id, data) {
        return api.put(`/orders/${id}`, data)
    },

    // Update order status (specific endpoint if exists, else use updateOrder)
    updateStatus(id, status) {
        return api.patch(`/orders/${id}/status`, { status })
    },

    // Get my orders (for wholesaler)
    getMyOrders() {
        return api.get('/orders/my')
    },

    deleteOrder(id) {
        return api.delete(`/orders/${id}`)
    },

    getById(id) {
        return this.getOrder(id)
    }
}
