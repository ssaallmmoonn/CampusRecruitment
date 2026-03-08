<template>
  <div class="dashboard-container">
    <!-- Hero Search Section -->
    <div class="hero-section">
      <div class="search-box">
        <el-icon class="search-icon"><Search /></el-icon>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="输入职位关键词搜索" 
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" round class="search-button" @click="handleSearch">
          搜索
        </el-button>
      </div>
    </div>

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
            class="nav-item"
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
            class="nav-item"
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

        <div class="nav-footer">
          <span>{{ activeTab === 'major' ? '全部专业' : '全部职类' }}</span>
        </div>

        <!-- Level 3 Flyout Menu -->
        <div class="flyout-menu" v-show="activeTab === 'major' && activeCategory !== null">
          <template v-if="activeCategory !== null && majorCategories[activeCategory]">
            <div v-for="(subGroup, sIndex) in majorCategories[activeCategory].children" :key="sIndex" class="flyout-group">
              <div class="group-title">{{ subGroup.name }}</div>
              <div class="group-items">
                <span v-for="(item, iIndex) in subGroup.items" :key="iIndex" class="flyout-item">
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
                <span v-for="(item, iIndex) in subGroup.items" :key="iIndex" class="flyout-item">
                  {{ item }}
                </span>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Right: Banner Carousel -->
      <div class="banner-carousel">
        <el-carousel trigger="click" height="420px">
          <el-carousel-item v-for="item in carouselItems" :key="item.id">
            <div class="carousel-item-content" :style="{ backgroundImage: `url(${item.image})` }">
              <div class="carousel-overlay">
                <h3>{{ item.title }}</h3>
                <p>{{ item.subtitle }}</p>
              </div>
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
        <div v-for="brand in brandCards" :key="brand.id" class="brand-card">
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
            <img :src="job.company.logo" :alt="job.company.name" class="company-logo" />
            <div class="company-info">
              <div class="company-name" :title="job.company.name">{{ job.company.name }}</div>
              <div class="company-details" :title="`${job.company.industry} ${job.company.size} ${job.company.type}`">
                {{ job.company.industry }} {{ job.company.size }} {{ job.company.type }}
              </div>
            </div>
            <div class="job-location">{{ job.location }}</div>
          </div>
        </div>
      </div>
      <div class="view-more-container">
        <el-button type="primary" class="view-more-btn" round @click="$router.push('/jobs')">
          查看更多 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
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

const userStore = useUserStore()
const router = useRouter()
const searchQuery = ref('')
const activeTab = ref('major')
const activeCategory = ref(null)
const activeJobCategory = ref(null)

const majorCategories = [
  { 
    name: '工学', 
    icon: 'Monitor',
    children: [
      { name: '计算机类', items: ['计算机科学与技术', '软件工程', '网络工程', '信息安全', '物联网工程'] },
      { name: '机械类', items: ['机械工程', '机械设计制造及其自动化', '车辆工程', '测控技术与仪器'] },
      { name: '电子信息类', items: ['电子信息工程', '电子科学与技术', '通信工程', '微电子科学与工程'] }
    ]
  },
  { 
    name: '理学', 
    icon: 'Cpu',
    children: [
      { name: '数学类', items: ['数学与应用数学', '信息与计算科学', '统计学'] },
      { name: '物理学类', items: ['物理学', '应用物理学', '核物理'] },
      { name: '化学类', items: ['化学', '应用化学', '化学生物学'] }
    ]
  },
  { 
    name: '医学', 
    icon: 'FirstAidKit',
    children: [
      { name: '临床医学类', items: ['临床医学', '麻醉学', '医学影像学'] },
      { name: '药学类', items: ['药学', '药物制剂', '临床药学'] },
      { name: '护理学类', items: ['护理学', '助产学'] }
    ]
  },
  { 
    name: '农学', 
    icon: 'Apple',
    children: [
      { name: '植物生产类', items: ['农学', '园艺', '植物保护'] },
      { name: '动物生产类', items: ['动物科学', '蚕学', '蜂学'] }
    ]
  },
  { 
    name: '管理学', 
    icon: 'Management',
    children: [
      { name: '工商管理类', items: ['工商管理', '市场营销', '会计学', '财务管理', '人力资源管理'] },
      { name: '公共管理类', items: ['公共事业管理', '行政管理', '劳动与社会保障'] }
    ]
  },
  { 
    name: '文学', 
    icon: 'Notebook',
    children: [
      { name: '中国语言文学类', items: ['汉语言文学', '汉语言', '汉语国际教育'] },
      { name: '外国语言文学类', items: ['英语', '俄语', '德语', '法语', '日语'] },
      { name: '新闻传播学类', items: ['新闻学', '广播电视学', '广告学', '传播学'] }
    ]
  },
  { 
    name: '法学', 
    icon: 'ScaleToOriginal',
    children: [
      { name: '法学类', items: ['法学', '知识产权', '监狱学'] },
      { name: '政治学类', items: ['政治学与行政学', '国际政治', '外交学'] },
      { name: '社会学类', items: ['社会学', '社会工作', '人类学'] }
    ]
  },
  { 
    name: '艺术学', 
    icon: 'Brush',
    children: [
      { name: '美术学类', items: ['美术学', '绘画', '雕塑', '摄影'] },
      { name: '设计学类', items: ['艺术设计学', '视觉传达设计', '环境设计', '产品设计'] },
      { name: '音乐与舞蹈学类', items: ['音乐表演', '音乐学', '舞蹈表演'] }
    ]
  },
]

