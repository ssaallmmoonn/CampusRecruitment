<template>
  <div class="company-jobs-container">
    <!-- Filter Section -->
    <div class="filter-card section-card">
      <div class="filter-row">
        <span class="label">职位类别</span>
        <div class="filter-options">
          <span 
            v-for="cat in jobCategories" 
            :key="cat" 
            class="filter-option"
            :class="{ active: activeCategory === cat }"
            @click="handleCategoryChange(cat)"
          >
            {{ cat }}
          </span>
        </div>
      </div>
      <div class="filter-row">
        <span class="label">其他筛选</span>
        <div class="filter-selects">
          <el-select 
            v-model="filters.location" 
            placeholder="工作地点" 
            clearable 
            multiple 
            collapse-tags 
            collapse-tags-tooltip
            :max-collapse-tags="1"
            @change="fetchJobs" 
            style="width: 140px"
            :class="{ 'active-filter': filters.location.length > 0 }"
            :teleported="false"
            :popper-class="'hover-dropdown'"
          >
            <template #tag>
              <span v-if="filters.location.length > 0" class="custom-select-tag">
                工作地点 · {{ filters.location.length }}
              </span>
            </template>
            <el-option v-for="item in locations" :key="item" :label="item" :value="item">
              <div class="option-content">
                <span :class="{ 'active-text': filters.location.includes(item) }">{{ item }}</span>
                <el-icon v-if="filters.location.includes(item)" class="check-icon"></el-icon>
              </div>
            </el-option>
          </el-select>
          
          <el-select 
            v-model="filters.experience" 
            placeholder="工作经验" 
            clearable 
            @change="fetchJobs" 
            style="width: 140px"
            :class="{ 'active-filter': filters.experience }"
            :teleported="false"
          >
            <el-option label="不限" value="" />
            <el-option v-for="item in experiences" :key="item" :label="item" :value="item" />
          </el-select>
          
          <el-select 
            v-model="filters.education" 
            placeholder="学历要求" 
            clearable 
            @change="fetchJobs" 
            style="width: 140px"
            :class="{ 'active-filter': filters.education }"
            :teleported="false"
          >
            <el-option label="不限" value="" />
            <el-option v-for="item in educations" :key="item" :label="item" :value="item" />
          </el-select>
        </div>
      </div>
    </div>

    <div class="jobs-layout" v-loading="loading">
      <!-- Left: Job List -->
      <div class="jobs-list">
        <el-empty v-if="jobs.length === 0" description="暂无在招职位" />
        <div 
          v-else 
          v-for="job in jobs" 
          :key="job.id" 
          class="job-item-card"
          :class="{ active: selectedJob?.id === job.id }"
          @click="selectJob(job)"
        >
          <div class="job-info">
            <div class="job-title-row">
              <span class="job-name">{{ job.job_name }}</span>
              <span class="job-salary">{{ job.salary }}</span>
            </div>
            <div class="job-tags">
              <span>{{ job.location }}</span>
              <el-divider direction="vertical" />
              <span>{{ job.job_type }}</span>
              <el-divider direction="vertical" />
              <span>{{ job.experience_requirement }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Job Detail Panel -->
      <div class="job-detail-panel" v-if="selectedJob">
        <div class="panel-header">
          <div class="panel-title-row">
            <h3>{{ selectedJob.job_name }}</h3>
            <span class="panel-salary">{{ selectedJob.salary }}</span>
          </div>
          <div class="panel-meta">
            <el-tag size="small" effect="plain">{{ selectedJob.location }}</el-tag>
            <el-tag size="small" effect="plain">{{ selectedJob.job_type }}</el-tag>
            <el-tag size="small" effect="plain">招1人</el-tag>
          </div>
          <div class="panel-actions">
            <el-button type="primary" round @click="goToDetail(selectedJob.id)">立即投递</el-button>
            <el-button circle icon="Star" plain />
          </div>
        </div>

        <el-divider />

        <div class="panel-content">
          <div class="content-section">
            <h4>岗位职责</h4>
            <div class="text">{{ selectedJob.description }}</div>
          </div>
          <div class="content-section">
            <h4>任职要求</h4>
            <div class="text">{{ selectedJob.requirements }}</div>
          </div>
        </div>

        <div class="panel-footer">
          <el-button type="text" @click="goToDetail(selectedJob.id)">查看更多职位信息 <el-icon><ArrowRight /></el-icon></el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Star, Check } from '@element-plus/icons-vue'
import { getJobs, getCompanyJobCategories } from '@/api/jobs'

