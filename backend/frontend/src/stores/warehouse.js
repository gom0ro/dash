import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { productionAPI } from '@/api/production'

export const useWarehouseStore = defineStore('warehouse', () => {
    const products = ref([])
    const loading = ref(false)
    const error = ref(null)

    const lowStockProducts = computed(() => products.value.filter(p => p.stock > 0 && p.stock <= 10))
    const outOfStockProducts = computed(() => products.value.filter(p => p.stock === 0))

    async function fetchProducts() {
        loading.value = true
        error.value = null
        try {
            const { data } = await productionAPI.getProducts()
            products.value = data
        } catch (err) {
            error.value = err.response?.data?.detail || 'Failed to fetch products'
            console.error(err)
        } finally {
            loading.value = false
        }
    }

    async function createProduct(data) {
        const res = await productionAPI.createProduct(data)
        products.value.push(res.data)
        return res.data
    }

    async function updateProduct(id, data) {
        const res = await productionAPI.updateProduct(id, data)
        const index = products.value.findIndex(p => p.id === id)
        if (index !== -1) products.value[index] = res.data
        return res.data
    }

    async function deleteProduct(id) {
        await productionAPI.deleteProduct(id)
        products.value = products.value.filter(p => p.id !== id)
    }

    async function updateStock(id, quantity) {
        const res = await productionAPI.updateStock(id, quantity)
        const index = products.value.findIndex(p => p.id === id)
        if (index !== -1) products.value[index] = res.data
        return res.data
    }

    async function launchProduction(productId, quantity) {
        await productionAPI.launchProduction(productId, quantity)
    }

    const getProductById = (id) => {
        return products.value.find(p => p.id === id)
    }

    return {
        products,
        loading,
        error,
        lowStockProducts,
        outOfStockProducts,
        fetchProducts,
        createProduct,
        updateProduct,
        deleteProduct,
        updateStock,
        launchProduction,
        getProductById
    }
})
