<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header">
        <div class="logo">Campus Recruitment</div>
        <div class="user-info" v-if="userStore.isLoggedIn">
          <span>Welcome, {{ userStore.user.username }} ({{ roleText }})</span>
          <el-button type="text" @click="handleLogout">Logout</el-button>
        </div>
        <div v-else>
           <el-button @click="$router.push('/login')">Login / Register</el-button>
        </div>
      </el-header>
      
      <el-container>
        <el-aside width="200px">
           <el-menu router :default-active="$route.path">
             <el-menu-item index="/">
               <el-icon><House /></el-icon>
               <span>Home</span>
             </el-menu-item>
             
             <!-- Guest Menu -->
             <template v-if="!userStore.isLoggedIn">
               <el-menu-item index="/jobs">
                 <el-icon><Search /></el-icon>
                 <span>Jobs</span>
               </el-menu-item>
               <el-menu-item index="/login">
                 <el-icon><User /></el-icon>
                 <span>Login</span>
               </el-menu-item>
             </template>

             <!-- Student Menu -->
             <template v-if="userStore.role === 1">
               <el-menu-item index="/jobs">
                 <el-icon><Search /></el-icon>
                 <span>Jobs</span>
               </el-menu-item>
               <el-menu-item index="/my-applications">
                 <el-icon><Document /></el-icon>
                 <span>My Applications</span>
               </el-menu-item>
               <el-menu-item index="/resume">
                 <el-icon><User /></el-icon>
                 <span>My Resume</span>
               </el-menu-item>
             </template>
             
             <!-- Company Menu -->
             <template v-if="userStore.role === 2">
               <el-menu-item index="/company/jobs">
                 <el-icon><Briefcase /></el-icon>
                 <span>My Jobs</span>
               </el-menu-item>
               <el-menu-item index="/company/applications">
                 <el-icon><Files /></el-icon>
                 <span>Applications</span>
               </el-menu-item>
             </template>
             
           </el-menu>
        </el-aside>
        
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const roleText = computed(() => {
  if (userStore.role === 1) return 'Student'
  if (userStore.role === 2) return 'Company'
  if (userStore.role === 3) return 'Admin'
  return ''
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.header {
  background-color: #409EFF;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}
.logo {
  font-size: 20px;
  font-weight: bold;
}
.user-info span {
  margin-right: 15px;
}
.welcome-hero {
  text-align: center;
  margin-top: 100px;
}
</style>
