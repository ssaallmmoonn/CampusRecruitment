<template>
  <div class="notice-management">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item>
          <el-input v-model="searchForm.keyword" placeholder="请输入标题查询" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" plain @click="handleSearch">查询</el-button>
          <el-button type="warning" plain @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="action-card">
      <div class="action-bar">
        <el-button type="primary" plain @click="handleAdd">新增</el-button>
        <el-button type="danger" plain @click="handleBatchDelete" :disabled="selectedRows.length === 0">批量删除</el-button>
      </div>

      <!-- 表格 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="create_time" label="发布时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" circle size="small" :icon="Edit" @click="handleEdit(scope.row)" />
            <el-button type="danger" circle size="small" :icon="Delete" @click="handleDelete(scope.row)" />
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="prev, pager, next"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增公告' : '编辑公告'"
      width="600px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="6"
            placeholder="请输入公告内容"
          />
        </el-form-item>
        <el-form-item label="启用" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete } from '@element-plus/icons-vue'
import { getNotices, createNotice, updateNotice, deleteNotice } from '@/api/ads'

// 搜索相关
const searchForm = reactive({
  keyword: ''
})

// 表格相关
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const selectedRows = ref([])

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref('add') // 'add' or 'edit'
const submitting = ref(false)
const formRef = ref(null)
const form = reactive({
  id: undefined,
  title: '',
  content: '',
  is_active: true
})

const rules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'blur' }]
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchForm.keyword
    }
    const res = await getNotices(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error('Fetch notices failed:', error)
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const resetSearch = () => {
  searchForm.keyword = ''
  handleSearch()
}

// 表格操作
const handleSelectionChange = (val) => {
  selectedRows.value = val
}

const handleAdd = () => {
  dialogType.value = 'add'
  form.id = undefined
  form.title = ''
  form.content = ''
  form.is_active = true
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  form.id = row.id
  form.title = row.title
  form.content = row.content
  form.is_active = row.is_active
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该公告吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteNotice(row.id)
      ElMessage.success('删除成功')
      if (tableData.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }
      fetchData()
    } catch (error) {
      console.error('Delete notice failed:', error)
      ElMessage.error('删除失败')
    }
  })
}

const handleBatchDelete = () => {
  ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 条公告吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 并行删除
      await Promise.all(selectedRows.value.map(row => deleteNotice(row.id)))
      ElMessage.success('批量删除成功')
      if (tableData.value.length === selectedRows.value.length && currentPage.value > 1) {
        currentPage.value--
      }
      fetchData()
      selectedRows.value = []
    } catch (error) {
      console.error('Batch delete failed:', error)
      ElMessage.error('批量删除部分或全部失败')
    }
  })
}

// 表单提交
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const formData = { ...form }
        delete formData.id // Ensure ID is not sent in payload if creating
        
        if (dialogType.value === 'add') {
          await createNotice(formData)
          ElMessage.success('新增成功')
        } else {
          await updateNotice(form.id, formData)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('Submit notice failed:', error)
        ElMessage.error(dialogType.value === 'add' ? '新增失败' : '更新失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

// 工具函数
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }).replace(/\//g, '-')
}

// 初始化
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.notice-management {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
  border-radius: 4px;
}

.search-form {
  display: flex;
  align-items: center;
}

.search-form .el-form-item {
  margin-bottom: 0;
  margin-right: 10px;
}

.action-card {
  min-height: 500px;
  border-radius: 4px;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-start;
}

/* 按钮图标样式调整 */
:deep(.el-button.is-circle) {
  padding: 8px;
}
</style>