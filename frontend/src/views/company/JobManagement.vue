<template>
  <div class="job-management">
    <!-- Search Bar -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item>
          <el-input v-model="searchForm.job_name" placeholder="请输入职位名称查询" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Action Bar -->
    <div class="action-bar">
      <el-button type="primary" @click="showCreateDialog">发布职位</el-button>
      <el-button type="danger" plain @click="handleBatchDelete" :disabled="selectedJobs.length === 0">批量删除</el-button>
    </div>

    <!-- Job Table -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="jobs"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="job_name" label="职位名称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="company.company_name" label="招聘企业" min-width="100" show-overflow-tooltip />
        <el-table-column prop="company.industry" label="行业" min-width="50" />
        <el-table-column prop="job_type" label="求职类型" width="100" />
        <el-table-column prop="experience_requirement" label="工作经验" width="120" />
        <el-table-column prop="salary" label="薪资待遇" width="120" />
        <el-table-column prop="degree_requirement" label="学历要求" width="100" />
        <el-table-column prop="views_count" label="浏览量" width="90" sortable="custom" />
        <el-table-column prop="collections_count" label="收藏量" width="90" sortable="custom" />
        <el-table-column prop="deliveries_count" label="投递量" width="90" sortable="custom" />
        <el-table-column label="职业描述与要求" width="130">
          <template #default="scope">
            <el-button type="primary" size="small" @click="showDescription(scope.row)">点击查看</el-button>
          </template>
        </el-table-column>

        <el-table-column prop="audit_status" label="职位状态" width="100">
          <template #default="scope">
            <el-tag type="success" v-if="scope.row.audit_status === 1">审核通过</el-tag>
            <el-tag type="warning" v-else-if="scope.row.audit_status === 0">待审核</el-tag>
            <el-popover
              v-if="scope.row.audit_status === 2"
              placement="top-start"
              title="驳回理由"
              :width="200"
              trigger="click"
              :content="scope.row.reject_reason || '无驳回理由'"
            >
              <template #reference>
                <el-tag type="danger" style="cursor: pointer">审核失败</el-tag>
              </template>
            </el-popover>
            <el-tag type="info" v-if="scope.row.audit_status === 3">已下架</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" circle size="small" @click="handleEdit(scope.row)">
               <el-icon><Edit /></el-icon>
            </el-button>
            <el-button type="danger" circle size="small" @click="handleDelete(scope.row)">
               <el-icon><Delete /></el-icon>
            </el-button>
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

    <!-- Dialogs -->
    <el-dialog v-model="descriptionDialogVisible" title="职业描述与要求" width="1000px">
      <div v-if="currentJob" class="description-content">
        <h3>职位描述</h3>
        <div class="text-block">{{ currentJob.description }}</div>
        <el-divider />
        <h3>任职要求</h3>
        <div class="text-block">{{ currentJob.requirements }}</div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="descriptionDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog 
      v-model="jobDialogVisible" 
      :title="isEdit ? '编辑职位' : '发布职位'" 
      width="60%"
      :close-on-click-modal="false"
    >
      <el-form :model="jobForm" ref="jobFormRef" :rules="jobRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位名称" prop="job_name">
              <el-input v-model="jobForm.job_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="薪资待遇" prop="salary">
              <el-input v-model="jobForm.salary" placeholder="例如: 10k-20k" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位类型" prop="job_type">
              <el-select v-model="jobForm.job_type" style="width: 100%">
                <el-option label="全职" value="全职" />
                <el-option label="实习" value="实习" />
                <el-option label="兼职" value="兼职" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工作地点" prop="location">
              <el-cascader
                v-model="jobForm.location"
                :options="locationOptions"
                :props="cascaderProps"
                placeholder="请选择工作地点"
                filterable
                clearable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学历要求" prop="degree_requirement">
              <el-select v-model="jobForm.degree_requirement" style="width: 100%">
                <el-option label="初中及以下" value="初中及以下" />
                <el-option label="高中" value="高中" />
                <el-option label="中专/中技" value="中专/中技" />
                <el-option label="大专" value="大专" />
                <el-option label="本科" value="本科" />
                <el-option label="硕士" value="硕士" />
                <el-option label="博士" value="博士" />
                <el-option label="学历不限" value="学历不限" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="经验要求" prop="experience_requirement">
              <el-select v-model="jobForm.experience_requirement" style="width: 100%">
                <el-option label="经验不限" value="经验不限" />
                <el-option label="1年以下" value="1年以下" />
                <el-option label="1-3年" value="1-3年" />
                <el-option label="3-5年" value="3-5年" />
                <el-option label="5-10年" value="5-10年" />
                <el-option label="10年以上" value="10年以上" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
             <el-form-item label="职位分类" prop="job_category">
              <el-cascader
                v-model="jobForm.job_category"
                :options="jobCategoryOptions"
                :props="cascaderProps"
                clearable
                filterable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
             <el-form-item label="专业分类" prop="major">
              <el-cascader
                v-model="jobForm.major"
                :options="majorOptions"
                :props="cascaderProps"
                clearable
                filterable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="专业要求" prop="major_requirement">
               <el-input v-model="jobForm.major_requirement" placeholder="例如: 计算机相关专业" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="职位描述" prop="description">
          <el-input type="textarea" :rows="4" v-model="jobForm.description" />
        </el-form-item>
        
        <el-form-item label="任职要求" prop="requirements">
          <el-input type="textarea" :rows="4" v-model="jobForm.requirements" />
        </el-form-item>

        <el-form-item label="搜索关键词" prop="search_keywords">
            <!-- Simple input for now, could be tag input later -->
            <el-select
                v-model="jobForm.search_keywords"
                multiple
                filterable
                allow-create
                default-first-option
                :reserve-keyword="false"
                placeholder="请输入关键词并回车"
                style="width: 100%"
            >
            </el-select>
        </el-form-item>

      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="jobDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitJob" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getJobs, createJob, updateJob, deleteJob, getJobCategoryTree, getMajorCategoryTree } from '@/api/jobs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete } from '@element-plus/icons-vue'
