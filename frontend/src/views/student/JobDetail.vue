<template>
  <div class="job-detail-page" v-loading="loading">
    <div class="container">
      <!-- Back Button -->
      <div class="back-btn-container">
        <el-button @click="$router.back()" :icon="ArrowLeft" circle />
        <span class="back-text" @click="$router.back()">返回</span>
      </div>

      <div class="job-detail-layout" v-if="job">
        <!-- Left: Job Content -->
        <div class="job-content-card card-box">
          <div class="job-header">
            <div class="header-top">
              <h1 class="job-title">{{ job.job_name }}</h1>
              <div class="salary">{{ job.salary }}</div>
            </div>
            <div class="job-tags-row">
              <span class="tag-item">{{ job.location }}</span>
              <el-divider direction="vertical" />
              <span class="tag-item">{{ job.experience_requirement }}</span>
              <el-divider direction="vertical" />
              <span class="tag-item">{{ job.degree_requirement }}</span>
              <el-divider direction="vertical" />
              <span class="tag-item">{{ job.job_type }}</span>
            </div>
            <div class="job-actions-top">
               <el-button 
                 :type="isApplied ? 'info' : 'primary'" 
                 size="large" 
                 class="apply-btn" 
                 @click="handleApplyClick"
               >
                 {{ isApplied ? '已投递' : '立即投递' }}
               </el-button>
               <div class="action-icons">
                 <div class="action-item" @click="handleCollect">
                   <el-icon :class="{ collected: isCollected }"><component :is="isCollected ? 'StarFilled' : 'Star'" /></el-icon>
                   <span>{{ isCollected ? '已收藏' : '收藏' }}</span>
                 </div>
               </div>
            </div>
          </div>

          <el-divider />

          <div class="job-body">
            <div class="section-title">职位描述</div>
            
            <div class="content-block">
               <!-- <div class="sub-title">工作职责：</div> -->
               <div class="content-text">{{ job.description }}</div>
            </div>

            <div class="content-block">
               <div class="sub-title">任职要求：</div>
               <div class="content-text">{{ job.requirements }}</div>
            </div>
            
             <div class="meta-info">
              <span>{{ formatDate(job.create_time) }} 发布</span>
              <span class="separator">·</span>
              <span>浏览: {{ job.views_count }}</span>
              <span class="separator">·</span>
              <span>收藏: {{ job.collections_count }}</span>
            </div>
          </div>
        </div>

        <!-- Right: Company & Recommendations -->
        <div class="right-sidebar">
          <!-- Company Card -->
          <div class="company-card card-box" @click="goToCompanyDetail" style="cursor: pointer">
            <div class="company-header">
              <img :src="job.company?.logo || defaultCompanyLogo" alt="logo" class="company-logo" />
              <div class="company-name">{{ job.company?.company_name }}</div>
            </div>
            <div class="company-attrs">
              <div class="attr-item">
                <span class="label">所属行业：</span>
                <span class="value">{{ job.company?.industry || '未填写' }}</span>
              </div>
              <div class="attr-item">
                <span class="label">企业规模：</span>
                <span class="value">{{ job.company?.scale || '未填写' }}</span>
              </div>
              <div class="attr-item">
                <span class="label">企业性质：</span>
                <span class="value">{{ job.company?.nature || '未填写' }}</span>
              </div>
            </div>
            <el-button class="company-btn" plain round @click="goToCompanyDetail">查看企业详情</el-button>
          </div>

          <!-- Recommendation Card -->
          <div class="recommend-card card-box" v-if="recommendations.length > 0">
            <div class="rec-header">
              你可能对这些职位感兴趣
            </div>
            
            <div class="rec-list">
              <div 
                v-for="rec in recommendations" 
                :key="rec.job.id" 
                class="rec-item"
                @click="goToJobDetail(rec.job.id)"
              >
                <div class="rec-item-top">
                  <div class="rec-item-title">{{ rec.job.job_name }}</div>
                  <div class="rec-item-salary">{{ rec.job.salary }}</div>
                </div>
                <div class="rec-item-tags">
                  <span class="rec-tag-pill">{{ rec.job.job_type }}</span>
                  <span class="rec-tag-pill">{{ rec.job.degree_requirement }}</span>
                  <span class="rec-tag-pill">{{ rec.job.experience_requirement }}</span>
                </div>
                <div class="rec-item-bottom">
                  <div class="rec-company">
                    <img :src="rec.job.company?.logo || defaultCompanyLogo" class="rec-company-logo" />
                    <span class="company-text">{{ rec.job.company?.company_name }}</span>
                  </div>
                  <div class="rec-status">{{ rec.job.location }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    
      <el-empty v-else-if="!loading" description="未找到该职位" />
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
          <el-button type="primary" @click="handleApply" :disabled="!applyForm.resume">确认投递</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getJobDetail } from '@/api/jobs'
