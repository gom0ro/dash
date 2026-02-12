import api from './index'

export const financeAPI = {
    // Get expenses
    getExpenses(params) {
        return api.get('/finance/expenses', { params })
    },

    // Create expense
    createExpense(data) {
        return api.post('/finance/expenses', data)
    },

    // Get Statistics / KPI
    getStats(period = 'month') {
        return api.get('/finance/stats', { params: { period } })
    },

    // Get Salary info (for admin or user)
    getSalaries() {
        return api.get('/finance/salaries')
    },

    // Process withdrawal
    withdrawCash(amount) {
        return api.post('/finance/withdraw', { amount })
    }
}