import provinceData from '@/assets/provinces.json'

const loading = ref(false)
const jobs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const searchForm = reactive({
  job_name: ''
})

const selectedJobs = ref([])

// Dialog states
const descriptionDialogVisible = ref(false)
const currentJob = ref(null)

const jobDialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const jobFormRef = ref(null)

const jobCategoryOptions = ref([])
const majorOptions = ref([])
const locationOptions = ref([])
const cascaderProps = { emitPath: false }

const jobForm = reactive({
  id: null,
  job_name: '',
  salary: '',
  job_type: '全职',
  location: '',
  degree_requirement: '学历不限',
  experience_requirement: '经验不限',
  job_category: '',
  major: '',
  major_requirement: '',
  description: '',
  requirements: '',
  search_keywords: []
})

const jobRules = {
  job_name: [{ required: true, message: '请输入职位名称', trigger: 'blur' }],
  salary: [{ required: true, message: '请输入薪资待遇', trigger: 'blur' }],
  location: [{ required: true, message: '请输入工作地点', trigger: 'blur' }],
  job_category: [{ required: true, message: '请选择职位分类', trigger: 'change' }],
  major: [{ required: true, message: '请选择专业分类', trigger: 'change' }],
  description: [{ required: true, message: '请输入职位描述', trigger: 'blur' }]
}

const findLeafValueByLabel = (label, options) => {
  if (!label) return ''
  const stack = Array.isArray(options) ? [...options] : []
  while (stack.length) {
    const node = stack.shift()
    if (!node) continue
    const children = node.children || []
    if (!children.length && node.label === label) return node.value
    if (children.length) stack.unshift(...children)
  }
  return ''
}

const normalizeCategoryValue = (value, options) => {
  if (!value) return ''
  if (typeof value === 'string' && value.includes('/')) return value
  const mapped = findLeafValueByLabel(value, options)
  return mapped || value
}

