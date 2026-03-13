<template>
  <div class="user-management">
    <el-card>
      <!-- Search Bar -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="请输入学生姓名或账号查询"
          style="width: 250px"
          clearable
          @clear="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button type="warning" @click="handleReset">重置</el-button>
      </div>

      <!-- Action Bar -->
      <div class="action-bar">
        <el-button type="primary" plain @click="handleAdd">新增</el-button>
        <el-button type="danger" plain @click="handleBatchDelete" :disabled="selectedRows.length === 0">批量删除</el-button>
      </div>

      <!-- Table -->
      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="username" label="账号" min-width="120" />
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column label="头像" width="80">
          <template #default="scope">
            <el-avatar :size="40" :src="scope.row.avatar || defaultAvatar" shape="square"/>
          </template>
        </el-table-column>
        <el-table-column prop="school" label="学校" min-width="150" show-overflow-tooltip />
        <el-table-column prop="major" label="专业" min-width="120" show-overflow-tooltip />
        <el-table-column prop="education" label="学历" min-width="100" />
        <el-table-column prop="graduation_year" label="毕业年份" min-width="100" />
        <el-table-column prop="phone" label="电话" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column label="角色" width="100">
          <template #default>
            <el-tag>学生</el-tag>
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
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增学生' : '编辑学生信息'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="头像" v-if="dialogType === 'edit'">
           <el-avatar :size="60" :src="form.avatar || defaultAvatar" />
           <div style="margin-left: 10px; font-size: 12px; color: #999;">头像仅支持学生自行上传</div>
        </el-form-item>

        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" :disabled="dialogType === 'edit'" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogType === 'add'">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学校" prop="school">
              <el-input v-model="form.school" placeholder="请输入学校" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专业" prop="major">
              <el-input v-model="form.major" placeholder="请输入专业" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学历" prop="education">
              <el-select v-model="form.education" placeholder="请选择学历" style="width: 100%">
                <el-option label="大专" value="大专" />
                <el-option label="本科" value="本科" />
                <el-option label="硕士" value="硕士" />
                <el-option label="博士" value="博士" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="毕业年份" prop="graduation_year">
              <el-date-picker
                v-model="form.graduation_year"
                type="year"
                placeholder="选择年份"
                value-format="YYYY"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const tableData = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedRows = ref([])
const defaultAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'

// Dialog
const dialogVisible = ref(false)
const dialogType = ref('add')
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  username: '',
  password: '',
  name: '',
  school: '',
  major: '',
  education: '',
  graduation_year: '',
  phone: '',
  email: '',
  avatar: ''
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码不能少于6位', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  school: [{ required: true, message: '请输入学校', trigger: 'blur' }],
  major: [{ required: true, message: '请输入专业', trigger: 'blur' }],
  education: [{ required: true, message: '请选择学历', trigger: 'change' }],
  graduation_year: [{ required: true, message: '请选择毕业年份', trigger: 'change' }],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined
    }
    const res = await request.get('/users/students/', { params })
    tableData.value = res.results
    total.value = res.count
  } catch (error) {
    console.error(error)
    ElMessage.error('获取学生列表失败')
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

const handleSelectionChange = (val) => {
  selectedRows.value = val
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

const handleAdd = () => {
  dialogType.value = 'add'
  Object.assign(form, {
    id: null,
    username: '',
    password: '',
    name: '',
    school: '',
    major: '',
    education: '',
    graduation_year: '',
    phone: '',
    email: '',
    avatar: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  Object.assign(form, {
    id: row.user, // pk is user id
    username: row.username,
    name: row.name,
    school: row.school,
    major: row.major,
    education: row.education,
    graduation_year: row.graduation_year ? String(row.graduation_year) : '',
    phone: row.phone,
    email: row.email,
    avatar: row.avatar
  })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该学生账号吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async () => {
    try {
      await request.delete(`/users/students/${row.user}/`)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleBatchDelete = () => {
  ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 个学生账号吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async () => {
    try {
      const ids = selectedRows.value.map(row => row.user)
      await request.post('/users/students/batch_delete/', { ids })
      ElMessage.success('批量删除成功')
      fetchData()
    } catch (error) {
      ElMessage.error('批量删除失败')
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = { ...form }
        // Remove avatar if it's string/null
        if (typeof payload.avatar === 'string' || payload.avatar === null) {
            delete payload.avatar
        }

        if (dialogType.value === 'add') {
          await request.post('/users/students/', payload)
          ElMessage.success('新增成功')
        } else {
          await request.patch(`/users/students/${form.id}/`, payload)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.user-management {
  padding: 0;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.action-bar {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>