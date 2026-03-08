<template>
  <div class="job-board">
    <!-- Hero Search Section -->
    <div class="hero-section">
      <div class="search-box">
        <el-icon class="search-icon"><Search /></el-icon>
        <input 
          v-model="searchForm.search" 
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
        <div class="filter-options">
          <span 
            class="filter-option" 
            :class="{ active: !searchForm.major_requirement }" 
            @click="handleFilterChange('major_requirement', '')"
          >不限</span>
          <span 
            v-for="cat in filterOptions.majorCategories" 
            :key="cat.name"
            class="filter-option"
            :class="{ active: searchForm.major_requirement === cat.name }"
            @click="handleFilterChange('major_requirement', cat.name)"
          >
            {{ cat.name }}
          </span>
        </div>
      </div>

      <div class="filter-row" v-else>
        <span class="filter-label">职位分类</span>
        <div class="filter-options">
          <span 
            class="filter-option" 
            :class="{ active: !searchForm.job_category }" 
            @click="handleFilterChange('job_category', '')"
          >不限</span>
          <span 
            v-for="cat in filterOptions.jobCategories" 
            :key="cat.name"
            class="filter-option"
            :class="{ active: searchForm.job_category === cat.name }"
            @click="handleFilterChange('job_category', cat.name)"
          >
            {{ cat.name }}
          </span>
        </div>
      </div>

      <!-- Location Filter -->
      <div class="filter-row">
        <span class="filter-label">工作地点</span>
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
            @change="handleFilterChange"
          >
            <el-option v-for="item in filterOptions.degrees" :key="item" :label="item" :value="item" />
          </el-select>

          <el-select 
            v-model="searchForm.experience_requirement" 
            placeholder="经验要求" 
            clearable 
            class="filter-select"
            @change="handleFilterChange"
          >
            <el-option v-for="item in filterOptions.experiences" :key="item" :label="item" :value="item" />
          </el-select>

          <el-select 
            v-model="searchForm.company__industry" 
            placeholder="公司行业" 
            clearable 
            class="filter-select"
            @change="handleFilterChange"
          >
            <el-option v-for="item in filterOptions.industries" :key="item" :label="item" :value="item" />
          </el-select>

          <el-select 
            v-model="searchForm.company__nature" 
            placeholder="公司性质" 
            clearable 
            class="filter-select"
            @change="handleFilterChange"
          >
            <el-option v-for="item in filterOptions.natures" :key="item" :label="item" :value="item" />
          </el-select>

          <el-select 
            v-model="searchForm.company__scale" 
            placeholder="公司规模" 
            clearable 
            class="filter-select"
            @change="handleFilterChange"
          >
            <el-option v-for="item in filterOptions.scales" :key="item" :label="item" :value="item" />
          </el-select>
        </div>
      </div>

      <!-- Selected Conditions -->
      <div class="selected-conditions" v-if="hasActiveFilters">
        <span class="filter-label">已选条件</span>
        <div class="selected-tags">
          <el-tag 
            v-for="loc in searchForm.location" 
            :key="loc"
            closable 
            @close="handleFilterChange('location', loc)"
          >
            工作地点: {{ loc }}
          </el-tag>
          <el-tag v-if="searchForm.job_type" closable @close="handleFilterChange('job_type', '')">
            职位类型: {{ searchForm.job_type }}
          </el-tag>
          <el-tag v-if="searchForm.degree_requirement" closable @close="handleFilterChange('degree_requirement', '')">
            学历: {{ searchForm.degree_requirement }}
          </el-tag>
          <el-tag v-if="searchForm.experience_requirement" closable @close="handleFilterChange('experience_requirement', '')">
            经验: {{ searchForm.experience_requirement }}
          </el-tag>
          <el-tag v-if="searchForm.company__industry" closable @close="handleFilterChange('company__industry', '')">
            行业: {{ searchForm.company__industry }}
          </el-tag>
          <el-tag v-if="searchForm.company__nature" closable @close="handleFilterChange('company__nature', '')">
            性质: {{ searchForm.company__nature }}
          </el-tag>
          <el-tag v-if="searchForm.company__scale" closable @close="handleFilterChange('company__scale', '')">
            规模: {{ searchForm.company__scale }}
          </el-tag>
          <span class="clear-filters-btn" @click="clearFilters">清空筛选</span>
        </div>
      </div>
    </div>

    <div class="job-list" v-loading="loading">
      <el-empty v-if="!loading && jobs.length === 0" description="暂无职位" />
      
      <el-row :gutter="20">
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
              <div class="company-info">
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
                <el-button type="primary" class="apply-btn" @click.stop="applyJob(job.id)">立即投递</el-button>
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
  </div>
