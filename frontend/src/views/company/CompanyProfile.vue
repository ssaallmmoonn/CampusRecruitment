<template>
  <div class="company-profile-edit">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>企业资料设置</span>
        </div>
      </template>

      <el-form 
        :model="form" 
        :rules="rules" 
        ref="formRef" 
        label-width="140px"
        class="profile-form"
      >
        <el-form-item label="企业Logo" prop="logo">
           <el-upload
             class="avatar-uploader"
             action="#"
             :show-file-list="false"
             :before-upload="beforeLogoUpload"
             :http-request="uploadLogo2"
           >
             <img v-if="form.logo" :src="form.logo" class="avatar" />
             <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
           </el-upload>
           <div class="upload-tip">只能上传jpg/png文件，且不超过2MB</div>
        </el-form-item>

        <el-form-item label="企业名称" prop="company_name">
          <el-input v-model="form.company_name" />
        </el-form-item>

        <el-form-item label="统一社会信用代码" prop="credit_code">
          <el-input v-model="form.credit_code" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact_person">
              <el-input v-model="form.contact_person" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input v-model="form.contact_phone" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="办公地点" prop="address">
          <el-input v-model="form.address" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
             <el-form-item label="所属行业" prop="industry">
              <el-select v-model="form.industry" style="width: 100%" allow-create filterable default-first-option>
                <el-option label="计算机软件" value="计算机软件" />
                <el-option label="互联网" value="互联网" />
                <el-option label="电子通信" value="电子通信" />
                <el-option label="金融" value="金融" />
                <el-option label="教育" value="教育" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="人员规模" prop="scale">
              <el-select v-model="form.scale" style="width: 100%">
                <el-option label="0-20人" value="0-20人" />
                <el-option label="20-99人" value="20-99人" />
                <el-option label="100-499人" value="100-499人" />
                <el-option label="500-999人" value="500-999人" />
                <el-option label="1000-9999人" value="1000-9999人" />
                <el-option label="10000人以上" value="10000人以上" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="企业性质" prop="nature">
              <el-select v-model="form.nature" style="width: 100%">
                <el-option label="民营" value="民营" />
                <el-option label="国企" value="国企" />
                <el-option label="外企" value="外企" />
                <el-option label="合资" value="合资" />
                <el-option label="上市公司" value="上市公司" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="企业简介" prop="description">
          <el-input type="textarea" :rows="6" v-model="form.description" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">保存修改</el-button>
          <el-button type="warning" @click="passwordDialogVisible = true">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Password Change Dialog -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px" @close="resetPasswordForm">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="80px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleChangePassword" :loading="passwordLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getCompanyDetail, updateCompanyProfile } from '@/api/company'
import { changePassword } from '@/api/user'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const originalForm = reactive({}) // To store original data for comparison

const form = reactive({
  company_name: '',
  credit_code: '',
  contact_person: '',
  contact_phone: '',
  address: '',
  industry: '',
  scale: '',
  nature: '',
  description: '',
  logo: ''
})

// Function to convert file to base64 for preview and simple upload
const getBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = error => reject(error)
  })
}

const beforeLogoUpload = (file) => {
  const isJPGOrPNG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPGOrPNG) {
    ElMessage.error('上传头像图片只能是 JPG/PNG 格式!')
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
  }
  return isJPGOrPNG && isLt2M
}

const uploadLogo = async (options) => {
  const { file } = options
  try {
    // For now, convert to base64 string to simulate upload and store in 'logo' field
    // In real app, this would upload to server and get a URL back
    // Or we could send FormData to backend if backend supports multipart/form-data
    // Assuming backend 'logo' field can take base64 or url for now, or we just keep it client side for preview
    // To support real file upload, we need a file upload endpoint.
    // Let's use Base64 for simplicity as per requirement "support local upload" implies handling the file.
    // If backend expects a URL, base64 data URI works as a URL in <img> src.
    // BUT Django ImageField expects a file object usually.
    // If we want to support ImageField, we should use FormData in updateCompanyProfile.
    
    // Let's assume we convert to Base64 to show preview, but for actual saving:
    // If we want to save the file to backend, we need to change how we submit the form.
    // We will store the file object temporarily and submit as FormData.
    
    // Wait, the prompt says "support local upload".
    // I will read as DataURL for preview.
    // For submission, I will update 'form.logo' with the base64 string? 
    // Django ImageField doesn't accept Base64 string directly without extra handling.
    // However, if the backend 'logo' field is a CharField (URL) or ImageField?
    // In models.py (I can't see it but likely ImageField).
    // Let's try to handle it as base64 string first, if backend fails, we might need FormData.
    // But since I can't easily change backend to support Base64 upload logic without reading models/serializers deep,
    // I will implement a "mock" upload where I just read it as Base64 and put it in the form.
    // If it's an ImageField, DRF might reject string.
    
    const base64 = await getBase64(file)
    form.logo = base64
    ElMessage.success('图片读取成功')
  } catch (error) {
    ElMessage.error('图片读取失败')
  }
}

