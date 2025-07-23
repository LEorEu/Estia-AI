import axios from 'axios'
import type { 
  ApiResponse,
  DashboardData,
  SessionContext,
  SessionEvaluation,
  PipelineStatus
} from '@/types'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加时间戳防止缓存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API请求失败:', error)
    
    // 网络错误处理
    if (!error.response) {
      return Promise.reject(new Error('网络连接失败，请检查网络设置'))
    }
    
    // HTTP状态码错误处理
    const { status, data } = error.response
    switch (status) {
      case 404:
        return Promise.reject(new Error('请求的资源不存在'))
      case 500:
        return Promise.reject(new Error('服务器内部错误'))
      case 503:
        return Promise.reject(new Error('服务暂时不可用'))
      default:
        return Promise.reject(new Error(data?.error || '请求失败'))
    }
  }
)

// API服务类
class ApiService {
  // 获取仪表板综合数据
  async getDashboardData(): Promise<DashboardData> {
    try {
      // 首先尝试获取实时数据
      const liveData = await api.get('/live_data')
      return liveData
    } catch (error) {
      console.warn('实时数据获取失败，尝试获取仪表板数据:', error)
      
      try {
        // 降级到仪表板数据
        const dashboardData = await api.get('/dashboard_data')
        return dashboardData
      } catch (fallbackError) {
        console.warn('仪表板数据获取失败，使用测试数据:', fallbackError)
        
        // 最后降级到测试数据
        return await api.get('/generate_test_data')
      }
    }
  }

  // 获取系统状态
  async getStatus(): Promise<ApiResponse> {
    return await api.get('/status')
  }

  // 获取性能数据
  async getPerformance(): Promise<ApiResponse> {
    return await api.get('/performance')
  }

  // 获取会话列表
  async getSessions(): Promise<ApiResponse> {
    return await api.get('/sessions')
  }

  // 获取关键词分析
  async getKeywords(): Promise<ApiResponse> {
    return await api.get('/keywords')
  }

  // 获取记忆分析
  async getMemoryAnalysis(): Promise<ApiResponse> {
    return await api.get('/memory_analysis')
  }

  // === 新功能API ===
  
  // 获取会话上下文详情
  async getSessionContext(sessionId: string): Promise<SessionContext> {
    return await api.get(`/session/${sessionId}/context`)
  }

  // 获取当前构建中的上下文
  async getCurrentContext(): Promise<SessionContext> {
    return await api.get('/current_context')
  }

  // 获取会话异步评估结果
  async getSessionEvaluation(sessionId: string): Promise<SessionEvaluation> {
    return await api.get(`/session/${sessionId}/evaluation`)
  }

  // 获取待处理评估队列
  async getPendingEvaluations(): Promise<SessionEvaluation[]> {
    return await api.get('/evaluations/pending')
  }

  // 获取评估历史
  async getEvaluationHistory(limit = 20): Promise<SessionEvaluation[]> {
    return await api.get('/evaluations/history', { params: { limit } })
  }

  // 获取流程状态
  async getPipelineStatus(): Promise<PipelineStatus> {
    return await api.get('/pipeline/status')
  }

  // 获取流程性能指标
  async getPipelineMetrics(): Promise<ApiResponse> {
    return await api.get('/pipeline/metrics')
  }

  // 获取特定步骤详情
  async getStepDetails(stepId: string): Promise<ApiResponse> {
    return await api.get(`/pipeline/step/${stepId}/details`)
  }

  // 获取系统健康状态
  async getSystemHealth(): Promise<ApiResponse> {
    return await api.get('/system/health')
  }

  // 获取系统指标趋势
  async getSystemMetricsTrend(period = '1h'): Promise<ApiResponse> {
    return await api.get('/system/metrics/trend', { params: { period } })
  }

  // 获取系统告警
  async getSystemAlerts(): Promise<ApiResponse> {
    return await api.get('/system/alerts')
  }

  // === v6.0监控系统API ===
  
  // 获取v6.0综合统计
  async getV6ComprehensiveStats(): Promise<ApiResponse> {
    return await api.get('/v6_comprehensive_stats')
  }

  // 获取15步监控详情
  async get15StepMonitoring(): Promise<ApiResponse> {
    return await api.get('/13_step_monitoring') // 注意：后端URL仍是13_step
  }

  // === 增强监控系统API ===
  
  // 获取监控系统状态
  async getMonitoringStatus(): Promise<ApiResponse> {
    return await api.get('/monitoring/status')
  }

  // 获取当前性能指标
  async getCurrentMetrics(): Promise<ApiResponse> {
    return await api.get('/monitoring/metrics/current')
  }

  // 获取指标历史数据
  async getMetricsHistory(minutes = 60, metric?: string): Promise<ApiResponse> {
    const params: any = { minutes }
    if (metric) params.metric = metric
    return await api.get('/monitoring/metrics/history', { params })
  }

  // 获取活跃告警
  async getActiveAlerts(): Promise<ApiResponse> {
    return await api.get('/monitoring/alerts')
  }

  // 确认告警
  async acknowledgeAlert(alertId: string, acknowledgedBy = 'web_user'): Promise<ApiResponse> {
    return await api.post(`/monitoring/alerts/${alertId}/acknowledge`, { acknowledged_by: acknowledgedBy })
  }

  // 获取增强性能摘要
  async getEnhancedPerformanceSummary(): Promise<ApiResponse> {
    return await api.get('/monitoring/performance/summary')
  }

  // 获取系统健康状态
  async getEnhancedSystemHealth(): Promise<ApiResponse> {
    return await api.get('/monitoring/health')
  }

  // 获取综合监控报告
  async getComprehensiveMonitoringReport(): Promise<ApiResponse> {
    return await api.get('/monitoring/comprehensive')
  }

  // === 工具方法 ===
  
  // 批量获取多个API数据
  async getBatchData(endpoints: string[]): Promise<Record<string, any>> {
    try {
      const promises = endpoints.map(endpoint => 
        api.get(endpoint).catch(error => ({ error: error.message }))
      )
      
      const results = await Promise.all(promises)
      
      const batchData: Record<string, any> = {}
      endpoints.forEach((endpoint, index) => {
        const key = endpoint.replace('/api/', '').replace('/', '_')
        batchData[key] = results[index]
      })
      
      return batchData
    } catch (error) {
      console.error('批量获取数据失败:', error)
      throw error
    }
  }

  // 检查API健康状态
  async checkHealth(): Promise<boolean> {
    try {
      await api.get('/status', { timeout: 3000 })
      return true
    } catch (error) {
      return false
    }
  }

  // 获取API版本信息
  async getVersion(): Promise<{ version: string; build: string }> {
    try {
      return await api.get('/version')
    } catch (error) {
      return { version: 'unknown', build: 'unknown' }
    }
  }
}

// 导出单例实例
export const apiService = new ApiService()

// 导出类型
export type { ApiService }

// 默认导出
export default apiService