<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title flex items-center">
        <component 
          :is="statusIcon" 
          :class="['w-5 h-5 mr-2', statusColor]"
        />
        系统状态
      </h3>
    </div>
    
    <div class="space-y-4">
      <!-- 当前状态 -->
      <div class="flex items-center justify-between">
        <span class="text-gray-600">运行状态</span>
        <span :class="['status-indicator', statusClass]">
          {{ statusText }}
        </span>
      </div>
      
      <!-- 当前会话 -->
      <div class="flex items-center justify-between">
        <span class="text-gray-600">当前会话</span>
        <span class="font-medium text-gray-900">
          {{ currentSessionDisplay }}
        </span>
      </div>
      
      <!-- 运行时间 -->
      <div class="flex items-center justify-between">
        <span class="text-gray-600">运行时间</span>
        <span class="font-medium text-gray-900">
          {{ runningTimeDisplay }}
        </span>
      </div>
      
      <!-- 进度百分比（如果有） -->
      <div 
        v-if="systemStatus?.progress_percentage && systemStatus.progress_percentage > 0" 
        class="space-y-2"
      >
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600">处理进度</span>
          <span class="font-medium text-gray-900">
            {{ Math.round(systemStatus.progress_percentage) }}%
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-primary-500 h-2 rounded-full transition-all duration-500 ease-out"
            :style="{ width: `${systemStatus.progress_percentage}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { formatDuration } from '@/utils/formatters'

// 图标导入
import {
  PlayIcon,
  PauseIcon,
  ExclamationTriangleIcon,
  WifiIcon
} from '@heroicons/vue/24/outline'

const monitoringStore = useMonitoringStore()

// 计算属性
const systemStatus = computed(() => monitoringStore.systemStatus)

const statusIcon = computed(() => {
  if (!systemStatus.value) return WifiIcon
  
  switch (systemStatus.value.status) {
    case 'running':
      return PlayIcon
    case 'idle':
      return PauseIcon
    case 'error':
      return ExclamationTriangleIcon
    default:
      return WifiIcon
  }
})

const statusColor = computed(() => {
  if (!systemStatus.value) return 'text-gray-500'
  
  switch (systemStatus.value.status) {
    case 'running':
      return 'text-green-500'
    case 'idle':
      return 'text-gray-500'
    case 'error':
      return 'text-red-500'
    default:
      return 'text-gray-500'
  }
})

const statusClass = computed(() => {
  if (!systemStatus.value) return 'status-idle'
  
  switch (systemStatus.value.status) {
    case 'running':
      return 'status-running'
    case 'idle':
      return 'status-idle'
    case 'error':
      return 'status-error'
    default:
      return 'status-idle'
  }
})

const statusText = computed(() => {
  if (!systemStatus.value) return '离线'
  
  switch (systemStatus.value.status) {
    case 'running':
      return '运行中'
    case 'idle':
      return '空闲'
    case 'error':
      return '错误'
    case 'offline':
      return '离线'
    default:
      return '未知'
  }
})

const currentSessionDisplay = computed(() => {
  if (!systemStatus.value?.session_id) {
    return '无'
  }
  
  const sessionId = systemStatus.value.session_id
  // 显示会话ID的前8位
  return sessionId.length > 8 ? `${sessionId.substring(0, 8)}...` : sessionId
})

const runningTimeDisplay = computed(() => {
  if (!systemStatus.value?.running_time) {
    return '0秒'
  }
  
  return formatDuration(systemStatus.value.running_time)
})
</script>