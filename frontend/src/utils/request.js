import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: '/api', // Use relative path for proxy
  timeout: 5000
})

// Request interceptor
service.interceptors.request.use(
  config => {
    let token = localStorage.getItem('token')
    // Clean token if it's invalid string
    if (token === 'undefined' || token === 'null' || token === '"undefined"' || token === '"null"') {
      localStorage.removeItem('token')
      token = null
    }
    
    // Don't send token for login/register endpoints to avoid 401 if token is invalid
    // Also exclude public dashboard endpoints to ensure they load even with bad token
    if (
      config.url.includes('users/login/') || 
      config.url.includes('users/register/') ||
      config.url.includes('jobs/dashboard/brand-zone/') ||
      config.url.includes('jobs/dashboard/selected-jobs/')
    ) {
      delete config.headers['Authorization']
      return config
    }
    
    if (token) {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    return config
  },
  error => {
    console.log(error)
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  response => {
    const res = response.data
    return res
  },
  error => {
    console.log('err' + error)
    if (error.response && error.response.status === 401) {
      // If 401 Unauthorized, clear token and refresh page
      const token = localStorage.getItem('token')
      if (token) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        ElMessage.error('登录状态失效，正在刷新页面...')
        setTimeout(() => {
          window.location.reload()
        }, 1500)
      }
    } else {
      ElMessage({
        message: error.message || 'Error',
        type: 'error',
        duration: 5 * 1000
      })
    }
    return Promise.reject(error)
  }
)

export default service
