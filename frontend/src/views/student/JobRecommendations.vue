<template>
  <div class="recommendations-page">
    <!-- Left Sidebar: Recommendation Strategies (Sibling of page-container now) -->
    <div class="sidebar">
      <div 
        v-for="item in strategies" 
        :key="item.value"
        class="strategy-item"
        :class="{ active: currentStrategy === item.value }"
        @click="changeStrategy(item.value)"
      >
        {{ item.label }}
      </div>
    </div>

    <div class="page-container">
      <!-- Right Content Area -->
      <div class="main-content">
        <!-- Top Info Bar -->
        <div class="info-bar">
          <div class="info-left">
            <el-icon class="algo-icon"><MagicStick /></el-icon>
            <span class="algo-text">{{ currentStrategyLabel }}推荐给您的职位</span>
          </div>
          <div class="info-right">
            <el-space :size="10">
              <div class="custom-location-selector" @click="locationDialogVisible = true">
                <span class="location-text" :class="{ 'has-value': filters.location }">
                  {{ filters.location || '工作城市' }}
                </span>
                <el-icon v-if="filters.location" class="clear-icon" @click.stop="clearLocation"><Close /></el-icon>
                <el-icon v-else class="arrow-icon"><ArrowDown /></el-icon>
              </div>
              <el-select
                v-model="filters.degree_requirement"
                placeholder="学历要求"
                clearable
                @change="handleFilterChange"
                class="filter-select"
              >
                <el-option v-for="item in degreeOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-select
                v-model="filters.job_type"
                placeholder="工作性质"
                clearable
                @change="handleFilterChange"
                class="filter-select"
              >
                <el-option label="全职" value="全职" />
                <el-option label="实习" value="实习" />
              </el-select>
              <el-select
                v-model="filters.company_nature"
                placeholder="企业性质"
                clearable
                @change="handleFilterChange"
                class="filter-select"
              >
                <el-option v-for="item in natureOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-space>
          </div>
        </div>

        <!-- Job List -->
        <div v-loading="loading" class="job-list">
          <template v-if="recommendations.length > 0">
            <el-card 
              v-for="item in recommendations" 
              :key="item.job.id" 
              shadow="hover" 
              class="job-card"
            >
              <div class="job-content" @click="goToDetail(item.job.id)">
                <div class="job-header">
                  <div class="title-row">
                    <h3 class="job-title">{{ item.job.job_name }}</h3>
                    <el-tag size="small" effect="plain" class="location-tag">{{ item.job.location }}</el-tag>
                    
                    <!-- Recommend Reason moved here -->
                    <div class="recommend-reason-inline" v-if="item.reason && item.reason.length > 0">
                      <el-icon><MagicStick /></el-icon>
                      <span v-for="(reason, index) in item.reason" :key="index">
                        {{ reason.text }}{{ index < item.reason.length - 1 ? ' · ' : '' }}
                      </span>
                    </div>
                  </div>
                  <span class="salary">{{ item.job.salary }}</span>
                </div>

                <div class="job-tags-row">
                  <span class="tag-item">{{ item.job.job_type }}</span>
                  <span class="tag-item">{{ item.job.degree_requirement }}</span>
                  <span class="tag-item">{{ item.job.experience_requirement }}</span>
                </div>
                
                <div class="job-desc-row">
                  <div class="job-desc-preview">
                    {{ item.job.description ? item.job.description.substring(0, 100) + '...' : '无描述' }}
                  </div>
                  <span class="time">{{ formatDate(item.job.create_time) }}发布</span>
                </div>
              </div>
              
              <div class="job-footer">
                <div class="company-info" @click.stop="goToCompanyDetail(item.job.company?.id)">
                  <el-avatar :size="40" :src="item.job.company?.logo || defaultLogo" shape="square" class="company-logo" />
                  <div class="company-details">
                    <div class="company-name-row">
                      <span class="company-name">{{ item.job.company?.company_name || '未知企业' }}</span>
                    </div>
                    <div class="company-tags">
                      <span>{{ item.job.company?.industry || '行业未知' }}</span>
                      <el-divider direction="vertical" />
                      <span>{{ item.job.company?.scale || '规模未知' }}</span>
                      <el-divider direction="vertical" />
                      <span>{{ item.job.company?.nature || '性质未知' }}</span>
                    </div>
                  </div>
                </div>

                <div class="job-actions">
                  <el-button 
                    :type="item.applied ? 'info' : 'primary'" 
                    class="apply-btn" 
                    @click.stop="handleApply(item)"
                  >
                    {{ item.applied ? '已投递' : '立即投递' }}
                  </el-button>
                  <el-button @click.stop="goToDetail(item.job.id)">查看详情</el-button>
                </div>
              </div>
            </el-card>
          </template>
          <el-empty v-else description="暂无推荐，多去投递和收藏职位吧！" />
        </div>
      </div>
    </div>

    <!-- Application Dialog -->
    <el-dialog v-model="applyDialogVisible" title="投递简历" width="500px">
      <el-form :model="applyForm" label-width="100px">
        <el-form-item label="选择简历">
          <el-select v-model="applyForm.resume" placeholder="请选择一份简历">
            <el-option
              v-for="item in resumes"
              :key="item.id"
              :label="item.resume_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <div v-if="resumes.length === 0" class="no-resume-tip">
        您还没有任何简历，请先创建一份 <router-link to="/student/resumes">创建简历</router-link>.
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="applyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitApply" :disabled="!applyForm.resume">确认投递</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Location Selection Dialog -->
    <el-dialog v-model="locationDialogVisible" title="选择工作城市" width="700px" custom-class="location-dialog">
      <div class="location-container">
        <div class="province-list">
          <div 
            v-for="province in provinceOptions" 
            :key="province.name"
            class="province-item"
            :class="{ active: selectedProvince === province.name }"
            @mouseenter="selectedProvince = province.name"
          >
            {{ province.name }}
          </div>
        </div>
        <div class="city-list" v-if="currentCityList">
          <div 
            v-for="city in currentCityList" 
            :key="city.name"
            class="city-item"
            :class="{ active: filters.location === city.name }"
            @click="selectCity(city.name)"
          >
            {{ city.name }}
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { getRecommendations } from '@/api/recommendation';
import { MagicStick, ArrowDown, Close } from '@element-plus/icons-vue';
import provinceData from '@/assets/provinces.json';
import { applyJob, cancelApplication, getResumes } from '@/api/recruitment';
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();
const loading = ref(false);
const recommendations = ref([]);
const currentStrategy = ref('hybrid');
const defaultLogo = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';
const resumes = ref([]);

