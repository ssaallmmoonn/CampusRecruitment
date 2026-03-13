<template>
  <div class="company-management">
    <el-card>
      <!-- Search Bar -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="请输入企业名称查询"
          style="width: 200px"
          clearable
          @clear="handleSearch"
        />
        <el-select v-model="auditStatus" placeholder="请选择审核状态" clearable @change="handleSearch" style="width: 180px">
          <el-option label="待审核" :value="0" />
          <el-option label="通过" :value="1" />
          <el-option label="驳回" :value="2" />
        </el-select>
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
        <el-table-column type="selection" width="40" />
        <el-table-column prop="username" label="企业账号" min-width="180" />
        <el-table-column prop="company_name" label="企业名称" min-width="200" />
        <el-table-column label="企业Logo" width="100">
          <template #default="scope">
            <el-avatar :size="40" :src="scope.row.logo || defaultLogo" shape="square" />
          </template>
        </el-table-column>
        <el-table-column prop="contact_person" label="联系人" min-width="100" />
        <el-table-column prop="contact_phone" label="联系电话" min-width="120" />
        <el-table-column prop="address" label="办公地点" min-width="150" show-overflow-tooltip />
        <el-table-column prop="industry" label="所属行业" min-width="120" />
        <el-table-column prop="scale" label="公司规模" min-width="120" />
        <el-table-column label="审核状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.audit_status)">
              {{ getStatusLabel(scope.row.audit_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="100">
          <template #default>
            <el-tag type="info">企业</el-tag>
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
      :title="dialogType === 'add' ? '新增企业' : '审核企业信息'"
      width="1000px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="140px">
        <el-form-item label="企业Logo">
           <el-avatar :size="80" :src="form.logo || defaultLogo" shape="square" />
           <div style="margin-left: 10px; font-size: 12px; color: #999;">（此处仅展示企业Logo，不支持上传）</div>
        </el-form-item>
        
        <el-form-item label="企业账号" prop="username">
          <el-input v-model="form.username" :disabled="dialogType === 'edit'" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogType === 'add'">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="企业名称" prop="company_name">
          <el-input v-model="form.company_name" placeholder="请输入企业名称" />
        </el-form-item>
        <el-form-item label="统一社会信用代码" prop="credit_code">
          <el-input v-model="form.credit_code" placeholder="请输入统一社会信用代码" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact_person">
              <el-input v-model="form.contact_person" placeholder="请输入联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="办公地点" prop="address">
          <el-input v-model="form.address" placeholder="请输入详细办公地点" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="8">
             <el-form-item label="所属行业" prop="industry">
               <el-input v-model="form.industry" placeholder="请输入行业" />
             </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="人员规模" prop="scale">
              <el-select v-model="form.scale" placeholder="请选择规模" style="width: 100%">
                <el-option label="少于15人" value="少于15人" />
                <el-option label="15-50人" value="15-50人" />
                <el-option label="50-150人" value="50-150人" />
                <el-option label="150-500人" value="150-500人" />
                <el-option label="500-2000人" value="500-2000人" />
                <el-option label="2000人以上" value="2000人以上" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
             <el-form-item label="企业性质" prop="nature">
               <el-select v-model="form.nature" placeholder="请选择性质" style="width: 100%">
                 <el-option label="国企" value="国企" />
                 <el-option label="民营" value="民营" />
                 <el-option label="外商独资" value="外商独资" />
                 <el-option label="合资" value="合资" />
                 <el-option label="股份制企业" value="股份制企业" />
                 <el-option label="事业单位" value="事业单位" />
                 <el-option label="其他" value="其他" />
               </el-select>
             </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="企业简介" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入企业简介" />
        </el-form-item>

        <el-form-item label="审核状态" prop="audit_status" v-if="dialogType === 'edit'">
          <el-radio-group v-model="form.audit_status">
            <el-radio :label="0">待审核</el-radio>
            <el-radio :label="1">通过</el-radio>
            <el-radio :label="2">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="驳回原因" prop="reject_reason" v-if="dialogType === 'edit' && form.audit_status === 2">
           <el-input v-model="form.reject_reason" type="textarea" :rows="2" placeholder="请输入驳回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button v-if="dialogType === 'edit'" type="warning" @click="handleUpdateInfo" :loading="submitting">修改信息</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ dialogType === 'add' ? '确认新增' : '确认审核' }}
          </el-button>
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
const auditStatus = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedRows = ref([])
const defaultLogo = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'

// Dialog
const dialogVisible = ref(false)
const dialogType = ref('add')
const submitting = ref(false)
const formRef = ref(null)
const originalForm = ref({}) // Store original form data for comparison

const form = reactive({
  id: null,
  username: '',
  password: '',
  company_name: '',
  credit_code: '',
  contact_person: '',
  contact_phone: '',
  industry: '',
  scale: '',
  nature: '',
  address: '',
  description: '',
  audit_status: 0,
  reject_reason: '',
  logo: ''
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码不能少于6位', trigger: 'blur' }],
  company_name: [{ required: true, message: '请输入企业名称', trigger: 'blur' }],
  credit_code: [{ required: true, message: '请输入统一社会信用代码', trigger: 'blur' }],
  contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  industry: [{ required: true, message: '请输入所属行业', trigger: 'blur' }],
  scale: [{ required: true, message: '请选择规模', trigger: 'change' }],
  nature: [{ required: true, message: '请选择企业性质', trigger: 'change' }],
  address: [{ required: true, message: '请输入办公地点', trigger: 'blur' }],
  reject_reason: [{ required: true, message: '请输入驳回原因', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      audit_status: auditStatus.value !== null ? auditStatus.value : undefined
    }
    const res = await request.get('/users/companies/', { params })
    tableData.value = res.results
    total.value = res.count
  } catch (error) {
    console.error(error)
    ElMessage.error('获取企业列表失败')
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
  auditStatus.value = null
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

const getStatusLabel = (status) => {
  const map = { 0: '待审核', 1: '审核通过', 2: '已驳回' }
  return map[status] || '未知'
}

const getStatusType = (status) => {
  const map = { 0: 'warning', 1: 'success', 2: 'danger' }
  return map[status] || 'info'
}

const handleAdd = () => {
  dialogType.value = 'add'
  Object.assign(form, {
    id: null,
    username: '',
    password: '',
    company_name: '',
    credit_code: '',
    contact_person: '',
    contact_phone: '',
    industry: '',
    scale: '',
    nature: '',
    address: '',
    description: '',
    audit_status: 1, // Default to approved when admin adds
    reject_reason: '',
    logo: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  const formData = {
    id: row.user, // pk is user id
    username: row.username,
    company_name: row.company_name,
    credit_code: row.credit_code,
    contact_person: row.contact_person,
    contact_phone: row.contact_phone,
    industry: row.industry,
    scale: row.scale,
    nature: row.nature,
    address: row.address,
    description: row.description,
    audit_status: row.audit_status,
    reject_reason: row.reject_reason || '',
    logo: row.logo
  }
  Object.assign(form, formData)
  originalForm.value = JSON.parse(JSON.stringify(formData)) // Deep copy
  dialogVisible.value = true
}

const handleUpdateInfo = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (valid) {
             // Check if changed
             let hasChanged = false
             const currentData = JSON.parse(JSON.stringify(form))
             const original = originalForm.value
             
             // Compare fields that are editable
             const fieldsToCheck = [
                 'company_name', 'credit_code', 'contact_person', 'contact_phone',
                 'industry', 'scale', 'nature', 'address', 'description'
             ]
             
             for (const key of fieldsToCheck) {
                 if (currentData[key] !== original[key]) {
                     hasChanged = true
                     break
                 }
             }
             
             if (!hasChanged) {
                 ElMessage.info('信息无更改')
                 return
             }
        
            submitting.value = true
            try {
                // Prepare payload for updating info
                // We should NOT include audit_status unless we want to allow updating it here too.
                // But the requirement implies this button is for "info" modification.
                // To be safe, let's include everything currently in form except logo string.
                
                const payload = { ...form }
                if (typeof payload.logo === 'string' || payload.logo === null) {
                    delete payload.logo
                }
                
                await request.patch(`/users/companies/${form.id}/`, payload)
                ElMessage.success('信息修改成功')
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

const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该企业吗？此操作将同时删除该企业的所有职位和账号信息。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async () => {
    try {
      await request.delete(`/users/companies/${row.user}/`)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleBatchDelete = () => {
  ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 家企业吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async () => {
    try {
      const ids = selectedRows.value.map(row => row.user)
      await request.post('/users/companies/batch_delete/', { ids })
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
        if (dialogType.value === 'add') {
           // Create a copy of form to modify payload
           const payload = { ...form }
           if (typeof payload.logo === 'string' || payload.logo === null) {
               delete payload.logo
           }
           await request.post('/users/companies/', payload)
           ElMessage.success('新增成功')
        } else {
           // For audit (edit), we ONLY send audit_status and reject_reason
           const payload = {
               audit_status: form.audit_status,
               reject_reason: form.audit_status === 2 ? form.reject_reason : ''
           }
           
           await request.patch(`/users/companies/${form.id}/`, payload)
           ElMessage.success('审核完成')
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
.company-management {
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