<template>
  <div class="company-dashboard">
    <!-- 1. Core Metrics (Top) -->
    <div class="metric-container">
      <div v-for="(item, index) in coreMetrics" :key="index" class="metric-col">
        <el-card shadow="hover" class="metric-card">
          <div class="metric-content">
            <div class="metric-icon" :style="{ backgroundColor: item.color }">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">{{ item.label }}</div>
              <div class="metric-value">{{ stats.overview?.[item.key] || 0 }}</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 2. Job Analysis & CF Algorithm -->
    <el-row :gutter="20" class="chart-row">
      <!-- Funnel Chart for Job Performance -->
      <el-col :span="12">
        <el-card shadow="hover" header="招聘漏斗分析 (全岗位平均)">
          <div class="chart-container">
            <v-chart class="chart" :option="funnelOption" autoresize />
          </div>
        </el-card>
      </el-col>
      
      <!-- CF Algorithm Feedback -->
      <el-col :span="12">
        <el-card shadow="hover" header="推荐算法效果反馈">
          <div class="algorithm-stats">
            <div class="rate-item">
              <div class="rate-label">推荐投递占比</div>
              <el-progress type="dashboard" :percentage="stats.algorithm?.recommendation_rate || 0" color="#67C23A" />
              <div class="rate-desc">通过“智能推荐”入口产生的投递比例</div>
            </div>
            <div class="dist-chart">
              <v-chart class="chart" :option="matchOption" autoresize />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 3. Job Rankings & Student Profiling -->
    <el-row :gutter="20" class="chart-row">
      <!-- Top Jobs -->
      <el-col :span="12">
        <el-card shadow="hover" header="热门职位排行 (Top 10)">
          <el-table :data="stats.performance?.funnel || []" stripe style="width: 100%" max-height="350">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="name" label="职位名称" show-overflow-tooltip />
            <el-table-column prop="deliveries" label="投递量" width="100" sortable />
            <el-table-column prop="interest_rate" label="兴趣率" width="100">
              <template #default="scope">
                <span style="color: #E6A23C">{{ scope.row.interest_rate }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="apply_rate" label="投递率" width="100">
              <template #default="scope">{{ scope.row.apply_rate }}%</template>
            </el-table-column>
          </el-table>
          <div v-if="stats.performance?.cold_jobs?.length > 0" class="warning-section">
            <div class="warning-title"><el-icon><Warning /></el-icon> 冷门职位预警 (浏览多但投递少)</div>
            <div class="warning-tags">
              <el-tag v-for="job in stats.performance.cold_jobs" :key="job.name" type="danger" effect="plain">
                {{ job.name }} ({{ job.rate }}%)
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Student Profiling -->
      <el-col :span="12">
        <el-card shadow="hover" header="人才画像分析 (投递学生)">
          <el-tabs v-model="activeProfileTab">
            <el-tab-pane label="专业分布" name="major">
              <div class="chart-container-small">
                <v-chart class="chart" :option="majorOption" autoresize />
              </div>
            </el-tab-pane>
            <el-tab-pane label="学历分布" name="education">
              <div class="chart-container-small">
                <v-chart class="chart" :option="eduOption" autoresize />
              </div>
            </el-tab-pane>
            <el-tab-pane label="技能词云" name="skills">
              <div class="skill-cloud">
                <el-tag 
                  v-for="skill in stats.profiling?.skill_cloud || []" 
                  :key="skill.name"
                  :size="getTagSize(skill.value)"
                  :type="getTagType(skill.value)"
                  class="skill-tag"
                >
                  {{ skill.name }}
                </el-tag>
                <el-empty v-if="!stats.profiling?.skill_cloud?.length" description="暂无技能数据" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, provide } from 'vue'
import { getCompanyDashboard } from '@/api/company'
import { 
  Briefcase, Document, Timer, Edit, View, Warning, Star, DataAnalysis
} from '@element-plus/icons-vue'

// ECharts setup
import { use } from "echarts/core"
import { CanvasRenderer } from "echarts/renderers"
import { PieChart, BarChart, FunnelChart } from "echarts/charts"
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from "echarts/components"
import VChart, { THEME_KEY } from "vue-echarts"

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  FunnelChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const stats = ref({
  overview: {},
  performance: {},
  algorithm: {},
  profiling: {}
})

const activeProfileTab = ref('major')

