<template>
  <div class="job-detail-container" v-loading="loading">
    <div class="back-btn-container">
      <el-button @click="$router.back()" :icon="ArrowLeft" circle />
      <span class="back-text" @click="$router.back()">返回</span>
    </div>

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
        <h3>岗位描述</h3>
        <div class="content-text">{{ job.description }}</div>

        <h3>岗位要求</h3>
        <div class="content-text">{{ job.requirements }}</div>
        
        <div class="meta-info">
          <span>浏览: {{ job.views_count }}</span>
          <span>收藏: {{ job.collections_count }}</span>
        </div>
      </div>

      <el-divider />  

      <div class="action-section">
        <el-button type="primary" size="large" @click="openApplyDialog">投递简历</el-button>
        <el-button size="large" @click="handleCollect" :type="isCollected ? 'warning' : ''" :icon="isCollected ? 'StarFilled' : 'Star'">{{ isCollected ? '已收藏' : '收藏' }}</el-button>
      </div>
    </el-card>

    <el-empty v-else-if="!loading" description="未找到该职位" />

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
          <el-button type="primary" @click="handleApply" :disabled="!applyForm.resume">确认投递</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getJobDetail } from '@/api/jobs'
import { applyJob, getResumes, recordBehavior, toggleCollect, checkCollectStatus } from '@/api/recruitment'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { ArrowLeft, Star, StarFilled } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
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
    
    // Record browse behavior only if logged in
    if (userStore.isLoggedIn) {
      recordBehavior({
          job: id,
          behavior_type: 1 // Browse
      })
      
      // Check collection status
      const res = await checkCollectStatus({ job_id: id })
      isCollected.value = res.collected
    }
  } catch (error) {
    console.error('Failed to fetch job detail:', error)
    ElMessage.error('加载职位详情失败')
  } finally {
    loading.value = false
  }
}

const openApplyDialog = async () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录后再投递')
        router.push('/login')
        return
    }
    applyDialogVisible.value = true
    try {
        const res = await getResumes()
        resumes.value = res.results || res
    } catch (error) {
        ElMessage.error('加载简历失败')
    }
}

const handleApply = async () => {
  try {
      await applyJob({
          job: job.value.id,
          resume: applyForm.resume
      })
      ElMessage.success('简历投递成功！')
      applyDialogVisible.value = false
  } catch (error) {
      // Error handled in interceptor
  }
}

const handleCollect = async () => {
  if (!userStore.isLoggedIn) {
      ElMessage.warning('请先登录后再收藏')
      router.push('/login')
      return
  }

  try {
      const res = await toggleCollect({ job_id: job.value.id })
      isCollected.value = res.collected
      ElMessage.success(res.msg)
      
      // Update collection count locally
      if (res.collected) {
        job.value.collections_count += 1
      } else {
        job.value.collections_count = Math.max(0, job.value.collections_count - 1)
      }
  } catch (error) {
      console.error('Toggle collect failed:', error)
      ElMessage.error('操作失败')
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
.back-btn-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  cursor: pointer;
}
.back-text {
  margin-left: 10px;
  font-size: 16px;
  color: #606266;
}
.back-text:hover {
  color: #409EFF;
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
