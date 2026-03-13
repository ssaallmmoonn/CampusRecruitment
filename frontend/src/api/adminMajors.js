import request from '@/utils/request'

export function getAdminMajorTree(params) {
  return request({
    url: '/jobs/admin/majors/',
    method: 'get',
    params
  })
}

export function createAdminMajor(data) {
  return request({
    url: '/jobs/admin/majors/',
    method: 'post',
    data
  })
}

export function updateAdminMajor(id, data) {
  return request({
    url: `/jobs/admin/majors/${id}/`,
    method: 'put',
    data
  })
}

export function deleteAdminMajor(id) {
  return request({
    url: `/jobs/admin/majors/${id}/`,
    method: 'delete'
  })
}

