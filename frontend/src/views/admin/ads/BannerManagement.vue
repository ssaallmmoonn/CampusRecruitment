<template>
  <div class="banner-management">
    <el-card shadow="never">
      <div class="header-actions">
        <h3>轮播图管理</h3>
        <el-button type="primary" @click="openDialog('create')">新增轮播图</el-button>
      </div>

      <el-table :data="bannerList" v-loading="loading" style="width: 100%; margin-top: 20px;">
        <el-table-column prop="title" label="标题" min-width="150" />
        <el-table-column label="图片" width="300">
          <template #default="{ row }">
            <el-image 
              :src="row.image" 
              :preview-src-list="[row.image]" 
              fit="cover" 
              style="width: 160px; height: 90px; border-radius: 4px;"
            />
          </template>
        </el-table-column>
        <el-table-column prop="link_url" label="跳转链接" min-width="150" show-overflow-tooltip />
        <el-table-column prop="order" label="排序" width="150" align="center" />
        <el-table-column label="状态" width="150" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="large">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="medium" @click="openDialog('edit', row)">编辑</el-button>
            <el-button size="medium" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新增轮播图' : '编辑轮播图'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" ref="formRef" :rules="rules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        
        <el-form-item label="图片" prop="image">
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
          <div class="el-upload__tip">建议尺寸：1920x400，支持 jpg/png</div>
        </el-form-item>

        <el-form-item label="跳转链接" prop="link_url">
          <el-input v-model="form.link_url" placeholder="请输入跳转链接 (可选)" />
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
import { Plus } from '@element-plus/icons-vue'
import { getBanners, createBanner, updateBanner, deleteBanner } from '@/api/ads'

const loading = ref(false)
const bannerList = ref([])
const dialogVisible = ref(false)
const dialogType = ref('create')
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  title: '',
  link_url: '',
  order: 0,
  is_active: true,
  imageFile: null
})

const previewUrl = ref('')

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  // Create mode: image is required. Edit mode: optional (if not changed)
  image: [{ 
    validator: (rule, value, callback) => {
      if (dialogType.value === 'create' && !form.imageFile) {
        callback(new Error('请上传图片'))
      } else {
        callback()
      }
    }, 
    trigger: 'change' 
  }]
}

const fetchBanners = async () => {
  loading.value = true
  try {
    const res = await getBanners()
    bannerList.value = res.results || res
  } catch (error) {
    console.error(error)
    ElMessage.error('获取轮播图失败')
  } finally {
    loading.value = false
  }
}

const openDialog = (type, row) => {
  dialogType.value = type
  dialogVisible.value = true
  if (type === 'edit') {
    form.id = row.id
    form.title = row.title
    form.link_url = row.link_url
    form.order = row.order
    form.is_active = row.is_active
    form.imageFile = null
    previewUrl.value = row.image
  } else {
    form.id = null
    form.title = ''
    form.link_url = ''
    form.order = 0
    form.is_active = true
    form.imageFile = null
    previewUrl.value = ''
  }
}

const handleFileChange = (file) => {
  const isImage = file.raw.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return
  }
  form.imageFile = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  // Trigger validation manually if needed
  if (formRef.value) formRef.value.validateField('image')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const formData = new FormData()
      formData.append('title', form.title)
      if (form.link_url) formData.append('link_url', form.link_url)
      formData.append('order', form.order)
      formData.append('is_active', form.is_active)
      if (form.imageFile) {
        formData.append('image', form.imageFile)
      }

      if (dialogType.value === 'create') {
        await createBanner(formData)
        ElMessage.success('创建成功')
      } else {
        await updateBanner(form.id, formData)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      fetchBanners()
    } catch (error) {
      console.error(error)
      ElMessage.error('操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该轮播图吗?', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteBanner(row.id)
      ElMessage.success('删除成功')
      fetchBanners()
    } catch (error) {
      console.error(error)
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  fetchBanners()
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
  width: 320px;
  height: 180px;
  display: block;
  object-fit: cover;
  border-radius: 6px;
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
  width: 320px;
  height: 180px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
}
</style>
