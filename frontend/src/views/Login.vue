<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>三之文鱼校园招聘系统</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" class="demo-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" label-width="80px">
            <el-form-item label="用户名">
              <el-input v-model="loginForm.username" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="loginForm.password" type="password" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
           <el-form :model="registerForm" label-width="100px">
            <el-form-item label="角色">
              <el-radio-group v-model="registerForm.role">
                <el-radio :label="1">学生</el-radio>
                <el-radio :label="2">企业</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="用户名">
              <el-input v-model="registerForm.username" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="registerForm.password" type="password" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="registerForm.email" />
            </el-form-item>
            
            <!-- Student Specific -->
            <template v-if="registerForm.role === 1">
               <el-form-item label="姓名">
                <el-input v-model="registerForm.name" />
              </el-form-item>
               <el-form-item label="专业">
                <el-input v-model="registerForm.major" />
              </el-form-item>
               <el-form-item label="学历">
                 <el-select v-model="registerForm.education">
                    <el-option label="本科" value="Bachelor" />
                    <el-option label="硕士" value="Master" />
                    <el-option label="博士" value="PhD" />
                 </el-select>
              </el-form-item>
               <el-form-item label="毕业年份">
                <el-input v-model.number="registerForm.graduation_year" />
              </el-form-item>
            </template>
            
            <!-- Company Specific -->
             <template v-if="registerForm.role === 2">
               <el-form-item label="企业名称">
                <el-input v-model="registerForm.company_name" />
              </el-form-item>
               <el-form-item label="统一社会信用代码">
                <el-input v-model="registerForm.credit_code" />
              </el-form-item>
               <el-form-item label="联系人">
                <el-input v-model="registerForm.contact_person" />
              </el-form-item>
               <el-form-item label="联系电话">
                <el-input v-model="registerForm.contact_phone" />
              </el-form-item>
            </template>

            <el-form-item>
              <el-button type="primary" @click="handleRegister" :loading="loading">注册</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    <div class="back-home-btn" @click="$router.push('/')">
      <el-button type="info" plain round>
        <el-icon><HomeFilled /></el-icon> 返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { HomeFilled } from '@element-plus/icons-vue'

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
    ElMessage.success('登录成功')
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
    ElMessage.success('注册成功，请登录')
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
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-image: url('https://images.unsplash.com/photo-1586281380349-632531db7ed4?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80');
  background-size: cover;
  background-position: center;
  position: relative;
}
.back-home-btn {
  margin-top: 20px;
}
.login-card {
  width: 500px;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}
.card-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
}
</style>