// Pagination
const limit = 20;
const offset = ref(0);
const hasMore = ref(true);
const initialLoading = ref(true);

// Filter states
const filters = reactive({
  location: '',
  degree_requirement: '',
  job_type: '',
  company_nature: ''
});

// Location Dialog State
const locationDialogVisible = ref(false);
const selectedProvince = ref('');

// Options
const provinceOptions = (provinceData['地区分类'] || []).map(p => ({
  name: p['一级分类'],
  cities: (p['二级分类'] || []).map(c => ({ name: c }))
}));

// Set initial province for dialog
if (provinceOptions.length > 0) {
  selectedProvince.value = provinceOptions[0].name;
}

const degreeOptions = ['初中及以下', '高中', '中专/中技', '大专', '本科', '硕士', '博士'];
const natureOptions = ['国企', '民营', '外商独资', '合资', '股份制企业', '事业单位', '其他'];

const strategies = [
  { label: '综合推荐', value: 'hybrid' },
  { label: '猜你喜欢/相似职位', value: 'item' },
  { label: '相似同学都在投的职位', value: 'user' },
];

const currentStrategyLabel = computed(() => {
  if (currentStrategy.value === 'item') return '根据协同过滤算法';
  if (currentStrategy.value === 'user') return '根据您的同学行为';
  return '根据综合推荐算法';
});

const currentCityList = computed(() => {
  const province = provinceOptions.find(p => p.name === selectedProvince.value);
  return province ? province.cities : [];
});

const selectCity = (cityName) => {
  filters.location = cityName;
  locationDialogVisible.value = false;
  handleFilterChange();
};

const clearLocation = () => {
  filters.location = '';
  handleFilterChange();
};

const fetchRecommendations = async (loadMore = false) => {
  if (loadMore && !hasMore.value) return;
  
  loading.value = true;
  try {
    const params = {
      strategy: currentStrategy.value,
      degree_requirement: filters.degree_requirement || undefined,
      job_type: filters.job_type || undefined,
      company_nature: filters.company_nature || undefined,
      limit: limit,
      offset: offset.value
    };
    
    // City handling
    if (filters.location) {
      params.location = filters.location;
    }
    
    const res = await getRecommendations(params);
    let data = [];
    
    // Handle pagination response structure
    if (res.results && Array.isArray(res.results)) {
      data = res.results;
      // Check if there are more items
      if (res.next === null || data.length < limit) {
        hasMore.value = false;
      }
    } else if (Array.isArray(res)) {
      data = res;
      hasMore.value = false; // Assume no pagination if direct array
    }
    
    // Initialize items with applied status
    const newItems = data.map(item => ({
      ...item,
      applied: false,
      application_id: null
    }));
    
    if (loadMore) {
      recommendations.value = [...recommendations.value, ...newItems];
    } else {
      recommendations.value = newItems;
    }
    
    // Increment offset for next page
    if (data.length > 0) {
      offset.value += limit;
    }
    
    // Check application status for new items only to be efficient? 
    // For simplicity, we can check all or just new ones. 
    // Checking all is safer but slower. Let's check new ones.
    await checkApplicationsStatus(newItems);
  } catch (error) {
    console.error('Failed to fetch recommendations:', error);
    hasMore.value = false;
  } finally {
    loading.value = false;
    initialLoading.value = false;
  }
};

