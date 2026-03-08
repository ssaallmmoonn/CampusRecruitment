<template>
  <div class="job-board">
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="Keyword">
          <el-input v-model="searchForm.search" placeholder="Job title or Company" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="Location">
          <el-input v-model="searchForm.location" placeholder="City" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetSearch">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="job-list" v-loading="loading">
      <el-empty v-if="!loading && jobs.length === 0" description="No jobs found" />
      
      <el-row :gutter="20">
        <el-col :span="24" v-for="job in jobs" :key="job.id" class="job-item-col">
          <el-card shadow="hover" class="job-card">
            <div class="job-content">
              <div class="job-header">
                <h3 class="job-title">{{ job.job_name }}</h3>
                <span class="salary">{{ job.salary }}</span>
              </div>
              
              <div class="job-meta">
                <el-tag size="small" effect="plain">{{ job.location }}</el-tag>
                <span class="separator">|</span>
                <span class="company-name">{{ job.company ? job.company.company_name : 'Unknown Company' }}</span>
                <span class="separator">|</span>
                <span class="time">{{ formatDate(job.create_time) }}</span>
              </div>
              
              <div class="job-desc-preview">
                {{ job.description ? job.description.substring(0, 100) + '...' : 'No description' }}
              </div>
            </div>
            
            <div class="job-actions">
              <el-button type="primary" size="small" @click="viewDetail(job.id)">View Details</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getJobs } from '@/api/jobs'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const jobs = ref([])

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
      ordering: '-create_time'
    }
    const response = await getJobs(params)
    // Handle both paginated and non-paginated responses
    if (response.results) {
      jobs.value = response.results
    } else if (Array.isArray(response)) {
      jobs.value = response
    } else {
      jobs.value = []
    }
  } catch (error) {
    console.error('Failed to fetch jobs:', error)
    ElMessage.error('Failed to load jobs')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchJobs()
}

const resetSearch = () => {
  searchForm.search = ''
  searchForm.location = ''
  fetchJobs()
}

const viewDetail = (id) => {
  router.push(`/jobs/${id}`)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

onMounted(() => {
  if (route.query.search) {
    searchForm.search = route.query.search
  }
  fetchJobs()
})
</script>

<style scoped>
.job-board {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.search-card {
  margin-bottom: 20px;
}
.job-item-col {
  margin-bottom: 15px;
}
.job-card {
  display: flex;
  flex-direction: column;
}
.job-content {
  flex: 1;
}
.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.job-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}
.salary {
  color: #f56c6c;
  font-weight: bold;
  font-size: 16px;
}
.job-meta {
  display: flex;
  align-items: center;
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}
.separator {
  margin: 0 10px;
  color: #dcdfe6;
}
.job-desc-preview {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 10px;
}
.job-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}
</style>
