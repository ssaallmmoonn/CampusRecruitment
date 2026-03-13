<template>
  <div class="dashboard-page">
    <!-- Hero Search Section with Background -->
    <div class="hero-section">
      <div class="hero-bg-decoration left"></div>
      <div class="hero-bg-decoration right"></div>
      <div class="container hero-container">
        <h1 class="hero-title">寻找你的理想职位</h1>
        <p class="hero-subtitle">海量名企校招，助力职业起航</p>
        <div class="search-box">
          <el-icon class="search-icon"><Search /></el-icon>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索职位、专业、关键词" 
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <el-button type="primary" round class="search-button" @click="handleSearch">
            搜索
          </el-button>
        </div>
        <!-- Hot Keywords (Optional, nice to have) -->
        <div class="hot-tags">
          <span>热门搜索：</span>
          <a @click="router.push('/jobs?search=Java')">Java</a>
          <a @click="router.push('/jobs?search=产品经理')">产品经理</a>
          <a @click="router.push('/jobs?search=运营')">运营</a>
          <a @click="router.push('/jobs?search=管培生')">管培生</a>
        </div>
      </div>
    </div>

    <div class="container main-content">
      <!-- Main Content Section: Navigation & Carousel -->
      <div class="main-layout">
      <!-- Left: Category Navigation -->
      <div class="category-nav" @mouseleave="clearActiveCategory" @mouseenter="cancelClear">
        <div class="nav-tabs">
          <span 
            :class="{ active: activeTab === 'major' }" 
            @click="activeTab = 'major'"
          >按专业筛选</span>
          <span 
            :class="{ active: activeTab === 'job' }" 
            @click="activeTab = 'job'"
          >按职类筛选</span>
        </div>
        
        <div class="nav-list" v-if="activeTab === 'major'">
          <div 
            v-for="(category, index) in majorCategories" 
            :key="index" 
            class="nav-item is-major"
            @mouseenter="activeCategory = index"
          >
            <div class="nav-item-content">
              <el-icon class="nav-icon"><component :is="category.icon" /></el-icon>
              <span class="category-name">{{ category.name }}</span>
              <span class="sub-category">{{ getSubCategoryPreview(category) }}</span>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>

        <div class="nav-list" v-else>
          <div 
            v-for="(category, index) in jobCategories" 
            :key="index" 
            class="nav-item is-job"
            @mouseenter="activeJobCategory = index"
          >
            <div class="nav-item-content">
              <el-icon class="nav-icon"><component :is="category.icon" /></el-icon>
              <span class="category-name">{{ category.name }}</span>
              <span class="sub-category">{{ getSubCategoryPreview(category) }}</span>
              <el-icon class="arrow-icon"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>

        <div class="nav-footer" @click="handleViewAllCategories">
          <span>{{ activeTab === 'major' ? '全部专业' : '全部职类' }}</span>
        </div>

        <!-- Level 3 Flyout Menu -->
        <div class="flyout-menu" v-show="activeTab === 'major' && activeCategory !== null">
          <template v-if="activeCategory !== null && majorCategories[activeCategory]">
            <div v-for="(subGroup, sIndex) in majorCategories[activeCategory].children" :key="sIndex" class="flyout-group">
              <div class="group-title">{{ subGroup.name }}</div>
              <div class="group-items">
                <span 
                  v-for="(item, iIndex) in subGroup.items" 
                  :key="iIndex" 
                  class="flyout-item"
                  @click="handleCategoryClick(item, 'major')"
                >
                  {{ item }}
                </span>
              </div>
            </div>
          </template>
        </div>

         <!-- Level 3 Flyout Menu for Jobs -->
        <div class="flyout-menu" v-show="activeTab === 'job' && activeJobCategory !== null">
          <template v-if="activeJobCategory !== null && jobCategories[activeJobCategory]">
            <div v-for="(subGroup, sIndex) in jobCategories[activeJobCategory].children" :key="sIndex" class="flyout-group">
              <div class="group-title">{{ subGroup.name }}</div>
              <div class="group-items">
                <span 
                  v-for="(item, iIndex) in subGroup.items" 
                  :key="iIndex" 
                  class="flyout-item"
                  @click="handleCategoryClick(item, 'job')"
                >
                  {{ item }}
                </span>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Right: Banner Carousel -->
      <div class="banner-carousel">
        <el-carousel trigger="click" height="440px">
          <el-carousel-item v-for="item in carouselItems" :key="item.id">
            <div 
              class="carousel-item-content" 
              :style="{ backgroundImage: `url(${item.image})` }"
              @click="handleBannerClick(item)"
            >
              <!-- Ad Badge -->
              <div class="ad-badge">广告</div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>
    </div>

    <!-- Brand Zone -->
    <div class="brand-zone">
      <div class="section-header">
        <el-icon class="header-icon"><PriceTag /></el-icon>
        <h2 class="section-title">品牌专区</h2>
        <span class="section-subtitle">行业领导者，邀你共创辉煌</span>
      </div>
      <div class="brand-grid">
        <div 
          v-for="brand in brandCards" 
          :key="brand.id" 
          class="brand-card"
          @click="handleBrandClick(brand)"
        >
          <div class="brand-image-wrapper">
            <img :src="brand.image" :alt="brand.name" class="brand-image" />
            <div class="ad-badge">广告</div>
          </div>
          <div class="brand-name">{{ brand.name }}</div>
        </div>
      </div>
    </div>

    <!-- Selected Jobs -->
    <div class="selected-jobs">
      <div class="section-header">
        <el-icon class="header-icon"><Suitcase /></el-icon>
        <h2 class="section-title">精选职位</h2>
        <span class="section-subtitle">根据求职意向匹配</span>
      </div>
      <div class="jobs-grid">
        <div v-for="job in selectedJobs" :key="job.id" class="job-card" @click="$router.push(`/jobs/${job.id}`)">
          <div class="job-header">
            <span class="job-title" :title="job.title">{{ job.title }}</span>
            <span class="job-salary">{{ job.salary }}</span>
          </div>
          <div class="job-tags">
            <span v-for="(tag, index) in job.tags" :key="index" class="job-tag">{{ tag }}</span>
          </div>
          <div class="job-company">
            <div class="company-clickable-area" @click.stop="goToCompanyDetail(job.company.id)">
              <img :src="job.company.logo" :alt="job.company.name" class="company-logo" />
              <div class="company-info">
                <div class="company-name" :title="job.company.name">{{ job.company.name }}</div>
                <div class="company-details" :title="`${job.company.industry} ${job.company.size} ${job.company.type}`">
                  {{ job.company.industry }} {{ job.company.size }} {{ job.company.type }}
                </div>
              </div>
            </div>
            <div class="job-location">{{ job.location }}</div>
          </div>
        </div>
      </div>
      <div class="view-more-container">
        <el-button type="primary" class="view-more-btn" round @click="handleViewMoreJobs">
          查看更多 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>
  </div>

  <!-- Back to Top Button -->
  <el-backtop :right="40" :bottom="40" :visibility-height="300">
    <div class="back-to-top-content">
      <el-icon><ArrowUpBold /></el-icon>
    </div>
  </el-backtop>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../../stores/user'