const jobCategories = [
  { 
    name: '互联网', 
    icon: 'Connection',
    children: [
      { name: '研发', items: ['Java开发', 'C++开发', '前端开发', '移动端开发', '测试工程师'] },
      { name: '产品/运营', items: ['产品经理', '用户运营', '内容运营', '新媒体运营'] },
      { name: '设计', items: ['UI设计师', '交互设计师', '视觉设计师'] }
    ]
  },
  { 
    name: '金融', 
    icon: 'Money',
    children: [
      { name: '银行', items: ['柜员', '客户经理', '风险控制', '信贷审批'] },
      { name: '证券/基金', items: ['投资顾问', '行业研究员', '交易员'] },
      { name: '保险', items: ['保险精算师', '核保理赔', '保险代理人'] }
    ]
  },
  { 
    name: '教育', 
    icon: 'School',
    children: [
      { name: '教师', items: ['幼教', '小学教师', '初高中教师', '大学教师'] },
      { name: '培训', items: ['培训讲师', '课程顾问', '教务管理'] },
      { name: '行政', items: ['行政专员', '辅导员', '图书管理员'] }
    ]
  },
  { 
    name: '制造', 
    icon: 'Van',
    children: [
      { name: '机械', items: ['机械工程师', '模具设计', '机电工程师'] },
      { name: '电子/半导体', items: ['电子工程师', 'IC设计', '嵌入式开发'] },
      { name: '汽车', items: ['车辆工程', '汽车设计', '汽车维修'] }
    ]
  },
]

const getSubCategoryPreview = (category) => {
  if (!category.children || category.children.length === 0) return ''
  // Return the first group name or a few items joined
  return category.children.map(c => c.name).slice(0, 2).join('/')
}

const carouselItems = [
  { 
    id: 1, 
    title: '开启你的职业生涯', 
    subtitle: '海量名企校招职位等你来投', 
    image: 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80'
  },
  { 
    id: 2, 
    title: '寻找志同道合的伙伴', 
    subtitle: '加入优秀团队，共创未来', 
    image: 'https://images.unsplash.com/photo-1551434678-e076c223a692?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80'
  },
  { 
    id: 3, 
    title: '技术改变世界', 
    subtitle: '在科技前沿探索无限可能', 
    image: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80'
  }
]

const brandCards = ref([])
const selectedJobs = ref([])

const fetchBrandZone = async () => {
  try {
    const res = await request.get('/jobs/dashboard/brand-zone/')
    brandCards.value = res.map(item => ({
      id: item.user,
      name: item.company_name,
      image: item.logo
    }))
  } catch (error) {
    console.error('Failed to fetch brand zone:', error)
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
})

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/jobs', query: { search: searchQuery.value } })
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
.dashboard-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  margin-bottom: 30px;
  display: flex;
  justify-content: center;
  padding: 20px 0 30px 0;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 50px;
  padding: 8px 8px 8px 24px;
  width: 100%;
  max-width: 800px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.search-box:hover, .search-box:focus-within {
  border-color: #0056b3;
  box-shadow: 0 4px 12px rgba(0, 86, 179, 0.15);
}

.search-icon {
  font-size: 24px;
  color: #909399;
  margin-right: 12px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 18px;
  color: #303133;
  background: transparent;
  line-height: 1.5;
}

.search-input::placeholder {
  color: #c0c4cc;
}

.search-button {
  padding: 12px 32px;
  font-size: 18px;
  border-radius: 24px;
  background-color: #0056b3;
  border-color: #0056b3;
  font-weight: 500;
  letter-spacing: 1px;
}

.search-button:hover {
  background-color: #004494;
  border-color: #004494;
}

.main-layout {
  display: flex;
  gap: 20px;
  margin-bottom: 40px;
  height: 420px;
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
  padding: 15px 0;
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
  font-size: 15px;
  color: #303133;
  font-weight: 500;
  margin-right: auto;
}

.sub-category {
  font-size: 13px;
  color: #909399;
  margin-right: 10px;
  max-width: 100px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  width: 800px; /* Match carousel width */
  height: 375px;
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