import request from '@/utils/request'

export function getAdminDashboard() {
  return request({
    url: '/users/admin-dashboard/',
    method: 'get'
  })
}
