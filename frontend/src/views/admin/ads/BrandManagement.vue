<template>
  <div class="brand-management">
    <el-card shadow="never">
      <div class="header-actions">
        <h3>品牌专区管理</h3>
        <el-button type="primary" @click="openDialog('create')">新增品牌</el-button>
      </div>

      <el-table :data="brandList" v-loading="loading" style="width: 100%; margin-top: 20px;">
        <el-table-column prop="name" label="品牌名称" min-width="150" />
        <el-table-column label="Logo" width="250">
          <template #default="{ row }">
            <el-image 
              :src="row.logo || row.company_detail?.logo" 
              :preview-src-list="[row.logo || row.company_detail?.logo]" 
              fit="contain" 
              style="width: 80px; height: 80px; border-radius: 4px; background: #f5f7fa;"
            >
              <template #error>
                <div class="image-slot" style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; color: #909399; background: #f5f7fa;">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        <el-table-column label="关联企业" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.company_detail">{{ row.company_detail.company_name }}</span>
            <el-tag v-else type="info" size="small">未关联</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order" label="排序" width="80" align="center" />
        <el-table-column label="状态" width="150" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="large">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="middle" @click="openDialog('edit', row)">编辑</el-button>
            <el-button size="middle" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新增品牌' : '编辑品牌'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" ref="formRef" :rules="rules" label-width="80px">
        <el-form-item label="品牌名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入品牌名称" />
        </el-form-item>
        
        <el-form-item label="Logo" prop="logo">
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :auto-upload="false"
            :on-change="handleFileChange"
          >
            <img v-if="previewUrl" :src="previewUrl" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="el-upload__tip">建议尺寸：200x200，支持 jpg/png。未上传将使用关联企业的Logo</div>
        </el-form-item>

        <el-form-item label="关联企业" prop="company">
          <el-select
            v-model="form.company"
            placeholder="请选择关联企业 (用于跳转)"
            filterable
            remote
            :remote-method="searchCompanies"
            :loading="companyLoading"
            clearable
            @change="handleCompanyChange"
            style="width: 100%"
          >
            <el-option
              v-for="item in companyOptions"
              :key="item.id"
              :label="item.company_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="排序" prop="order">
          <el-input-number v-model="form.order" :min="0" :max="999" />
          <span class="el-upload__tip" style="margin-left: 10px;">数值越小越靠前</span>
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Picture } from '@element-plus/icons-vue'
import { getBrands, createBrand, updateBrand, deleteBrand } from '@/api/ads'
import request from '@/utils/request'

const loading = ref(false)
const brandList = ref([])
const dialogVisible = ref(false)
const dialogType = ref('create')
const submitting = ref(false)
const formRef = ref(null)

const companyLoading = ref(false)
const companyOptions = ref([])

const form = reactive({
  id: null,
  name: '',
  company: null,
  order: 0,
  is_active: true,
  logoFile: null
})

const previewUrl = ref('')

const rules = {
  name: [{ required: true, message: '请输入品牌名称', trigger: 'blur' }]
}

const fetchBrands = async () => {
  loading.value = true
  try {
    const res = await getBrands()
    brandList.value = res.results || res
  } catch (error) {
    console.error(error)
    ElMessage.error('获取品牌列表失败')
  } finally {
    loading.value = false
  }
}

const searchCompanies = async (query) => {
  if (!query) {
    companyOptions.value = []
    return
  }
  companyLoading.value = true
  try {
    // Assuming there's an API to search companies. Using users list with role=2 filter or dedicated company search
    // Since we don't have a direct search API documented, we might need to use existing endpoint
    // Let's try to use the admin companies endpoint or just generic user search
    // Actually, AdminCompanyManagement uses /api/users/companies/
    const res = await request.get('/users/companies/', { params: { search: query } })
    companyOptions.value = res.results || res
  } catch (error) {
    console.error(error)
  } finally {
    companyLoading.value = false
  }
}

const handleCompanyChange = (val) => {
  if (!val) return
  const selected = companyOptions.value.find(item => item.id === val)
  if (selected) {
    // If name is empty, auto fill with company name
    if (!form.name) {
      form.name = selected.company_name
    }
    // If no custom logo uploaded, show company logo as preview
    if (!form.logoFile && selected.logo) {
      previewUrl.value = selected.logo
    }
  }
}

const openDialog = (type, row) => {
  dialogType.value = type
  dialogVisible.value = true
  companyOptions.value = [] // Reset options
  
  if (type === 'edit') {
    form.id = row.id
    form.name = row.name
    form.company = row.company
    form.order = row.order
    form.is_active = row.is_active
    form.logoFile = null
    previewUrl.value = row.logo
    
    // Pre-fill company option if exists
    if (row.company_detail) {
      companyOptions.value = [row.company_detail]
    }
  } else {
    form.id = null
    form.name = ''
    form.company = null
    form.order = 0
    form.is_active = true
    form.logoFile = null
    previewUrl.value = ''
  }
}

const handleFileChange = (file) => {
  const isImage = file.raw.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return
  }
  form.logoFile = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  if (formRef.value) formRef.value.validateField('logo')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const formData = new FormData()
      formData.append('name', form.name)
      if (form.company) formData.append('company', form.company)
      formData.append('order', form.order)
      formData.append('is_active', form.is_active)
      if (form.logoFile) {
        formData.append('logo', form.logoFile)
      }

      if (dialogType.value === 'create') {
        await createBrand(formData)
        ElMessage.success('创建成功')
      } else {
        await updateBrand(form.id, formData)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      fetchBrands()
    } catch (error) {
      console.error(error)
      ElMessage.error('操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该品牌吗?', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteBrand(row.id)
      ElMessage.success('删除成功')
      fetchBrands()
    } catch (error) {
      console.error(error)
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  fetchBrands()
})
</script>

<style scoped>
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.avatar-uploader .avatar {
  width: 120px;
  height: 120px;
  display: block;
  object-fit: contain;
  border-radius: 6px;
  background: #f5f7fa;
}

.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
}
</style>