</template>

<script>
export default {
  name: 'JobBoard'
}
</script>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { getJobs } from '@/api/jobs'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const jobs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const defaultCompanyLogo = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'
const activeFilterTab = ref('major')

const filterOptions = {
  locations: ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安', '重庆'],
  jobTypes: ['全职', '实习'],
  degrees: ['大专', '本科', '硕士', '博士'],
  experiences: ['无经验', '1-3年', '3-5年', '5-10年', '10年以上'],
  industries: ['互联网', '金融', '教育', '制造', '医疗', '传媒', '服务业', '运营商/增值服务', '房地产/建筑'],
  natures: ['国企', '民营', '外企', '合资', '事业单位', '股份制企业'],
  scales: ['0-20人', '20-99人', '100-499人', '500-999人', '1000-9999人', '10000人以上'],
  majorCategories: [
    { name: '计算机类' }, { name: '机械类' }, { name: '电子信息类' }, 
    { name: '数学类' }, { name: '物理学类' }, { name: '化学类' },
    { name: '临床医学类' }, { name: '药学类' }, { name: '工商管理类' }, 
    { name: '公共管理类' }, { name: '外国语言文学类' }, { name: '艺术学类' }
  ],
  jobCategories: [
    { name: '研发' }, { name: '产品/运营' }, { name: '设计' }, 
    { name: '金融' }, { name: '教育' }, { name: '制造' }, 
    { name: '销售' }, { name: '市场' }, { name: '行政' }
  ]
}

const searchForm = reactive({
  search: '',
  location: [],
  job_type: '',
  degree_requirement: '',
  experience_requirement: '',
  company__industry: '',
  company__nature: '',
  company__scale: '',
  major_requirement: '',
  job_category: ''
})

const hasActiveFilters = computed(() => {
  return searchForm.location.length > 0 || 
         searchForm.job_type || 
         searchForm.degree_requirement || 
         searchForm.experience_requirement || 
         searchForm.company__industry || 
         searchForm.company__nature || 
         searchForm.company__scale ||
         searchForm.major_requirement ||
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
      } else {
        searchForm.location.splice(index, 1)
      }
    }
  } else if (typeof key === 'string') {
    searchForm[key] = value
  }
  
  currentPage.value = 1
  fetchJobs()
}

const clearFilters = () => {
  searchForm.location = []
  searchForm.job_type = ''
  searchForm.degree_requirement = ''
  searchForm.experience_requirement = ''
  searchForm.company__industry = ''
  searchForm.company__nature = ''
  searchForm.company__scale = ''
  searchForm.major_requirement = ''
  searchForm.job_category = ''
  handleSearch()
}

const fetchJobs = async () => {
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
      major_requirement: searchForm.major_requirement,
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

const applyJob = (id) => {
  // TODO: Implement apply job logic
  console.log('Apply job:', id)
  ElMessage.success('投递功能开发中')
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString()
}

onMounted(() => {
  const query = route.query
  if (query.search) searchForm.search = query.search
  if (query.location) searchForm.location = query.location.split(',')
  if (query.job_type) searchForm.job_type = query.job_type
  if (query.degree_requirement) searchForm.degree_requirement = query.degree_requirement
  if (query.experience_requirement) searchForm.experience_requirement = query.experience_requirement
  if (query.company__industry) searchForm.company__industry = query.company__industry
  if (query.company__nature) searchForm.company__nature = query.company__nature
  if (query.company__scale) searchForm.company__scale = query.company__scale
  
  if (query.page) currentPage.value = parseInt(query.page)
  if (query.page_size) pageSize.value = parseInt(query.page_size)
  
  fetchJobs()
})
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

.filter-row {
  display: flex;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid #f5f7fa;
}

.filter-row:last-child {
  border-bottom: none;
}

.filter-label {
  width: 80px;
  color: #909399;
  font-weight: 500;
  font-size: 14px;
  line-height: 28px;
  flex-shrink: 0;
}

.filter-options {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
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
</style>
