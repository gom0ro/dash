import api from './index'
import qs from 'qs'

export const authAPI = {
    login(email, password) {
        const data = qs.stringify({ grant_type: 'password', username: email, password })
        return api.post('/auth/login', data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
    },

    loginQR(qrData) {
        return api.post('/auth/login-qr', null, { params: { qr_data: qrData } })
    },

    register(payload) {
        return api.post('/auth/register', payload)
    },

    getMe() {
        return api.get('/auth/me') // axios автоматически добавит Authorization
    }
}
