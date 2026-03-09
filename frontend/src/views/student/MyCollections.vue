<template>
  <div class="collections-container">
    <div class="page-header">
      <div class="header-left">
        <div class="icon-wrapper">
          <el-icon><StarFilled /></el-icon>
        </div>
        <div class="title-content">
          <h2 class="page-title">我的收藏</h2>
          <p class="page-subtitle">管理您感兴趣的职位，随时查看和投递</p>
        </div>
      </div>
      <div class="header-right">
        <div class="stat-card">
          <span class="stat-value">{{ collections.length }}</span>
          <span class="stat-label">已收藏职位</span>
        </div>
      </div>
    </div>

    <div v-loading="loading">
      <el-empty v-if="!loading && collections.length === 0" description="暂无收藏的职位" />
      
      <el-row :gutter="20" v-else>
        <el-col :span="24" v-for="item in collections" :key="item.id" class="collection-item">
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
                <span class="time">收藏于 {{ formatDate(item.create_time) }}</span>
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
                <el-button type="danger" plain @click.stop="handleUncollect(item)">取消收藏</el-button>
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
import { getBehaviors, toggleCollect } from '@/api/recruitment'
import { ElMessage, ElMessageBox } from 'element-plus'
import { StarFilled } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const collections = ref([])
const defaultCompanyLogo = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'

const fetchCollections = async () => {
  loading.value = true
  try {
    const res = await getBehaviors({ behavior_type: 2 })
    collections.value = res.results || res
  } catch (error) {
    console.error('Fetch collections failed:', error)
    ElMessage.error('加载收藏列表失败')
  } finally {
    loading.value = false
  }
}

const handleUncollect = (item) => {
  ElMessageBox.confirm(
    '确定要取消收藏该职位吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await toggleCollect({ job_id: item.job_detail.id })
      ElMessage.success('已取消收藏')
      // Remove from list
      collections.value = collections.value.filter(c => c.id !== item.id)
    } catch (error) {
      console.error('Uncollect failed:', error)
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

const viewDetail = (id) => {
  router.push(`/jobs/${id}`)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  fetchCollections()
})
</script>

<style scoped>
.collections-container {
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
  background: linear-gradient(135deg, #ffba00 0%, #ff9c00 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(255, 156, 0, 0.2);
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

.collection-item {
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
  gap: 10px;
}
</style>