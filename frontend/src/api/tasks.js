import api from './index'

export const tasksAPI = {
    getAll() {
        return api.get('/tasks/')
    },
    create(data) {
        return api.post('/tasks/', data)
    },
    update(id, data) {
        return api.patch(`/tasks/${id}`, data)
    },
    delete(id) {
        return api.delete(`/tasks/${id}`)
    }
}