import { useRouter } from 'vue-router'
import request from '../../utils/request'
import { ElMessage } from 'element-plus'
import { 
  Search, ArrowRight, ArrowUpBold, PriceTag, Suitcase,
  Monitor, DataLine, FirstAidKit, Apple, Management, Notebook, ScaleToOriginal,
  Money, Connection, Tools, Brush, Headset, Trophy
} from '@element-plus/icons-vue'
import { getBanners, getBrands } from '@/api/ads'

const userStore = useUserStore()
const router = useRouter()
const searchQuery = ref('')
const activeTab = ref('major')
const activeCategory = ref(null)
const activeJobCategory = ref(null)
const carouselItems = ref([])

const majorIcons = {
  '工学': 'Monitor',
  '理学': 'DataLine',
  '医学': 'FirstAidKit',
  '农学': 'Apple',
  '管理学': 'Management',
  '文学': 'Notebook',
  '法学': 'ScaleToOriginal'
}

const jobIcons = {
  '销售/商务拓展': 'Money',
  '人事/行政/财务/法务': 'Suitcase',
  '互联网/通信及硬件': 'Connection',
  '运维/测试': 'Tools',
  '视觉/交互/设计': 'Brush',
  '运营/客服': 'Headset',
  '产品/项目/高级管理': 'Trophy'
}

import majorJson from '@/assets/major.json'
import jobJson from '@/assets/jobs.json'

const transformMajors = (data) => {
  if (!data || !data['专业分类']) return []
  return data['专业分类'].map(cat => ({
    name: cat['一级分类'],
    icon: majorIcons[cat['一级分类']] || 'Monitor',
    children: cat['二级分类列表'].map(sub => ({
      name: sub['二级分类'],
      items: sub['三级分类']
    }))
  }))
}

