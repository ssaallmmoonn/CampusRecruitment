import request from '@/utils/request'

export function getJobs(params) {
  return request({
    url: '/jobs/',
    method: 'get',
    params
  })
}

export function getJobDetail(id) {
  return request({
    url: `/jobs/${id}/`,
    method: 'get'
  })
}

export function createJob(data) {
  return request({
    url: '/jobs/',
    method: 'post',
    data
  })
}

export function updateJob(id, data) {
  return request({
    url: `/jobs/${id}/`,
    method: 'put',
    data
  })
}

export function deleteJob(id) {
  return request({
    url: `/jobs/${id}/`,
    method: 'delete'
  })
}