const coreMetrics = [
  { label: '在招职位', key: 'total_jobs', icon: Briefcase, color: '#409EFF' },
  { label: '共收到简历', key: 'total_applications', icon: Document, color: '#67C23A' },
  { label: '待处理简历', key: 'pending_applications', icon: Timer, color: '#E6A23C' },
  { label: '今日新增投递', key: 'today_applications', icon: Edit, color: '#F56C6C' },
  { label: '今日新增浏览', key: 'today_views', icon: View, color: '#909399' },
]

// Chart Options
const funnelOption = computed(() => {
  const overall = stats.value.performance?.overall_funnel
  if (!overall) return {}
  
  const avgViews = overall.avg_views || 0
  const avgCollections = overall.avg_collections || 0
  const avgDeliveries = overall.avg_deliveries || 0

  return {
    tooltip: { trigger: 'item', formatter: '{b} : {c}' },
    legend: { data: ['浏览量', '收藏量', '投递量'], bottom: 0 },
    series: [
      {
        name: '招聘漏斗',
        type: 'funnel',
        left: '10%',
        top: 20,
        bottom: 60,
        width: '80%',
        min: 0,
        max: Math.max(avgViews, 1), // Avoid max 0
        minSize: '0%',
        maxSize: '100%',
        sort: 'descending',
        gap: 2,
        label: { show: true, position: 'inside' },
        labelLine: { show: false },
        itemStyle: { borderColor: '#fff', borderWidth: 1 },
        data: [
          { value: avgViews, name: '浏览量' },
          { value: avgCollections, name: '收藏量' },
          { value: avgDeliveries, name: '投递量' }
        ]
      }
    ]
  }
})

const matchOption = computed(() => {
  return {
    title: { text: '申请人匹配度分布', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'item' },
    legend: { bottom: '0', left: 'center' },
    series: [
      {
        name: '匹配度',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: { label: { show: true, fontSize: '16', fontWeight: 'bold' } },
        labelLine: { show: false },
        data: stats.value.algorithm?.match_distribution || []
      }
    ]
  }
})

const majorOption = computed(() => {
  return {
    tooltip: { trigger: 'item' },
    series: [
      {
        name: '专业分布',
        type: 'pie',
        radius: '70%',
        data: stats.value.profiling?.major_distribution || [],
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
        }
      }
    ]
  }
})

const eduOption = computed(() => {
  const data = stats.value.profiling?.education_distribution || []
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', boundaryGap: [0, 0.01] },
    yAxis: { type: 'category', data: data.map(i => i.name) },
    series: [
      {
        name: '人数',
        type: 'bar',
        data: data.map(i => i.value),
        itemStyle: { color: '#409EFF' }
      }
    ]
  }
})

const getTagSize = (val) => {
  if (val > 10) return 'large'
  if (val > 5) return 'default'
  return 'small'
}

const getTagType = (val) => {
  const types = ['', 'success', 'info', 'warning', 'danger']
  return types[val % 5]
}

const fetchStats = async () => {
  try {
    const res = await getCompanyDashboard()
    stats.value = res
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.company-dashboard {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.metric-container {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
  width: 100%;
}

.metric-col {
  flex: 1; /* Equal 5-column split across the row */
  min-width: 0;
}

.metric-card {
  height: 130px; /* Increased height further */
  display: flex;
  align-items: center;
  transition: all 0.3s;
  border-radius: 12px;
}

.metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.metric-content {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0 0; /* Increased horizontal padding */
}

.metric-icon {
  width: 72px; /* Larger icon container */
  height: 72px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 36px; /* Larger icon */
  margin-right: 20px;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.metric-info {
  flex: 1;
}

.metric-label {
  font-size: 16px; /* Larger label */
  color: #909399;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 32px; /* Larger value */
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-container {
  height: 350px;
}

.chart-container-small {
  height: 385px;
}

.chart {
  width: 100%;
  height: 100%;
}

.algorithm-stats {
  display: flex;
  height: 350px;
  align-items: center;
}

.rate-item {
  flex: 1;
  text-align: center;
  padding: 20px;
  border-right: 1px solid #ebeef5;
}

.rate-label {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 20px;
}

.rate-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 15px;
}

.dist-chart {
  flex: 1.5;
  height: 100%;
}

.warning-section {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px dashed #ebeef5;
}

.warning-title {
  font-size: 14px;
  color: #F56C6C;
  font-weight: bold;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.warning-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-cloud {
  height: 365px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-content: flex-start;
  overflow-y: auto;
  padding: 10px;
}

.skill-tag {
  margin-bottom: 5px;
}

:deep(.el-card__header) {
  font-weight: bold;
  color: #303133;
}
</style>
