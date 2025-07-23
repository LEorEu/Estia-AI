import { io, Socket } from 'socket.io-client'
import type { WebSocketEvents } from '@/types'
import { useAppStore } from '@/stores/app'
import { useMonitoringStore } from '@/stores/monitoring'

// WebSocket事件管理器
class WebSocketManager {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private isConnecting = false
  private eventListeners: Map<string, Function[]> = new Map()

  constructor() {
    this.initializeSocket()
  }

  // 初始化Socket连接
  private initializeSocket() {
    if (this.socket) {
      return
    }

    this.socket = io({
      autoConnect: false,
      transports: ['websocket', 'polling'],
      timeout: 5000,
      forceNew: true,
    })

    this.setupEventListeners()
  }

  // 设置事件监听器
  private setupEventListeners() {
    if (!this.socket) return

    // 连接事件
    this.socket.on('connect', () => {
      console.log('✅ WebSocket连接已建立')
      this.reconnectAttempts = 0
      this.isConnecting = false
      
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'success',
        title: '连接成功',
        message: 'WebSocket连接已建立',
        duration: 3000
      })

      // 开始监控
      this.startMonitoring()
    })

    // 断开连接事件
    this.socket.on('disconnect', (reason) => {
      console.warn('⚠️ WebSocket连接已断开:', reason)
      
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'warning',
        title: '连接断开',
        message: `WebSocket连接已断开: ${reason}`,
        duration: 5000
      })

      // 自动重连
      if (reason !== 'io client disconnect') {
        this.handleReconnect()
      }
    })

    // 连接错误事件
    this.socket.on('connect_error', (error) => {
      console.error('❌ WebSocket连接错误:', error)
      this.isConnecting = false
      
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'error',
        title: '连接失败',
        message: `WebSocket连接失败: ${error.message}`,
        duration: 5000
      })

      this.handleReconnect()
    })

    // === 业务事件监听 ===
    
    // 状态更新
    this.socket.on('status_update', (data) => {
      const monitoringStore = useMonitoringStore()
      
      if (data.status) {
        monitoringStore.updateSystemStatus(data.status)
      }
      
      if (data.summary) {
        monitoringStore.updatePerformanceSummary(data.summary)
      }
    })

    // 流程状态更新
    this.socket.on('pipeline_status_update', (data) => {
      const monitoringStore = useMonitoringStore()
      monitoringStore.updatePipelineStatus(data)
      
      // 触发自定义事件给监控重构组件
      this.emit('pipeline_status_update', data)
    })

    // 上下文状态更新 (新增)
    this.socket.on('context_status_update', (data) => {
      console.log('📝 上下文状态更新:', data)
      this.emit('context_status_update', data)
    })

    // 实时性能指标 (新增)
    this.socket.on('real_time_metrics', (data) => {
      console.log('📈 实时性能指标:', data)
      this.emit('real_time_metrics', data)
    })

    // 监控重构相关错误处理 (新增)
    this.socket.on('pipeline_error', (data) => {
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'error',
        title: '流程监控错误',
        message: data.error,
        duration: 5000
      })
    })

    this.socket.on('context_error', (data) => {
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'error',
        title: '上下文监控错误',
        message: data.error,
        duration: 5000
      })
    })

    this.socket.on('metrics_error', (data) => {
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'error',
        title: '性能指标错误',
        message: data.error,
        duration: 5000
      })
    })

    // 新会话通知
    this.socket.on('new_session', (data) => {
      const monitoringStore = useMonitoringStore()
      monitoringStore.addSession(data)
      
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'info',
        title: '新会话',
        message: `会话 ${data.session_id} 已开始`,
        duration: 3000
      })
    })

    // 评估完成通知
    this.socket.on('evaluation_complete', (data) => {
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'success',
        title: '评估完成',
        message: `会话 ${data.session_id} 的异步评估已完成`,
        duration: 4000
      })

      // 触发自定义事件
      this.emit('evaluation_complete', data)
    })

    // 监控错误通知
    this.socket.on('monitoring_error', (data) => {
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'error',
        title: '监控错误',
        message: data.error,
        duration: 8000
      })
    })

    // 系统告警
    this.socket.on('system_alert', (data) => {
      const appStore = useAppStore()
      appStore.addNotification(data)
    })
  }

  // 连接WebSocket
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.socket) {
        this.initializeSocket()
      }

      if (this.socket!.connected) {
        resolve()
        return
      }

      if (this.isConnecting) {
        resolve()
        return
      }

      this.isConnecting = true

      // 设置一次性事件监听器
      this.socket!.once('connect', () => {
        resolve()
      })

      this.socket!.once('connect_error', (error) => {
        reject(new Error(`WebSocket连接失败: ${error.message}`))
      })

      this.socket!.connect()
    })
  }

  // 断开连接
  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.reconnectAttempts = 0
    this.isConnecting = false
  }

  // 处理重连
  private handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ WebSocket重连次数已达上限')
      
      const appStore = useAppStore()
      appStore.addNotification({
        type: 'error',
        title: '连接失败',
        message: '无法连接到服务器，请刷新页面重试',
        persistent: true
      })
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

    console.log(`🔄 ${delay}ms后尝试第${this.reconnectAttempts}次重连`)

    setTimeout(() => {
      if (this.socket && !this.socket.connected) {
        this.socket.connect()
      }
    }, delay)
  }

  // 开始监控
  private startMonitoring() {
    if (!this.socket) return

    // 请求开始实时监控
    this.socket.emit('start_monitoring')
    
    // 请求流程状态监控
    this.socket.emit('request_pipeline_status')
  }

  // === 监控重构专用方法 ===

  /**
   * 订阅流程状态更新
   */
  subscribePipeline() {
    if (!this.socket?.connected) {
      console.warn('⚠️ WebSocket未连接，无法订阅流程状态')
      return
    }
    
    this.socket.emit('subscribe_pipeline')
    console.log('📊 已订阅流程状态更新')
  }

  /**
   * 订阅上下文更新
   */
  subscribeContext() {
    if (!this.socket?.connected) {
      console.warn('⚠️ WebSocket未连接，无法订阅上下文更新')
      return
    }
    
    this.socket.emit('subscribe_context_updates')
    console.log('📝 已订阅上下文更新')
  }

  /**
   * 获取实时性能指标
   */
  getRealTimeMetrics() {
    if (!this.socket?.connected) {
      console.warn('⚠️ WebSocket未连接，无法获取实时指标')
      return
    }
    
    this.socket.emit('get_real_time_metrics')
    console.log('📈 已请求实时性能指标')
  }

  // 发送消息
  emit<K extends keyof WebSocketEvents>(event: K, data?: any) {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    } else {
      console.warn('WebSocket未连接，无法发送消息:', event)
    }
  }

  // 添加事件监听器
  on<K extends keyof WebSocketEvents>(
    event: K, 
    callback: (data: WebSocketEvents[K]) => void
  ) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    
    this.eventListeners.get(event)!.push(callback)

    // 如果socket已存在，直接添加监听器
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  // 移除事件监听器
  off<K extends keyof WebSocketEvents>(
    event: K, 
    callback?: (data: WebSocketEvents[K]) => void
  ) {
    if (callback) {
      const listeners = this.eventListeners.get(event) || []
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
      
      if (this.socket) {
        this.socket.off(event, callback)
      }
    } else {
      this.eventListeners.delete(event)
      if (this.socket) {
        this.socket.off(event)
      }
    }
  }

  // 获取连接状态
  get isConnected(): boolean {
    return this.socket?.connected || false
  }

  // 获取重连状态
  get isReconnecting(): boolean {
    return this.reconnectAttempts > 0 && this.reconnectAttempts < this.maxReconnectAttempts
  }

  // 获取连接ID
  get connectionId(): string | undefined {
    return this.socket?.id
  }
}

// 创建单例实例
export const websocketManager = new WebSocketManager()

// Vue组合式API Hook
export function useWebSocket() {
  const connect = () => websocketManager.connect()
  const disconnect = () => websocketManager.disconnect()
  const emit = (event: string, data?: any) => websocketManager.emit(event, data)
  const on = (event: string, callback: Function) => websocketManager.on(event, callback)
  const off = (event: string, callback?: Function) => websocketManager.off(event, callback)
  
  return {
    connect,
    disconnect,
    emit,
    on,
    off,
    isConnected: () => websocketManager.isConnected,
    isReconnecting: () => websocketManager.isReconnecting,
    connectionId: () => websocketManager.connectionId,
  }
}

export default websocketManager