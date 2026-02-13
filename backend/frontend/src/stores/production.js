import { defineStore } from 'pinia'
import { ref } from 'vue'
import { productionAPI } from '@/api/production'

export const useProductionStore = defineStore('production', () => {
    const products = ref([])
    const tasks = ref([])
    const loading = ref(false)
    const error = ref(null)

    async function fetchProducts() {
        loading.value = true
        try {
            const { data } = await productionAPI.getProducts()
            products.value = data
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    async function fetchMyTasks() {
        loading.value = true
        try {
            const { data } = await productionAPI.getMyTasks()
            tasks.value = data
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    async function startStage(orderId, stageId) {
        try {
            await productionAPI.startStage(orderId, stageId)
            await fetchMyTasks()
        } catch (err) {
            throw err
        }
    }

    async function completeStage(workLogId) {
        try {
            await productionAPI.completeStage(workLogId)
            await fetchMyTasks() // Refresh tasks
        } catch (err) {
            throw err
        }
    }

    return {
        products,
        tasks,
        loading,
        error,
        fetchProducts,
        fetchMyTasks,
        startStage,
        completeStage
    }
})
