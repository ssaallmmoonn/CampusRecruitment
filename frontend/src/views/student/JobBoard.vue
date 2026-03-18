<template>
  <div class="job-board">
    <!-- Hero Search Section -->
    <div class="hero-section">
      <div class="search-box">
        <el-icon class="search-icon"><Search /></el-icon>
        <input 
          v-model="searchInput" 
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

    <!-- Filter Section -->
    <div class="filter-section">
      <!-- Top Tabs: Major vs Job Category -->
      <div class="filter-tabs">
        <span 
          class="filter-tab" 
          :class="{ active: activeFilterTab === 'major' }" 
          @click="activeFilterTab = 'major'"
        >按专业筛选</span>
        <span 
          class="filter-tab" 
          :class="{ active: activeFilterTab === 'job' }" 
          @click="activeFilterTab = 'job'"
        >按职类筛选</span>
      </div>

      <!-- Category Filter Row (Dynamic) -->
      <div class="filter-row" v-if="activeFilterTab === 'major'">
        <span class="filter-label">专业分类</span>
        <div class="filter-options-container">
          <div class="filter-options">
            <span 
              class="filter-option" 
              :class="{ active: !searchForm.major }" 
              @click="handleFilterChange('major', '')"
            >不限</span>
            <span 
              v-for="major in filterOptions.majorCategories" 
              :key="major"
              class="filter-option"
              :class="{ active: searchForm.major === major }"
              @click="handleFilterChange('major', major)"
            >
              {{ major }}
            </span>
             <span 
              v-if="searchForm.major && !filterOptions.majorCategories.includes(searchForm.major)"
              class="filter-option active"
            >
              {{ searchForm.major }}
            </span>
          </div>
        </div>
        
        <!-- More Button -->
        <div class="filter-more-wrapper">
          <el-popover
            v-model:visible="showMajorPopup"
            placement="bottom-start"
            :width="800"
            trigger="click"
            popper-class="filter-popup"
          >
            <template #reference>
              <span class="filter-more-btn">
                更多专业 <el-icon><ArrowRight /></el-icon>
              </span>
            </template>
            <div class="popup-content">
              <div class="popup-column l1">
                <div 
                  v-for="l1 in allMajors" 
                  :key="l1['一级分类']" 
                  class="popup-item"
                  :class="{ active: selectedMajorL1 === l1 }"
                  @mouseenter="selectedMajorL1 = l1; selectedMajorL2 = null"
                >
                  {{ l1['一级分类'] }} <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
              <div class="popup-column l2" v-if="selectedMajorL1">
                <div 
                  v-for="l2 in selectedMajorL1['二级分类列表']" 
                  :key="l2['二级分类']" 
                  class="popup-item"
                  :class="{ active: selectedMajorL2 === l2 }"
                  @mouseenter="selectedMajorL2 = l2"
                >
                  {{ l2['二级分类'] }} <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
              <div class="popup-column l3" v-if="selectedMajorL2">
                <div 
                  v-for="l3 in selectedMajorL2['三级分类']" 
                  :key="l3" 
                  class="popup-item"
                  :class="{ active: searchForm.major === l3 }"
                  @click="handleFilterChange('major', l3); showMajorPopup = false"
                >
                  {{ l3 }}
                </div>
              </div>
            </div>
          </el-popover>
        </div>
      </div>

      <div class="filter-row" v-else>
        <span class="filter-label">职位分类</span>
        <div class="filter-options-container">
          <div class="filter-options">
            <span 
              class="filter-option" 
              :class="{ active: !searchForm.job_category }" 
              @click="handleFilterChange('job_category', '')"
            >不限</span>
            <span 
              v-for="cat in filterOptions.jobCategories" 
              :key="cat"
              class="filter-option"
              :class="{ active: searchForm.job_category === cat }"
              @click="handleFilterChange('job_category', cat)"
            >
              {{ cat }}
            </span>
             <span 
              v-if="searchForm.job_category && !filterOptions.jobCategories.includes(searchForm.job_category)"
              class="filter-option active"
            >
              {{ searchForm.job_category }}
            </span>
          </div>
        </div>

        <!-- More Button -->
        <div class="filter-more-wrapper">
          <el-popover
            v-model:visible="showJobPopup"
            placement="bottom-start"
            :width="800"
            trigger="click"
            popper-class="filter-popup"
          >
            <template #reference>
              <span class="filter-more-btn">
                更多职位 <el-icon><ArrowRight /></el-icon>
              </span>
            </template>
            <div class="popup-content">
              <div class="popup-column l1">
                <div 
                  v-for="l1 in allJobs" 
                  :key="l1['一级分类']" 
                  class="popup-item"
                  :class="{ active: selectedJobL1 === l1 }"
                  @mouseenter="selectedJobL1 = l1; selectedJobL2 = null"
                >
                  {{ l1['一级分类'] }} <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
              <div class="popup-column l2" v-if="selectedJobL1">
                <div 
                  v-for="l2 in selectedJobL1['二级分类列表']" 
                  :key="l2['二级分类']" 
                  class="popup-item"
                  :class="{ active: selectedJobL2 === l2 }"
                  @mouseenter="selectedJobL2 = l2"
                >
                  {{ l2['二级分类'] }} <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
              <div class="popup-column l3" v-if="selectedJobL2">
                <div 
                  v-for="l3 in selectedJobL2['三级分类']" 
                  :key="l3" 
                  class="popup-item"
                  :class="{ active: searchForm.job_category === l3 }"
                  @click="handleFilterChange('job_category', l3); showJobPopup = false"
                >
                  {{ l3 }}
                </div>
              </div>
            </div>
          </el-popover>
        </div>
      </div>

      <!-- Location Filter -->
      <div class="filter-row">
        <span class="filter-label">工作地点</span>
        <div class="filter-options-container">
          <div class="filter-options">
            <span 
              class="filter-option" 
              :class="{ active: searchForm.location.length === 0 }" 
              @click="handleFilterChange('location', '')"
            >全国</span>
            <span 
              v-for="city in filterOptions.locations" 
              :key="city"
              class="filter-option"
              :class="{ active: searchForm.location.includes(city) }"
              @click="handleFilterChange('location', city)"
            >
              {{ city }}
            </span>
          </div>
        </div>

        <!-- More Button -->
        <div class="filter-more-wrapper">
          <el-popover
            v-model:visible="showLocationPopup"
            placement="bottom-start"
            :width="600"
            trigger="click"
            popper-class="filter-popup"
          >
            <template #reference>
              <span class="filter-more-btn">
                更多城市 <el-icon><ArrowRight /></el-icon>
              </span>
            </template>
            <div class="popup-content">
              <div class="popup-column l1">
                <div 
                  v-for="l1 in allLocations" 
                  :key="l1['一级分类']" 
                  class="popup-item"
                  :class="{ active: selectedLocationL1 === l1 }"
                  @mouseenter="selectedLocationL1 = l1"
                >
                  {{ l1['一级分类'] }} <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
              <div class="popup-column l2" v-if="selectedLocationL1">
                <div 
                  v-for="city in selectedLocationL1['二级分类'].filter(c => !c.startsWith('全'))" 
                  :key="city" 
                  class="popup-item"
                  :class="{ active: searchForm.location.includes(city) }"
                  @click="handleFilterChange('location', city); showLocationPopup = false"
                >
                  {{ city }}
                </div>
              </div>
            </div>
          </el-popover>
        </div>
      </div>

      <!-- Job Type Filter -->
      <div class="filter-row">
        <span class="filter-label">职位类型</span>
        <div class="filter-options">
          <span 
            class="filter-option" 
            :class="{ active: !searchForm.job_type }" 
            @click="handleFilterChange('job_type', '')"
          >不限</span>
          <span 
            v-for="type in filterOptions.jobTypes" 
            :key="type"
            class="filter-option"
            :class="{ active: searchForm.job_type === type }"
            @click="handleFilterChange('job_type', type)"
          >
            {{ type }}
          </span>
        </div>
      </div>

      <!-- Other Filters -->
      <div class="filter-row">
        <span class="filter-label">其他筛选</span>
        <div class="filter-dropdowns">
          <el-select 
            v-model="searchForm.degree_requirement" 
            placeholder="学历要求" 
            clearable 
            class="filter-select"
            :class="{ 'active-filter': searchForm.degree_requirement }"
            :teleported="false"
            @change="(val) => handleFilterChange('degree_requirement', val)"
          >
            <el-option label="不限" value="" />
            <el-option v-for="item in filterOptions.degrees" :key="item" :label="item" :value="item" />
          </el-select>

          <el-select 
            v-model="searchForm.experience_requirement" 
            placeholder="经验要求" 
            clearable 
            class="filter-select"
            :class="{ 'active-filter': searchForm.experience_requirement }"
            :teleported="false"
            @change="(val) => handleFilterChange('experience_requirement', val)"
          >
            <el-option label="不限" value="" />
            <el-option v-for="item in filterOptions.experiences" :key="item" :label="item" :value="item" />
          </el-select>

          <el-select 
            v-model="searchForm.company__industry" 
            placeholder="企业行业" 
            clearable 
            class="filter-select"
            :class="{ 'active-filter': searchForm.company__industry }"
            :teleported="false"
            @change="(val) => handleFilterChange('company__industry', val)"
          >
            <el-option label="不限" value="" />
            <el-option v-for="item in filterOptions.industries" :key="item" :label="item" :value="item" />
          </el-select>

          <el-select 
            v-model="searchForm.company__nature" 
            placeholder="企业性质" 
            clearable 
            class="filter-select"
            :class="{ 'active-filter': searchForm.company__nature }"
            :teleported="false"
            @change="(val) => handleFilterChange('company__nature', val)"
          >
            <el-option label="不限" value="" />
            <el-option v-for="item in filterOptions.natures" :key="item" :label="item" :value="item" />
          </el-select>

          <el-select 
            v-model="searchForm.company__scale" 
            placeholder="企业规模" 
            clearable 
            class="filter-select"
            :class="{ 'active-filter': searchForm.company__scale }"
            :teleported="false"
            @change="(val) => handleFilterChange('company__scale', val)"
          >
            <el-option label="不限" value="" />
            <el-option v-for="item in filterOptions.scales" :key="item" :label="item" :value="item" />
          </el-select>
        </div>
      </div>

      <!-- Selected Conditions -->
      <div class="selected-conditions" v-if="hasActiveFilters">
        <span class="filter-label">已选条件</span>
        <div class="selected-tags">
          <el-tag v-if="searchForm.search" closable @close="handleFilterChange('search', '')">
            关键词: {{ searchForm.search }}
          </el-tag>
          <el-tag 
            v-for="loc in searchForm.location" 
            :key="loc"
            closable 
            @close="handleFilterChange('location', loc)"
          >
            工作地点: {{ loc }}
          </el-tag>
          <el-tag v-if="searchForm.job_type && searchForm.job_type !== ''" closable @close="handleFilterChange('job_type', '')">
            职位类型: {{ searchForm.job_type }}
          </el-tag>
          <el-tag v-if="searchForm.degree_requirement && searchForm.degree_requirement !== ''" closable @close="handleFilterChange('degree_requirement', '')">
            学历: {{ searchForm.degree_requirement }}
          </el-tag>
          <el-tag v-if="searchForm.experience_requirement && searchForm.experience_requirement !== ''" closable @close="handleFilterChange('experience_requirement', '')">
            经验: {{ searchForm.experience_requirement }}
          </el-tag>
          <el-tag v-if="searchForm.company__industry && searchForm.company__industry !== ''" closable @close="handleFilterChange('company__industry', '')">
            行业: {{ searchForm.company__industry }}
          </el-tag>
          <el-tag v-if="searchForm.company__nature && searchForm.company__nature !== ''" closable @close="handleFilterChange('company__nature', '')">
            性质: {{ searchForm.company__nature }}
          </el-tag>
          <el-tag v-if="searchForm.company__scale && searchForm.company__scale !== ''" closable @close="handleFilterChange('company__scale', '')">
            规模: {{ searchForm.company__scale }}
          </el-tag>
          <el-tag v-if="searchForm.major && searchForm.major !== ''" closable @close="handleFilterChange('major', '')">
            专业: {{ searchForm.major }}
          </el-tag>
          <el-tag v-if="searchForm.job_category && searchForm.job_category !== ''" closable @close="handleFilterChange('job_category', '')">
            类别: {{ searchForm.job_category }}
          </el-tag>
          <span class="clear-filters-btn" @click="clearFilters">清空筛选</span>
        </div>
      </div>
    </div>

    <div class="job-list" v-loading="loading">
      <div v-if="!loading && jobs.length === 0" class="no-results-box">
        <el-empty description=" " :image-size="200">
           <template #description>
             <p class="no-results-text">没有符合条件的职位，请修改筛选条件后再试</p>
           </template>
        </el-empty>
      </div>
      
      <el-row :gutter="20" v-else>
        <el-col :span="24" v-for="job in jobs" :key="job.id" class="job-item-col">
          <el-card shadow="hover" class="job-card">
            <div class="job-content" @click="viewDetail(job.id)">
              <div class="job-header">
                <div class="title-row">
                  <h3 class="job-title">{{ job.job_name }}</h3>
                  <el-tag size="small" effect="plain" class="location-tag">{{ job.location }}</el-tag>
                </div>
                <span class="salary">{{ job.salary }}</span>
              </div>

              <div class="job-tags-row">
                <span class="tag-item">{{ job.job_type }}</span>
                <span class="tag-item">{{ job.degree_requirement }}</span>
                <span class="tag-item">{{ job.experience_requirement }}</span>
              </div>
              
              <div class="job-desc-row">
                <div class="job-desc-preview">
                  {{ job.description ? job.description.substring(0, 100) + '...' : '无描述' }}
                </div>
                <span class="time">{{ formatDate(job.create_time) }}发布</span>
              </div>
            </div>
            
            <div class="job-footer">
              <div class="company-info" @click.stop="goToCompanyDetail(job.company?.id)">
                <el-avatar :size="40" :src="job.company?.logo || defaultCompanyLogo" shape="square" class="company-logo" />
                <div class="company-details">
                  <div class="company-name-row">
                    <span class="company-name">{{ job.company?.company_name || '未知企业' }}</span>
                  </div>
                  <div class="company-tags">
                    <span>{{ job.company?.industry || '行业未知' }}</span>
                    <el-divider direction="vertical" />
                    <span>{{ job.company?.scale + '人' || '规模未知' }}</span>
                    <el-divider direction="vertical" />
                    <span>{{ job.company?.nature || '性质未知' }}</span>
                  </div>
                </div>
              </div>

              <div class="job-actions">
  <el-button 
    :type="job.is_applied ? 'info' : 'primary'" 
    class="apply-btn" 
    @click.stop="applyJob(job.id)"
  >
    {{ job.is_applied ? '已投递' : '立即投递' }}
  </el-button>
  <el-button @click.stop="viewDetail(job.id)">查看详情</el-button>
