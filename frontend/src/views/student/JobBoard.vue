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

    <div class="job-list" v-loading="loading">
      <el-empty v-if="!loading && jobs.length === 0" description="暂无职位" />
      
      <el-row :gutter="20">
        <el-col :span="24" v-for="job in jobs" :key="job.id" class="job-item-col">
          <el-card shadow="hover" class="job-card">
            <div class="job-content" @click="viewDetail(job.id)">
              <div class="job-header">
                <h3 class="job-title">{{ job.job_name }}</h3>
                <span class="salary">{{ job.salary }}</span>
              </div>

              <div class="job-tags-row">
                <span class="tag-item">{{ job.job_type }}</span>
                <span class="tag-item">{{ job.degree_requirement }}</span>
                <span class="tag-item">{{ job.experience_requirement }}</span>
              </div>
              
              <div class="job-meta">
                <el-tag size="small" effect="plain">{{ job.location }}</el-tag>
                <span class="separator">|</span>
                <span class="time">{{ formatDate(job.create_time) }}发布</span>
              </div>
              
              <div class="job-desc-preview">
                {{ job.description ? job.description.substring(0, 100) + '...' : '无描述' }}
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
import { ref, reactive, onMounted, watch } from 'vue'
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

const searchForm = reactive({
  search: '',
  location: ''
})

const fetchJobs = async () => {
  loading.value = true
  try {
    const params = {
      search: searchForm.search,
      location: searchForm.location,
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
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchForm.search,
        location: searchForm.location
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
  const { search, location, page, page_size } = route.query
  if (search) searchForm.search = search
  if (location) searchForm.location = location
  if (page) currentPage.value = parseInt(page)
  if (page_size) pageSize.value = parseInt(page_size)
  
  fetchJobs()
})
</script>

<style scoped>
.job-board {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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

.job-meta {
  margin-bottom: 10px;
  color: #909399;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.separator {
  margin: 0 8px;
  color: #dcdfe6;
}

.company-name {
  color: #303133;
  font-weight: 500;
  font-size: 14px;
}

.time {
  margin-left: auto;
}

.job-desc-preview {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
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
