<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title flex items-center">
        <HeartIcon class="w-5 h-5 mr-2" :class="healthIconColor" />
        系统健康状态
      </h3>
      <div class="text-xs text-gray-500">
        {{ lastUpdateDisplay }}
      </div>
    </div>
    
    <div class="space-y-4">
      <!-- 健康评分 -->
      <div class="text-center">
        <div class="flex items-center justify-center mb-2">
          <span class="text-3xl mr-2">{{ healthData?.status_emoji || '❓' }}</span>
          <div>
            <div class="text-2xl font-bold" :class="healthScoreColor">
              {{ healthScore }}
            </div>
            <div class="text-sm text-gray-600">健康评分</div>
          </div>
        </div>
        
        <!-- 健康状态条 -->
        <div class="w-full bg-gray-200 rounded-full h-3 mt-3">
          <div 
            class="h-3 rounded-full transition-all duration-1000"
            :class="healthBarColor"
            :style="{ width: `${healthScore}%` }"
          ></div>
        </div>
        
        <div class="text-sm mt-2" :class="healthStatusColor">
          {{ healthData?.status || '未知' }}
        </div>
      </div>
      
      <!-- 系统指标概览 -->
      <div class="grid grid-cols-2 gap-3">
        <div class="metric-mini">
          <div class="text-xs text-gray-600 mb-1">CPU使用率</div>
          <div class="flex items-center">
            <div class="text-lg font-semibold mr-2" :class="cpuColor">
              {{ cpuUsage }}%
            </div>
            <div class="w-8 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                class="h-full transition-all duration-500"
                :class="cpuBarColor"
                :style="{ width: `${Math.min(cpuUsage, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
        
        <div class="metric-mini">
          <div class="text-xs text-gray-600 mb-1">内存使用率</div>
          <div class="flex items-center">
            <div class="text-lg font-semibold mr-2" :class="memoryColor">
              {{ memoryUsage }}%
            </div>
            <div class="w-8 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                class="h-full transition-all duration-500"
                :class="memoryBarColor"
                :style="{ width: `${Math.min(memoryUsage, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
        
        <div class="metric-mini">
          <div class="text-xs text-gray-600 mb-1">缓存命中率</div>
          <div class="flex items-center">
            <div class="text-lg font-semibold mr-2" :class="cacheColor">
              {{ cacheHitRate }}%
            </div>
            <CheckCircleIcon v-if="cacheHitRate >= 80" class="w-4 h-4 text-green-500" />
            <ExclamationTriangleIcon v-else class="w-4 h-4 text-yellow-500" />
          </div>
        </div>
        
        <div class="metric-mini">
          <div class="text-xs text-gray-600 mb-1">错误率</div>
          <div class="flex items-center">
            <div class="text-lg font-semibold mr-2" :class="errorRateColor">
              {{ errorRateDisplay }}%
            </div>
            <XCircleIcon v-if="errorRate > 0.05" class="w-4 h-4 text-red-500" />
            <CheckCircleIcon v-else class="w-4 h-4 text-green-500" />
          </div>
        </div>
      </div>
      
      <!-- 问题列表 -->
      <div v-if="healthData?.issues && healthData.issues.length > 0" class="mt-4">
        <div class="text-sm font-medium text-gray-700 mb-2">⚠️ 需要关注的问题:</div>
        <div class="space-y-1">
          <div 
            v-for="(issue, index) in healthData.issues.slice(0, 3)" 
            :key="index"
            class="text-xs text-red-600 bg-red-50 px-2 py-1 rounded"
          >
            {{ issue }}
          </div>
        </div>
      </div>
      
      <!-- 告警摘要 -->
      <div v-if="alertsData" class="border-t pt-3">
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">活跃告警</span>
          <div class="flex space-x-2">
            <span 
              v-if="alertsData.critical_alerts > 0" 
              class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-100 text-red-800"
            >
              🔴 {{ alertsData.critical_alerts }}
            </span>
            <span 
              v-if="alertsData.warning_alerts > 0" 
              class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800"
            >
              ⚠️ {{ alertsData.warning_alerts }}
            </span>
            <span 
              v-if="alertsData.critical_alerts === 0 && alertsData.warning_alerts === 0"
              class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800"
            >
              ✅ 无告警
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 刷新按钮 -->
    <div class="mt-4 pt-4 border-t border-gray-200">
      <button 
        @click="refreshHealth"
        :disabled="isRefreshing"
        class="w-full text-sm text-primary-600 hover:text-primary-700 disabled:opacity-50 py-2 px-4 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors"
      >
        {{ isRefreshing ? '刷新中...' : '🔄 刷新健康状态' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { useAppStore } from '@/stores/app'
import { formatRelativeTime } from '@/utils/formatters'
import { apiService } from '@/services/api'
import {
  HeartIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'

const monitoringStore = useMonitoringStore()
const appStore = useAppStore()

const isRefreshing = ref(false)
const healthData = ref<any>(null)
const metricsData = ref<any>(null)
const alertsData = ref<any>(null)
const lastUpdateTime = ref<Date | null>(null)
const refreshInterval = ref<NodeJS.Timeout | null>(null)

// 计算属性
const healthScore = computed(() => {
  return healthData.value?.health_score || 0
})

const cpuUsage = computed(() => {
  return Math.round(metricsData.value?.cpu_usage || 0)
})

const memoryUsage = computed(() => {
  return Math.round(metricsData.value?.memory_usage_percent || 0)
})

const cacheHitRate = computed(() => {
  return Math.round((metricsData.value?.cache_hit_rate || 0) * 100)
})

const errorRate = computed(() => {
  return metricsData.value?.error_rate || 0
})

const errorRateDisplay = computed(() => {
  return (errorRate.value * 100).toFixed(2)
})

const lastUpdateDisplay = computed(() => {
  if (!lastUpdateTime.value) return '从未更新'
  return formatRelativeTime(lastUpdateTime.value)
})

// 样式计算
const healthIconColor = computed(() => {
  if (healthScore.value >= 90) return 'text-green-500'
  if (healthScore.value >= 70) return 'text-yellow-500'
  return 'text-red-500'
})

const healthScoreColor = computed(() => {
  if (healthScore.value >= 90) return 'text-green-600'
  if (healthScore.value >= 70) return 'text-yellow-600'
  return 'text-red-600'
})

const healthBarColor = computed(() => {
  if (healthScore.value >= 90) return 'bg-gradient-to-r from-green-400 to-green-500'
  if (healthScore.value >= 70) return 'bg-gradient-to-r from-yellow-400 to-yellow-500'
  return 'bg-gradient-to-r from-red-400 to-red-500'
})

const healthStatusColor = computed(() => {
  if (healthScore.value >= 90) return 'text-green-700'
  if (healthScore.value >= 70) return 'text-yellow-700'
  return 'text-red-700'
})

const cpuColor = computed(() => {
  if (cpuUsage.value >= 90) return 'text-red-600'
  if (cpuUsage.value >= 80) return 'text-yellow-600'
  return 'text-green-600'
})

const cpuBarColor = computed(() => {
  if (cpuUsage.value >= 90) return 'bg-red-400'
  if (cpuUsage.value >= 80) return 'bg-yellow-400'
  return 'bg-green-400'
})

const memoryColor = computed(() => {
  if (memoryUsage.value >= 95) return 'text-red-600'
  if (memoryUsage.value >= 85) return 'text-yellow-600'
  return 'text-green-600'
})

const memoryBarColor = computed(() => {
  if (memoryUsage.value >= 95) return 'bg-red-400'
  if (memoryUsage.value >= 85) return 'bg-yellow-400'
  return 'bg-green-400'
})

const cacheColor = computed(() => {
  if (cacheHitRate.value >= 80) return 'text-green-600'
  if (cacheHitRate.value >= 60) return 'text-yellow-600'
  return 'text-red-600'
})

const errorRateColor = computed(() => {
  if (errorRate.value > 0.05) return 'text-red-600'
  if (errorRate.value > 0.01) return 'text-yellow-600'
  return 'text-green-600'
})

// 方法
const refreshHealth = async () => {
  if (isRefreshing.value) return
  
  try {
    isRefreshing.value = true
    
    // 并行获取健康状态、指标和告警数据
    const [healthResponse, metricsResponse, alertsResponse] = await Promise.allSettled([
      apiService.getEnhancedSystemHealth(),
      apiService.getCurrentMetrics(),
      apiService.getActiveAlerts()
    ])
    
    // 处理健康状态数据
    if (healthResponse.status === 'fulfilled' && healthResponse.value.success) {
      healthData.value = healthResponse.value.data
    }
    
    // 处理指标数据
    if (metricsResponse.status === 'fulfilled' && metricsResponse.value.success) {
      metricsData.value = metricsResponse.value.data
    }
    
    // 处理告警数据
    if (alertsResponse.status === 'fulfilled' && alertsResponse.value.success) {
      const alertStats = alertsResponse.value.data.statistics
      alertsData.value = {
        critical_alerts: alertStats?.severity_distribution?.critical || 0,
        warning_alerts: alertStats?.severity_distribution?.warning || 0,
        total_alerts: alertStats?.active_alerts || 0
      }
    }
    
    lastUpdateTime.value = new Date()
    
    // 显示成功通知
    appStore.addNotification({
      type: 'success',
      title: '健康状态已更新',
      message: `系统健康评分: ${healthScore.value}`,
      duration: 2000
    })
    
  } catch (error) {
    console.error('刷新健康状态失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '刷新失败',
      message: '无法获取系统健康状态',
      duration: 3000
    })
  } finally {
    isRefreshing.value = false
  }
}

const startAutoRefresh = () => {
  refreshInterval.value = setInterval(refreshHealth, 30000) // 每30秒刷新
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// 生命周期
onMounted(() => {
  refreshHealth()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.metric-mini {
  @apply bg-gray-50 p-3 rounded-lg;
}

.metric-mini:hover {
  @apply bg-gray-100 transform scale-105 transition-all duration-200;
}

/* 健康状态动画 */
.health-pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

/* 进度条动画 */
.progress-bar {
  transition: width 0.8s ease-in-out;
}

/* 悬停效果 */
.card:hover {
  @apply shadow-lg transform -translate-y-1 transition-all duration-300;
}
</style>