const props = defineProps({
  company: {
    type: Object,
    required: true
  }
})

const router = useRouter()
const loading = ref(false)
const jobs = ref([])
const selectedJob = ref(null)

const activeCategory = ref('全部')
const jobCategories = ref(['全部'])
const locations = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安', '重庆']
const experiences = ['无经验', '1-3年', '3-5年', '5-10年', '10年以上']
const educations = ['初中及以下', '高中', '中专/中技', '大专', '本科', '硕士', '博士']

const filters = reactive({
  location: [],
  experience: '',
  education: '',
  job_category: ''
})

const handleCategoryChange = (cat) => {
  activeCategory.value = cat
  filters.job_category = cat === '全部' ? '' : cat
  fetchJobs()
}

const fetchJobs = async () => {
  loading.value = true
  try {
    const params = {
      company: props.company.id,
      location: filters.location.length > 0 ? filters.location.join(',') : '',
      experience_requirement: filters.experience,
      degree_requirement: filters.education,
      job_category: filters.job_category,
      page_size: 20
    }
    const res = await getJobs(params)
    jobs.value = res.results || []
    if (jobs.value.length > 0 && !selectedJob.value) {
      selectedJob.value = jobs.value[0]
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const selectJob = (job) => {
  selectedJob.value = job
}

const goToDetail = (id) => {
  router.push(`/jobs/${id}`)
}

const fetchCategories = async () => {
  if (!props.company?.id) return
  try {
    const res = await getCompanyJobCategories(props.company.id)
    if (res && Array.isArray(res)) {
      jobCategories.value = ['全部', ...res]
    }
  } catch (error) {
    console.error('Failed to fetch job categories:', error)
  }
}

onMounted(() => {
  fetchCategories()
  fetchJobs()
})
</script>

<style scoped>
.section-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.filter-row {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-row .label {
  font-size: 14px;
  color: #666;
  width: 80px;
  flex-shrink: 0;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-option {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-option:hover {
  color: #409EFF;
  background-color: #ecf5ff;
}

.filter-option.active {
  background-color: #ecf5ff;
  color: #409EFF;
  font-weight: bold;
}

.filter-selects {
  display: flex;
  gap: 12px;
}

/* Layout */
.jobs-layout {
  display: flex;
  gap: 20px;
  height: calc(100vh - 350px);
  min-height: 500px;
}

.jobs-list {
  width: 350px;
  flex-shrink: 0;
  overflow-y: auto;
  padding-right: 4px;
}

.job-item-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  border: 1px solid #f0f2f5;
  transition: all 0.3s;
}

.job-item-card:hover {
  border-color: #409EFF;
  background-color: #f8fbfd;
}

.job-item-card.active {
  border-color: #409EFF;
  background-color: #ecf5ff;
}

.job-title-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.job-name {
  font-weight: bold;
  color: #333;
}

.job-salary {
  color: #409EFF;
  font-weight: bold;
}

.job-tags {
  font-size: 12px;
  color: #999;
}

/* Detail Panel */
.job-detail-panel {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.panel-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.panel-title-row h3 {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.panel-salary {
  font-size: 20px;
  color: #409EFF;
  font-weight: bold;
}

.panel-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.panel-actions {
  display: flex;
  gap: 12px;
}

.content-section {
  margin-bottom: 24px;
}

.content-section h4 {
  font-size: 16px;
  color: #333;
  margin-bottom: 12px;
  border-left: 4px solid #409EFF;
  padding-left: 12px;
}

.content-section .text {
  font-size: 14px;
  color: #666;
  line-height: 1.8;
  white-space: pre-wrap;
}

.panel-footer {
  text-align: center;
  margin-top: 40px;
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

/* Hover to open dropdown logic is tricky with standard el-select. 
   Element Plus doesn't support hover trigger natively. 
   We can simulate style but trigger is click.
   User asked for hover trigger. 
   We can use css to show dropdown? No, content is in popper.
   Best approach: Keep click for reliability or use el-dropdown.
   Given constraints, we'll focus on the visual style requested first:
   "Active state blue background and text"
*/

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

.active-filter :deep(.custom-select-tag) {
  color: #409EFF;
  font-weight: bold;
}

/* Dropdown Animation */
:deep(.el-select-dropdown__item.selected) {
  color: #409EFF;
  font-weight: bold;
}

.option-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.active-text {
  color: #409EFF;
  font-weight: bold;
}

.check-icon {
  color: #409EFF;
  font-weight: bold;
}

.custom-select-tag {
  color: #606266;
  font-size: 14px;
}
</style>