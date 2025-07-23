<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title flex items-center">
        <WifiIcon class="w-5 h-5 mr-2 text-primary-500" />
        连接状态
      </h3>
    </div>
    
    <div class="space-y-4">
      <!-- WebSocket连接状态 -->
      <div class="connection-item">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center space-x-2">
            <component 
              :is="wsStatusIcon" 
              :class="['w-4 h-4', wsStatusColor]"
            />
            <span class="text-sm font-medium text-gray-700">WebSocket</span>
          </div>
          <span :class="['text-xs px-2 py-1 rounded-full', wsStatusBadgeClass]">
            {{ wsStatusText }}
          </span>
        </div>
        
        <div class="text-xs text-gray-500 space-y-1">
          <div v-if="connectionId">连接ID: {{ connectionId }}</div>
          <div>延迟: {{ wsLatency }}ms</div>
          <div>重连次数: {{ wsReconnectCount }}</div>
        </div>
      </div>
      
      <!-- API连接状态 -->
      <div class="connection-item">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center space-x-2">
            <component 
              :is="apiStatusIcon" 
              :class="['w-4 h-4', apiStatusColor]"
            />
            <span class="text-sm font-medium text-gray-700">API服务</span>
          </div>
          <span :class="['text-xs px-2 py-1 rounded-full', apiStatusBadgeClass]">
            {{ apiStatusText }}
          </span>
        </div>
        
        <div class="text-xs text-gray-500 space-y-1">
          <div>端点: /api/*</div>
          <div>响应时间: {{ apiResponseTime }}ms</div>
          <div>最后检查: {{ lastHealthCheck }}</div>
        </div>
      </div>
      
      <!-- 数据源状态 -->
      <div class="connection-item">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center space-x-2">
            <component 
              :is="dataSourceIcon" 
              :class="['w-4 h-4', dataSourceColor]"
            />
            <span class="text-sm font-medium text-gray-700">数据源</span>
          </div>
          <span :class="['text-xs px-2 py-1 rounded-full', dataSourceBadgeClass]">
            {{ dataSourceText }}
          </span>
        </div>
        
        <div class="text-xs text-gray-500">
          <div>{{ dataSourceDescription }}</div>
        </div>
      </div>
    </div>
    
    <!-- 连接操作 -->
    <div class="mt-4 pt-4 border-t border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <button
            @click="handleReconnect"
            :disabled="isReconnecting"
            class="text-xs bg-primary-500 text-white px-3 py-1 rounded hover:bg-primary-600 disabled:opacity-50 transition-colors"
          >
            {{ isReconnecting ? '重连中...' : '重新连接' }}
          </button>
          
          <button
            @click="runConnectionTest"
            :disabled="isTestingConnection"
            class="text-xs bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600 disabled:opacity-50 transition-colors"
          >
            {{ isTestingConnection ? '测试中...' : '连接测试' }}
          </button>
        </div>
        
        <!-- 连接质量指示器 -->
        <div class="flex items-center space-x-1">
          <div 
            v-for="i in 4" 
            :key="i"
            :class="[
              'w-1 h-3 rounded-full transition-all duration-300',
              connectionQuality >= i ? 'bg-green-500' : 'bg-gray-300'
            ]"
          ></div>
          <span class="text-xs text-gray-500 ml-1">{{ connectionQualityText }}</span>
        </div>
      </div>
    </div>
    
    <!-- 连接历史图表 -->
    <div class="mt-4 pt-4 border-t border-gray-200">
      <div class="flex justify-between items-center mb-2">
        <span class="text-xs text-gray-600">连接稳定性</span>
        <span class="text-xs text-gray-500">最近10分钟</span>
      </div>
      
      <div class="h-8 w-full">
        <svg class="w-full h-full" viewBox="0 0 100 32">
          <!-- 连接状态条 -->
          <g v-for="(status, index) in connectionHistory" :key="index">
            <rect
              :x="index * 2"
              y="8"
              width="2"
              height="16"
              :fill="status ? '#10B981' : '#EF4444'"
              :opacity="0.8"
            />
          </g>
        </svg>
      </div>
      
      <div class="flex justify-between text-xs text-gray-500 mt-1">
        <span>10分钟前</span>
        <span>现在</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { useAppStore } from '@/stores/app'
import { useWebSocket } from '@/services/websocket'
import { apiService } from '@/services/api'
import { formatRelativeTime } from '@/utils/formatters'
import {
  WifiIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ServerIcon,
  CloudIcon,
  ComputerDesktopIcon
} from '@heroicons/vue/24/outline'

const monitoringStore = useMonitoringStore()
const appStore = useAppStore()
const { isConnected, isReconnecting, connectionId, connect } = useWebSocket()

const isTestingConnection = ref(false)
const wsLatency = ref(0)
const wsReconnectCount = ref(0)
const apiResponseTime = ref(0)
const lastHealthCheck = ref<Date | null>(null)

// 连接历史记录（最近50个检查点，每12秒一个）
const connectionHistory = ref<boolean[]>(new Array(50).fill(true))

// 计算属性 - WebSocket状态
const wsStatusIcon = computed(() => {
  if (isReconnecting()) return ExclamationTriangleIcon
  return isConnected() ? CheckCircleIcon : XCircleIcon
})

const wsStatusColor = computed(() => {
  if (isReconnecting()) return 'text-yellow-500'
  return isConnected() ? 'text-green-500' : 'text-red-500'
})

const wsStatusText = computed(() => {
  if (isReconnecting()) return '重连中'
  return isConnected() ? '已连接' : '断开'
})

const wsStatusBadgeClass = computed(() => {
  if (isReconnecting()) return 'bg-yellow-100 text-yellow-800'
  return isConnected() ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
})

// 计算属性 - API状态
const apiStatusIcon = computed(() => {
  return monitoringStore.isConnected ? CheckCircleIcon : XCircleIcon
})

const apiStatusColor = computed(() => {
  return monitoringStore.isConnected ? 'text-green-500' : 'text-red-500'
})

const apiStatusText = computed(() => {
  return monitoringStore.isConnected ? '正常' : '异常'
})

const apiStatusBadgeClass = computed(() => {
  return monitoringStore.isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
})

// 计算属性 - 数据源状态
const dataSourceIcon = computed(() => {
  switch (monitoringStore.dataSource) {
    case 'live':
      return ServerIcon
    case 'test':
      return ComputerDesktopIcon
    default:
      return CloudIcon
  }
})

const dataSourceColor = computed(() => {
  switch (monitoringStore.dataSource) {
    case 'live':
      return 'text-green-500'
    case 'test':
      return 'text-blue-500'
    default:
      return 'text-yellow-500'
  }
})

const dataSourceText = computed(() => {
  switch (monitoringStore.dataSource) {
    case 'live':
      return '实时数据'
    case 'test':
      return '测试数据'
    default:
      return '模拟数据'
  }
})

const dataSourceBadgeClass = computed(() => {
  switch (monitoringStore.dataSource) {
    case 'live':
      return 'bg-green-100 text-green-800'
    case 'test':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-yellow-100 text-yellow-800'
  }
})

const dataSourceDescription = computed(() => {
  switch (monitoringStore.dataSource) {
    case 'live':
      return 'Estia系统运行中，数据实时更新'
    case 'test':
      return '使用测试数据进行演示'
    default:
      return '使用模拟数据，功能受限'
  }
})

// 连接质量评估
const connectionQuality = computed(() => {
  let quality = 0
  
  if (isConnected()) quality += 1
  if (monitoringStore.isConnected) quality += 1
  if (wsLatency.value < 100) quality += 1
  if (wsReconnectCount.value < 3) quality += 1
  
  return quality
})

const connectionQualityText = computed(() => {
  switch (connectionQuality.value) {
    case 4: return '优秀'
    case 3: return '良好'
    case 2: return '一般'
    case 1: return '较差'
    default: return '断开'
  }
})

const lastHealthCheckDisplay = computed(() => {
  if (!lastHealthCheck.value) return '从未'
  return formatRelativeTime(lastHealthCheck.value)
})

// 方法
const handleReconnect = async () => {
  try {
    await connect()
    
    appStore.addNotification({
      type: 'success',
      title: '重连成功',
      message: 'WebSocket连接已恢复',
      duration: 3000
    })
    
    wsReconnectCount.value++
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      title: '重连失败',
      message: '无法建立WebSocket连接',
      duration: 5000
    })
  }
}

const runConnectionTest = async () => {
  if (isTestingConnection.value) return
  
  try {
    isTestingConnection.value = true
    
    // 测试API连接
    const startTime = Date.now()
    const isHealthy = await apiService.checkHealth()
    const endTime = Date.now()
    
    apiResponseTime.value = endTime - startTime
    lastHealthCheck.value = new Date()
    
    // 测试WebSocket延迟
    if (isConnected()) {
      const wsStart = Date.now()
      // 发送ping消息测试延迟
      setTimeout(() => {
        wsLatency.value = Date.now() - wsStart
      }, 50)
    }
    
    const testResult = {
      api: isHealthy,
      websocket: isConnected(),
      latency: apiResponseTime.value
    }
    
    appStore.addNotification({
      type: testResult.api && testResult.websocket ? 'success' : 'warning',
      title: '连接测试完成',
      message: `API: ${testResult.api ? '正常' : '异常'}, WebSocket: ${testResult.websocket ? '正常' : '异常'}, 延迟: ${testResult.latency}ms`,
      duration: 5000
    })
    
  } catch (error) {
    console.error('连接测试失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '测试失败',
      message: '无法完成连接测试',
      duration: 5000
    })
  } finally {
    isTestingConnection.value = false
  }
}

// 更新连接历史
const updateConnectionHistory = () => {
  const currentStatus = isConnected() && monitoringStore.isConnected
  
  connectionHistory.value.push(currentStatus)
  
  // 保持固定长度
  if (connectionHistory.value.length > 50) {
    connectionHistory.value.shift()
  }
}

// 定时器
let historyTimer: NodeJS.Timeout | null = null

// 生命周期
onMounted(() => {
  // 初始化连接测试
  runConnectionTest()
  
  // 每12秒更新一次连接历史
  historyTimer = setInterval(updateConnectionHistory, 12000)
})

onUnmounted(() => {
  if (historyTimer) {
    clearInterval(historyTimer)
  }
})
</script>

<style scoped>
.connection-item {
  @apply p-3 bg-gray-50 rounded-lg;
}

.connection-item:hover {
  @apply bg-gray-100 transition-colors;
}

/* 连接质量指示器动画 */
.w-1 {
  transition: all 0.3s ease;
}

.w-1:nth-child(1) {
  animation-delay: 0s;
}
.w-1:nth-child(2) {
  animation-delay: 0.1s;
}
.w-1:nth-child(3) {
  animation-delay: 0.2s;
}
.w-1:nth-child(4) {
  animation-delay: 0.3s;
}

@keyframes pulse-quality {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(1.2); }
}

.bg-green-500 {
  animation: pulse-quality 2s infinite;
}
</style>