import { getRecommendations } from '@/api/recommendation'
import { applyJob, getResumes, recordBehavior, toggleCollect, checkCollectStatus, checkApplicationStatus, cancelApplication } from '@/api/recruitment'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { ArrowLeft, Star, StarFilled, Bell, Plus } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const job = ref(null)
const recommendations = ref([])
const isCollected = ref(false)
const isApplied = ref(false)
const applicationId = ref(null)
const isFromRecommendation = ref(false)
const defaultCompanyLogo = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'

// Application related
const applyDialogVisible = ref(false)
const resumes = ref([])
const applyForm = reactive({
  resume: ''
})

const fetchRecommendations = async () => {
  try {
    const currentJobId = route.params.id
    const res = await getRecommendations({ page_size: 5 }) // Fetch a few more to allow filtering
    let list = res.results || res
    
    // Filter out the current job and take the first 3
    recommendations.value = list
      .filter(item => item.job && String(item.job.id) !== String(currentJobId))
      .slice(0, 3)
  } catch (error) {
    console.error('Failed to fetch recommendations:', error)
  }
}

const fetchJobDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    job.value = await getJobDetail(id)
    
    // Check if coming from recommendation
    isFromRecommendation.value = route.query.from === 'recommendation'
    
    // Fetch recommendations for the sidebar (Only for students)
    if (userStore.isLoggedIn && userStore.role === 1) {
      fetchRecommendations()
    }
    
    // Record browse behavior only if logged in
    if (userStore.isLoggedIn) {
      // Admin doesn't need to record behavior or check application status
      if (userStore.role === 0) {
        return
      }

      recordBehavior({
          job: id,
          behavior_type: 1 // Browse
      })
      
      // Check collection status
      const res = await checkCollectStatus({ job_id: id })
      isCollected.value = res.collected

      // Check application status
      const appRes = await checkApplicationStatus(id)
      isApplied.value = appRes.applied
      if (appRes.applied) {
        applicationId.value = appRes.application_id
      }
    }
  } catch (error) {
    console.error('Failed to fetch job detail:', error)
    ElMessage.error('加载职位详情失败')
  } finally {
    loading.value = false
  }
}