const transformJobs = (data) => {
  if (!data || !data['职位分类']) return []
  return data['职位分类'].map(cat => ({
    name: cat['一级分类'],
    icon: jobIcons[cat['一级分类']] || 'Suitcase',
    children: cat['二级分类列表'].map(sub => ({
      name: sub['二级分类'],
      items: sub['三级分类']
    }))
  }))
}

const majorCategories = transformMajors(majorJson)
const jobCategories = transformJobs(jobJson)

const getSubCategoryPreview = (category) => {
  if (!category.children || category.children.length === 0) return ''
  // Return the first group name or a few items joined
  // Modified to show sub-category names (二级分类) instead of items, as items are too deep
  return category.children.map(c => c.name).slice(0, 2).join('/')
}

const brandCards = ref([])
const selectedJobs = ref([])

const fetchBannersData = async () => {
  try {
    const res = await getBanners()
    carouselItems.value = res.results || res
  } catch (error) {
    console.error('Failed to fetch banners:', error)
  }
}

const handleBannerClick = (item) => {
  if (item.link_url) {
    window.open(item.link_url, '_blank')
  }
}

const fetchBrandZone = async () => {
  try {
    const res = await getBrands()
    brandCards.value = (res.results || res).map(item => ({
      id: item.id,
      name: item.name,
      image: item.logo,
      companyId: item.company
    }))
  } catch (error) {
    console.error('Failed to fetch brand zone:', error)
  }
}

const handleBrandClick = (brand) => {
  if (brand.companyId) {
    router.push(`/company/${brand.companyId}`)
  }
}

const fetchSelectedJobs = async () => {
  try {
    const res = await request.get('/jobs/dashboard/selected-jobs/')
    selectedJobs.value = res.map(item => ({
      id: item.id,
      title: item.job_name,
      salary: item.salary,
      tags: [item.job_type, item.degree_requirement, item.experience_requirement],
      company: {
        id: item.company.id,
        name: item.company.company_name,
        logo: item.company.logo,
        industry: item.company.industry,
        size: item.company.scale,
        type: item.company.nature
      },
      location: item.location
    }))
  } catch (error) {
    console.error('Failed to fetch selected jobs:', error)
  }
}

onMounted(() => {
  fetchBrandZone()
  fetchSelectedJobs()
  fetchBannersData()
})

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/jobs', query: { search: searchQuery.value } })
  }
}

const handleViewMoreJobs = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再访问该功能')
    router.push('/login')
    return
  }
  router.push('/jobs')
}

const handleViewAllCategories = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再访问该功能')
    router.push('/login')
    return
  }
  
  // Navigate to jobs page with the current tab filter activated
  // If activeTab is 'major', we want to show major filter. If 'job', show job filter.
  // The JobBoard component handles this via activeFilterTab ref, but we need to pass a signal.
  // Since activeFilterTab in JobBoard defaults to 'major', we can pass a query param to switch it if needed.
  // Or just go to /jobs and let user switch.
  // Requirement says "jump to job search interface".
  
  const query = {}
  if (activeTab.value === 'job') {
      // If we want to default to job tab in JobBoard, we might need to add logic there to read a query param
      // or just pass a dummy filter to activate the tab?
      // Let's check JobBoard logic: 
      // if (query.job_category) activeFilterTab.value = 'job'
      // So if we pass job_category='', it might not switch tab because of check `if (query.job_category)`.
      // Let's just go to /jobs for now, or maybe pass a special flag?
      // Actually, simply navigating to /jobs is usually enough for "All Majors/All Jobs".
      // But if user is on "Job Category" tab in dashboard, maybe they expect "Job Category" tab in search?
      // Let's keep it simple: go to /jobs. The user can switch tabs there.
      // But to be precise: "All Majors" button -> /jobs (defaults to major tab)
      // "All Jobs" button -> /jobs (but ideally switch to job tab?)
      
      // Let's add a small hack: pass a query param 'tab=job' if we want to switch tab?
      // JobBoard doesn't support 'tab' query param yet.
      // Let's just navigate to /jobs for now as per basic requirement.
  }
  
  router.push('/jobs')
}

const handleCategoryClick = (category, type) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再访问该功能')
    router.push('/login')
    return
  }
  
  // Construct query based on type
  const query = {}
  if (type === 'major') {
    // Pass as major_requirement filter instead of search
    query.major = category
  } else if (type === 'job') {
    // Pass as job_category filter instead of search
    query.job_category = category
  }
  
  router.push({ path: '/jobs', query })
}

const goToCompanyDetail = (companyId) => {
  if (companyId) {
    router.push(`/company/${companyId}`)
  }
}

let clearTimer = null

