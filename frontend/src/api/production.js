import api from './index'

export const productionAPI = {
    // Get all available products
    getProducts() {
        return api.get('/products/')
    },

    // Get production stages for a product
    getStages(productId) {
        return api.get(`/products/${productId}/stages`)
    },

    createProduct(data) {
        return api.post('/products/', data)
    },

    updateProduct(id, data) {
        return api.patch(`/products/${id}`, data)
    },

    deleteProduct(id) {
        return api.delete(`/products/${id}`)
    },

    updateStock(id, quantity) {
        return api.patch(`/products/${id}/stock`, null, { params: { quantity } })
    },

    // Work Logs / Tasks
    getMyTasks() {
        return api.get('/production/tasks/my')
    },

    // Assign task/stage to self (or start working)
    startStage(orderId, stageId) {
        return api.post('/production/work-log', {
            order_id: orderId,
            stage_id: stageId,
            action: 'start'
        })
    },

    // Complete stage
    completeStage(workLogId) {
        return api.put(`/production/work-log/${workLogId}/complete`)
    },

    getWipInventory() {
        return api.get('/products/wip/inventory')
    },

    getWipTasks() {
        return api.get('/products/wip/tasks')
    },

    getWipPipeline() {
        return api.get('/products/wip/pipeline')
    },

    launchProduction(productId, quantity) {
        return api.post(`/products/${productId}/produce`, null, { params: { quantity } })
    }
}
