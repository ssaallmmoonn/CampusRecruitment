import request from '@/utils/request'

// Resumes
export function getResumes() {
  return request({
    url: '/recruitment/resumes/',
    method: 'get'
  })
}

export function createResume(data) {
  return request({
    url: '/recruitment/resumes/',
    method: 'post',
    data
  })
}

export function updateResume(id, data) {
  return request({
    url: `/recruitment/resumes/${id}/`,
    method: 'put',
    data
  })
}

export function deleteResume(id) {
  return request({
    url: `/recruitment/resumes/${id}/`,
    method: 'delete'
  })
}

// Applications
export function applyJob(data) {
  return request({
    url: '/recruitment/applications/',
    method: 'post',
    data
  })
}

export function getApplications() {
  return request({
    url: '/recruitment/applications/',
    method: 'get'
  })
}

export function cancelApplication(id) {
  return request({
    url: `/recruitment/applications/${id}/`,
    method: 'delete'
  })
}

export function checkApplicationStatus(jobId) {
  return request({
    url: '/recruitment/applications/check_status/',
    method: 'get',
    params: { job_id: jobId }
  })
}

// Behaviors
export function recordBehavior(data) {
  return request({
    url: '/recruitment/behaviors/',
    method: 'post',
    data
  })
}

export function getBehaviors(params) {
  return request({
    url: '/recruitment/behaviors/',
    method: 'get',
    params
  })
}

export function toggleCollect(data) {
  return request({
    url: '/recruitment/behaviors/toggle_collect/',
    method: 'post',
    data
  })
}

export function checkCollectStatus(params) {
  return request({
    url: '/recruitment/behaviors/check_status/',
    method: 'get',
    params
  })
}
