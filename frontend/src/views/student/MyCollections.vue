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

    <!-- Filter Bar -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <div class="filter-row search-row">
            <el-form-item label="职位名称" class="search-item">
                <el-input 
                    v-model="filterForm.search" 
                    placeholder="请输入职位名称" 
                    clearable 
                    @change="handleFilterChange" 
                >
                    <template #prefix>
                        <el-icon><Search /></el-icon>
                    </template>
                </el-input>
            </el-form-item>
            <div class="search-actions">
                <el-form-item>
                    <el-button type="primary" @click="fetchCollections">搜索</el-button>
                    <el-button @click="resetFilter">重置</el-button>
                </el-form-item>
            </div>
        </div>
        <div class="filter-row">
            <el-form-item label="投递状态">
            <el-select 
                v-model="filterForm.is_applied" 
                placeholder="请选择投递状态" 
                clearable 
                class="filter-select"
                :class="{ 'active-filter': filterForm.is_applied }"
                :teleported="true"
                @change="handleFilterChange('is_applied')" 
                style="width: 180px"
            >
                <el-option label="已投递" value="true" />
                <el-option label="未投递" value="false" />
            </el-select>
            </el-form-item>
            <el-form-item label="排序方式">
            <el-select 
                v-model="filterForm.ordering" 
                placeholder="请选择排序方式" 
                clearable 
                class="filter-select"
                :class="{ 'active-filter': filterForm.ordering }"
                :teleported="true"
                @change="handleFilterChange('ordering')" 
                style="width: 180px"
            >
                <el-option label="投递时间 (新到旧)" value="-deliveries" />
                <el-option label="投递时间 (旧到新)" value="deliveries" />
                <el-option label="收藏时间 (新到旧)" value="-create_time" />
                <el-option label="收藏时间 (旧到新)" value="create_time" />
                <el-option label="薪资 (高到低)" value="-salary" />
                <el-option label="薪资 (低到高)" value="salary" />
            </el-select>
            </el-form-item>
            <el-form-item label="工作地点">
            <el-input v-model="filterForm.location" placeholder="请输入城市" clearable @change="handleFilterChange" style="width: 180px" />
            </el-form-item>
        </div>
      </el-form>
    </el-card>

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
                <el-button 
                    :type="item.job_detail.is_applied ? 'info' : 'primary'" 
                    @click.stop="handleApplyClick(item)"
                >
                    {{ item.job_detail.is_applied ? '已投递' : '立即投递' }}
                </el-button>
                <el-button type="primary" @click.stop="viewDetail(item.job_detail.id)">查看详情</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
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
          <el-button type="primary" @click="submitApply" :disabled="!applyForm.resume">确认投递</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getBehaviors, toggleCollect, applyJob as apiApplyJob, getResumes, checkApplicationStatus, cancelApplication } from '@/api/recruitment'
import { ElMessage, ElMessageBox } from 'element-plus'
import { StarFilled, Search } from '@element-plus/icons-vue'
import { reactive } from 'vue'

const router = useRouter()
const loading = ref(false)
const collections = ref([])
const defaultCompanyLogo = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'

// Application related
const applyDialogVisible = ref(false)
const resumes = ref([])
const applyForm = reactive({
  resume: '',
  jobId: null
})

const handleApplyClick = async (item) => {
    // Check if already applied
    try {
        const appRes = await checkApplicationStatus(item.job_detail.id)
        if (appRes.applied) {
            // If already applied, ask to cancel
            ElMessageBox.confirm(
                '确定要取消该职位的投递吗？',
                '提示',
                {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning',
                }
            ).then(async () => {
                try {
                    await cancelApplication(appRes.application_id)
                    ElMessage.success('已取消投递')
                    // Update local state
                    item.job_detail.is_applied = false
                } catch (error) {
                    console.error('Cancel application failed:', error)
                    ElMessage.error('取消投递失败')
                }
            }).catch(() => {})
            return
        }
        
        applyForm.jobId = item.job_detail.id
        openApplyDialog()
    } catch (error) {
        console.error(error)
        ElMessage.error('检查投递状态失败')
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

const submitApply = async () => {
  try {
      await apiApplyJob({
          job: applyForm.jobId,
          resume: applyForm.resume
      })
      ElMessage.success('简历投递成功！')
      applyDialogVisible.value = false
      // Update local state
      const item = collections.value.find(c => c.job_detail.id === applyForm.jobId)
      if (item) {
          item.job_detail.is_applied = true
      }
  } catch (error) {
      // Error handled in interceptor
  }
}

const filterForm = reactive({
  search: '',
  is_applied: null,
  location: '',
  ordering: null
})

const fetchCollections = async () => {
  loading.value = true
  try {
    const params = {
      behavior_type: 2,
      search: filterForm.search || undefined,
      is_applied: filterForm.is_applied || undefined,
      location: filterForm.location || undefined,
      ordering: filterForm.ordering || undefined
    }
    const res = await getBehaviors(params)
    collections.value = res.results || res
  } catch (error) {
    console.error('Fetch collections failed:', error)
    ElMessage.error('加载收藏列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = (field) => {
  if (field === 'ordering') {
      if ((filterForm.ordering === 'deliveries' || filterForm.ordering === '-deliveries') && !filterForm.is_applied) {
        filterForm.is_applied = 'true'
      } else if (filterForm.ordering !== 'deliveries' && filterForm.ordering !== '-deliveries' && filterForm.is_applied === 'true') {
        filterForm.is_applied = null
      }
  }
  
  fetchCollections()
}

const resetFilter = () => {
  filterForm.search = ''
  filterForm.is_applied = null
  filterForm.location = ''
  filterForm.ordering = null
  fetchCollections()
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

.filter-card {
    margin-bottom: 20px;
    border-radius: 12px;
}

.filter-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
    width: 100%;
    margin-bottom: 0;
}

.search-row {
    flex-wrap: nowrap;
}

.search-item {
    flex-grow: 1;
    margin-right: 10px;
}

.search-actions {
    flex-shrink: 0;
}

.search-item :deep(.el-form-item__content) {
    width: 100%;
}

.filter-form {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-bottom: -18px;
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

:deep(.el-select__wrapper:hover) {
  background-color: #e5e6eb;
}

:deep(.el-select__wrapper.is-focused) {
  box-shadow: none !important;
}

/* Fix dropdown positioning */
:deep(.el-select__popper) {
    top: 100% !important;
    left: 0 !important;
    margin-top: 8px !important;
}

/* Active State (Blue) */
.active-filter :deep(.el-select__wrapper) {
  background-color: #e6f0ff;
  color: #409EFF;
}

.active-filter :deep(.el-select__placeholder) {
  color: #409EFF !important;
}

.active-filter :deep(.el-select__selected-item) {
  color: #409EFF !important;
}

.active-filter :deep(.el-select__caret) {
  color: #409EFF;
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