const handleApplyClick = async () => {
    if (!userStore.isLoggedIn) {
        ElMessage.warning('请先登录后再投递')
        router.push('/login')
        return
    }

    if (userStore.role === 0) {
        ElMessage.info('管理员无需投递')
        return
    }

    if (isApplied.value) {
      try {
        await ElMessageBox.confirm(
          '确定要取消该职位的投递吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )
        
        await cancelApplication(applicationId.value)
        ElMessage.success('已取消投递')
        isApplied.value = false
        applicationId.value = null
      } catch (error) {
        if (error !== 'cancel') {
           console.error('Cancel application failed:', error)
           ElMessage.error('取消投递失败')
        }
      }
    } else {
       openApplyDialog()
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

const handleApply = async () => {
  try {
      await applyJob({
          job: job.value.id,
          resume: applyForm.resume,
          is_recommended: isFromRecommendation.value
      })
      ElMessage.success('简历投递成功！')
      applyDialogVisible.value = false
      
      // Update status
      isApplied.value = true
      const appRes = await checkApplicationStatus(job.value.id)
      if (appRes.applied) {
          applicationId.value = appRes.application_id
      }
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

  if (userStore.role === 0) {
      ElMessage.info('管理员无需收藏')
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

const goToJobDetail = (id) => {
  router.push({
    path: `/jobs/${id}`,
    query: { from: 'recommendation' }
  })
  window.scrollTo(0, 0)
}

// Watch for route changes to refresh job detail for same component navigation
watch(() => route.params.id, (newId) => {
  if (newId && route.name === 'JobDetail') {
    fetchJobDetail()
  }
})

const goToCompanyDetail = () => {
  if (job.value && job.value.company) {
    router.push(`/company/${job.value.company.id}`)
  }
}

onMounted(() => {
  fetchJobDetail()
})
</script>

<style scoped>
.job-detail-page {
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
  padding-bottom: 40px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.back-btn-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  cursor: pointer;
}

.back-text {
  margin-left: 10px;
  font-size: 14px;
  color: #606266;
  transition: color 0.3s;
}

.back-text:hover {
  color: #409EFF;
}

.job-detail-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.card-box {
  background: #fff;
  border-radius: 25px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  padding: 30px;
  border: 1px solid #ebeef5;
}

/* Left Content */
.job-content-card {
  flex: 1;
}

.job-header {
  margin-bottom: 20px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.job-title {
  font-size: 28px;
  font-weight: 800;
  color: #303133;
  margin: 0;
  line-height: 1.4;
}

.salary {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  white-space: nowrap;
  margin-left: 20px;
}

.job-tags-row {
  display: flex;
  align-items: center;
  color: #606266;
  font-size: 14px;
  margin-bottom: 24px;
}

.tag-item {
  margin: 0 4px;
}

.tag-item:first-child {
  margin-left: 0;
}

.job-actions-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.apply-btn {
  width: 180px;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  background: linear-gradient(90deg, #409EFF 0%, #3a8ee6 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: transform 0.2s;
}

.apply-btn:hover {
  transform: translateY(-2px);
}

.action-icons {
  display: flex;
  gap: 20px;
}

.action-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #909399;
  font-size: 14px;
  transition: color 0.3s;
}

.action-item:hover {
  color: #409EFF;
}

.action-item .el-icon {
  font-size: 18px;
  margin-right: 4px;
}

.collected {
  color: #e6a23c;
}

/* Job Body */
.job-body {
  padding-top: 10px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 20px;
  position: relative;
  padding-left: 0;
}

.content-block {
  margin-bottom: 25px;
}

.sub-title {
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
  font-size: 15px;
}

.content-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  white-space: pre-line;
}

.meta-info {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px dashed #ebeef5;
  color: #909399;
  font-size: 13px;
  display: flex;
  align-items: center;
}

.separator {
  margin: 0 8px;
}

/* Right Sidebar */
.right-sidebar {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.company-card {
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
}

.company-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #409EFF;
}

.company-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.company-logo {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  border: 1px solid #f2f2f2;
  margin-right: 15px;
  object-fit: cover;
}

.company-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  line-height: 1.4;
}

.company-attrs {
  margin-bottom: 20px;
}

.attr-item {
  display: flex;
  margin-bottom: 12px;
  font-size: 14px;
}

.attr-item .label {
  color: #909399;
  width: 80px;
  flex-shrink: 0;
}

.attr-item .value {
  color: #303133;
}

.company-btn {
  width: 100%;
  border-color: #409EFF;
  color: #409EFF;
}

.company-btn:hover {
  background-color: #ecf5ff;
}

/* Recommend Card */
.recommend-card {
  padding: 0;
  overflow: hidden;
}

.rec-header {
  background-color: #e8ecef;
  padding: 12px;
  text-align: center;
  font-weight: bold;
  color: #303133;
  font-size: 15px;
}

.rec-list {
  padding: 0 12px;
}

.rec-item {
  padding: 15px 12px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  margin: 0 -12px;
  transition: background-color 0.2s;
}

.rec-item:hover {
  background-color: #f5f7fa;
}

.rec-item:last-child {
  border-bottom: none;
}

.rec-item-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.rec-item-title {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
}

.rec-item-salary {
  font-size: 14px;
  font-weight: bold;
  color: #f56c6c;
}

.rec-item-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}

.rec-tag-pill {
  background-color: #f4f4f5;
  color: #909399;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.rec-item-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rec-company {
  display: flex;
  align-items: center;
}

.rec-company-logo {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  margin-right: 8px;
  object-fit: cover;
}

.company-text {
  font-size: 13px;
  color: #303133;
}

.rec-status {
  font-size: 12px;
  color: #909399;
}

.no-resume-tip {
  margin-top: 10px;
  color: #909399;
  font-size: 14px;
}
</style>
