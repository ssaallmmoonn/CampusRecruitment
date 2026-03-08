import { defineStore } from 'pinia'
import request from '../utils/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user')) || null,
    userInfo: null, // Detailed user info including avatar
  }),
  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user,
    role: (state) => state.user?.role,
    avatar: (state) => state.userInfo?.avatar
  },
  actions: {
    async login(username, password) {
      try {
        const res = await request.post('/users/login/', { username, password })
        this.token = res.access
        this.user = { username: res.username, role: res.role, id: res.id }
        
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        
        // Fetch detailed user info
        await this.fetchUserInfo()

        return res
      } catch (error) {
        throw error
      }
    },
    async fetchUserInfo() {
        try {
            const res = await request.get('/users/profile/')
            this.userInfo = res
        } catch (error) {
            console.error('Failed to fetch user info', error)
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
      this.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
