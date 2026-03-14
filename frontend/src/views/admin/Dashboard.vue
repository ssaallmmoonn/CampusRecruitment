<template>
  <div class="admin-dashboard">
    <!-- 1. Platform Scale (Core Metrics) -->
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

    <!-- 2. Activity & Stickiness (Trends) -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover" header="平台活跃度趋势 (近7日)">
          <div class="chart-container">
            <v-chart class="chart" :option="activityOption" autoresize />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" header="协同过滤算法监控">
          <div class="algorithm-monitor">
            <div class="algo-item">
              <div class="algo-label">算法覆盖率</div>
              <el-progress type="circle" :percentage="stats.algorithm?.coverage_rate || 0" color="#409EFF" />
              <div class="algo-desc">成功计算出推荐列表的学生比例</div>
            </div>
            <div class="algo-item">
              <div class="algo-label">推荐转化贡献</div>
              <el-progress type="circle" :percentage="stats.algorithm?.conversion_contribution || 0" color="#67C23A" />
              <div class="algo-desc">推荐位产生的投递占总投递比例</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 3. Ecosystem & Distribution -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover" header="职位类别分布 (Top 10)">
          <div class="chart-container">
            <v-chart class="chart" :option="categoryOption" autoresize />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header-with-action">
              <span>投递热力图 (时段/日期分布)</span>
              <el-select v-model="heatmapMode" size="small" style="width: 140px">
                <el-option label="24小时 × 7天" value="24h" />
                <el-option label="日期 × 月份" value="monthly" />
              </el-select>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="heatmapOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 4. Supply-Demand Analysis -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover" header="最紧缺职位 (投递量/浏览量)">
          <el-table :data="stats.ecosystem?.tight_jobs || []" stripe style="width: 100%">
            <el-table-column prop="name" label="职位类别" />
            <el-table-column prop="ratio" label="投递率" width="120">
              <template #default="scope">
                <span style="color: #F56C6C">{{ scope.row.ratio }}%</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default>
                <el-tag type="danger" size="small">急需优化</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" header="竞争最激烈职位 (投递量/职位数)">
          <el-table :data="stats.ecosystem?.competitive_jobs || []" stripe style="width: 100%">
            <el-table-column prop="name" label="职位类别" />
            <el-table-column prop="ratio" label="平均投递人次" width="150">
              <template #default="scope">
                <span style="font-weight: bold">{{ scope.row.ratio }}</span>
              </template>
            </el-table-column>
            <el-table-column label="竞争程度" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.ratio > 50 ? 'danger' : 'warning'" size="small">
                  {{ scope.row.ratio > 50 ? '极高' : '较高' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getAdminDashboard } from '@/api/adminDashboard'
import { User, OfficeBuilding, Briefcase, Document } from '@element-plus/icons-vue'

// ECharts setup
import { use } from "echarts/core"
import { CanvasRenderer } from "echarts/renderers"
import { LineChart, PieChart, HeatmapChart, BarChart } from "echarts/charts"
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent
} from "echarts/components"
import VChart from "vue-echarts"

use([
  CanvasRenderer, LineChart, PieChart, HeatmapChart, BarChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent, VisualMapComponent
])

const stats = ref({
  overview: {},
  activity: [],
  algorithm: {},
  ecosystem: {}
})

const coreMetrics = [
  { label: '学生总数', key: 'students', icon: User, color: '#409EFF' },
  { label: '企业总数', key: 'companies', icon: OfficeBuilding, color: '#67C23A' },
  { label: '在招职位', key: 'jobs', icon: Briefcase, color: '#E6A23C' },
  { label: '累计投递简历', key: 'applications', icon: Document, color: '#F56C6C' },
]

