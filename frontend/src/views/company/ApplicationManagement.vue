<template>
  <div class="application-management">
    <!-- Search Bar -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item>
          <el-input v-model="searchForm.search" placeholder="请输入关键字查询" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Application Table -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="applications"
        style="width: 100%"
      >
        <el-table-column label="企业名称" min-width="120" show-overflow-tooltip>
             <template #default="scope">
                 <span class="company-name">{{ scope.row.job_detail?.company?.company_name || '-' }}</span>
             </template>
        </el-table-column>
        <el-table-column label="岗位名称" min-width="120" show-overflow-tooltip>
            <template #default="scope">
                <span class="job-name">{{ scope.row.job_detail?.job_name || '-' }}</span>
            </template>
        </el-table-column>
        <el-table-column label="投递用户" min-width="80" show-overflow-tooltip>
             <template #default="scope">
                 {{ scope.row.student_detail?.name || scope.row.student_detail?.username || '-' }}
             </template>
        </el-table-column>
        <el-table-column label="投递简历" width="150">
          <template #default="scope">
            <el-button link type="primary" @click="viewResume(scope.row)">查看简历</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="投递时间" width="200">
            <template #default="scope">
                {{ formatTime(scope.row.create_time) }}
            </template>
        </el-table-column>
        <el-table-column label="浏览量" width="100" align="center">
            <template #default="scope">
                {{ scope.row.job_detail?.views_count || 0 }}
            </template>
        </el-table-column>
        <el-table-column label="收藏量" width="100" align="center">
            <template #default="scope">
                {{ scope.row.job_detail?.collections_count || 0 }}
            </template>
        </el-table-column>
        <el-table-column label="投递量" width="100" align="center">
            <template #default="scope">
                {{ scope.row.job_detail?.deliveries_count || 0 }}
            </template>
        </el-table-column>
        <el-table-column label="沟通" width="100">
          <template #default="scope">
             <el-badge :value="scope.row.unread_count" :hidden="!scope.row.unread_count" class="msg-badge">
               <el-button link type="primary" @click="openChat(scope.row)">联系用户</el-button>
             </el-badge>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="投递状态" width="150">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusLabel(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="scope">
             <div class="action-buttons">
                <el-button 
                    type="danger" 
                    size="small" 
                    @click="handleStatusUpdate(scope.row, 3)"
                    :disabled="scope.row.status === 3"
                >不合适</el-button>
                <el-button 
                    type="primary" 
                    size="small" 
                    @click="handleStatusUpdate(scope.row, 2)"
                    :disabled="scope.row.status === 2"
                >面试中</el-button>
                <el-button 
                    type="success" 
                    size="small" 
                    @click="handleStatusUpdate(scope.row, 4)"
                    :disabled="scope.row.status === 4"
                >通过</el-button>
                <el-button 
                    type="warning" 
                    size="small" 
                    @click="handleStatusUpdate(scope.row, 5)"
                    :disabled="scope.row.status === 5"
                >不通过</el-button>
             </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Resume Dialog -->
    <el-dialog v-model="resumeDialogVisible" title="简历详情" width="800px" custom-class="preview-dialog">
        <div class="resume-preview" v-if="currentResume && currentResume.content">
        <!-- Header -->
        <div class="preview-header">
           <div class="preview-info">
             <h1 class="preview-name">{{ currentResume.content.personal_info?.name || currentResume.student_detail?.name || '未填写姓名' }}</h1>
             <div class="preview-basic-info">
                <span v-if="currentResume.content.personal_info?.gender">{{ currentResume.content.personal_info.gender }}</span>
                <span class="sep" v-if="currentResume.content.personal_info?.gender && currentResume.content.personal_info?.age">|</span>
                <span v-if="currentResume.content.personal_info?.age">{{ currentResume.content.personal_info.age }}岁</span>
                <span class="sep" v-if="currentResume.content.personal_info?.age && currentResume.content.personal_info?.status">|</span>
                <span v-if="currentResume.content.personal_info?.status">{{ currentResume.content.personal_info.status }}</span>
             </div>
             <div class="preview-contact">
                <div class="contact-item" v-if="currentResume.content.personal_info?.phone">
                  <el-icon><Iphone /></el-icon> {{ currentResume.content.personal_info.phone }}
                </div>
                <span class="sep" v-if="currentResume.content.personal_info?.phone && currentResume.content.personal_info?.email">|</span>
                <div class="contact-item" v-if="currentResume.content.personal_info?.email">
                  <el-icon><Message /></el-icon> {{ currentResume.content.personal_info.email }}
                </div>
             </div>
             <div class="preview-intention-line" v-if="currentResume.content.job_intention?.job_type">
               <div class="intention-item">
                  <el-icon><Briefcase /></el-icon>
                  <span>{{ currentResume.content.job_intention.job_type }}</span>
               </div>
               <span class="sep" v-if="currentResume.content.job_intention.city">|</span>
               <div class="intention-item" v-if="currentResume.content.job_intention.city">
                  <el-icon><Location /></el-icon>
                  <span>{{ currentResume.content.job_intention.city }}</span>
               </div>
               <span class="sep" v-if="currentResume.content.job_intention.salary">|</span>
               <div class="intention-item" v-if="currentResume.content.job_intention.salary">
                  <el-icon><Money /></el-icon>
                  <span>{{ currentResume.content.job_intention.salary }}</span>
               </div>
               <span class="sep" v-if="currentResume.content.job_intention.type">|</span>
               <div class="intention-item" v-if="currentResume.content.job_intention.type">
                  <el-icon><Timer /></el-icon>
                  <span>{{ currentResume.content.job_intention.type }}</span>
               </div>
             </div>
           </div>
           <div class="preview-avatar">
             <el-avatar :shape="'square'" :size="100" :src="currentResume.content.personal_info?.avatar || currentResume.student_detail?.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
           </div>
        </div>
        
        <!-- Sections -->
        <div class="preview-section" v-if="currentResume.content.personal_advantage">
           <h3 class="preview-title">
             <el-icon><User /></el-icon> 个人优势
           </h3>
           <div class="preview-text">
             <ul>
               <li v-for="(line, i) in (currentResume.content.personal_advantage || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
             </ul>
           </div>
        </div>

        <div class="preview-section" v-if="currentResume.content.work_experience && currentResume.content.work_experience.length">
           <h3 class="preview-title">
             <el-icon><OfficeBuilding /></el-icon> 工作经历
           </h3>
           <div class="preview-list">
             <div class="preview-item" v-for="(work, idx) in currentResume.content.work_experience" :key="idx">
               <div class="preview-item-header">
                 <span class="company">{{ work.company }}</span>
                 <span class="time">{{ work.time_range }}</span>
               </div>
               <div class="preview-item-sub">{{ work.position }}</div>
               <div class="preview-item-desc">
                 <ul>
                   <li v-for="(line, i) in (work.description || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
                 </ul>
               </div>
             </div>
           </div>
        </div>

        <div class="preview-section" v-if="currentResume.content.project_experience && currentResume.content.project_experience.length">
           <h3 class="preview-title">
             <el-icon><Collection /></el-icon> 项目经历
           </h3>
           <div class="preview-list">
             <div class="preview-item" v-for="(proj, idx) in currentResume.content.project_experience" :key="idx">
               <div class="preview-item-header">
                 <span class="project">{{ proj.name }}</span>
                 <span class="time">{{ proj.time_range }}</span>
               </div>
               <div class="preview-item-sub">{{ proj.role }}</div>
               <div class="preview-item-desc">
                 <ul>
                   <li v-for="(line, i) in (proj.description || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
                 </ul>
               </div>
             </div>
           </div>
        </div>

        <div class="preview-section" v-if="currentResume.content.education_history && currentResume.content.education_history.length">
           <h3 class="preview-title">
             <el-icon><School /></el-icon> 教育经历
           </h3>
           <div class="preview-list">
             <div class="preview-item" v-for="(edu, idx) in currentResume.content.education_history" :key="idx">
               <div class="preview-item-header">
                 <span class="school">{{ edu.school }}</span>
                 <span class="time">{{ edu.time_range }}</span>
               </div>
               <div class="preview-item-sub">
                 {{ edu.degree }} | {{ edu.major }}
               </div>
               <div class="preview-item-desc" v-if="edu.description">
                 <ul>
                   <li v-for="(line, i) in (edu.description || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
                 </ul>
               </div>
             </div>
           </div>
        </div>

        <div class="preview-section" v-if="currentResume.content.professional_skills">
           <h3 class="preview-title">
             <el-icon><Trophy /></el-icon> 专业技能
           </h3>
           <div class="preview-text">
             <ul>
               <li v-for="(line, i) in (currentResume.content.professional_skills || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
             </ul>
           </div>
        </div>

        <div class="preview-section" v-if="currentResume.content.other_skills">
           <h3 class="preview-title">
             <el-icon><Medal /></el-icon> 其他技能/证书
           </h3>
           <div class="preview-text">
             <ul>
               <li v-for="(line, i) in (currentResume.content.other_skills || '').split('\n')" :key="i" v-if="line && line.trim()">{{ line }}</li>
             </ul>
           </div>
        </div>

      </div>
      <el-empty v-else description="暂无简历内容" />
    </el-dialog>

    <!-- Chat Dialog -->
    <chat-dialog
      v-model="chatVisible"
      :application-id="currentApplicationId"
      :other-user="currentOtherUser"
      @close="handleChatClose"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getApplications, updateApplicationStatus } from '@/api/recruitment'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, OfficeBuilding, Collection, School, Trophy, Medal, Iphone, Message, Briefcase, Money, Location, Timer } from '@element-plus/icons-vue'