const checkApplicationsStatus = async (itemsToCheck) => {
  try {
    const { checkApplicationStatus } = await import('@/api/recruitment');
    
    // We update the reactive objects in recommendations.value directly
    // itemsToCheck are references to objects inside recommendations.value
    const promises = itemsToCheck.map(async (item) => {
      try {
        const statusRes = await checkApplicationStatus(item.job.id);
        item.applied = statusRes.applied;
        item.application_id = statusRes.application_id;
      } catch (err) {
        console.error(`Failed to check status for job ${item.job.id}:`, err);
      }
    });
    await Promise.all(promises);
  } catch (error) {
    console.error('Failed to check application status:', error);
  }
};

const handleScroll = () => {
  const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
  const clientHeight = document.documentElement.clientHeight;
  const scrollHeight = document.documentElement.scrollHeight;
  
  // Load more when near bottom (100px threshold)
  if (scrollTop + clientHeight >= scrollHeight - 100 && !loading.value && hasMore.value) {
    fetchRecommendations(true);
  }
};

const handleFilterChange = () => {
  // Reset pagination
  offset.value = 0;
  hasMore.value = true;
  recommendations.value = [];
  fetchRecommendations(false);
};

const fetchResumes = async () => {
  try {
    const res = await getResumes();
    // Support both direct list and paginated results
    resumes.value = Array.isArray(res) ? res : (res.results || []);
  } catch (error) {
    console.error('Failed to fetch resumes:', error);
  }
};

// Application related
const applyDialogVisible = ref(false)
const applyForm = reactive({
  resume: '',
  jobId: null,
  recommendationItem: null
})

const handleApply = async (item) => {
  if (item.applied) {
    // Cancel application
    try {
      await ElMessageBox.confirm('确定要取消投递该职位吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      });
      await cancelApplication(item.application_id);
      ElMessage.success('已取消投递');
      item.applied = false;
      item.application_id = null;
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('取消投递失败');
      }
    }
  } else {
    // Show dialog to select resume (consistent with JobBoard.vue)
    if (resumes.value.length === 0) {
      ElMessage.warning('请先创建简历后再进行投递');
      router.push('/student/resumes');
      return;
    }
    
    applyForm.jobId = item.job.id;
    applyForm.recommendationItem = item;
    applyForm.resume = resumes.value[0]?.id || ''; // Default to first resume
    applyDialogVisible.value = true;
  }
};

const submitApply = async () => {
  try {
    const res = await applyJob({
      job: applyForm.jobId,
      resume: applyForm.resume
    });
    ElMessage.success('投递成功');
    
    // Update the item state in recommendations list
    if (applyForm.recommendationItem) {
      applyForm.recommendationItem.applied = true;
      applyForm.recommendationItem.application_id = res.id;
    }
    
    applyDialogVisible.value = false;
  } catch (error) {
    console.error('Apply error:', error);
    let errorMsg = '投递失败';
    if (error.response && error.response.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data;
      } else if (error.response.data.detail) {
        errorMsg = error.response.data.detail;
      } else {
        const firstError = Object.values(error.response.data)[0];
        if (Array.isArray(firstError)) {
          errorMsg = firstError[0];
        }
      }
    }
    ElMessage.error(errorMsg);
  }
};

const changeStrategy = (val) => {
  currentStrategy.value = val;
  handleFilterChange();
};

const goToDetail = (id) => {
  if (id) {
    router.push(`/jobs/${id}`);
  }
};

