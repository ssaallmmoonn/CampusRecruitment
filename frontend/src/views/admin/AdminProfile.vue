<template>
  <div class="admin-profile">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人资料设置</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="100px" ref="formRef" :rules="rules">
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            action=""
            :show-file-list="false"
            :auto-upload="false"
            :on-change="handleAvatarChange"
          >
            <img v-if="form.avatarUrl" :src="form.avatarUrl" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="avatar-tip">点击上传头像，支持 JPG/PNG 格式</div>
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" disabled placeholder="用户名不可修改" />
        </el-form-item>
        
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入电话号码" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">保存修改</el-button>
          <el-button type="warning" @click="dialogVisible = true">修改密码</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Change Password Dialog -->
    <el-dialog v-model="dialogVisible" title="修改密码" width="400px">
      <el-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef" label-width="100px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleChangePassword" :loading="pwdLoading">确认修改</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import request from '@/utils/request'

const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)
const avatarFile = ref(null)

// Password change related
const dialogVisible = ref(false)
const pwdLoading = ref(false)
const pwdFormRef = ref(null)
const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const pwdRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== pwdForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// To store initial data for comparison
const initialForm = reactive({})

const form = reactive({
  username: '',
  name: '',
  email: '',
  phone: '',
  avatarUrl: ''
})

const rules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: ['blur', 'change'] }
  ]
}

const fetchProfile = async () => {
  try {
    // Admin uses base user profile endpoint or we can use the same endpoint as others
    // Since we fixed backend to return user info for admin at /users/profile/
    const res = await request.get('/users/profile/')
    form.username = res.username
    form.name = res.name
    form.email = res.email
    form.phone = res.phone
    form.avatarUrl = res.avatar || ''
    
    // Save initial state
    Object.assign(initialForm, {
      name: res.name,
      email: res.email,
      phone: res.phone,
      avatarUrl: res.avatar || ''
    })
  } catch (error) {
    console.error('Fetch profile failed:', error)
    ElMessage.error('获取个人资料失败')
  }
}

const handleAvatarChange = (file) => {
  const isJPG = file.raw.type === 'image/jpeg' || file.raw.type === 'image/png'
  const isLt2M = file.raw.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error('头像只能是 JPG 或 PNG 格式!')
    return
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB!')
    return
  }

  avatarFile.value = file.raw
  form.avatarUrl = URL.createObjectURL(file.raw)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      // Check for changes
      const hasChanges = 
        form.name !== initialForm.name ||
        form.email !== initialForm.email ||
        form.phone !== initialForm.phone ||
        avatarFile.value !== null

      if (!hasChanges) {
        ElMessage.info('用户信息无更改')
        return
      }

      loading.value = true
      try {
        const formData = new FormData()
        if (form.name !== initialForm.name) formData.append('name', form.name)
        if (form.email !== initialForm.email) formData.append('email', form.email)
        if (form.phone !== initialForm.phone) formData.append('phone', form.phone)
        if (avatarFile.value) {
          formData.append('avatar', avatarFile.value)
        }
        
        // Use PATCH to update partial fields
        const res = await request.patch('/users/profile/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        ElMessage.success('个人资料更新成功')
        // Update store info if needed
        userStore.setUserInfo(res)
        // Update initial form
        Object.assign(initialForm, {
            name: res.name,
            email: res.email,
            phone: res.phone,
            avatarUrl: res.avatar || ''
        })
        avatarFile.value = null
        
      } catch (error) {
        console.error('Update profile failed:', error)
        ElMessage.error('更新失败: ' + (error.response?.data?.detail || '未知错误'))
      } finally {
        loading.value = false
      }
    }
  })
}

const handleChangePassword = async () => {
  if (!pwdFormRef.value) return
  
  await pwdFormRef.value.validate(async (valid) => {
    if (valid) {
      pwdLoading.value = true
      try {
        await request.put('/users/change-password/', {
          old_password: pwdForm.old_password,
          new_password: pwdForm.new_password,
          confirm_password: pwdForm.confirm_password
        })
        ElMessage.success('密码修改成功，请重新登录')
        dialogVisible.value = false
        userStore.logout()
        // Router push to login handled by store or component logic if needed
        window.location.href = '/login'
      } catch (error) {
         const errorMsg = error.response?.data?.old_password?.[0] || 
                          error.response?.data?.new_password?.[0] ||
                          error.response?.data?.confirm_password?.[0] ||
                          '密码修改失败'
        ElMessage.error(errorMsg)
      } finally {
        pwdLoading.value = false
      }
    }
  })
}

const resetForm = () => {
  fetchProfile()
  avatarFile.value = null
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.admin-profile {
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  border-radius: 8px;
}

.card-header {
  font-weight: bold;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100px;
  height: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: border-color 0.3s;
}

.avatar-uploader:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.avatar {
  width: 100px;
  height: 100px;
  display: block;
  object-fit: cover;
}

.avatar-tip {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}
</style>