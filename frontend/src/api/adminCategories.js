import request from '@/utils/request'

export function getAdminJobCategoryTree(params) {
  return request({
    url: '/jobs/admin/categories/',
    method: 'get',
    params
  })
}

export function createAdminJobCategory(data) {
  return request({
    url: '/jobs/admin/categories/',
    method: 'post',
    data
  })
}

export function updateAdminJobCategory(id, data) {
  return request({
    url: `/jobs/admin/categories/${id}/`,
    method: 'put',
    data
  })
}

export function deleteAdminJobCategory(id) {
  return request({
    url: `/jobs/admin/categories/${id}/`,
    method: 'delete'
  })
}

