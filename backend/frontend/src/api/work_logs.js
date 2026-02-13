import api from './index'

export const workLogsAPI = {
    getAll(params) {
        return api.get('/work-logs/', { params })
    },
    create(data) {
        return api.post('/work-logs/', data)
    },
    getMySalary() {
        return api.get('/work-logs/my-salary')
    },
    markAsPaid(data) {
        return api.post('/work-logs/mark-paid', data)
    }
}
