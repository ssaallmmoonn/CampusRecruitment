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

// Behaviors
export function recordBehavior(data) {
  return request({
    url: '/recruitment/behaviors/',
    method: 'post',
    data
  })
}
