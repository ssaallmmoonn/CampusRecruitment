<template>
  <div class="application-management">
    <el-card>
      <!-- Search Bar -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="请输入职位名称或学生姓名查询"
          style="width: 250px"
          clearable
          @clear="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button type="warning" @click="handleReset">重置</el-button>
      </div>

      <!-- Table -->
      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
      >
        <el-table-column label="企业名称" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            <span class="link-text" @click="handleCompanyDetail(scope.row.job_detail.company.id)">
              {{ scope.row.job_detail.company.company_name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="职位名称" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            <span class="link-text" @click="handleJobDetail(scope.row.job_detail.id)">
              {{ scope.row.job_detail.job_name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="投递用户" min-width="150">
          <template #default="scope">
            {{ scope.row.student_detail.name }}
          </template>
        </el-table-column>
        <el-table-column label="投递简历" width="150">
          <template #default="scope">
            <el-button type="primary" link @click="handleViewResume(scope.row.resume_detail)">
              查看简历
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="投递时间" min-width="150">
          <template #default="scope">
            {{ formatTime(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="投递状态" width="150">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Resume Dialog -->
    <el-dialog
      v-model="resumeDialogVisible"
      title="简历预览"
      width="800px"
      custom-class="preview-dialog"
    >
      <div class="resume-preview" v-if="currentResume && currentResume.content">
        <!-- Header -->
        <div class="preview-header">
           <div class="preview-info">
             <h1 class="preview-name">{{ currentResume.content.personal_info?.name || '未填写姓名' }}</h1>
             <div class="preview-basic-info">
                <span v-if="currentResume.content.personal_info?.gender">{{ currentResume.content.personal_info.gender }}</span>
                <span class="sep" v-if="currentResume.content.personal_info?.gender && currentResume.content.personal_info?.age">|</span>
                <span v-if="currentResume.content.personal_info?.age">{{ currentResume.content.personal_info.age }}岁</span>
                <span class="sep" v-if="currentResume.content.personal_info?.age && currentResume.content.personal_info?.status">|</span>
                <span v-if="currentResume.content.personal_info?.status">{{ currentResume.content.personal_info.status }}</span>
             </div>
             <div class="preview-contact">
                <span v-if="currentResume.content.personal_info?.phone">{{ currentResume.content.personal_info.phone }}</span>
                <span class="sep" v-if="currentResume.content.personal_info?.phone && currentResume.content.personal_info?.email">|</span>
                <span v-if="currentResume.content.personal_info?.email">{{ currentResume.content.personal_info.email }}</span>
             </div>
             <div class="preview-intention-line" v-if="currentResume.content.job_intention?.job_type">
               <span>求职意向：{{ currentResume.content.job_intention.job_type }}</span>
               <span class="sep" v-if="currentResume.content.job_intention.city">|</span>
               <span>{{ currentResume.content.job_intention.city }}</span>
               <span class="sep" v-if="currentResume.content.job_intention.salary">|</span>
               <span>{{ currentResume.content.job_intention.salary }}</span>
               <span class="sep" v-if="currentResume.content.job_intention.type">|</span>
               <span>{{ currentResume.content.job_intention.type }}</span>
             </div>
           </div>
           <div class="preview-avatar">
             <el-avatar :shape="'square'" :size="100" :src="currentResume.content.personal_info?.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
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
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, OfficeBuilding, Collection, School, Trophy, Medal } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// Resume Dialog
const resumeDialogVisible = ref(false)
const currentResume = ref(null)

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined
    }
    const res = await request.get('/recruitment/applications/', { params })
    tableData.value = res.results
    total.value = res.count
  } catch (error) {
    console.error(error)
    ElMessage.error('获取投递记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleReset = () => {
  searchQuery.value = ''
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

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString()
}

const getStatusLabel = (status) => {
  const map = { 0: '未查看', 1: '已查看', 2: '面试中', 3: '不合适', 4: '通过', 5: '不通过' }
  return map[status] || '未知'
}

const getStatusType = (status) => {
  const map = { 0: 'info', 1: 'primary', 2: 'warning', 3: 'danger', 4: 'success', 5: 'danger' }
  return map[status] || 'info'
}

const handleCompanyDetail = (companyId) => {
  router.push(`/company/${companyId}`)
}

const handleJobDetail = (jobId) => {
  router.push(`/jobs/${jobId}`)
}

const handleViewResume = (resume) => {
  if (!resume) {
    ElMessage.warning('该申请未关联简历')
    return
  }
  currentResume.value = resume
  resumeDialogVisible.value = true
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.application-management {
  padding: 0;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.link-text {
  color: #606266;
  cursor: pointer;
  transition: color 0.3s;
}

.link-text:hover {
  color: #409EFF;
}

/* Resume Preview Styles */
.resume-preview {
  padding: 30px;
  color: #333;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  background: white;
  min-height: 800px;
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