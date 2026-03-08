<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <!-- Left: System Name -->
          <div class="logo" @click="$router.push('/')">
            三之文鱼招聘
          </div>

          <!-- Center: Navigation Menu -->
          <div class="nav-menu">
            <el-menu
              :default-active="$route.path"
              mode="horizontal"
              router
              background-color="#ffffff"
              text-color="#303133"
              active-text-color="#409EFF"
              :ellipsis="false"
            >
              <el-menu-item index="/">首页</el-menu-item>
              
              <!-- Student / Guest Navigation -->
              <template v-if="!userStore.isLoggedIn || userStore.role === 1">
                <el-menu-item index="/recommendations">职位推荐</el-menu-item>
                <el-menu-item index="/jobs">职位搜索</el-menu-item>
                <el-menu-item index="/my-collections">我的收藏</el-menu-item>
                <el-menu-item index="/my-applications">我的投递</el-menu-item>
                <el-menu-item index="/resume">我的简历</el-menu-item>
              </template>

              <!-- Company Navigation (Keep for compatibility) -->
              <template v-if="userStore.role === 2">
                <el-menu-item index="/company/jobs">我的发布</el-menu-item>
                <el-menu-item index="/company/applications">收到的投递</el-menu-item>
              </template>
            </el-menu>
          </div>

          <!-- Right: User Info -->
          <div class="user-actions">
            <template v-if="userStore.isLoggedIn">
              <el-dropdown trigger="click" @command="handleCommand">
                <div class="user-profile">
                  <el-avatar :size="32" :src="userAvatar" class="avatar" />
                  <span class="username">{{ userStore.userInfo?.username }}</span>
                  <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                    <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button type="primary" link @click="$router.push('/login')">登录 / 注册</el-button>
            </template>
          </div>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <keep-alive include="JobBoard">
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </el-main>

      <div class="site-footer">
          <div class="footer-bottom">
            <div class="footer-content">
            <p>未经 Zhaopin.com 同意，不得转载本网站之所有招聘信息及作品 智联招聘网版权所有</p>
            <p>京ICP备 17067871号 合字 B2-20210134 京公网安备 11010502030147号 人力资源许可证 1101052003273号</p>
            <p>网上有害信息举报专区 违法不良信息举报电话: 400-885-9898 关爱未成年举报热线: 400-885-9898-3 朝阳区人力资源与社会保障局 监督电话</p>
            <div class="footer-icons">
            <span class="icon-placeholder"><el-icon><Trophy /></el-icon> 电子营业执照</span>
            <span class="icon-placeholder"><el-icon><Lock /></el-icon> 网络110报警服务</span>
          </div>
        </div>
      </div>
    </div>
    </el-container>
  </div>

  
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()

// Placeholder avatar
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const userAvatar = computed(() => {
  return userStore.userInfo?.avatar || defaultAvatar
})

onMounted(() => {
  if (userStore.isLoggedIn && !userStore.userInfo) {
    userStore.fetchUserInfo()
  }
})

  const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.common-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

:deep(.el-container) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.el-main) {
  flex: 1;
  padding: 0; /* Let child views handle padding */
}
</style>
<style>
.header {
  background-color: #ffffff;
  border-bottom: 1px solid #dcdfe6;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  cursor: pointer;
  display: flex;
  align-items: center;
  min-width: 200px;
}

.nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
  height: 100%;
}

.el-menu {
  border-bottom: none !important;
  background-color: transparent !important;
}

.el-menu-item {
  font-size: 16px;
  height: 60px !important;
  line-height: 60px !important;
  border-bottom: none !important;
}



.el-menu-item.is-active {
  border-bottom: 2px solid #409EFF !important;
}

.user-actions {
  min-width: 150px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-profile:hover {
  background-color: #f5f7fa;
}

.avatar {
  margin-right: 8px;
}

.username {
  font-size: 16px;
  color: #606266;
  margin-right: 4px;
}

/* Footer Styles */
.site-footer {
  width: 100%;
  margin-top: 60px;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.footer-bottom {
  background-color: #1f2126;
  padding: 30px 0;
  color: #909399;
  font-size: 12px;
  line-height: 1.8;
  text-align: center;
}

.footer-bottom .footer-content {
  flex-direction: column;
}

.footer-bottom p {
  margin: 5px 0;
}

.footer-icons {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  gap: 20px;
}

.icon-placeholder {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border: 1px solid #4c4d50;
  border-radius: 4px;
  cursor: pointer;
}

.icon-placeholder:hover {
  color: #fff;
  border-color: #fff;
}
</style>