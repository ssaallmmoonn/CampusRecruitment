<template>
  <div class="company-layout">
    <el-container>
      <!-- Header -->
      <el-header class="company-header">
        <div class="header-left">
          <div class="logo">
            <span class="logo-text">三之文鱼招聘系统管理后台</span>
          </div>
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/company/jobs' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRouteName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-profile">
              <el-avatar :size="32" :src="userAvatar" class="avatar" />
              <span class="username">{{ userStore.userInfo?.company_name || userStore.user?.username }}</span>
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">企业资料</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-container class="main-container">
        <!-- Sidebar -->
        <el-aside width="200px" class="company-sidebar">
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical"
            background-color="#001529"
            text-color="#bfcbd9"
            active-text-color="#fff"
            router
          >
            <el-sub-menu index="1">
              <template #title>
                <el-icon><User /></el-icon>
                <span>信息管理</span>
              </template>
              <el-menu-item index="/company/jobs">职位信息</el-menu-item>
              <el-menu-item index="/company/applications">职位投递</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-aside>

        <!-- Main Content -->
        <el-main class="company-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter, useRoute } from 'vue-router'
import { ArrowDown, User } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const userAvatar = computed(() => {
  return userStore.userInfo?.logo || userStore.userInfo?.avatar || defaultAvatar
})

const activeMenu = computed(() => {
  return route.path
})

const currentRouteName = computed(() => {
  if (route.path.includes('/jobs')) return '职位信息'
  if (route.path.includes('/applications')) return '职位投递'
  if (route.path.includes('/profile')) return '企业资料'
  return ''
})

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/company/profile')
  }
}

onMounted(() => {
    if (!userStore.userInfo) {
        userStore.fetchUserInfo()
    }
})
</script>

<style scoped>
.company-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.company-header {
  background-color: #007bff; /* Blue header as per image */
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
}

.breadcrumb :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.8) !important;
}

.breadcrumb :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: white !important;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: white;
}

.username {
  margin-left: 8px;
  margin-right: 4px;
}

.main-container {
  flex: 1;
  overflow: hidden;
}

.company-sidebar {
  background-color: #001529;
}

.el-menu-vertical {
  border-right: none;
}

.company-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
