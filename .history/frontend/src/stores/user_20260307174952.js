import { defineStore } from 'pinia'
import request from '../utils/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user')) || null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    role: (state) => state.user?.role
  },
  actions: {
    async login(username, password) {
      try {
        const res = await request.post('/users/login/', { username, password })
        this.token = res.access
        this.user = { username: res.username, role: res.role, id: res.id }
        
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        
        return res
      } catch (error) {
        throw error
      }
    },
    async register(data) {
        try {
            await request.post('/users/register/', data)
        } catch (error) {
            throw error
        }
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
