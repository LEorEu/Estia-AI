import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification } from '@/types'

export const useAppStore = defineStore('app', () => {
  // 状态
  const isLoading = ref(false)
  const isInitialized = ref(false)
  const notifications = ref<Notification[]>([])
  
  // 系统信息
  const appVersion = ref('1.0.0')
  const lastUpdateTime = ref<Date | null>(null)
  
  // Actions
  const initialize = async () => {
    if (isInitialized.value) return
    
    try {
      setLoading(true)
      
      // 模拟初始化过程
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      isInitialized.value = true
      lastUpdateTime.value = new Date()
      
      addNotification({
        type: 'success',
        title: '系统初始化完成',
        message: 'Estia AI 监控仪表板已就绪',
        duration: 3000
      })
      
    } catch (error) {
      console.error('应用初始化失败:', error)
      addNotification({
        type: 'error',
        title: '初始化失败',
        message: '应用初始化过程中发生错误',
        persistent: true
      })
    } finally {
      setLoading(false)
    }
  }
  
  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }
  
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      id: `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      duration: 5000, // 默认5秒
      ...notification
    }
    
    notifications.value.push(newNotification)
    
    // 自动移除非持久化通知
    if (!newNotification.persistent && newNotification.duration) {
      setTimeout(() => {
        removeNotification(newNotification.id)
      }, newNotification.duration)
    }
  }
  
  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }
  
  const clearAllNotifications = () => {
    notifications.value = []
  }
  
  const updateLastUpdateTime = () => {
    lastUpdateTime.value = new Date()
  }
  
  // Getters
  const hasUnreadNotifications = computed(() => {
    return notifications.value.length > 0
  })
  
  const errorNotifications = computed(() => {
    return notifications.value.filter(n => n.type === 'error')
  })
  
  return {
    // State
    isLoading,
    isInitialized,
    notifications,
    appVersion,
    lastUpdateTime,
    
    // Actions
    initialize,
    setLoading,
    addNotification,
    removeNotification,
    clearAllNotifications,
    updateLastUpdateTime,
    
    // Getters
    hasUnreadNotifications,
    errorNotifications
  }
})

// 为了向后兼容，导出通知store的别名
export const useNotificationStore = useAppStore