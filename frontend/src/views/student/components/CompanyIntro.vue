<template>
  <div class="company-intro-container">
    <!-- Hot Jobs Section -->
    <div class="section-card hot-jobs">
      <div class="section-header">
        <h3>热招职位</h3>
        <el-button type="text" @click="$emit('switch-tab', 'jobs')">查看全部 <el-icon><ArrowRight /></el-icon></el-button>
      </div>
      <div class="hot-jobs-list" v-loading="loading">
        <el-empty v-if="jobs.length === 0" description="暂无热招职位" />
        <div 
          v-else 
          v-for="job in jobs.slice(0, 3)" 
          :key="job.id" 
          class="hot-job-card"
          @click="goToJob(job.id)"
        >
          <div class="job-top">
            <span class="job-name">{{ job.job_name }}</span>
            <span class="job-salary">{{ job.salary }}</span>
          </div>
          <div class="job-tags">
            <el-tag size="small" effect="plain">{{ job.location }}</el-tag>
            <el-tag size="small" effect="plain">{{ job.job_type }}</el-tag>
            <el-tag size="small" effect="plain">{{ job.experience_requirement }}</el-tag>
          </div>
        </div>
      </div>
    </div>

    <div class="intro-layout">
      <!-- Main Intro Content -->
      <div class="intro-main section-card">
        <div class="section-header">
          <h3>公司简介</h3>
        </div>
        <div class="intro-text">
          <p v-if="company.description">{{ company.description }}</p>
          <p v-else class="no-desc">该公司暂无详细介绍。</p>
        </div>
      </div>

      <!-- Right Sidebar -->
      <div class="intro-sidebar">
        <!-- Promotional Banners (Mock) -->
        <div class="promo-banner resume-template">
          <div class="promo-content">
            <div class="promo-title">打造你的职场名片</div>
            <div class="promo-subtitle">专业简历模板</div>
            <el-button size="small" color="#333" class="promo-btn">查看详情</el-button>
          </div>
        </div>
        
        <div class="promo-banner resume-optimize">
          <div class="promo-content">
            <div class="promo-title">提升你的职场竞争力</div>
            <div class="promo-subtitle">简历优化服务</div>
            <el-button size="small" color="#333" class="promo-btn">查看详情</el-button>
          </div>
        </div>

        <!-- Related Companies (Mock) -->
        <div class="related-companies section-card">
          <div class="section-header">
            <h3>相关公司 · 46</h3>
          </div>
          <div class="related-list">
            <div class="related-item" v-for="i in 3" :key="i">
              <div class="related-logo">
                <el-avatar shape="square" :size="40" :src="company.logo || defaultLogo" />
              </div>
              <div class="related-info">
                <div class="related-name">{{ company.company_name }}分公司{{ i }}</div>
                <div class="related-meta">{{ company.scale }} | {{ company.industry }}</div>
              </div>
            </div>
            <div class="related-footer">
              <span>35 在招职位</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'
import { getJobs } from '@/api/jobs'

const props = defineProps({
  company: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['switch-tab'])
const router = useRouter()
const jobs = ref([])
const loading = ref(false)
const defaultLogo = 'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png'

const fetchHotJobs = async () => {
  loading.value = true
  try {
    // Fetch jobs for this company, ordered by deliveries count descending to show hot jobs
    const res = await getJobs({ 
      company: props.company.id, 
      page_size: 3,
      ordering: '-deliveries_count'
    })
    jobs.value = res.results || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goToJob = (id) => {
  router.push(`/jobs/${id}`)
}

onMounted(() => {
  fetchHotJobs()
})
</script>

<style scoped>
.section-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

/* Hot Jobs */
.hot-jobs-list {
  display: flex;
  gap: 20px;
}

.hot-job-card {
  flex: 1;
  background: #f8fbfd;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #f0f2f5;
}

.hot-job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  border-color: #409EFF;
}

.job-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.job-name {
  font-weight: bold;
  color: #333;
  font-size: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.job-salary {
  color: #409EFF;
  font-weight: bold;
}

.job-tags {
  display: flex;
  gap: 8px;
}

/* Intro Layout */
.intro-layout {
  display: flex;
  gap: 20px;
}

.intro-main {
  flex: 1;
}

.intro-text {
  font-size: 14px;
  color: #666;
  line-height: 1.8;
  white-space: pre-wrap;
}

/* Sidebar */
.intro-sidebar {
  width: 300px;
  flex-shrink: 0;
}

.promo-banner {
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}

.resume-template {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
}

.resume-optimize {
  background: linear-gradient(135deg, #fffbe6 0%, #fff1b8 100%);
}

.promo-title {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.promo-subtitle {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 12px;
}

/* Related Companies */
.related-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.related-logo {
  margin-right: 12px;
}

.related-name {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.related-meta {
  font-size: 12px;
  color: #999;
}

.related-footer {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 10px;
}
</style>