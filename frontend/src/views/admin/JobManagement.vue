<template>
  <div class="job-management">
    <el-card>
      <!-- Search Bar -->
      <div class="search-bar">
        <el-input
          v-model="searchJobName"
          placeholder="请输入职位名称查询"
          style="width: 200px"
          clearable
          @clear="handleSearch"
        />
        <el-input
          v-model="searchCompany"
          placeholder="请输入公司名称查询"
          style="width: 200px"
          clearable
          @clear="handleSearch"
        />
        <el-select
          v-model="searchAuditStatus"
          placeholder="请选择审核状态"
          style="width: 160px"
          clearable
          @change="handleSearch"
        >
          <el-option label="待审核" :value="0" />
          <el-option label="通过" :value="1" />
          <el-option label="驳回" :value="2" />
          <el-option label="已下架" :value="3" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button type="warning" @click="handleReset">重置</el-button>
      </div>

      <!-- Table -->
      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="job_name" label="职位名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="招聘企业" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.company?.company_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="行业" min-width="120" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.company?.industry || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="job_type" label="求职类型" width="100" />
        <el-table-column prop="experience_requirement" label="工作经验" width="120" />
        <el-table-column prop="salary" label="薪资待遇" width="120" />
        <el-table-column prop="degree_requirement" label="学历要求" width="100" />
        <el-table-column prop="views_count" label="浏览量" width="90" sortable="custom" />
        <el-table-column prop="collections_count" label="收藏量" width="90" sortable="custom" />
        <el-table-column prop="deliveries_count" label="投递量" width="90" sortable="custom" />
        <el-table-column label="职位描述与要求" width="150" align="center">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleViewDescription(scope.row)">
              点击查看
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="职位状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.audit_status)">
              {{ getStatusLabel(scope.row.audit_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button
                v-if="scope.row.audit_status === 0 || scope.row.audit_status === 2"
                type="success"
                circle
                size="small"
                @click="handleApprove(scope.row)"
              >
                <el-icon><Check /></el-icon>
              </el-button>
              <el-button
                v-if="scope.row.audit_status === 1"
                type="success"
                circle
                size="small"
                disabled
              >
                <el-icon><Check /></el-icon>
              </el-button>
              <el-button
                v-if="scope.row.audit_status === 2"
                type="danger"
                circle
                size="small"
                disabled
              >
                <el-icon><Close /></el-icon>
              </el-button>
              <el-button
                v-if="scope.row.audit_status === 0 || scope.row.audit_status === 1"
                type="danger"
                circle
                size="small"
                @click="handleReject(scope.row)"
              >
                <el-icon><Close /></el-icon>
              </el-button>
              <el-button
                type="danger"
                circle
                size="small"
                @click="handleDelete(scope.row)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
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
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Description Dialog -->
    <el-dialog v-model="descDialogVisible" title="职位描述与要求" width="1000px">
      <div v-if="currentJob" class="desc-content">
        <h3>职位描述</h3>
        <div class="text-block">{{ currentJob.description }}</div>
        <el-divider />
        <h3>任职要求</h3>
        <div class="text-block">{{ currentJob.requirements }}</div>
      </div>
    </el-dialog>

    <!-- Reject Reason Dialog -->
    <el-dialog v-model="rejectDialogVisible" title="驳回职位" width="600px">
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="驳回原因">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入驳回原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="rejectDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmReject" :loading="submitting">确认驳回</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Close, Delete } from '@element-plus/icons-vue'
import request from '@/utils/request'
import jobsData from '@/assets/jobs.json'

const loading = ref(false)
const tableData = ref([])
const searchJobName = ref('')
const searchCompany = ref('')
const searchAuditStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const multipleSelection = ref([])

// Dialogs
const descDialogVisible = ref(false)
const currentJob = ref(null)

const rejectDialogVisible = ref(false)
const rejectForm = reactive({
  id: null,
  reason: ''
})
const submitting = ref(false)

// Build Category Map (3rd level -> 1st level)
const categoryMap = new Map()

const initCategoryMap = () => {
  const topCategories = jobsData['职位分类'] || []
  topCategories.forEach(topCat => {
    const topName = topCat['一级分类']
    const subList = topCat['二级分类列表'] || []
    subList.forEach(subCat => {
      // If we want 2nd level as parent: const parentName = subCat['二级分类']
      // If we want 1st level as parent: const parentName = topName
      // User requested "upper-level classification". Usually implies immediate parent (2nd level).
      // But looking at the example "计算机软件", it feels like a broad industry.
      // Let's use 1st level for now as it maps better to "Industry".
      // Wait, let's use 1st level.
      const leafList = subCat['三级分类'] || []
      leafList.forEach(leaf => {
        categoryMap.set(leaf, topName)
      })
    })
  })
}

const getParentCategory = (categoryName) => {
  if (!categoryName) return '-'
  // Try exact match
  if (categoryMap.has(categoryName)) {
    return categoryMap.get(categoryName)
  }
  // If not found, maybe it's a partial match or stored differently
  // For now return '-' or original if map fails
  return '-'
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

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      job_name: searchJobName.value || undefined,
      company_name: searchCompany.value || undefined,
      audit_status: searchAuditStatus.value !== '' ? searchAuditStatus.value : undefined,
      ordering: currentOrdering.value || '-create_time'
    }

    const res = await request.get('/jobs/', { params })
    tableData.value = res.results
    total.value = res.count
  } catch (error) {
    console.error(error)
    ElMessage.error('获取职位列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleReset = () => {
  searchJobName.value = ''
  searchCompany.value = ''
  searchAuditStatus.value = ''
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

const handleSelectionChange = (val) => {
  multipleSelection.value = val
}

const handleViewDescription = (row) => {
  currentJob.value = row
  descDialogVisible.value = true
}

const getStatusLabel = (status) => {
  const map = { 0: '待审核', 1: '审核通过', 2: '已驳回', 3: '已下架' }
  return map[status] || '未知'
}

const getStatusType = (status) => {
  const map = { 0: 'warning', 1: 'success', 2: 'danger', 3: 'info' }
  return map[status] || 'info'
}

const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm(`确定通过职位 "${row.job_name}" 的审核吗？`, '提示', {
      type: 'warning'
    })
    
    await request.patch(`/jobs/${row.id}/`, { audit_status: 1 })
    ElMessage.success('审核通过')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('操作失败')
    }
  }
}

const handleReject = (row) => {
  rejectForm.id = row.id
  rejectForm.reason = ''
  rejectDialogVisible.value = true
}

const confirmReject = async () => {
  if (!rejectForm.reason.trim()) {
    ElMessage.warning('请输入驳回原因')
    return
  }
  
  submitting.value = true
  try {
    await request.patch(`/jobs/${rejectForm.id}/`, { 
      audit_status: 2,
      reject_reason: rejectForm.reason 
    })
    ElMessage.success('已驳回')
    rejectDialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error(error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除职位 "${row.job_name}" 吗？此操作不可恢复。`, '警告', {
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
    
    await request.delete(`/jobs/${row.id}/`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  initCategoryMap()
  fetchData()
})
</script>

<style scoped>
.job-management {
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

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 0px;
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