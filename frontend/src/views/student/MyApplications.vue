<template>
  <div class="applications-container">
    <div class="page-header">
      <div class="header-left">
        <div class="icon-wrapper">
          <el-icon><Postcard /></el-icon>
        </div>
        <div class="title-content">
          <h2 class="page-title">我的投递</h2>
          <p class="page-subtitle">查看您的职位申请进度和历史记录</p>
        </div>
      </div>
      <div class="header-right">
        <div class="stat-card">
          <span class="stat-value">{{ applications.length }}</span>
          <span class="stat-label">已投递职位</span>
        </div>
      </div>
    </div>

    <div v-loading="loading">
      <el-empty v-if="!loading && applications.length === 0" description="暂无投递记录" />
      
      <el-row :gutter="20" v-else>
        <el-col :span="24" v-for="item in applications" :key="item.id" class="application-item">
          <el-card shadow="hover" class="job-card" @click="viewDetail(item.job_detail.id)">
            <div class="job-content">
              <div class="job-header">
                <div class="title-row">
                  <h3 class="job-title">{{ item.job_detail.job_name }}</h3>
                  <el-tag size="small" effect="plain" class="location-tag">{{ item.job_detail.location }}</el-tag>
                </div>
                <span class="salary">{{ item.job_detail.salary }}</span>
              </div>
              
              <div class="job-tags-row">
                <span class="tag-item" v-if="item.job_detail.job_type">{{ item.job_detail.job_type }}</span>
                <span class="tag-item" v-if="item.job_detail.degree_requirement">{{ item.job_detail.degree_requirement }}</span>
                <span class="tag-item" v-if="item.job_detail.experience_requirement">{{ item.job_detail.experience_requirement }}</span>
                <span class="time">投递于 {{ formatDate(item.create_time) }}</span>
              </div>
            </div>

            <div class="job-footer">
              <div class="company-info">
                <el-avatar :size="40" :src="item.job_detail.company?.logo || defaultCompanyLogo" shape="square" class="company-logo" />
                <div class="company-details">
                  <div class="company-name-row">
                    <span class="company-name">{{ item.job_detail.company?.company_name || '未知企业' }}</span>
                  </div>
                  <div class="company-tags">
                    <span>{{ item.job_detail.company?.industry || '行业未知' }}</span>
                    <el-divider direction="vertical" />
                    <span>{{ item.job_detail.company?.scale || '规模未知' }}</span>
                    <el-divider direction="vertical" />
                    <span>{{ item.job_detail.company?.nature || '性质未知' }}</span>
                  </div>
                </div>
              </div>

              <div class="job-actions">
                <el-tag :type="getStatusType(item.status)" class="status-tag" size="large">
                  {{ getStatusText(item.status) }}
                </el-tag>
                <el-button type="danger" @click.stop="handleCancel(item)">取消投递</el-button>
                <el-button type="primary" @click.stop="viewDetail(item.job_detail.id)">查看详情</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getApplications, cancelApplication } from '@/api/recruitment'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Postcard } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const applications = ref([])
const defaultCompanyLogo = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'

const fetchApplications = async () => {
  loading.value = true
  try {
    const res = await getApplications()
    applications.value = res.results || res
  } catch (error) {
    console.error('Fetch applications failed:', error)
    ElMessage.error('加载投递记录失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (id) => {
  router.push(`/jobs/${id}`)
}

const handleCancel = (item) => {
  ElMessageBox.confirm(
    '确定要取消该职位的投递吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await cancelApplication(item.id)
        ElMessage.success('取消投递成功')
        fetchApplications()
      } catch (error) {
        console.error('Cancel application failed:', error)
        ElMessage.error('取消投递失败')
      }
    })
    .catch(() => {
      // cancel
    })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getStatusText = (status) => {
  const map = {
    1: '已投递',
    2: '被查看',
    3: '面试中',
    4: '不合适',
    5: '录用'
  }
  return map[status] || '未知状态'
}

const getStatusType = (status) => {
  const map = {
    1: 'info',
    2: 'primary',
    3: 'warning',
    4: 'danger',
    5: 'success'
  }
  return map[status] || 'info'
}

onMounted(() => {
  fetchApplications()
})
</script>

<style scoped>
.applications-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 0 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 24px 32px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(64, 158, 255, 0.2);
}

.icon-wrapper .el-icon {
  font-size: 28px;
  color: #fff;
}

.title-content {
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
}

.stat-card {
  text-align: right;
  padding: 0 16px;
  border-left: 1px solid #f0f0f0;
}

.stat-value {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.application-item {
  margin-bottom: 20px;
}

.job-card {
  cursor: pointer;
  border-radius: 25px;
  transition: all 0.3s;
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

.job-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin: 0;
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

.salary {
  font-size: 16px;
  color: #f56c6c;
  font-weight: bold;
}

.job-tags-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  align-items: center;
}

.tag-item {
  background-color: #f4f4f5;
  color: #909399;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.time {
  margin-left: auto;
  color: #909399;
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

.company-name {
  color: #303133;
  font-weight: 500;
  font-size: 14px;
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
  align-items: center;
  gap: 15px;
}

.status-tag {
  min-width: 80px;
  text-align: center;
  font-weight: bold;
}
</style>