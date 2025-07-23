<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title flex items-center">
        <BoltIcon class="w-5 h-5 mr-2 text-primary-500" />
        快速操作
      </h3>
    </div>
    
    <div class="space-y-3">
      <button
        @click="refreshData"
        :disabled="isRefreshing"
        class="w-full flex items-center justify-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 transition-colors"
      >
        <ArrowPathIcon :class="['w-4 h-4 mr-2', { 'animate-spin': isRefreshing }]" />
        {{ isRefreshing ? '刷新中...' : '刷新数据' }}
      </button>
      
      <button
        @click="exportData"
        :disabled="isExporting"
        class="w-full flex items-center justify-center px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 transition-colors"
      >
        <DocumentArrowDownIcon :class="['w-4 h-4 mr-2', { 'animate-pulse': isExporting }]" />
        {{ isExporting ? '导出中...' : '导出数据' }}
      </button>
      
      <button
        @click="clearData"
        class="w-full flex items-center justify-center px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
      >
        <TrashIcon class="w-4 h-4 mr-2" />
        清空数据
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { useAppStore } from '@/stores/app'
import {
  BoltIcon,
  ArrowPathIcon,
  DocumentArrowDownIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const monitoringStore = useMonitoringStore()
const appStore = useAppStore()

const isRefreshing = ref(false)
const isExporting = ref(false)

const refreshData = async () => {
  if (isRefreshing.value) return
  
  try {
    isRefreshing.value = true
    await monitoringStore.fetchDashboardData()
    
    appStore.addNotification({
      type: 'success',
      title: '刷新成功',
      message: '数据已更新',
      duration: 2000
    })
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      title: '刷新失败',
      message: '无法获取最新数据',
      duration: 3000
    })
  } finally {
    isRefreshing.value = false
  }
}

const exportData = async () => {
  if (isExporting.value) return
  
  try {
    isExporting.value = true
    
    // 模拟导出过程
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    appStore.addNotification({
      type: 'success',
      title: '导出成功',
      message: '数据已导出到下载目录',
      duration: 3000
    })
  } catch (error) {
    appStore.addNotification({
      type: 'error',
      title: '导出失败',
      message: '无法导出数据',
      duration: 3000
    })
  } finally {
    isExporting.value = false
  }
}

const clearData = () => {
  if (confirm('确定要清空所有监控数据吗？此操作不可撤销。')) {
    monitoringStore.reset()
    
    appStore.addNotification({
      type: 'info',
      title: '数据已清空',
      message: '所有监控数据已重置',
      duration: 3000
    })
  }
}
</script>