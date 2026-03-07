<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>Campus Recruitment System</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" class="demo-tabs">
        <el-tab-pane label="Login" name="login">
          <el-form :model="loginForm" label-width="80px">
            <el-form-item label="Username">
              <el-input v-model="loginForm.username" />
            </el-form-item>
            <el-form-item label="Password">
              <el-input v-model="loginForm.password" type="password" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleLogin" :loading="loading">Login</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="Register" name="register">
           <el-form :model="registerForm" label-width="100px">
            <el-form-item label="Role">
              <el-radio-group v-model="registerForm.role">
                <el-radio :label="1">Student</el-radio>
                <el-radio :label="2">Company</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="Username">
              <el-input v-model="registerForm.username" />
            </el-form-item>
            <el-form-item label="Password">
              <el-input v-model="registerForm.password" type="password" />
            </el-form-item>
             <el-form-item label="Email">
              <el-input v-model="registerForm.email" />
            </el-form-item>
            
            <!-- Student Specific -->
            <template v-if="registerForm.role === 1">
               <el-form-item label="Name">
                <el-input v-model="registerForm.name" />
              </el-form-item>
               <el-form-item label="Major">
                <el-input v-model="registerForm.major" />
              </el-form-item>
               <el-form-item label="Education">
                 <el-select v-model="registerForm.education">
                    <el-option label="Bachelor" value="Bachelor" />
                    <el-option label="Master" value="Master" />
                    <el-option label="PhD" value="PhD" />
                 </el-select>
              </el-form-item>
               <el-form-item label="Grad Year">
                <el-input v-model.number="registerForm.graduation_year" />
              </el-form-item>
            </template>
            
            <!-- Company Specific -->
             <template v-if="registerForm.role === 2">
               <el-form-item label="Company">
                <el-input v-model="registerForm.company_name" />
              </el-form-item>
               <el-form-item label="Credit Code">
                <el-input v-model="registerForm.credit_code" />
              </el-form-item>
               <el-form-item label="Contact">
                <el-input v-model="registerForm.contact_person" />
              </el-form-item>
               <el-form-item label="Phone">
                <el-input v-model="registerForm.contact_phone" />
              </el-form-item>
            </template>

            <el-form-item>
              <el-button type="primary" @click="handleRegister" :loading="loading">Register</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()

const activeTab = ref('login')
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  email: '',
  role: 1,
  // Student
  name: '',
  major: '',
  education: 'Bachelor',
  graduation_year: new Date().getFullYear(),
  // Company
  company_name: '',
  credit_code: '',
  contact_person: '',
  contact_phone: ''
})

const handleLogin = async () => {
  loading.value = true
  try {
    await userStore.login(loginForm.username, loginForm.password)
    ElMessage.success('Login successful')
    router.push('/')
  } catch (error) {
    // Error handled in interceptor
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  loading.value = true
  try {
    await userStore.register(registerForm)
    ElMessage.success('Registration successful, please login')
    activeTab.value = 'login'
  } catch (error) {
     // Error handled in interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}
.login-card {
  width: 500px;
}
.card-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
}
</style>
