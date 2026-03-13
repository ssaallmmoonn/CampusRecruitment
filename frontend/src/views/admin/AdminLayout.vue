<template>
  <el-container class="admin-layout">
    <el-header class="admin-header">
      <div class="header-left">
        <img src="@/assets/超级三文鱼.jpg" alt="Logo" class="logo" />
        <span class="system-name">三之文鱼招聘管理后台</span>
      </div>
      <div class="header-center">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>{{ currentRouteName }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-avatar :size="32" :src="userAvatar" />
        <el-dropdown @command="handleCommand">
          <span class="el-dropdown-link">
            {{ adminName }} <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人资料</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container>
      <el-aside width="200px" class="admin-aside">
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          background-color="#001529"
          text-color="#fff"
          active-text-color="#409EFF"
          router
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>系统首页</span>
          </el-menu-item>
          
          <el-sub-menu index="info">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/admin/notices">系统公告</el-menu-item>
            <el-sub-menu index="ads">
              <template #title>广告信息</template>
              <el-menu-item index="/admin/ads/banner">轮播图区</el-menu-item>
              <el-menu-item index="/admin/ads/brand">品牌专区</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/admin/majors">专业分类</el-menu-item>
            <el-menu-item index="/admin/job-categories">职位分类</el-menu-item>
            <el-menu-item index="/admin/industries">行业信息</el-menu-item>
            <el-menu-item index="/admin/jobs">职位信息</el-menu-item>
            <el-menu-item index="/admin/applications">职位投递</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="user">
            <template #title>
              <el-icon><User /></el-icon>
              <span>用户信息</span>
            </template>
            <el-menu-item index="/admin/admins">管理员信息</el-menu-item>
            <el-menu-item index="/admin/companies">企业信息</el-menu-item>
            <el-menu-item index="/admin/students">学生信息</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { HomeFilled, Document, User, ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const currentRouteName = computed(() => route.meta.title || '当前页面')

// Use user info from store
const userAvatar = computed(() => {
  return userStore.userInfo?.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
})

const adminName = computed(() => {
  return userStore.userInfo?.name || userStore.userInfo?.username || '管理员'
})

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/admin/profile')
  }
}

onMounted(() => {
  if (!userStore.userInfo) {
    userStore.fetchUserInfo()
  }
})
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}

.admin-header {
  background-color: #0078d4; /* Blue header matching the screenshot */
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
  gap: 10px;
}

.logo {
  height: 32px;
  width: 32px;
  border-radius: 50%;
  background: white; /* Placeholder background */
  flex-shrink: 0; /* Prevent logo from shrinking */
  object-fit: cover; /* Ensure image covers the area without distortion */
}

.system-name {
  font-size: 18px;
  font-weight: bold;
  white-space: nowrap; /* Prevent text wrapping */
}

.header-center {
  flex: 1;
  margin-left: 40px;
}

/* Breadcrumb customization to match dark blue background */
:deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.7) !important;
}
:deep(.el-breadcrumb__inner.is-link) {
  color: white !important;
}
:deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.7) !important;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.el-dropdown-link {
  color: white;
  display: flex;
  align-items: center;
  cursor: pointer;
  outline: none;
}

.el-dropdown-link:focus-visible {
  outline: none;
}

.admin-aside {
  background-color: #001529;
  flex-shrink: 0; /* Prevent sidebar from shrinking */
}

.el-menu-vertical {
  border-right: none;
}

.admin-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
