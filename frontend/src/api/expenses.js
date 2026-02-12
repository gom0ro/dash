import api from './index'

export const expensesAPI = {
    getAll(params) {
        return api.get('/expenses/', { params })
    },
    create(data) {
        return api.post('/expenses/', data)
    },
    update(id, data) {
        return api.patch(`/expenses/${id}`, data)
    },
    delete(id) {
        return api.delete(`/expenses/${id}`)
    }
}