const rules = {
  company_name: [{ required: true, message: '请输入企业名称', trigger: 'blur' }],
  credit_code: [{ required: true, message: '请输入统一社会信用代码', trigger: 'blur' }],
  contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

const fetchData = async () => {
  // Use company ID from store (userInfo.id is company ID for company users)
  // Wait, userStore.userInfo might be null on refresh if not persisted or re-fetched.
  // userStore.user has basic info.
  // userStore.userInfo has profile info.
  // If we just logged in, userInfo is populated.
  // If we refresh, we need to ensure userInfo is fetched.
  // The 'user' store usually handles this.
  
  // Also, for 'getCompanyDetail', the ID passed is user ID (from CompanyPublicView logic: filter_kwargs = {'user__id': ...})
  // userStore.user.id is the User ID.
  const userId = userStore.user?.id
  if (!userId) return

  try {
    const res = await getCompanyDetail(userId)
    // Fill form
    Object.keys(form).forEach(key => {
      // Handle logo specifically if it's a full URL or relative path
      // If res[key] is null, don't overwrite default ''
      if (res[key] !== undefined && res[key] !== null) {
          form[key] = res[key]
          originalForm[key] = res[key] // Store original value
      }
    })
  } catch (error) {
    console.error(error)
    ElMessage.error('获取企业信息失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      // Check for changes
      let hasChanges = false
      Object.keys(form).forEach(key => {
          if (key === 'logo') {
              if (rawLogoFile.value) hasChanges = true
          } else {
              if (form[key] !== originalForm[key]) hasChanges = true
          }
      })
      
      if (!hasChanges) {
          ElMessage.info('信息无发生更改')
          return
      }

      loading.value = true
      try {
        // We need to determine if we are sending JSON or FormData
        // If logo is a Base64 string (starts with data:image), we might need to handle it.
        // If it's a URL (starts with http), it's fine.
        // Backend CompanySerializer has 'logo' field.
        // If we send JSON with base64 string to ImageField, it fails.
        // We should really use FormData if we are uploading a file.
        // But 'uploadLogo' just sets form.logo to base64 string.
        
        // Let's assume for this task, we just send what we have.
        // If it fails, we might need to adjust backend or frontend strategy.
        // But since I am an agent, I should try to make it work.
        // A common pattern is to not upload file in 'uploadLogo', but just save the file object.
        // Then in handleSubmit, create FormData.
        
        // BUT, existing updateCompanyProfile uses JSON (request default).
        // Let's try to stick to JSON first. 
        // If the backend doesn't support base64 for ImageField, this part will fail for logo updates.
        // Given I haven't seen Base64 decoding in backend, this is risky.
        // However, I can't change backend to support Base64 easily without adding a library.
        
        // Alternative: Assume logo is just a URL string for now as per previous implementation?
        // But requirement is "local upload".
        // If I can't change backend, I can't support real file upload unless backend supports it.
        // Let's check backend serializer. It uses default ModelSerializer.
        // DRF ModelSerializer ImageField expects a file upload (multipart/form-data).
        
        // So I MUST use FormData for the request if I want to upload a file.
        // And I must update api/company.js to support FormData or let axios handle it.
        
        // Let's construct FormData here.
        const formData = new FormData()
        Object.keys(form).forEach(key => {
            // If logo is base64, we need to convert it back to blob? 
            // Or better, store the original file object in 'uploadLogo'.
            if (key === 'logo') {
                // We will handle logo separately
            } else {
                formData.append(key, form[key])
            }
        })
        
        // We need a way to store the raw file
        // I'll add a separate ref for the file
        if (rawLogoFile.value) {
            formData.append('logo', rawLogoFile.value)
        }
        
        // Note: updateCompanyProfile in api currently sends JSON. 
        // We need to override headers to multipart/form-data?
        // Axios does this automatically if data is FormData.
        
        const userId = userStore.user?.id
        const res = await updateCompanyProfile(userId, formData)
        
        ElMessage.success('保存成功')
        // Update store if needed
        // userStore.setUserInfo({ ...userStore.userInfo, ...res })
        // Directly update state to avoid potential HMR issues with new actions
        if (userStore.userInfo) {
            Object.assign(userStore.userInfo, res)
        } else {
            userStore.userInfo = res
        }
        
        // Update form with response (e.g. new logo url)
        if (res.logo) form.logo = res.logo
        
        // Update originalForm with new values
        Object.keys(form).forEach(key => {
            if (res[key] !== undefined) {
                originalForm[key] = res[key]
            }
        })
        
        rawLogoFile.value = null // Reset raw file
        
      } catch (error) {
        console.error(error)
        ElMessage.error('保存失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// Add a ref for raw file
const rawLogoFile = ref(null)

// Override uploadLogo to store file
const uploadLogo2 = async (options) => {
    const { file } = options
    rawLogoFile.value = file
    // Generate preview
    form.logo = await getBase64(file)
}

// Password Change Logic
const passwordDialogVisible = ref(false)
const passwordLoading = ref(false)
const passwordFormRef = ref(null)
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const resetPasswordForm = () => {
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields()
  }
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      passwordLoading.value = true
      try {
        await changePassword(passwordForm)
        ElMessage.success('密码修改成功，请重新登录')
        passwordDialogVisible.value = false
        // Logout and redirect to login
        userStore.logout()
        router.push('/login')
      } catch (error) {
        // Error is handled in request.js interceptor or here if needed
        // request.js handles general errors, but if we need specific handling:
        if (error.response && error.response.data) {
             const data = error.response.data
             if (data.old_password) {
                 ElMessage.error(data.old_password[0])
             } else if (data.new_password) {
                 ElMessage.error(data.new_password[0])
             } else if (data.confirm_password) {
                 ElMessage.error(data.confirm_password[0])
             }
        }
      } finally {
        passwordLoading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.company-profile-edit {
  max-width: 1000px;
  margin: 0 auto;
}

.profile-form {
  margin-top: 20px;
}

.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  display: block;
  border-radius: 4px;
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
  width: 100px;
  height: 100px;
  text-align: center;
  line-height: 100px; /* Center icon vertically */
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
}

.upload-tip {
    font-size: 12px;
    color: #999;
    margin-top: 5px;
}
</style>
