import { defineStore } from 'pinia'
import { ref } from 'vue'
import { financeAPI } from '@/api/finance'

export const useFinanceStore = defineStore('finance', () => {
    const expenses = ref([])
    const stats = ref(null)
    const salaries = ref([])
    const loading = ref(false)
    const error = ref(null)

    async function fetchExpenses(params) {
        loading.value = true
        try {
            const { data } = await financeAPI.getExpenses(params)
            expenses.value = data
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    async function fetchStats(period) {
        loading.value = true
        try {
            const { data } = await financeAPI.getStats(period)
            stats.value = data
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    async function fetchSalaries() {
        loading.value = true
        try {
            // Mock data if API fails or empty
            /* 
            const mock = [
                { id: 1, user: { full_name: 'Ivan' }, amount: 5000, paid: false }
            ]
            */
            const { data } = await financeAPI.getSalaries()
            salaries.value = data
        } catch (err) {
            console.error(err)
            // error.value = err.message
        } finally {
            loading.value = false
        }
    }

    return {
        expenses,
        stats,
        salaries,
        loading,
        fetchExpenses,
        fetchStats,
        fetchSalaries
    }
})
