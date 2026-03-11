import request from '@/utils/request'

export function getCompanyDetail(id) {
  return request({
    url: `/users/companies/${id}/`,
    method: 'get'
  })
}

export function updateCompanyProfile(id, data) {
  return request({
    url: `/users/profile/`,
    method: 'patch',
    data
  })
}