const loadCategoryOptions = async () => {
  try {
    if (!jobCategoryOptions.value.length) {
      jobCategoryOptions.value = await getJobCategoryTree()
    }
    if (!majorOptions.value.length) {
      majorOptions.value = await getMajorCategoryTree()
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取分类数据失败')
  }
}

const initLocationOptions = () => {
  if (provinceData && provinceData['地区分类']) {
    locationOptions.value = provinceData['地区分类'].map(province => ({
      label: province['一级分类'],
      value: province['一级分类'],
      children: province['二级分类'].map(city => ({
        label: city,
        value: city
      }))
    }))
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchForm.job_name || undefined, // Use search parameter for fuzzy search
      my_jobs: 'true', // Important: Filter for current company
      ordering: currentOrdering.value || '-create_time'
    }
    const res = await getJobs(params)
    if (res.results) {
      jobs.value = res.results
      total.value = res.count
    } else {
      jobs.value = res
      total.value = res.length
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取职位列表失败')
  } finally {
    loading.value = false
  }
}

const currentOrdering = ref('-create_time')

const handleSortChange = ({ prop, order }) => {
  if (!order) {
    currentOrdering.value = '-create_time'
  } else {
    currentOrdering.value = order === 'ascending' ? prop : `-${prop}`
  }
  currentPage.value = 1
  fetchData()
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const resetSearch = () => {
  searchForm.job_name = ''
  handleSearch()
}

const handleSelectionChange = (val) => {
  selectedJobs.value = val
}

const handleBatchDelete = () => {
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedJobs.value.length} 个职位吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        // Sequential delete for now as API might not support batch
        for (const job of selectedJobs.value) {
            await deleteJob(job.id)
        }
        ElMessage.success('批量删除成功')
        fetchData()
      } catch (error) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    '确定要删除该职位吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await deleteJob(row.id)
        ElMessage.success('删除成功')
        fetchData()
      } catch (error) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

const showDescription = (row) => {
  currentJob.value = row
  descriptionDialogVisible.value = true
}

const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  loadCategoryOptions()
  jobDialogVisible.value = true
}

const originalJobForm = reactive({})

const handleEdit = async (row) => {
  isEdit.value = true
  await loadCategoryOptions()
  // Fill form
  Object.keys(jobForm).forEach(key => {
    if (key in row) {
      jobForm[key] = row[key]
    }
  })
  jobForm.id = row.id
  // Handle search_keywords if it's JSON/Array
  if (row.search_keywords) {
      jobForm.search_keywords = Array.isArray(row.search_keywords) ? row.search_keywords : []
  } else {
      jobForm.search_keywords = []
  }
  
  // Save original state for comparison
  Object.assign(originalJobForm, JSON.parse(JSON.stringify(jobForm)))

  jobForm.job_category = normalizeCategoryValue(jobForm.job_category, jobCategoryOptions.value)
  jobForm.major = normalizeCategoryValue(jobForm.major, majorOptions.value)
  
  jobDialogVisible.value = true
}

const resetForm = () => {
  if (jobFormRef.value) {
    jobFormRef.value.resetFields()
  }
  jobForm.id = null
  jobForm.job_name = ''
  jobForm.salary = ''
  jobForm.job_type = '全职'
  jobForm.location = ''
  jobForm.degree_requirement = '学历不限'
  jobForm.experience_requirement = '经验不限'
  jobForm.job_category = ''
  jobForm.major = ''
  jobForm.major_requirement = ''
  jobForm.description = ''
  jobForm.requirements = ''
  jobForm.search_keywords = []
  
  // Clear original form
  Object.keys(originalJobForm).forEach(key => delete originalJobForm[key])
}

const submitJob = async () => {
  if (!jobFormRef.value) return
  
  await jobFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        const data = { ...jobForm }
        if (isEdit.value) {
          // Check for changes
          const hasChanges = JSON.stringify(jobForm) !== JSON.stringify(originalJobForm)
          
          if (!hasChanges) {
            ElMessage.info('信息无更改')
            submitLoading.value = false
            return
          }
          
          await updateJob(data.id, data)
          ElMessage.success('更新成功，已提交至管理员审核')
        } else {
          await createJob(data)
          ElMessage.success('发布成功')
        }
        jobDialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error(error)
        ElMessage.error(isEdit.value ? '更新失败' : '发布失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

onMounted(() => {
  loadCategoryOptions()
  initLocationOptions()
  fetchData()
})
</script>

<style scoped>
.job-management {
  padding: 0;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  justify-content: flex-start;
  margin-bottom: -18px; /* Offset default form bottom margin */
}

.action-bar {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.text-block {
  white-space: pre-wrap;
  line-height: 1.6;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  color: #606266;
}
</style>
