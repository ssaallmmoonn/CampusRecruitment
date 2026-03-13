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
      config.url.includes('jobs/dashboard/selected-jobs/') ||
      config.url.includes('jobs/categories/') ||
      config.url.includes('jobs/majors/')
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
    if (error.response) {
      if (error.response.status === 401) {
        // If 401 Unauthorized, clear token and refresh page
        // But only if we had a token to begin with (to avoid loop on login page if we handled 401 there)
        // Actually, the request interceptor removes header for login, so 401 on login is normal?
        // No, simplejwt returns 401 if credentials are wrong (AuthenticationFailed).
        // But we are now returning 400 (ValidationError) for our custom checks.
        // If super().validate() fails (e.g. inactive user), it returns 401.
        
        const token = localStorage.getItem('token')
        if (token) {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          ElMessage.error('登录状态失效，正在刷新页面...')
          setTimeout(() => {
            window.location.reload()
          }, 1500)
        } else {
           // 401 during login (e.g. inactive user, or if we didn't catch something)
           const resData = error.response.data
           const msg = resData.detail || '认证失败'
           ElMessage.error(msg)
        }
      } else {
        // Handle other errors (400, 403, 404, 500)
        const resData = error.response.data
        let message = error.message
        
        if (resData) {
             let detail = resData.detail
             // Handle case where detail is an array (DRF sometimes wraps strings in list)
             if (Array.isArray(detail) && detail.length > 0) {
                 detail = detail[0]
             }

             if (detail) {
                 if (detail === 'user_not_found') {
                     message = '该用户不存在，请先注册'
                 } else if (detail === 'password_error') {
                     message = '密码输入错误'
                 } else {
                     message = detail
                 }
             } else if (typeof resData === 'string') {
                 message = resData
             } else if (typeof resData === 'object') {
                 // Join values if it's an object of errors (e.g. form validation)
                 // exclude 'detail' if it exists (already handled)
                 const values = []
                 Object.keys(resData).forEach(key => {
                     if (key !== 'detail') {
                         const val = resData[key]
                         if (Array.isArray(val)) {
                             values.push(...val)
                         } else {
                             values.push(val)
                         }
                     }
                 })
                 if (values.length > 0) {
                     message = values.join(', ')
                 }
             }
        }

        ElMessage({
          message: message,
          type: 'error',
          duration: 5 * 1000
        })
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
