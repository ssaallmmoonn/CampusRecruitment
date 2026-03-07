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
        <el-button type="primary" size="large" @click="openApplyDialog">Apply Now</el-button>
        <el-button size="large" @click="handleCollect" :type="isCollected ? 'warning' : ''" :icon="isCollected ? 'StarFilled' : 'Star'">{{ isCollected ? 'Collected' : 'Collect' }}</el-button>
      </div>
    </el-card>

    <el-empty v-else-if="!loading" description="Job not found" />

    <!-- Application Dialog -->
    <el-dialog v-model="applyDialogVisible" title="Apply for Job" width="500px">
      <el-form :model="applyForm" label-width="100px">
        <el-form-item label="Select Resume">
          <el-select v-model="applyForm.resume" placeholder="Please select a resume">
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
        You don't have any resumes yet. <router-link to="/resume">Create one now</router-link>.
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="applyDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="handleApply" :disabled="!applyForm.resume">Confirm Apply</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getJobDetail } from '@/api/jobs'
import { applyJob, getResumes, recordBehavior } from '@/api/recruitment'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const job = ref(null)
const isCollected = ref(false)

// Application related
const applyDialogVisible = ref(false)
const resumes = ref([])
const applyForm = reactive({
  resume: ''
})

const fetchJobDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    job.value = await getJobDetail(id)
    // Record browse behavior
    recordBehavior({
        job: id,
        behavior_type: 1 // Browse
    })
  } catch (error) {
    console.error('Failed to fetch job detail:', error)
    ElMessage.error('Failed to load job details')
  } finally {
    loading.value = false
  }
}

const openApplyDialog = async () => {
    applyDialogVisible.value = true
    try {
        const res = await getResumes()
        resumes.value = res.results || res
    } catch (error) {
        ElMessage.error('Failed to load resumes')
    }
}

const handleApply = async () => {
  try {
      await applyJob({
          job: job.value.id,
          resume: applyForm.resume
      })
      ElMessage.success('Application submitted successfully!')
      applyDialogVisible.value = false
  } catch (error) {
      // Error handled in interceptor
  }
}

const handleCollect = async () => {
  if (isCollected.value) return
  
  try {
      await recordBehavior({
          job: job.value.id,
          behavior_type: 2 // Collect
      })
      isCollected.value = true
      ElMessage.success('Job collected!')
  } catch (error) {
      // Error handled in interceptor
  }
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
.no-resume-tip {
    margin-top: 10px;
    color: #909399;
    font-size: 14px;
}
</style>
