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

export function getCompanyJobCategories(companyId) {
  return request({
    url: '/jobs/company-categories/',
    method: 'get',
    params: { company: companyId }
  })
}

export function getCompanyLocations(companyId, jobCategory) {
  const params = { company: companyId }
  if (jobCategory) {
    params.job_category = jobCategory
  }
  return request({
    url: '/jobs/company-locations/',
    method: 'get',
    params
  })
}

export function getJobCategoryTree() {
  return request({
    url: '/jobs/categories/',
    method: 'get'
  })
}

export function getMajorCategoryTree() {
  return request({
    url: '/jobs/majors/',
    method: 'get'
  })
}