</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- Pagination -->
      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :background="true"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Application Dialog -->
    <el-dialog v-model="applyDialogVisible" title="投递简历" width="500px">
      <el-form :model="applyForm" label-width="100px">
        <el-form-item label="选择简历">
          <el-select v-model="applyForm.resume" placeholder="请选择一份简历">
            <el-option
              v-for="item in resumes"
              :key="item.id"
              :label="item.resume_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <div v-if="resumes.length === 0" class="no-resume-tip">
        您还没有任何简历，请先创建一份 <router-link to="/resume">创建简历</router-link>.
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="applyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitApply" :disabled="!applyForm.resume">确认投递</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'JobBoard'
}
</script>

<script setup>
import { ref, reactive, onMounted, onActivated, watch, computed } from 'vue'
import { getJobs } from '@/api/jobs'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { applyJob as apiApplyJob, getResumes, checkApplicationStatus, cancelApplication } from '@/api/recruitment'
import { useUserStore } from '@/stores/user'

import majorJson from '@/assets/major.json'
import jobJson from '@/assets/jobs.json'
import provinceJson from '@/assets/provinces.json'
import { ArrowRight, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const jobs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const defaultCompanyLogo = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'
const activeFilterTab = ref('major')

// Data Processing
const allMajors = majorJson['专业分类'] || []
const allJobs = jobJson['职位分类'] || []
const allLocations = provinceJson['地区分类'] || []

// Flatten locations for easier access
const flatLocations = []
allLocations.forEach(p => {
  if (p['二级分类']) {
    flatLocations.push(...p['二级分类'].filter(c => !c.startsWith('全')))
  }
})

// Top items for display (Hot/Common items)
const topMajors = ['计算机科学与技术', '软件工程', '会计学', '金融学', '英语', '法学', '临床医学', '土木工程', '机械设计制造及其自动化', '电气工程及其自动化']
const topJobCategories = ['Java开发', '前端开发', '产品经理', '销售专员', '会计', '人力资源专员', '行政专员', '平面设计', '运营专员']
const topLocations = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安', '重庆']

// Popup States
const showMajorPopup = ref(false)
const showJobPopup = ref(false)
const showLocationPopup = ref(false)

// Popup Selections
const selectedMajorL1 = ref(null)
const selectedMajorL2 = ref(null)

const selectedJobL1 = ref(null)
const selectedJobL2 = ref(null)

const selectedLocationL1 = ref(null)

const filterOptions = reactive({
  locations: topLocations,
  jobTypes: ['全职', '实习'],
  degrees: ['初中及以下', '高中', '中专/中技', '大专', '本科', '硕士', '博士', '学历不限'],
  experiences: ['无经验', '1-3年', '3-5年', '5-10年', '10年以上'],
  industries: ['互联网', '金融', '教育', '制造', '医疗', '传媒', '服务业', '运营商/增值服务', '房地产/建筑'],
  natures: ['国企', '民营', '外企', '合资', '事业单位', '股份制企业'],
  scales: ['0-20人', '20-99人', '100-499人', '500-999人', '1000-9999人', '10000人以上'],
  majorCategories: topMajors, // Display specific majors directly
  jobCategories: topJobCategories // Display specific jobs directly
})

const searchInput = ref('')
const searchForm = reactive({
  search: '',
  location: [],
  job_type: '',
  degree_requirement: '',
  experience_requirement: '',
  company__industry: '',
  company__nature: '',
  company__scale: '',
  major: '',
  job_category: ''
})

const hasActiveFilters = computed(() => {
  return searchForm.search ||
         searchForm.location.length > 0 || 
         searchForm.job_type || 
         searchForm.degree_requirement || 
         searchForm.experience_requirement || 
         searchForm.company__industry || 
         searchForm.company__nature || 
         searchForm.company__scale ||
         searchForm.major ||
         searchForm.job_category
})

const handleFilterChange = (key, value) => {
  if (key === 'location') {
    if (value === '') {
      searchForm.location = []
    } else {
      const index = searchForm.location.indexOf(value)
      if (index === -1) {
        searchForm.location.push(value)
        // Optimization: Move selected location to front if not in topLocations
        if (!filterOptions.locations.includes(value)) {
           filterOptions.locations.pop()
           filterOptions.locations.unshift(value)
        }
      } else {
        searchForm.location.splice(index, 1)
      }
    }
  } else if (key === 'search') {
    searchForm.search = value
    if (value === '') {
      searchInput.value = ''
    }
  } else if (typeof key === 'string') {
    searchForm[key] = value

    // Logic to move selected item to front for Major and Job Category
    if (key === 'major' && value) {
      if (!filterOptions.majorCategories.includes(value)) {
        // Remove the last item to keep length consistent
        filterOptions.majorCategories.pop()
        // Add new item to the front
        filterOptions.majorCategories.unshift(value)
      }
    } else if (key === 'job_category' && value) {
      if (!filterOptions.jobCategories.includes(value)) {
        filterOptions.jobCategories.pop()
        filterOptions.jobCategories.unshift(value)
      }
    }
  }
  
  currentPage.value = 1
  fetchJobs()
}

const clearFilters = () => {
  searchForm.search = ''
  searchInput.value = ''
  searchForm.location = []
  searchForm.job_type = ''
  searchForm.degree_requirement = ''
  searchForm.experience_requirement = ''
  searchForm.company__industry = ''
  searchForm.company__nature = ''
  searchForm.company__scale = ''
  searchForm.major = ''
  searchForm.job_category = ''
  currentPage.value = 1
  fetchJobs()
}

const fetchJobs = async () => {
  // If component is deactivated, do NOT fetch. 
  // This is a safety check for async calls.
  if (route.name !== 'JobBoard') return

  loading.value = true
  try {
    const params = {
      search: searchForm.search,
      location: searchForm.location.length > 0 ? searchForm.location.join(',') : '',
      job_type: searchForm.job_type,
      degree_requirement: searchForm.degree_requirement,
      experience_requirement: searchForm.experience_requirement,
      company__industry: searchForm.company__industry,
      company__nature: searchForm.company__nature,
      company__scale: searchForm.company__scale,
      major: searchForm.major,
      job_category: searchForm.job_category,
      ordering: '-create_time',
      page: currentPage.value,
      page_size: pageSize.value
    }
    const response = await getJobs(params)
    // Handle both paginated and non-paginated responses
    if (response.results) {
      jobs.value = response.results
      total.value = response.count
    } else if (Array.isArray(response)) {
      jobs.value = response
      total.value = response.length
    } else {
      jobs.value = []
      total.value = 0
    }
    
    // Update URL query
    router.replace({
      query: {
        ...route.query,
        ...params
      }
    })
  } catch (error) {
    console.error('Failed to fetch jobs:', error)
    ElMessage.error('加载职位失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (!searchInput.value || !searchInput.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  searchForm.search = searchInput.value
  currentPage.value = 1
  fetchJobs()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchJobs()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchJobs()
}

const viewDetail = (id) => {
  router.push(`/jobs/${id}`)
}

const goToCompanyDetail = (companyId) => {
  if (companyId) {
    router.push(`/company/${companyId}`)
  }
}



// ... existing imports

const userStore = useUserStore()

// Application related
const applyDialogVisible = ref(false)
const resumes = ref([])
const applyForm = reactive({
  resume: '',
  jobId: null
})

const handleApplyClick = async (jobId) => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录后再投递')
        router.push('/login')
        return
    }
    
    // Check if already applied
    try {
        const appRes = await checkApplicationStatus(jobId)
        if (appRes.applied) {
            // If already applied, ask to cancel
            ElMessageBox.confirm(
                '确定要取消该职位的投递吗？',
                '提示',
                {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning',
                }
            ).then(async () => {
                try {
                    await cancelApplication(appRes.application_id)
                    ElMessage.success('已取消投递')
                    // Refresh job list to update status
                    fetchJobs()
                } catch (error) {
                    console.error('Cancel application failed:', error)
                    ElMessage.error('取消投递失败')
                }
            }).catch(() => {})
            return
        }
        
        applyForm.jobId = jobId
        openApplyDialog()
    } catch (error) {
        console.error(error)
        ElMessage.error('检查投递状态失败')
    }
}

const openApplyDialog = async () => {
    applyDialogVisible.value = true
    try {
        const res = await getResumes()
        resumes.value = res.results || res
    } catch (error) {
        ElMessage.error('加载简历失败')
    }
}

const submitApply = async () => {
  try {
      await apiApplyJob({
          job: applyForm.jobId,
          resume: applyForm.resume
      })
      ElMessage.success('简历投递成功！')
      applyDialogVisible.value = false
      // Refresh job list to update status
      fetchJobs()
  } catch (error) {
      // Error handled in interceptor
  }
}

const applyJob = (id) => {
  handleApplyClick(id)
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString()
}

const isActivated = ref(false)

onMounted(() => {
  // Initial load
  if (!isActivated.value) {
      initPage()
  }
})

onActivated(() => {
    isActivated.value = true
    // When returning from keep-alive, we don't need to refetch if we want to keep scroll
    // But we might want to update filters if URL changed from outside? 
    // Usually keep-alive handles state.
    
    // Check if we need to restore anything specific or just let it be.
    // If the user navigates back, the component is activated.
})

const initPage = () => {
  const queryParams = route.query
  
  // Reset all filters first to ensure clean state
  // But since searchForm is reactive and initialized empty, we just overwrite if present
  
  // NOTE: We do NOT restore searchForm.search from queryParams.search to satisfy 
  // "clear text in search box on refresh" requirement.
  // The searchInput is also initialized to empty string.
  
  if (queryParams.location) searchForm.location = queryParams.location.split(',')
  if (queryParams.job_type) searchForm.job_type = queryParams.job_type
  if (queryParams.degree_requirement) searchForm.degree_requirement = queryParams.degree_requirement
  if (queryParams.experience_requirement) searchForm.experience_requirement = queryParams.experience_requirement
  if (queryParams.company__industry) searchForm.company__industry = queryParams.company__industry
  if (queryParams.company__nature) searchForm.company__nature = queryParams.company__nature
  if (queryParams.company__scale) searchForm.company__scale = queryParams.company__scale
  
  if (queryParams.major) {
    searchForm.major = queryParams.major
    activeFilterTab.value = 'major'
  }
  if (queryParams.job_category) {
    searchForm.job_category = queryParams.job_category
    activeFilterTab.value = 'job'
  }
  
  if (queryParams.page) currentPage.value = parseInt(queryParams.page)
  if (queryParams.page_size) pageSize.value = parseInt(queryParams.page_size)
  
  // Apply optimizations for initial load if major/job_category/location is present in query
  if (queryParams.major) {
      if (!filterOptions.majorCategories.includes(queryParams.major)) {
        filterOptions.majorCategories.pop()
        filterOptions.majorCategories.unshift(queryParams.major)
      }
      activeFilterTab.value = 'major'
  }
  if (queryParams.job_category) {
      if (!filterOptions.jobCategories.includes(queryParams.job_category)) {
        filterOptions.jobCategories.pop()
        filterOptions.jobCategories.unshift(queryParams.job_category)
      }
      activeFilterTab.value = 'job'
  }
  if (queryParams.location) {
      const locs = queryParams.location.split(',')
      if (locs.length > 0) {
          const firstLoc = locs[0]
          if (!filterOptions.locations.includes(firstLoc)) {
            filterOptions.locations.pop()
            filterOptions.locations.unshift(firstLoc)
          }
      }
  }

  fetchJobs()
}

const lastQueryStr = ref(JSON.stringify(route.query))

// Watch route changes to update filters or clear them
watch(
  () => route.query,
  (newQuery) => {
    // Only fetch if we are actually on the JobBoard page.
    if (route.name !== 'JobBoard') return

    // If query hasn't actually changed (deep comparison), do nothing.
    // This prevents re-fetching when returning from keep-alive details page
    // where route object is updated but params are effectively same.
    const newQueryStr = JSON.stringify(newQuery)
    if (newQueryStr === lastQueryStr.value) return
    lastQueryStr.value = newQueryStr

    // Reset all filters first - CRITICAL for "Clear conditions when re-entering"
    // If newQuery is empty (e.g. clicking "Job Board" link), this clears everything.
    searchForm.search = ''
    searchInput.value = ''
    searchForm.location = []
    searchForm.job_type = ''
    searchForm.degree_requirement = ''
    searchForm.experience_requirement = ''
    searchForm.company__industry = ''
    searchForm.company__nature = ''
    searchForm.company__scale = ''
    searchForm.major = ''
    searchForm.job_category = ''
    
    // Reset active tab to default unless specified?
    // If I go from ?major=X to /jobs, should tab stay 'major'? 
    // Usually yes, or reset to default. 
    // Let's keep current tab unless query specifies otherwise.

    // Apply new query params
    if (newQuery.search) {
       searchForm.search = newQuery.search
       searchInput.value = newQuery.search
    }
    if (newQuery.location) searchForm.location = newQuery.location.split(',')
    if (newQuery.job_type) searchForm.job_type = newQuery.job_type
    if (newQuery.degree_requirement) searchForm.degree_requirement = newQuery.degree_requirement
    if (newQuery.experience_requirement) searchForm.experience_requirement = newQuery.experience_requirement
    if (newQuery.company__industry) searchForm.company__industry = newQuery.company__industry
    if (newQuery.company__nature) searchForm.company__nature = newQuery.company__nature
    if (newQuery.company__scale) searchForm.company__scale = newQuery.company__scale
    
    if (newQuery.major) {
      searchForm.major = newQuery.major
      activeFilterTab.value = 'major'
    }
    if (newQuery.job_category) {
      searchForm.job_category = newQuery.job_category
      activeFilterTab.value = 'job'
    }
    
    // Optimization for filter row display
    if (newQuery.major) {
       if (!filterOptions.majorCategories.includes(newQuery.major)) {
          filterOptions.majorCategories.pop()
          filterOptions.majorCategories.unshift(newQuery.major)
       }
    }
    if (newQuery.job_category) {
       if (!filterOptions.jobCategories.includes(newQuery.job_category)) {
          filterOptions.jobCategories.pop()
          filterOptions.jobCategories.unshift(newQuery.job_category)
       }
    }
    
    currentPage.value = newQuery.page ? parseInt(newQuery.page) : 1
    
    fetchJobs()
  }
)
</script>

<style scoped>
.job-board {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.filter-section {
  background: white;
  border-radius: 12px;
  padding: 0 24px 20px 24px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #ebeef5;
}

.filter-tabs {
  display: flex;
  border-bottom: 1px solid #f5f7fa;
  margin: 0 -24px 10px -24px;
  padding: 0 24px;
  background-color: #fafafa;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
}

.filter-tab {
  padding: 16px 24px;
  font-size: 15px;
  color: #606266;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
  font-weight: 500;
}

.filter-tab:hover {
  color: #409EFF;
}

.filter-tab.active {
  color: #409EFF;
  background-color: #fff;
  font-weight: bold;
}

.filter-tab.active::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #409EFF;
}

.filter-options {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  height: 28px; /* Limit height to one line */
  overflow: hidden; /* Hide overflow */
  position: relative;
}

.filter-options.expanded {
  height: auto;
  overflow: visible;
}

/* Make filter-option smaller to fit more */
.filter-option {
  padding: 4px 10px;
  font-size: 14px;
  line-height: 20px;
  white-space: nowrap;
}

/* Position "More" button absolutely to the right if needed, or just let it flow?
   User said: "fill this line as much as possible, but once it recognizes that it wants to wrap, stop filling"
   This implies a single line layout with overflow handling or a smart list that cuts off.
   
   If we use flex-wrap: wrap and height: 28px + overflow: hidden, items that wrap will be hidden.
   But the "More" button needs to be visible at the end.
   
   A pure CSS way is hard because we don't know which item wraps.
   
   However, since we have a fixed list of "top items", maybe we can just render them all and let flex-wrap hide them?
   But we need the "More" button to be the last visible item.
   
   Alternative: Flex with hidden overflow.
   But user wants "More" button at the end of the line.
   
   Let's try this:
   Use a container with max-height corresponding to one line.
   Put the "More" button as the last element in DOM.
   But if previous items fill the line, "More" button might wrap and be hidden.
   
   Solution:
   We can't easily detect wrap in CSS.
   We can try to just list a reasonable number of items (e.g. top 10) and hope they fit?
   The current implementation lists topMajors (10 items).
   Let's ensure the container handles them gracefully.
   
   User's request: "fill this line as much as possible... stop filling once it wraps".
   This sounds like: Show as many as fit, then show "More".
   
   Let's use a simpler approach:
   1. Keep `flex-wrap: wrap` but restrict height to show only one line.
   2. Position the "More" button absolutely at the right end of the container?
      No, that might cover items.
      
   Actually, the user might just mean: "Don't show a second line of specific options. Just one line. And the 'More' button should be accessible."
   
   If I set `height: 30px; overflow: hidden;` on `.filter-options`, and put the "More" button float right?
   
   Let's try `flex-wrap: nowrap` with `overflow: hidden`? 
   No, `flex-wrap: wrap` + fixed height is better to "stop filling".
   But the "More" button must be visible.
   
   Let's try to put the "More" button OUTSIDE the `.filter-options` div, but inside `.filter-row`.
   So `.filter-row` has: Label | Options (flex 1, hidden overflow) | More Button
*/

.filter-row {
  display: flex;
  align-items: center; /* Align vertically center */
  padding: 12px 0;
  border-bottom: 1px solid #f5f7fa;
}

.filter-label {
  width: 80px;
  color: #909399;
  font-weight: 500;
  font-size: 14px;
  line-height: 28px;
  flex-shrink: 0;
}

.filter-options-container {
  flex: 1;
  display: flex;
  align-items: center;
  overflow: hidden;
  height: 28px; /* Fixed height for single line */
  margin-right: 10px;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  /* Negative margin to counteract gap if needed, but let's just rely on container clipping */
}

.filter-more-wrapper {
  flex-shrink: 0;
  margin-left: auto; /* Push to right if container doesn't fill? No, it's a separate flex item in row */
}

.filter-option {
  padding: 4px 12px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
  color: #303133;
  transition: all 0.3s;
  line-height: 20px;
}

.filter-option:hover {
  color: #409EFF;
  background-color: #ecf5ff;
}

.filter-option.active {
  color: #fff;
  background-color: #409EFF;
  font-weight: 500;
}

.filter-dropdowns {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-select {
  width: 140px;
}

.selected-conditions {
  display: flex;
  align-items: center;
  padding-top: 16px;
  margin-top: 4px;
  border-top: 1px dashed #ebeef5;
}

.selected-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  flex: 1;
}

.clear-filters-btn {
  margin-left: auto;
  font-size: 14px;
  color: #909399;
  cursor: pointer;
  transition: color 0.3s;
}

.clear-filters-btn:hover {
  color: #409EFF;
}

:deep(.el-tag) {
  border-radius: 4px;
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

.job-list {
  min-height: 400px;
  
}

.job-item-col {
  margin-bottom: 20px;
}

.job-card {
  transition: all 0.3s;
  cursor: pointer;
  border-radius: 25px;
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.job-content {
  margin-bottom: 15px;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.location-tag {
  border: none;
  background: transparent;
  padding: 0;
  font-size: 14px;
  color: #3e81e6;
}

.location-tag::before {
  content: '[';
  margin-right: 2px;
}

.location-tag::after {
  content: ']';
  margin-left: 2px;
}

.job-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.salary {
  font-size: 16px;
  color: #f56c6c;
  font-weight: bold;
}

.job-tags-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.tag-item {
  background-color: #f4f4f5;
  color: #909399;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.job-desc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #909399;
  font-size: 14px;
}

.job-desc-preview {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
  flex: 1;
  margin-right: 20px;
}

.time {
  white-space: nowrap;
  font-size: 12px;
}

.job-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}

.company-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.company-info:hover .company-name {
  color: #60b3ff;
}

.company-logo {
  margin-right: 12px;
  background-color: #f5f7fa;
}

.company-details {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.company-name-row {
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.company-name {
  color: #303133;
  font-weight: 500;
  font-size: 14px;
  transition: color 0.3s;
}

.company-tags {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.company-tags .el-divider--vertical {
  margin: 0 8px;
  height: 10px;
}

.job-actions {
  display: flex;
}

.apply-btn {
  margin-right: 12px;
}

.pagination-container {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

/* Filter Styles Override */
:deep(.el-select) {
  --el-select-border-color-hover: transparent;
  --el-select-input-focus-border-color: transparent;
}

:deep(.el-select__wrapper) {
  background-color: #f2f3f5;
  border-radius: 20px;
  border: none !important;
  box-shadow: none !important;
  padding: 4px 12px;
  min-height: 32px;
  transition: all 0.3s;
}

:deep(.el-select__wrapper:hover) {
  background-color: #e5e6eb;
}

:deep(.el-select__wrapper.is-focused) {
  box-shadow: none !important;
}

/* Active State (Blue) */
.active-filter :deep(.el-select__wrapper) {
  background-color: #e6f0ff;
  color: #409EFF;
}

.active-filter :deep(.el-select__placeholder) {
  color: #409EFF;
  font-weight: bold;
}

.active-filter :deep(.el-select__caret) {
  color: #409EFF;
}

/* Dropdown Animation */
/* Popup Styles */
.filter-more-btn {
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  padding: 4px 12px;
  display: inline-flex;
  align-items: center;
  transition: all 0.3s;
  margin-left: auto;
  border-radius: 4px;
}

.filter-more-btn:hover {
  color: #409EFF;
  background-color: #ecf5ff;
}

.filter-more-btn .el-icon {
  margin-left: 4px;
}

/* Global popup style (cannot use scoped for popper-class) */
</style>

<style>
.filter-popup {
  padding: 0 !important;
}

.popup-content {
  display: flex;
  height: 300px;
}

.popup-column {
  flex: 1;
  overflow-y: auto;
  border-right: 1px solid #ebeef5;
}

.popup-column:last-child {
  border-right: none;
}

.popup-item {
  padding: 10px 16px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.popup-item:hover {
  background-color: #f5f7fa;
  color: #409EFF;
}

.popup-item.active {
  color: #409EFF;
  font-weight: 500;
  background-color: #ecf5ff;
}

.no-results-box {
  padding: 40px 0;
  background: white;
  border-radius: 12px;
  text-align: center;
}

.no-results-text {
  font-size: 16px;
  color: #606266;
  margin-top: 10px;
}
</style>