// Chart Options
const activityOption = computed(() => {
  const data = stats.value.activity || []
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['浏览量', '投递量', '活跃用户(DAU)'] , top: 'top'},
    grid: { left: '3%', right: '4%', bottom: '3%' },
    xAxis: { type: 'category', boundaryGap: false, data: data.map(i => i.date) },
    yAxis: { type: 'value' },
    series: [
      { name: '浏览量', type: 'line', smooth: true, data: data.map(i => i.views) },
      { name: '投递量', type: 'line', smooth: true, data: data.map(i => i.applications) },
      { name: '活跃用户(DAU)', type: 'line', smooth: true, areaStyle: { opacity: 0.1 }, data: data.map(i => i.dau) }
    ]
  }
})

const categoryOption = computed(() => {
  return {
    tooltip: { trigger: 'item' },
    series: [
      {
        name: '职位分布',
        type: 'pie',
        radius: ['40%', '70%'],
        data: stats.value.ecosystem?.category_distribution || [],
        emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
      }
    ]
  }
})

const heatmapMode = ref('24h')

const heatmapOption = computed(() => {
  const is24h = heatmapMode.value === '24h'
  
  // 1. Define Labels
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const hours = Array.from({length: 24}, (_, i) => i + '时')
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  const dates = Array.from({length: 31}, (_, i) => (i + 1) + '日')

  // 2. Select Data
  const data = is24h 
    ? (stats.value.ecosystem?.heatmap_24h || [])
    : (stats.value.ecosystem?.heatmap_monthly || [])
  
  const xAxisData = is24h ? hours : dates
  const yAxisData = is24h ? days : months

  return {
    tooltip: { 
      position: 'top',
      formatter: (p) => {
        const val = p.data[2]
        return is24h 
          ? `${days[p.data[1]]} ${hours[p.data[0]]}: ${val} 次投递`
          : `${months[p.data[1]]} ${dates[p.data[0]]}: ${val} 次投递`
      }
    },
    // Grid adjustment to avoid overlap with visualMap
    grid: { 
      height: '65%', 
      top: '10%',
      bottom: '25%', // Lift the grid bottom to make room for visualMap
      left: '10%',
      right: '5%'
    },
    xAxis: { 
      type: 'category', 
      data: xAxisData, 
      splitArea: { show: true },
      axisLabel: {
        interval: is24h ? 1 : 2, // Sparse labels for monthly view
        fontSize: 10
      }
    },
    yAxis: { 
      type: 'category', 
      data: yAxisData, 
      splitArea: { show: true } 
    },
    visualMap: {
      min: 0,
      max: Math.max(...data.map(i => i[2]), 5),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0', // Fixed at the very bottom
      itemWidth: 15,
      itemHeight: 140, // Length of the bar in horizontal mode
      text: ['高', '低'],
      inRange: {
        color: ['#e0ffff', '#006edd']
      }
    },
    series: [{
      name: '投递频率',
      type: 'heatmap',
      data: data,
      label: { show: false },
      emphasis: { 
        itemStyle: { 
          shadowBlur: 10, 
          shadowColor: 'rgba(0, 0, 0, 0.5)' 
        } 
      }
    }]
  }
})

const fetchStats = async () => {
  try {
    const res = await getAdminDashboard()
    stats.value = res
  } catch (error) {
    console.error('Failed to fetch admin stats:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.metric-container {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
}

.metric-col {
  flex: 1;
}

.metric-card {
  height: 130px;
  display: flex;
  align-items: center;
  border-radius: 12px;
}

.metric-content {
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.metric-icon {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 36px;
  margin-right: 20px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.metric-label {
  font-size: 16px;
  color: #909399;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-container {
  height: 350px;
}

.chart {
  width: 100%;
  height: 100%;
}

.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.algorithm-monitor {
  display: flex;
  flex-direction: column;
  height: 350px;
  justify-content: space-around;
  align-items: center;
}

.algo-item {
  text-align: center;
}

.algo-label {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #606266;
}

.algo-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

:deep(.el-card__header) {
  font-weight: bold;
}
</style>