const goToCompanyDetail = (companyId) => {
  if (companyId) {
    router.push(`/company/${companyId}`);
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString();
};

onMounted(() => {
  fetchRecommendations(false);
  fetchResumes();
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.recommendations-page {
  background-color: #f0f2f5;
  min-height: 100vh;
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.page-container {
  width: 940px;
  margin-left: 300px; /* Offset for fixed sidebar (240px + 20px gap) */
  max-width: 100%;
}

/* Sidebar Styling - Fixed to viewport */
.sidebar {
  width: 240px;
  background-color: #fff;
  border-radius: 8px;
  padding: 10px;
  height: fit-content;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  position: fixed;
  top: 80px; /* 60px header + 20px gap */
  left: calc(50% - 600px); /* Center based on 1200px total layout width */
  z-index: 100;
}

@media (max-width: 1240px) {
  .sidebar {
    left: 20px;
  }
  .page-container {
    margin-left: 300px;
    width: calc(100% - 280px);
  }
}

.strategy-item {
  padding: 15px 20px;
  margin-bottom: 5px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  color: #606266;
  transition: all 0.3s;
  text-align: center;
}

.strategy-item:hover {
  background-color: #f5f7fa;
  color: #409eff;
}

.strategy-item.active {
  background-color: #409eff;
  color: #fff;
  font-weight: 700;
}

/* Main Content Styling */
.main-content {
  flex: 1;
}

.info-bar {
  background-color: #fff;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.info-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.algo-icon {
  color: #f56c6c;
  font-size: 18px;
}

.algo-text {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.filter-select {
  width: 140px;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  background-color: #f5f7fa !important;
  box-shadow: none !important;
  border: none !important;
  border-radius: 20px; /* Match MyCollections.vue */
  height: 32px;
  padding: 0 15px !important;
}

/* Ensure placeholder and text are consistent */
:deep(.el-input__inner),
:deep(.el-select__placeholder) {
  font-size: 13px;
  color: #606266;
}

.no-resume-tip {
  margin-top: 15px;
  padding: 10px;
  background-color: #fff7e6;
  border: 1px solid #ffe58f;
  border-radius: 4px;
  color: #d46b08;
  font-size: 13px;
}

.no-resume-tip a {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

/* Custom Location Selector */
.custom-location-selector {
  width: 140px;
  height: 32px;
  background-color: #f5f7fa;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
  cursor: pointer;
  box-sizing: border-box;
  transition: all 0.3s;
}

.custom-location-selector:hover {
  background-color: #e6e8eb;
}

.location-text {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.location-text.has-value {
  color: #606266;
}

.arrow-icon {
  color: #c0c4cc;
  font-size: 12px;
}

.clear-icon {
  color: #c0c4cc;
  font-size: 14px;
  cursor: pointer;
}

.clear-icon:hover {
  color: #909399;
}

/* Location Dialog Styles */
.location-container {
  display: flex;
  height: 400px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.province-list {
  width: 200px;
  border-right: 1px solid #ebeef5;
  overflow-y: auto;
  background-color: #fafafa;
}

.province-item {
  padding: 12px 20px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: background-color 0.3s;
}

.province-item:hover {
  background-color: #f0f2f5;
}

.province-item.active {
  background-color: #fff;
  color: #409eff;
  font-weight: 500;
  border-left: 3px solid #409eff;
}

.city-list {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-content: flex-start;
  overflow-y: auto;
}

.city-item {
  padding: 8px 16px;
  background-color: #f4f4f5;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  transition: all 0.3s;
}

.city-item:hover {
  color: #409eff;
  background-color: #ecf5ff;
}

.city-item.active {
  background-color: #409eff;
  color: #fff;
}

/* Job Card Styling */
.job-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.job-card {
  transition: all 0.3s;
  cursor: pointer;
  border-radius: 25px;
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.job-content {
  margin-bottom: 15px;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.location-tag {
  border: none;
  background: transparent;
  padding: 0;
  font-size: 14px;
  color: #3e81e6;
}

.location-tag::before {
  content: '[';
  margin-right: 2px;
}

.location-tag::after {
  content: ']';
  margin-left: 2px;
}

.job-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.salary {
  font-size: 16px;
  color: #f56c6c;
  font-weight: bold;
}

.job-tags-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.tag-item {
  background-color: #f4f4f5;
  color: #909399;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.job-desc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #909399;
  font-size: 14px;
  margin-bottom: 12px;
}

.job-desc-preview {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
  flex: 1;
  margin-right: 20px;
}

.time {
  white-space: nowrap;
  font-size: 12px;
}

.recommend-reason-inline {
  padding: 2px 8px;
  background-color: #f0f7ff;
  border-radius: 4px;
  font-size: 12px;
  color: #409eff;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 10px;
}

.recommend-reason-inline .el-icon {
  font-size: 14px;
}

.job-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}

.company-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.company-info:hover .company-name {
  color: #60b3ff;
}

.company-logo {
  margin-right: 12px;
  background-color: #f5f7fa;
}

.company-details {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.company-name-row {
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.company-name {
  color: #303133;
  font-weight: 500;
  font-size: 14px;
  transition: color 0.3s;
}

.company-tags {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.company-tags .el-divider--vertical {
  margin: 0 8px;
  height: 10px;
}

.job-actions {
  display: flex;
}

.apply-btn {
  margin-right: 12px;
  padding: 8px 20px;
}
</style>
