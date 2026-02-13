import api from './index'

export const reportsAPI = {
    getCashReport(params) {
        return api.get('/reports/cash', { params })
    },
    getSalesReport(params) {
        return api.get('/reports/sales', { params })
    },
    getWorkersReport(params) {
        return api.get('/reports/workers', { params })
    },
    withdrawCash(data) {
        return api.post('/reports/cash/withdraw', data)
    },
    getDashboardStats() {
        return api.get('/reports/dashboard-stats')
    }
}
