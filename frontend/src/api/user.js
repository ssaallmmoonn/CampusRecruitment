import request from '@/utils/request'

export function changePassword(data) {
  return request({
    url: '/users/change-password/',
    method: 'put',
    data
  })
}
