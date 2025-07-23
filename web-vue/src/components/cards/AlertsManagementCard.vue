<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title flex items-center">
        <BellIcon class="w-5 h-5 mr-2" :class="alertIconColor" />
        系统告警
        <span v-if="totalAlerts > 0" class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-100 text-red-800">
          {{ totalAlerts }}
        </span>
      </h3>
      <div class="text-xs text-gray-500">
        {{ lastUpdateDisplay }}
      </div>
    </div>
    
    <div class="space-y-4">
      <!-- 告警统计概览 -->
      <div class="grid grid-cols-3 gap-3">
        <div class="alert-stat">
          <div class="text-center">
            <div class="text-2xl font-bold text-red-600">{{ criticalCount }}</div>
            <div class="text-xs text-gray-600">严重告警</div>
          </div>
        </div>
        
        <div class="alert-stat">
          <div class="text-center">
            <div class="text-2xl font-bold text-yellow-600">{{ warningCount }}</div>
            <div class="text-xs text-gray-600">警告告警</div>
          </div>
        </div>
        
        <div class="alert-stat">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">{{ infoCount }}</div>
            <div class="text-xs text-gray-600">信息告警</div>
          </div>
        </div>
      </div>
      
      <!-- 活跃告警列表 -->
      <div v-if="activeAlerts.length > 0" class="space-y-2">
        <div class="text-sm font-medium text-gray-700 mb-2">🚨 活跃告警:</div>
        
        <div 
          v-for="alert in displayedAlerts" 
          :key="alert.alert_id"
          class="alert-item"
          :class="getAlertClass(alert.severity)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center mb-1">
                <component 
                  :is="getAlertIcon(alert.severity)" 
                  :class="['w-4 h-4 mr-2', getAlertIconColor(alert.severity)]"
                />
                <span class="text-sm font-medium">{{ alert.rule_name }}</span>
                <span class="ml-2 text-xs px-2 py-1 rounded-full" :class="getSeverityBadgeClass(alert.severity)">
                  {{ getSeverityText(alert.severity) }}
                </span>
              </div>
              
              <div class="text-xs text-gray-600 mb-1">
                {{ alert.message }}
              </div>
              
              <div class="flex items-center space-x-4 text-xs text-gray-500">
                <span>触发时间: {{ formatAlertTime(alert.triggered_at) }}</span>
                <span v-if="alert.trigger_count > 1">触发次数: {{ alert.trigger_count }}</span>
              </div>
            </div>
            
            <div class="flex space-x-1 ml-2">
              <button 
                v-if="alert.status === 'active'"
                @click="acknowledgeAlert(alert.alert_id)"
                :disabled="isAcknowledging"
                class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50"
              >
                确认
              </button>
              
              <span 
                v-else-if="alert.status === 'acknowledged'"
                class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded"
              >
                已确认
              </span>
            </div>
          </div>
        </div>
        
        <!-- 显示更多按钮 -->
        <div v-if="activeAlerts.length > maxDisplayed" class="text-center">
          <button 
            @click="toggleShowAll"
            class="text-sm text-primary-600 hover:text-primary-700"
          >
            {{ showAll ? '收起' : `显示全部 ${activeAlerts.length} 个告警` }}
          </button>
        </div>
      </div>
      
      <!-- 无告警状态 -->
      <div v-else class="text-center py-4">
        <CheckCircleIcon class="w-12 h-12 text-green-400 mx-auto mb-2" />
        <div class="text-sm text-gray-600">✅ 暂无活跃告警</div>
        <div class="text-xs text-gray-500 mt-1">系统运行正常</div>
      </div>
      
      <!-- 告警规则状态 -->
      <div v-if="alertStatistics" class="border-t pt-3">
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600">告警规则状态</span>
          <div class="flex space-x-2 text-xs">
            <span class="text-green-600">
              ✅ {{ alertStatistics.enabled_rules }}/{{ alertStatistics.total_rules }} 已启用
            </span>
          </div>
        </div>
        
        <!-- 最近24小时告警趋势 -->
        <div class="mt-2 text-xs text-gray-500">
          最近24小时: {{ alertStatistics.alerts_24h }} 个告警
        </div>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="mt-4 pt-4 border-t border-gray-200 space-y-2">
      <div class="flex space-x-2">
        <button 
          @click="refreshAlerts"
          :disabled="isRefreshing"
          class="flex-1 text-sm text-primary-600 hover:text-primary-700 disabled:opacity-50 py-2 px-4 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors"
        >
          {{ isRefreshing ? '刷新中...' : '🔄 刷新告警' }}
        </button>
        
        <button 
          v-if="criticalCount > 0 || warningCount > 0"
          @click="acknowledgeAllAlerts"
          :disabled="isAcknowledging"
          class="flex-1 text-sm text-orange-600 hover:text-orange-700 disabled:opacity-50 py-2 px-4 border border-orange-200 rounded-lg hover:bg-orange-50 transition-colors"
        >
          {{ isAcknowledging ? '处理中...' : '🔔 确认全部' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { formatRelativeTime } from '@/utils/formatters'
import { apiService } from '@/services/api'
import {
  BellIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'

const appStore = useAppStore()

const isRefreshing = ref(false)
const isAcknowledging = ref(false)
const activeAlerts = ref<any[]>([])
const alertStatistics = ref<any>(null)
const lastUpdateTime = ref<Date | null>(null)
const refreshInterval = ref<NodeJS.Timeout | null>(null)
const showAll = ref(false)
const maxDisplayed = 3

// 计算属性
const totalAlerts = computed(() => activeAlerts.value.length)

const criticalCount = computed(() => 
  activeAlerts.value.filter(alert => alert.severity === 'critical').length
)

const warningCount = computed(() => 
  activeAlerts.value.filter(alert => alert.severity === 'warning').length
)

const infoCount = computed(() => 
  activeAlerts.value.filter(alert => alert.severity === 'info').length
)

const displayedAlerts = computed(() => {
  if (showAll.value || activeAlerts.value.length <= maxDisplayed) {
    return activeAlerts.value
  }
  return activeAlerts.value.slice(0, maxDisplayed)
})

const alertIconColor = computed(() => {
  if (criticalCount.value > 0) return 'text-red-500'
  if (warningCount.value > 0) return 'text-yellow-500'
  return 'text-green-500'
})

const lastUpdateDisplay = computed(() => {
  if (!lastUpdateTime.value) return '从未更新'
  return formatRelativeTime(lastUpdateTime.value)
})

// 工具方法
const getAlertIcon = (severity: string) => {
  switch (severity) {
    case 'critical': return XCircleIcon
    case 'warning': return ExclamationTriangleIcon
    case 'info': return InformationCircleIcon
    default: return BellIcon
  }
}

const getAlertIconColor = (severity: string) => {
  switch (severity) {
    case 'critical': return 'text-red-500'
    case 'warning': return 'text-yellow-500'
    case 'info': return 'text-blue-500'
    default: return 'text-gray-500'
  }
}

const getAlertClass = (severity: string) => {
  switch (severity) {
    case 'critical': return 'border-l-4 border-red-400 bg-red-50'
    case 'warning': return 'border-l-4 border-yellow-400 bg-yellow-50'
    case 'info': return 'border-l-4 border-blue-400 bg-blue-50'
    default: return 'border-l-4 border-gray-400 bg-gray-50'
  }
}

const getSeverityBadgeClass = (severity: string) => {
  switch (severity) {
    case 'critical': return 'bg-red-100 text-red-800'
    case 'warning': return 'bg-yellow-100 text-yellow-800'
    case 'info': return 'bg-blue-100 text-blue-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getSeverityText = (severity: string) => {
  switch (severity) {
    case 'critical': return '严重'
    case 'warning': return '警告'
    case 'info': return '信息'
    default: return '未知'
  }
}

const formatAlertTime = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleString()
}

// 方法
const refreshAlerts = async () => {
  if (isRefreshing.value) return
  
  try {
    isRefreshing.value = true
    
    const response = await apiService.getActiveAlerts()
    
    if (response.success) {
      activeAlerts.value = response.data.active_alerts || []
      alertStatistics.value = response.data.statistics || null
      lastUpdateTime.value = new Date()
      
      // 按严重程度排序
      activeAlerts.value.sort((a, b) => {
        const severityOrder = { 'critical': 3, 'warning': 2, 'info': 1 }
        return (severityOrder[b.severity] || 0) - (severityOrder[a.severity] || 0)
      })
      
    } else {
      throw new Error(response.error || '获取告警数据失败')
    }
    
  } catch (error) {
    console.error('刷新告警失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '刷新失败',
      message: '无法获取告警信息',
      duration: 3000
    })
  } finally {
    isRefreshing.value = false
  }
}

const acknowledgeAlert = async (alertId: string) => {
  if (isAcknowledging.value) return
  
  try {
    isAcknowledging.value = true
    
    const response = await apiService.acknowledgeAlert(alertId, 'web_user')
    
    if (response.success) {
      // 更新本地状态
      const alert = activeAlerts.value.find(a => a.alert_id === alertId)
      if (alert) {
        alert.status = 'acknowledged'
        alert.acknowledged_at = Date.now() / 1000
        alert.acknowledged_by = 'web_user'
      }
      
      appStore.addNotification({
        type: 'success',
        title: '告警已确认',
        message: '告警状态已更新',
        duration: 2000
      })
      
    } else {
      throw new Error(response.error || '确认告警失败')
    }
    
  } catch (error) {
    console.error('确认告警失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '确认失败',
      message: '无法确认告警',
      duration: 3000
    })
  } finally {
    isAcknowledging.value = false
  }
}

const acknowledgeAllAlerts = async () => {
  if (isAcknowledging.value) return
  
  const activeUnacknowledgedAlerts = activeAlerts.value.filter(
    alert => alert.status === 'active'
  )
  
  if (activeUnacknowledgedAlerts.length === 0) {
    appStore.addNotification({
      type: 'info',
      title: '无需确认',
      message: '没有未确认的告警',
      duration: 2000
    })
    return
  }
  
  try {
    isAcknowledging.value = true
    
    // 并行确认所有告警
    const promises = activeUnacknowledgedAlerts.map(alert =>
      apiService.acknowledgeAlert(alert.alert_id, 'web_user')
    )
    
    const results = await Promise.allSettled(promises)
    
    let successCount = 0
    let failCount = 0
    
    results.forEach((result, index) => {
      const alert = activeUnacknowledgedAlerts[index]
      
      if (result.status === 'fulfilled' && result.value.success) {
        alert.status = 'acknowledged'
        alert.acknowledged_at = Date.now() / 1000
        alert.acknowledged_by = 'web_user'
        successCount++
      } else {
        failCount++
      }
    })
    
    if (successCount > 0) {
      appStore.addNotification({
        type: 'success',
        title: '批量确认完成',
        message: `成功确认 ${successCount} 个告警${failCount > 0 ? `，${failCount} 个失败` : ''}`,
        duration: 3000
      })
    }
    
    if (failCount > 0 && successCount === 0) {
      appStore.addNotification({
        type: 'error',
        title: '批量确认失败',
        message: '无法确认告警，请重试',
        duration: 3000
      })
    }
    
  } catch (error) {
    console.error('批量确认告警失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '批量确认失败',
      message: '操作执行失败，请重试',
      duration: 3000
    })
  } finally {
    isAcknowledging.value = false
  }
}

const toggleShowAll = () => {
  showAll.value = !showAll.value
}

const startAutoRefresh = () => {
  refreshInterval.value = setInterval(refreshAlerts, 30000) // 每30秒刷新
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// 生命周期
onMounted(() => {
  refreshAlerts()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.alert-stat {
  @apply bg-gray-50 p-3 rounded-lg;
}

.alert-stat:hover {
  @apply bg-gray-100 transform scale-105 transition-all duration-200;
}

.alert-item {
  @apply p-3 rounded-lg transition-all duration-200;
}

.alert-item:hover {
  @apply shadow-sm transform translate-x-1;
}

/* 告警闪烁动画（仅严重告警） */
.alert-item.border-red-400 {
  animation: criticalPulse 2s infinite;
}

@keyframes criticalPulse {
  0%, 100% {
    background-color: #fef2f2;
  }
  50% {
    background-color: #fee2e2;
  }
}

/* 卡片悬停效果 */
.card:hover {
  @apply shadow-lg transform -translate-y-1 transition-all duration-300;
}
</style>