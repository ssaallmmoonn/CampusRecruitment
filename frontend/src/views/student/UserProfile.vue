<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人中心</span>
        </div>
      </template>

      <el-form 
        ref="profileFormRef"
        :model="form" 
        :rules="rules" 
        label-width="100px"
        v-loading="loading"
      >
        <!-- Avatar Section -->
        <div class="avatar-section">
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :on-change="handleAvatarChange"
            :before-upload="beforeAvatarUpload"
            :auto-upload="false"
          >
            <img v-if="avatarUrl" :src="avatarUrl" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="avatar-tip">点击图片更换头像 (JPG/PNG, 最大 2MB)</div>
        </div>

        <el-divider />

        <!-- Basic Info -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学历" prop="education">
              <el-select v-model="form.education" placeholder="请选择学历" style="width: 100%">
                <el-option label="初中及以下" value="初中及以下" />
                <el-option label="高中" value="高中" />
                <el-option label="中专/中技" value="中专/中技" />
                <el-option label="大专" value="大专" />
                <el-option label="本科" value="本科" />
                <el-option label="硕士" value="硕士" />
                <el-option label="博士" value="博士" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学校" prop="school">
              <el-input v-model="form.school" placeholder="请输入学校名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专业" prop="major">
              <el-input v-model="form.major" placeholder="请输入专业名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="毕业年份" prop="graduation_year">
              <el-input-number v-model="form.graduation_year" :min="1900" :max="2099" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider />

        <!-- Contact Info -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电话号码" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入电话号码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱地址" />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-actions">
          <el-button type="primary" @click="handleUpdate" :loading="submitting">
            修改信息
          </el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../utils/request'
import { useUserStore } from '../../stores/user'

import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
const loading = ref(false)
const submitting = ref(false)
const profileFormRef = ref(null)

const form = reactive({
  avatar: null, // Now stores file object or URL
  name: '',
  education: '',
  school: '',
  major: '',
  graduation_year: new Date().getFullYear(),
  phone: '',
  email: ''
})

const avatarUrl = ref('') // For display
const avatarFile = ref(null) // For upload

// Original data for reset
const originalData = ref({})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  education: [{ required: true, message: '请选择学历', trigger: 'change' }],
  school: [{ required: true, message: '请输入学校', trigger: 'blur' }],
  major: [{ required: true, message: '请输入专业', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入电话号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

const fetchProfile = async () => {
  loading.value = true
  try {
    const data = await request.get('/users/profile/')
    
    // Map response data to form
    Object.keys(form).forEach(key => {
      if (data[key] !== undefined && data[key] !== null) {
        if (key === 'avatar') {
            avatarUrl.value = data[key]
        } else {
            form[key] = data[key]
        }
      }
    })
    
    // Store original data
    originalData.value = JSON.parse(JSON.stringify(form))
    originalData.value.avatarUrl = avatarUrl.value
  } catch (error) {
    console.error('Error fetching profile:', error)
    if (error.response && error.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      userStore.logout()
      router.push('/login')
    } else {
      ElMessage.error('获取个人信息失败')
    }
  } finally {
    loading.value = false
  }
}

const handleAvatarChange = (file) => {
  avatarFile.value = file.raw
  avatarUrl.value = URL.createObjectURL(file.raw)
}

const beforeAvatarUpload = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('头像必须是 JPG 或 PNG 格式!')
    return false
  }
  if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

const handleUpdate = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid, fields) => {
    if (valid) {
      submitting.value = true
      try {
        const formData = new FormData()
        Object.keys(form).forEach(key => {
            if (key !== 'avatar' && form[key] !== null) {
                formData.append(key, form[key])
            }
        })
        
        if (avatarFile.value) {
            formData.append('avatar', avatarFile.value)
        }

        const response = await request.put('/users/profile/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        
        if (response.status === 'unchanged') {
            ElMessageBox.alert('信息无发生更改', '提示', {
            confirmButtonText: '确定',
            type: 'info'
          })
        } else {
          ElMessage.success('修改信息成功')
          // Update original data
          originalData.value = JSON.parse(JSON.stringify(form))
          originalData.value.avatarUrl = avatarUrl.value
          avatarFile.value = null // Reset file input
        }
      } catch (error) {
        console.error('Error updating profile:', error)
        if (error.response && error.response.data) {
             // Handle specific field errors if any
             const msg = Object.values(error.response.data).flat().join('; ')
             ElMessage.error(msg || '修改失败，请重试')
        } else {
            ElMessage.error('修改失败，请重试')
        }
      } finally {
        submitting.value = false
      }
    } else {
      ElMessage.warning('请填写所有必填项')
    }
  })
}

const resetForm = () => {
  Object.assign(form, JSON.parse(JSON.stringify(originalData.value)))
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 18px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
  width: 120px;
  height: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-uploader:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  text-align: center;
  line-height: 120px;
}

.avatar {
  width: 120px;
  height: 120px;
  display: block;
  object-fit: cover;
}

.avatar-tip {
    margin-top: 10px;
    font-size: 12px;
    color: #909399;
}

.mb-4 {
  margin-bottom: 16px;
}

.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  gap: 20px;
}
</style>