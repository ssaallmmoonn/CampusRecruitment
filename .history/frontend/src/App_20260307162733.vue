<script setup>
</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <el-menu :default-active="'1'" class="el-menu-demo" mode="horizontal">
          <el-menu-item index="1">首页</el-menu-item>
          <el-menu-item index="2">职位浏览</el-menu-item>
          <el-sub-menu index="3">
            <template #title>个人中心</template>
            <el-menu-item index="3-1">我的简历</el-menu-item>
            <el-menu-item index="3-2">投递记录</el-menu-item>
            <el-menu-item index="3-3">退出登录</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
  'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}
</style>
