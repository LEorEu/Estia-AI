<template>
  <footer class="bg-white/80 backdrop-blur-sm border-t border-gray-200 mt-12">
    <div class="container mx-auto px-4 py-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- 系统信息 -->
        <div class="space-y-2">
          <h4 class="font-semibold text-gray-800">系统信息</h4>
          <div class="text-sm text-gray-600 space-y-1">
            <div>版本: {{ appVersion }}</div>
            <div>构建: Vue {{ vueVersion }}</div>
            <div>最后更新: {{ lastUpdateDisplay }}</div>
          </div>
        </div>

        <!-- 连接状态 -->
        <div class="space-y-2">
          <h4 class="font-semibold text-gray-800">连接状态</h4>
          <div class="text-sm text-gray-600 space-y-1">
            <div class="flex items-center space-x-2">
              <div :class="['w-2 h-2 rounded-full', wsStatusColor]"></div>
              <span>WebSocket: {{ wsStatusText }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <div :class="['w-2 h-2 rounded-full', apiStatusColor]"></div>
              <span>API: {{ apiStatusText }}</span>
            </div>
            <div>数据源: {{ dataSource }}</div>
          </div>
        </div>

        <!-- 性能统计 -->
        <div class="space-y-2">
          <h4 class="font-semibold text-gray-800">性能统计</h4>
          <div class="text-sm text-gray-600 space-y-1">
            <div>总会话数: {{ totalSessions }}</div>
            <div>平均响应: {{ averageResponseTime }}ms</div>
            <div>成功率: {{ successRate }}%</div>
          </div>
        </div>
      </div>

      <!-- 底部版权和链接 -->
      <div class="mt-6 pt-6 border-t border-gray-200">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="text-sm text-gray-600">
            © 2025 Estia AI. 基于Vue 3构建的智能记忆监控系统
          </div>
          
          <div class="flex items-center space-x-4 mt-4 md:mt-0">
            <a
              href="https://github.com/your-repo"
              target="_blank"
              rel="noopener noreferrer"
              class="text-sm text-gray-600 hover:text-primary-600 transition-colors"
            >
              GitHub
            </a>
            <a
              href="/docs"
              class="text-sm text-gray-600 hover:text-primary-600 transition-colors"
            >
              文档
            </a>
            <button
              @click="showDebugInfo = !showDebugInfo"
              class="text-sm text-gray-600 hover:text-primary-600 transition-colors"
            >
              调试信息
            </button>
          </div>
        </div>
      </div>

      <!-- 调试信息面板 -->
      <div v-if="showDebugInfo" class="mt-4 p-4 bg-gray-50 rounded-lg">
        <h5 class="font-medium text-gray-800 mb-2">调试信息</h5>
        <div class="text-xs text-gray-600 font-mono space-y-1">
          <div>环境: {{ environment }}</div>
          <div>构建时间: {{ buildTime }}</div>
          <div>WebSocket ID: {{ connectionId || '未连接' }}</div>
          <div>浏览器: {{ userAgent }}</div>
          <div>屏幕分辨率: {{ screenResolution }}</div>
          <div>内存使用: {{ memoryUsage }}</div>
        </div>
        
        <!-- 系统健康检查 -->
        <div class="mt-3">
          <button
            @click="runHealthCheck"
            :disabled="isRunningHealthCheck"
            class="text-xs bg-primary-500 text-white px-3 py-1 rounded hover:bg-primary-600 disabled:opacity-50"
          >
            {{ isRunningHealthCheck ? '检查中...' : '运行健康检查' }}
          </button>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useMonitoringStore } from '@/stores/monitoring'
import { useWebSocket } from '@/services/websocket'
import { formatRelativeTime } from '@/utils/formatters'
import { apiService } from '@/services/api'

const appStore = useAppStore()
const monitoringStore = useMonitoringStore()
const { isConnected, connectionId } = useWebSocket()

const showDebugInfo = ref(false)
const isRunningHealthCheck = ref(false)