const clearActiveCategory = () => {
  if (clearTimer) clearTimeout(clearTimer)
  clearTimer = setTimeout(() => {
    activeCategory.value = null
    activeJobCategory.value = null
    clearTimer = null
  }, 100)
}

const cancelClear = () => {
  if (clearTimer) {
    clearTimeout(clearTimer)
    clearTimer = null
  }
}
</script>

<style scoped>
.dashboard-page {
  min-height: 100%;
}

.hero-section {
  position: relative;
  background: linear-gradient(135deg, #f6f8fd 0%, #f0f4ff 100%);
  padding: 10px 0 20px;
  text-align: center;
  overflow: hidden;
  margin-bottom: 10px;
}

.hero-bg-decoration {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
}

.hero-bg-decoration.left {
  top: -50px;
  left: -50px;
  width: 300px;
  height: 300px;
  background: rgba(64, 158, 255, 0.1);
}

.hero-bg-decoration.right {
  bottom: -50px;
  right: -50px;
  width: 400px;
  height: 400px;
  background: rgba(103, 194, 58, 0.05);
}

.hero-container {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-title {
  font-size: 36px;
  font-weight: 800;
  color: #303133;
  margin: 0 0 10px;
  letter-spacing: 1px;
}

.hero-subtitle {
  font-size: 16px;
  color: #606266;
  margin: 0 0 30px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 50px;
  padding: 8px 8px 8px 24px;
  width: 100%;
  max-width: 720px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.search-box:hover, .search-box:focus-within {
  border-color: #409EFF;
  box-shadow: 0 12px 32px rgba(64, 158, 255, 0.12);
  transform: translateY(-2px);
}

.search-icon {
  font-size: 20px;
  color: #909399;
  margin-right: 12px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  color: #303133;
  background: transparent;
  line-height: 1.5;
}

.search-input::placeholder {
  color: #c0c4cc;
}

.search-button {
  padding: 12px 36px;
  font-size: 16px;
  border-radius: 24px;
  background: linear-gradient(90deg, #409EFF 0%, #3a8ee6 100%);
  border: none;
  font-weight: 500;
  letter-spacing: 1px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;
}

.search-button:hover {
  background: linear-gradient(90deg, #66b1ff 0%, #409EFF 100%);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

.hot-tags {
  margin-top: 16px;
  font-size: 13px;
  color: #909399;
}

.hot-tags a {
  margin: 0 8px;
  color: #606266;
  cursor: pointer;
  transition: color 0.3s;
  text-decoration: none;
}

.hot-tags a:hover {
  color: #409EFF;
  text-decoration: underline;
}

.main-content {
  padding-bottom: 60px;
}

.main-layout {
  display: flex;
  gap: 24px;
  margin-bottom: 50px;
  height: 440px;
}

.category-nav {
  width: 280px;
  height: 100%;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  position: relative;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
  overflow: visible; /* Allow flyout to show */
}

/* Ensure border-radius clips content but flyout can still be seen? 
   Actually flyout is absolute positioned. If I put overflow: hidden on category-nav, flyout will be clipped.
   But I need border-radius.
   Solution: Apply border-radius to category-nav. Flyout is outside? 
   Wait, flyout is inside .nav-item inside .nav-list inside .category-nav.
   If category-nav has overflow: hidden, flyout is clipped.
   If category-nav does NOT have overflow: hidden, flyout is visible.
   But I want rounded corners. 
   The nav-tabs (top) and nav-footer (bottom) need to respect the border radius.
*/

.nav-tabs {
  display: flex;
  width: 100%;
}

.nav-tabs span {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  cursor: pointer;
  font-size: 15px;
  color: #606266;
  background-color: #f5f7fa;
  transition: all 0.3s;
}

.nav-tabs span:first-child {
  border-top-left-radius: 12px;
}

.nav-tabs span:last-child {
  border-top-right-radius: 12px;
}

.nav-tabs span.active {
  background-color: #fff;
  color: #409EFF;
  font-weight: bold;
  border-top: 2px solid #409EFF;
  border-bottom: 1px solid transparent;
}

.nav-list {
  flex: 1;
  padding: 10px 0 0 0; /* Removed bottom padding */
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.nav-list::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.nav-footer {
  width: calc(100% - 20px);
  background-color: #dfe4f8;
  color: #426eff;
  text-align: center;
  padding: 10px 0;
  cursor: pointer;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  margin: auto 10px 10px 10px;
  transition: background-color 0.3s;
}

.nav-footer:hover {
  background-color: #66b1ff;
}

.nav-item {
  padding: 14px 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.nav-item:hover {
  background-color: #ecf5ff;
}

.nav-item-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-icon {
  margin-right: 12px;
  font-size: 18px;
  color: #909399;
}

.nav-item:hover .nav-icon {
  color: #409EFF;
}

.category-name {
  font-size: 16px;
  color: #303133;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.nav-item.is-major .category-name {
  width: 80px; /* Fixed width for major names to align sub-categories */
  margin-right: 0;
}

.nav-item.is-job .category-name {
  width: auto;
  margin-right: 10px;
}

.nav-item.is-job .sub-category {
  text-align: right;
}

.sub-category {
  font-size: 12px;
  color: #909399;
  margin-right: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  text-align: left; /* Align left for major */
  min-width: 0;
}

.nav-item.is-job .sub-category {
  text-align: right; /* Align right for job to keep previous style */
}

.arrow-icon {
  font-size: 13px;
  color: #c0c4cc;
}

/* Flyout Menu Styles */
.flyout-menu {
  position: absolute;
  left: 300px; /* 280px width + 20px gap */
  top: 0;
  width: 850px; /* Match carousel width */
  height: 390px;
  background-color: #fff;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  z-index: 100;
  padding: 25px;
  overflow-y: auto;
  border-radius: 12px;
}

.flyout-group {
  margin-bottom: 25px;
}

.group-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f2f6fc;
}

.group-items {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.flyout-item {
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 4px;
  transition: all 0.2s;
}

.flyout-item:hover {
  color: #409EFF;
  background-color: #ecf5ff;
}


.banner-carousel {
  flex: 1;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
  position: relative;
  cursor: pointer;
}

.el-carousel {
  height: 100%;
}


.carousel-item-content {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  border-radius: 4px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.carousel-overlay {
  background: rgba(0, 0, 0, 0.3);
  padding: 30px 50px;
  border-radius: 8px;
  text-align: center;
  backdrop-filter: blur(2px);
  max-width: 80%;
}

.carousel-item-content h3 {
  font-size: 36px;
  margin-bottom: 16px;
  font-weight: bold;
  text-shadow: 0 2px 8px rgba(0,0,0,0.6);
  letter-spacing: 1px;
}

.carousel-item-content p {
  font-size: 20px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.6);
  font-weight: 500;
}

/* Ad Badge Styles */
.ad-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.4);
  color: #fff;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  pointer-events: none;
  z-index: 10;
}
.card-content {
  text-align: center;
  padding: 20px 0;
  cursor: pointer;
}
.card-content p {
  margin-top: 10px;
  color: #606266;
}
/* Brand Zone Styles */
.brand-zone {
  margin-top: 40px;
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.header-icon {
  font-size: 24px;
  color: #303133;
  margin-right: 10px;
}

.section-title {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 0 15px 0 0;
}

.section-subtitle {
  font-size: 14px;
  color: #909399;
}

.brand-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.brand-card {
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  border: 1px solid #ebeef5;
}

.brand-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.brand-image-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.brand-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.brand-card:hover .brand-image {
  transform: scale(1.05);
}

.brand-name {
  padding: 15px;
  text-align: center;
  font-size: 15px;
  color: #303133;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
/* Selected Jobs Styles */
.selected-jobs {
  margin-top: 40px;
  margin-bottom: 40px;
}

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.job-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  border: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.job-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.job-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 65%;
}

.job-salary {
  font-size: 16px;
  font-weight: bold;
  color: #409EFF;
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.job-tag {
  background-color: #f4f4f5;
  color: #909399;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.job-company {
  display: flex;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
  margin-top: auto;
}

.company-clickable-area {
  display: flex;
  align-items: center;
  flex: 1;
  overflow: hidden;
  cursor: pointer;
  margin-right: 10px;
}

.company-clickable-area:hover .company-name {
  color: #60b3ff;
}

.company-logo {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  margin-right: 12px;
  object-fit: cover;
  border: 1px solid #f2f2f2;
}

.company-info {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.company-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.company-details {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.job-location {
  font-size: 14px;
  color: #909399;
  margin-left: 8px;
  white-space: nowrap;
}

.view-more-container {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.view-more-btn {
  padding: 12px 40px;
  font-size: 16px;
  width: 200px;
  height: 44px;
}

.back-to-top-content {
  height: 100%;
  width: 100%;
  background-color: #fff;
  box-shadow: 0 0 6px rgba(0,0,0,0.12);
  text-align: center;
  line-height: 40px;
  color: #1989fa;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.back-to-top-content:hover {
  background-color: #f2f6fc;
}
</style>