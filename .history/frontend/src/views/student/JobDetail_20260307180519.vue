<template>
  <div class="job-detail-container" v-loading="loading">
    <el-card class="job-detail-card" v-if="job">
      <div class="job-header">
        <div class="title-section">
          <h1 class="job-title">{{ job.job_name }}</h1>
          <span class="salary">{{ job.salary }}</span>
        </div>
        <div class="company-section">
          <h3>{{ job.company.company_name }}</h3>
          <p>{{ job.location }} | {{ formatDate(job.create_time) }}</p>
        </div>
      </div>

      <el-divider />

      <div class="job-content">
        <h3>Job Description</h3>
        <div class="content-text">{{ job.description }}</div>

        <h3>Requirements</h3>
        <div class="content-text">{{ job.requirements }}</div>
        
        <div class="meta-info">
          <span>Views: {{ job.views_count }}</span>
          <span>Collections: {{ job.collections_count }}</span>
        </div>
      </div>

      <el-divider />

      <div class="action-section">
        <el-button type="primary" size="large" @click="handleApply">Apply Now</el-button>
        <el-button size="large" @click="handleCollect">Collect</el-button>
      </div>
    </el-card>

    <el-empty v-else-if="!loading" description="Job not found" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getJobDetail } from '@/api/jobs'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const job = ref(null)

const fetchJobDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    job.value = await getJobDetail(id)
  } catch (error) {
    console.error('Failed to fetch job detail:', error)
    ElMessage.error('Failed to load job details')
  } finally {
    loading.value = false
  }
}

const handleApply = () => {
  ElMessage.success('Application submitted successfully! (Mock)')
  // TODO: Implement actual application logic
}

const handleCollect = () => {
  ElMessage.success('Job collected! (Mock)')
  // TODO: Implement actual collection logic
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

onMounted(() => {
  fetchJobDetail()
})
</script>

<style scoped>
.job-detail-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 0 20px;
}
.job-header {
  margin-bottom: 20px;
}
.title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.job-title {
  font-size: 28px;
  margin: 0;
  color: #303133;
}
.salary {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
}
.company-section {
  margin-top: 10px;
  color: #606266;
}
.content-text {
  white-space: pre-line;
  color: #303133;
  line-height: 1.6;
  margin-bottom: 20px;
}
.meta-info {
  margin-top: 30px;
  color: #909399;
  font-size: 14px;
  display: flex;
  gap: 20px;
}
.action-section {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}
</style>
