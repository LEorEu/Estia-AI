import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { 
  DashboardData, 
  SystemStatusData, 
  PerformanceSummary,
  SessionData,
  KeywordAnalysis,
  MemoryAnalysis,
  PipelineStatus
} from '@/types'
import { apiService } from '@/services/api'
import { useAppStore } from './app'

export const useMonitoringStore = defineStore('monitoring', () => {
  const appStore = useAppStore()
  
  // 状态数据
  const systemStatus = ref<SystemStatusData | null>(null)
  const performanceSummary = ref<PerformanceSummary | null>(null)
  const sessions = ref<SessionData[]>([])
  const keywords = ref<KeywordAnalysis | null>(null)
  const memoryAnalysis = ref<MemoryAnalysis | null>(null)
  const pipelineStatus = ref<PipelineStatus | null>(null)
  
  // 系统状态
  const isConnected = ref(false)
  const lastUpdateTime = ref<Date | null>(null)
  const dataSource = ref<'live' | 'mock' | 'test'>('mock')
  
  // 错误状态
  const error = ref<string | null>(null)
  const isLoading = ref(false)
  
  // Actions
  const fetchDashboardData = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await apiService.getDashboardData()
      
      if (data.error) {
        throw new Error(data.error)
      }
      
      // 更新所有状态
      updateDashboardData(data)
      
      isConnected.value = true
      lastUpdateTime.value = new Date()
      
    } catch (err) {
      console.error('获取仪表板数据失败:', err)
      error.value = err instanceof Error ? err.message : '未知错误'
      isConnected.value = false
      
      appStore.addNotification({
        type: 'error',
        title: '数据获取失败',
        message: error.value,
        duration: 5000
      })
    } finally {
      isLoading.value = false
    }
  }
  
  const updateDashboardData = (data: DashboardData) => {
    // 更新系统状态
    if (data.status?.status) {
      systemStatus.value = data.status.status
    }
    
    if (data.status?.summary) {
      performanceSummary.value = data.status.summary
    }
    
    // 更新会话数据
    if (data.sessions?.sessions) {
      sessions.value = data.sessions.sessions
    }
    
    // 更新关键词分析
    if (data.keywords) {
      keywords.value = data.keywords
    }
    
    // 更新记忆分析
    if (data.memory) {
      memoryAnalysis.value = data.memory
    }
    
    // 设置数据源
    if (data.live_mode) {
      dataSource.value = 'live'
    } else if (data.test_mode) {
      dataSource.value = 'test'
    } else {
      dataSource.value = 'mock'
    }
  }
  
  const updateSystemStatus = (status: SystemStatusData) => {
    systemStatus.value = status
    lastUpdateTime.value = new Date()
  }
  
  const updatePerformanceSummary = (summary: PerformanceSummary) => {
    performanceSummary.value = summary
    lastUpdateTime.value = new Date()
  }
  
  const addSession = (session: SessionData) => {
    sessions.value.unshift(session) // 新会话添加到开头
    
    // 限制会话列表长度
    if (sessions.value.length > 50) {
      sessions.value = sessions.value.slice(0, 50)
    }
    
    // 更新性能摘要
    if (performanceSummary.value) {
      performanceSummary.value.total_sessions += 1
    }
  }
  
  const updatePipelineStatus = (status: PipelineStatus) => {
    pipelineStatus.value = status
    lastUpdateTime.value = new Date()
  }
  
  const clearError = () => {
    error.value = null
  }
  
  const reset = () => {
    systemStatus.value = null
    performanceSummary.value = null
    sessions.value = []
    keywords.value = null
    memoryAnalysis.value = null
    pipelineStatus.value = null
    error.value = null
    isConnected.value = false
    lastUpdateTime.value = null
  }
  
  // Getters
  const hasData = computed(() => {
    return systemStatus.value !== null || sessions.value.length > 0
  })
  
  const isSystemRunning = computed(() => {
    return systemStatus.value?.status === 'running'
  })
  
  const isSystemIdle = computed(() => {
    return systemStatus.value?.status === 'idle'
  })
  
  const isSystemError = computed(() => {
    return systemStatus.value?.status === 'error' || error.value !== null
  })
  
  const currentSessionId = computed(() => {
    return systemStatus.value?.session_id || null
  })
  
  const totalSessions = computed(() => {
    return performanceSummary.value?.total_sessions || sessions.value.length
  })
  
  const averageResponseTime = computed(() => {
    if (!performanceSummary.value?.average_duration) {
      return 0
    }
    return Math.round(performanceSummary.value.average_duration * 1000) // 转换为毫秒
  })
  
  const successRate = computed(() => {
    if (!performanceSummary.value?.success_rate) {
      return 0
    }
    return Math.round(performanceSummary.value.success_rate * 100) // 转换为百分比
  })
  
  const topKeywords = computed(() => {
    return keywords.value?.top_keywords?.slice(0, 10) || []
  })
  
  const recentSessions = computed(() => {
    return sessions.value.slice(0, 10)
  })
  
  const connectionStatusText = computed(() => {
    if (!isConnected.value) return '离线'
    
    switch (dataSource.value) {
      case 'live':
        return '实时数据'
      case 'test':
        return '测试数据'
      case 'mock':
        return '模拟数据'
      default:
        return '未知'
    }
  })
  
  const connectionStatusColor = computed(() => {
    if (!isConnected.value) return 'text-red-500'
    
    switch (dataSource.value) {
      case 'live':
        return 'text-green-500'
      case 'test':
        return 'text-blue-500'
      case 'mock':
        return 'text-yellow-500'
      default:
        return 'text-gray-500'
    }
  })
  
  return {
    // State
    systemStatus,
    performanceSummary,
    sessions,
    keywords,
    memoryAnalysis,
    pipelineStatus,
    isConnected,
    lastUpdateTime,
    dataSource,
    error,
    isLoading,
    
    // Actions
    fetchDashboardData,
    updateDashboardData,
    updateSystemStatus,
    updatePerformanceSummary,
    addSession,
    updatePipelineStatus,
    clearError,
    reset,
    
    // Getters
    hasData,
    isSystemRunning,
    isSystemIdle,
    isSystemError,
    currentSessionId,
    totalSessions,
    averageResponseTime,
    successRate,
    topKeywords,
    recentSessions,
    connectionStatusText,
    connectionStatusColor
  }
})