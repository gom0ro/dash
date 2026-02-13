import api from './index'

export const salariesAPI = {
    createPayment(data) {
        return api.post('/salaries/', data)
    },
    getHistory(workerId) {
        return api.get(`/salaries/history/${workerId}`)
    }
}
