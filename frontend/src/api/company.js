import request from '@/utils/request'

export function getCompanyDetail(id) {
  return request({
    url: `/users/companies/${id}/`,
    method: 'get'
  })
}
