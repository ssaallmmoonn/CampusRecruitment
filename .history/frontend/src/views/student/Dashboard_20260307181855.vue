<template>
  <div class="dashboard-container">
    <div v-if="userStore.isLoggedIn">
      <h1>Welcome back, {{ userStore.user.username }}!</h1>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="hover" @click="$router.push('/jobs')">
            <template #header>
              <div class="card-header">
                <span>Find Jobs</span>
              </div>
            </template>
            <div class="card-content">
              <el-icon :size="40"><Search /></el-icon>
              <p>Browse latest job openings</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" @click="$router.push('/resume')">
            <template #header>
              <div class="card-header">
                <span>My Resume</span>
              </div>
            </template>
            <div class="card-content">
              <el-icon :size="40"><User /></el-icon>
              <p>Manage your professional profile</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" @click="$router.push('/my-applications')">
            <template #header>
              <div class="card-header">
                <span>Applications</span>
              </div>
            </template>
            <div class="card-content">
              <el-icon :size="40"><Document /></el-icon>
              <p>Track your job applications</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <div v-else class="guest-dashboard">
      <h1>Find Your Dream Job</h1>
      <p>Join thousands of students and companies.</p>
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="$router.push('/jobs')">Browse Jobs</el-button>
        <el-button size="large" @click="$router.push('/login')">Login / Register</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from '../../stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}
.card-content {
  text-align: center;
  padding: 20px 0;
  cursor: pointer;
}
.card-content p {
  margin-top: 10px;
  color: #606266;
}
</style>