import ChatDialog from '@/components/ChatDialog.vue'

const loading = ref(false)
const applications = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const searchForm = reactive({
  search: ''
})

const resumeDialogVisible = ref(false)
const currentResume = ref(null)

// Chat state
const chatVisible = ref(false)
const currentApplicationId = ref(null)
const currentOtherUser = ref({ name: '', avatar: '' })

const statusMap = {
    0: '未查看',
    1: '已查看',
    2: '面试中',
    3: '不合适',
    4: '通过',
    5: '不通过'
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchForm.search || undefined,
      ordering: '-create_time'
    }
    const res = await getApplications(params)
    if (res.results) {
      applications.value = res.results
      total.value = res.count
    } else {
      applications.value = res
      total.value = res.length
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取投递列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const resetSearch = () => {
  searchForm.search = ''
  handleSearch()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

const getStatusLabel = (status) => {
    return statusMap[status] || '未知'
}

const getStatusType = (status) => {
    switch (status) {
        case 2: return 'primary' // 面试中 - Blue
        case 3: return 'danger'  // 不合适 - Red
        case 4: return 'success' // 通过 - Green
        case 5: return 'warning' // 不通过 - Orange
        default: return 'info'
    }
}

const handleStatusUpdate = (row, status) => {
    const actionName = statusMap[status]
    ElMessageBox.confirm(
        `确定将该申请状态标记为“${actionName}”吗？`,
        '提示',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        }
    ).then(async () => {
        try {
            await updateApplicationStatus(row.id, status)
            ElMessage.success('操作成功')
            // Update local state to avoid refresh
            row.status = status
        } catch (error) {
            ElMessage.error('操作失败')
        }
    }).catch(() => {})
}

const viewResume = (row) => {
    if (row.resume_detail) {
        currentResume.value = {
            ...row.resume_detail,
            student_detail: row.student_detail
        }
        resumeDialogVisible.value = true
        
        // If status is "Not Viewed" (0), mark as "Viewed" (1)
        if (row.status === 0) {
            updateApplicationStatus(row.id, 1).then(() => {
                row.status = 1
            })
        }
    } else {
        ElMessage.warning('未找到简历信息')
    }
}

const openChat = (row) => {
    currentApplicationId.value = row.id
    currentOtherUser.value = {
        name: row.student_detail?.name || row.student_detail?.username || '用户',
        avatar: row.student_detail?.avatar || defaultAvatar
    }
    chatVisible.value = true

    // If status is "Not Viewed" (0), mark as "Viewed" (1)
    if (row.status === 0) {
        updateApplicationStatus(row.id, 1).then(() => {
            row.status = 1
        })
    }
}

const handleChatClose = () => {
  fetchData()
}

const formatTime = (timeStr) => {
    if (!timeStr) return '-'
    const date = new Date(timeStr)
    return date.toLocaleString()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.application-management {
  padding: 0;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  justify-content: flex-start;
  margin-bottom: -18px;
}

.table-card :deep(.el-table__row) {
    height: 45px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.company-name {
    color: #409EFF;
    font-weight: 500;
}

.job-name {
    color: #722ed1; /* Purple as requested */
    font-weight: 500;
}

.action-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: nowrap;
    justify-content: flex-start;
}

.msg-badge :deep(.el-badge__content) {
  top: 12px;
  right: -20px;
  z-index: 10;
  transform: translateY(-50%);
}

.table-card :deep(.el-table__cell) {
  overflow: visible;
}

/* Resume Preview Styles */
.resume-preview {
  padding: 30px;
  color: #333;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  background: white;
  min-height: 500px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  border-bottom: 1px solid #333;
  padding-bottom: 20px;
}

.preview-info {
  flex: 1;
}

.preview-name {
  font-size: 32px;
  margin: 0 0 10px 0;
  font-weight: bold;
  color: #000;
  line-height: 1.2;
}

.preview-basic-info {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.preview-contact {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.preview-contact .sep, .preview-intention-line .sep, .preview-basic-info .sep {
  margin: 0 8px;
  color: #ccc;
}

.preview-intention-line {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.intention-item {
    display: flex;
    align-items: center;
    gap: 4px;
}

.preview-avatar {
  margin-left: 20px;
}

.preview-avatar .el-avatar {
  border-radius: 4px; 
  border: 1px solid #eee;
}

.preview-section {
  margin-bottom: 25px;
}

.preview-title {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  border-left: none;
  padding-left: 0;
}

.preview-title .el-icon {
  margin-right: 8px;
  font-size: 20px;
  background: #ecf5ff;
  padding: 4px;
  border-radius: 50%;
}

.preview-text {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}

.preview-text ul, .preview-item-desc ul {
  margin: 0;
  padding-left: 20px;
  list-style-type: disc;
}

.preview-text li, .preview-item-desc li {
  margin-bottom: 4px;
  line-height: 1.6;
}

.preview-list .preview-item {
  margin-bottom: 20px;
}

.preview-item-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 4px;
}

.preview-item-header .company, 
.preview-item-header .project, 
.preview-item-header .school {
  font-size: 16px;
  font-weight: bold;
  color: #000;
}

.preview-item-header .time {
  font-size: 14px;
  color: #666;
  font-weight: normal;
}

.preview-item-sub {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
}

.preview-item-desc {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}
</style>
