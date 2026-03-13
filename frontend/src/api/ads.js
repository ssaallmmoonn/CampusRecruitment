import request from '@/utils/request'

// 获取轮播图列表 (支持 params: { search })
export function getBanners(params) {
  return request({
    url: '/ads/banners/',
    method: 'get',
    params
  })
}

// 创建轮播图 (FormData)
export function createBanner(data) {
  return request({
    url: '/ads/banners/',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 更新轮播图 (FormData)
export function updateBanner(id, data) {
  return request({
    url: `/ads/banners/${id}/`,
    method: 'patch',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 删除轮播图
export function deleteBanner(id) {
  return request({
    url: `/ads/banners/${id}/`,
    method: 'delete'
  })
}

// 获取品牌专区列表
export function getBrands(params) {
  return request({
    url: '/ads/brands/',
    method: 'get',
    params
  })
}

// 创建品牌专区 (FormData)
export function createBrand(data) {
  return request({
    url: '/ads/brands/',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 更新品牌专区 (FormData)
export function updateBrand(id, data) {
  return request({
    url: `/ads/brands/${id}/`,
    method: 'patch',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 删除品牌专区
export function deleteBrand(id) {
  return request({
    url: `/ads/brands/${id}/`,
    method: 'delete'
  })
}

// 获取公告列表
export function getNotices(params) {
  return request({
    url: '/ads/notices/',
    method: 'get',
    params
  })
}

// 创建公告
export function createNotice(data) {
  return request({
    url: '/ads/notices/',
    method: 'post',
    data
  })
}

// 更新公告
export function updateNotice(id, data) {
  return request({
    url: `/ads/notices/${id}/`,
    method: 'patch',
    data
  })
}

// 删除公告
export function deleteNotice(id) {
  return request({
    url: `/ads/notices/${id}/`,
    method: 'delete'
  })
}
