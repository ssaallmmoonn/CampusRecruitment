import request from '@/utils/request'

export function getIndustries(params) {
  return request({
    url: '/users/industries/',
    method: 'get',
    params
  })
}

export function createIndustry(data) {
  return request({
    url: '/users/industries/',
    method: 'post',
    data
  })
}

export function updateIndustry(id, data) {
  return request({
    url: `/users/industries/${id}/`,
    method: 'put',
    data
  })
}

export function deleteIndustry(id) {
  return request({
    url: `/users/industries/${id}/`,
    method: 'delete'
  })
}

export function batchDeleteIndustries(ids) {
  return request({
    url: '/users/industries/batch_delete/',
    method: 'post',
    data: { ids }
  })
}
