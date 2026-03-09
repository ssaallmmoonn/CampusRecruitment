<template>
  <div class="company-detail-page" v-loading="loading">
    <div class="company-header-bg">
      <div class="container header-content">
        <div class="header-left">
          <div class="company-logo-wrapper">
             <img :src="company.logo || defaultLogo" class="company-logo" />
          </div>
          <div class="company-info">
            <h1 class="company-name">{{ company.company_name }}</h1>
            <div class="company-meta">
              <span>{{ company.nature || '性质未知' }}</span>
              <el-divider direction="vertical" />
              <span>{{ company.scale || '规模未知' }}</span>
              <el-divider direction="vertical" />
              <span>{{ company.industry || '行业未知' }}</span>
            </div>
          </div>
        </div>
        <div class="header-right">
          <div class="stat-item">
            <div class="stat-num">{{ jobCount }}</div>
            <div class="stat-label">在招职位</div>
          </div>
        </div>
      </div>
    </div>

    <div class="container main-content">
      <div class="nav-tabs">
        <div 
          class="nav-tab" 
          :class="{ active: activeTab === 'intro' }"
          @click="activeTab = 'intro'"
        >
          公司简介
        </div>
        <div 
          class="nav-tab" 
          :class="{ active: activeTab === 'jobs' }"
          @click="activeTab = 'jobs'"
        >
          在招职位 · {{ jobCount }}
        </div>
      </div>

      <div class="tab-content">
        <CompanyIntro 
          v-if="activeTab === 'intro'" 
          :company="company" 
          @switch-tab="activeTab = 'jobs'" 
        />
        <CompanyJobs 
          v-if="activeTab === 'jobs'" 
          :company="company" 
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'
import { getCompanyDetail } from '@/api/company'
import { getJobs } from '@/api/jobs'
import CompanyIntro from './components/CompanyIntro.vue'
import CompanyJobs from './components/CompanyJobs.vue'

const route = useRoute()
const loading = ref(false)
const company = ref({})
const jobCount = ref(0)
const activeTab = ref('intro')
const defaultLogo = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'

const fetchCompanyDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    const res = await getCompanyDetail(id)
    company.value = res
    
    // Fetch job count
    const jobsRes = await getJobs({ company_id: id, page_size: 1 })
    jobCount.value = jobsRes.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCompanyDetail()
})
</script>

<style scoped>
.company-detail-page {
  background-color: #f5f7fa;
  min-height: 100vh;
}

.company-header-bg {
  background: #fff;
  padding: 40px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.company-logo-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  border: 1px solid #eee;
  padding: 4px;
  margin-right: 20px;
  background: #fff;
}

.company-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.company-name {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin: 0 0 10px 0;
}

.company-meta {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-num {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

/* Tabs */
.nav-tabs {
  display: flex;
  gap: 40px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 2px;
}

.nav-tab {
  font-size: 16px;
  color: #666;
  padding-bottom: 12px;
  cursor: pointer;
  position: relative;
  font-weight: 500;
  transition: all 0.3s;
}

.nav-tab:hover {
  color: #409EFF;
}

.nav-tab.active {
  color: #409EFF;
  font-weight: bold;
}

.nav-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: #409EFF;
  border-radius: 2px;
}
</style>