// 系统信息
const appVersion = computed(() => appStore.appVersion)
const vueVersion = ref('3.4.15')
const environment = computed(() => import.meta.env.MODE)
const buildTime = computed(() => import.meta.env.VITE_BUILD_TIME || '未知')

// 连接状态
const wsStatusText = computed(() => isConnected() ? '已连接' : '断开')
const wsStatusColor = computed(() => isConnected() ? 'bg-green-500' : 'bg-red-500')

const apiStatusText = computed(() => monitoringStore.isConnected ? '正常' : '异常')
const apiStatusColor = computed(() => monitoringStore.isConnected ? 'bg-green-500' : 'bg-red-500')

const dataSource = computed(() => {
  const sourceMap: Record<string, string> = {
    'live': '实时数据',
    'mock': '模拟数据',
    'test': '测试数据'
  }
  return sourceMap[monitoringStore.dataSource] || '未知'
})

// 性能统计
const totalSessions = computed(() => monitoringStore.totalSessions)
const averageResponseTime = computed(() => monitoringStore.averageResponseTime)
const successRate = computed(() => monitoringStore.successRate)

// 最后更新时间
const lastUpdateDisplay = computed(() => {
  if (!appStore.lastUpdateTime) return '从未'
  return formatRelativeTime(appStore.lastUpdateTime)
})

// 调试信息
const userAgent = computed(() => {
  const ua = navigator.userAgent
  if (ua.includes('Chrome')) return `Chrome ${ua.match(/Chrome\/(\d+)/)?.[1]}`
  if (ua.includes('Firefox')) return `Firefox ${ua.match(/Firefox\/(\d+)/)?.[1]}`
  if (ua.includes('Safari')) return `Safari ${ua.match(/Version\/(\d+)/)?.[1]}`
  return 'Unknown'
})

const screenResolution = computed(() => `${screen.width}x${screen.height}`)

const memoryUsage = computed(() => {
  if ('memory' in performance) {
    const memory = (performance as any).memory
    const used = Math.round(memory.usedJSHeapSize / 1024 / 1024)
    const total = Math.round(memory.totalJSHeapSize / 1024 / 1024)
    return `${used}MB / ${total}MB`
  }
  return '不支持'
})

// 方法
const runHealthCheck = async () => {
  if (isRunningHealthCheck.value) return
  
  try {
    isRunningHealthCheck.value = true
    
    // 检查API健康状态
    const isHealthy = await apiService.checkHealth()
    
    // 检查WebSocket连接
    const wsHealthy = isConnected()
    
    // 检查本地存储
    const storageHealthy = typeof Storage !== 'undefined'
    
    // 生成健康报告
    const report = {
      api: isHealthy ? '✅ 正常' : '❌ 异常',
      websocket: wsHealthy ? '✅ 已连接' : '❌ 断开',
      storage: storageHealthy ? '✅ 可用' : '❌ 不可用',
      timestamp: new Date().toLocaleString()
    }
    
    appStore.addNotification({
      type: isHealthy && wsHealthy ? 'success' : 'warning',
      title: '健康检查完成',
      message: `API: ${isHealthy ? '正常' : '异常'}, WebSocket: ${wsHealthy ? '连接' : '断开'}`,
      duration: 5000
    })
    
    console.log('🏥 系统健康检查报告:', report)
    
  } catch (error) {
    console.error('健康检查失败:', error)
    appStore.addNotification({
      type: 'error',
      title: '健康检查失败',
      message: '无法完成系统健康检查',
      duration: 5000
    })
  } finally {
    isRunningHealthCheck.value = false
  }
}

// 生命周期
onMounted(() => {
  // 获取Vue版本（如果可能）
  if (typeof window !== 'undefined' && (window as any).Vue) {
    vueVersion.value = (window as any).Vue.version || vueVersion.value
  }
})
</script>

<style scoped>
/* 响应式调整 */
@media (max-width: 768px) {
  .container {
    @apply px-4;
  }
}
</style>