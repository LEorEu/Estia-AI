<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-50 space-y-3 w-96 max-w-[calc(100vw-2rem)]">
      <TransitionGroup
        name="notification"
        tag="div"
        class="space-y-3"
      >
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="[
            'notification-card rounded-xl p-4 shadow-lg backdrop-blur-sm',
            'border border-opacity-20 transition-all duration-300',
            getNotificationStyles(notification.type)
          ]"
        >
          <div class="flex items-start">
            <!-- 图标 -->
            <div class="flex-shrink-0 mr-3">
              <component 
                :is="getNotificationIcon(notification.type)"
                :class="[
                  'w-6 h-6',
                  getIconColor(notification.type)
                ]"
              />
            </div>
            
            <!-- 内容 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <h4 :class="[
                  'font-semibold text-sm',
                  getTitleColor(notification.type)
                ]">
                  {{ notification.title }}
                </h4>
                
                <!-- 关闭按钮 -->
                <button
                  @click="removeNotification(notification.id)"
                  :class="[
                    'ml-2 p-1 rounded-full hover:bg-black/10 transition-colors',
                    'focus:outline-none focus:ring-2 focus:ring-offset-1',
                    getFocusColor(notification.type)
                  ]"
                >
                  <CloseIcon class="w-4 h-4 text-gray-500" />
                </button>
              </div>
              
              <p :class="[
                'mt-1 text-sm leading-relaxed',
                getMessageColor(notification.type)
              ]">
                {{ notification.message }}
              </p>
              
              <!-- 时间戳 -->
              <div class="mt-2 text-xs text-gray-500">
                {{ formatTime(notification.timestamp) }}
              </div>
              
              <!-- 进度条（持久化通知显示持续时间） -->
              <div 
                v-if="!notification.persistent && notification.duration"
                class="mt-3 w-full bg-black/10 rounded-full h-1 overflow-hidden"
              >
                <div 
                  class="h-full bg-current opacity-30 transition-all ease-linear"
                  :style="{ 
                    width: `${getProgressWidth(notification)}%`,
                    transitionDuration: `${notification.duration}ms`
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

// 图标组件
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  XMarkIcon as CloseIcon
} from '@heroicons/vue/24/outline'

const appStore = useAppStore()

const notifications = computed(() => appStore.notifications)

const removeNotification = (id: string) => {
  appStore.removeNotification(id)
}

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'success':
      return CheckCircleIcon
    case 'warning':
      return ExclamationTriangleIcon
    case 'error':
      return XCircleIcon
    default:
      return InformationCircleIcon
  }
}

const getNotificationStyles = (type: string) => {
  switch (type) {
    case 'success':
      return 'bg-green-50/90 border-green-200 text-green-800'
    case 'warning':
      return 'bg-yellow-50/90 border-yellow-200 text-yellow-800'
    case 'error':
      return 'bg-red-50/90 border-red-200 text-red-800'
    default:
      return 'bg-blue-50/90 border-blue-200 text-blue-800'
  }
}

const getIconColor = (type: string) => {
  switch (type) {
    case 'success':
      return 'text-green-500'
    case 'warning':
      return 'text-yellow-500'
    case 'error':
      return 'text-red-500'
    default:
      return 'text-blue-500'
  }
}

const getTitleColor = (type: string) => {
  switch (type) {
    case 'success':
      return 'text-green-900'
    case 'warning':
      return 'text-yellow-900'
    case 'error':
      return 'text-red-900'
    default:
      return 'text-blue-900'
  }
}

const getMessageColor = (type: string) => {
  switch (type) {
    case 'success':
      return 'text-green-700'
    case 'warning':
      return 'text-yellow-700'
    case 'error':
      return 'text-red-700'
    default:
      return 'text-blue-700'
  }
}

const getFocusColor = (type: string) => {
  switch (type) {
    case 'success':
      return 'focus:ring-green-300'
    case 'warning':
      return 'focus:ring-yellow-300'
    case 'error':
      return 'focus:ring-red-300'
    default:
      return 'focus:ring-blue-300'
  }
}

const formatTime = (timestamp: number) => {
  try {
    return formatDistanceToNow(timestamp, { 
      addSuffix: true,
      locale: zhCN 
    })
  } catch (error) {
    return '刚刚'
  }
}

const getProgressWidth = (notification: any) => {
  if (!notification.duration) return 0
  
  const elapsed = Date.now() - notification.timestamp
  const progress = (elapsed / notification.duration) * 100
  
  return Math.min(100, Math.max(0, progress))
}
</script>

<style scoped>
.notification-enter-active {
  transition: all 0.3s ease-out;
}

.notification-leave-active {
  transition: all 0.3s ease-in;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-move {
  transition: transform 0.3s ease;
}

.notification-card {
  transform-origin: right center;
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

/* 响应式调整 */
@media (max-width: 640px) {
  .notification-card {
    margin-left: 1rem;
    margin-right: 1rem;
  }
}
</style>