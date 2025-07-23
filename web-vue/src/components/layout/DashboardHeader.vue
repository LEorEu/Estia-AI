<template>
  <header class="bg-white/90 backdrop-blur-sm shadow-sm border-b border-gray-200">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo和标题 -->
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
              <CpuChipIcon class="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900">Estia AI</h1>
              <p class="text-xs text-gray-600">记忆监控仪表板</p>
            </div>
          </div>
        </div>

        <!-- 导航菜单 -->
        <nav class="hidden md:flex items-center space-x-6">
          <router-link
            to="/"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'Dashboard' }"
          >
            概览
          </router-link>
          <router-link
            to="/context"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'Context' }"
          >
            上下文
          </router-link>
          <router-link
            to="/evaluation"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'Evaluation' }"
          >
            评估
          </router-link>
          <router-link
            to="/pipeline"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === 'Pipeline' }"
          >
            流程
          </router-link>
        </nav>

        <!-- 状态指示器和操作 -->
        <div class="flex items-center space-x-4">
          <!-- 连接状态 -->
          <div class="flex items-center space-x-2">
            <div :class="['w-2 h-2 rounded-full', connectionStatusColor]"></div>
            <span class="text-sm text-gray-600">{{ connectionStatusText }}</span>
          </div>

          <!-- 刷新按钮 -->
          <button
            @click="handleRefresh"
            :disabled="isRefreshing"
            class="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="刷新数据"
          >
            <ArrowPathIcon :class="['w-5 h-5', { 'animate-spin': isRefreshing }]" />
          </button>

          <!-- 通知按钮 -->
          <button
            @click="showNotifications = !showNotifications"
            class="relative p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="通知"
          >
            <BellIcon class="w-5 h-5" />
            <span
              v-if="unreadNotifications > 0"
              class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center"
            >
              {{ unreadNotifications > 9 ? '9+' : unreadNotifications }}
            </span>
          </button>

          <!-- 移动端菜单按钮 -->
          <button
            @click="showMobileMenu = !showMobileMenu"
            class="md:hidden p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Bars3Icon v-if="!showMobileMenu" class="w-5 h-5" />
            <XMarkIcon v-else class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- 移动端导航菜单 -->
      <div v-if="showMobileMenu" class="md:hidden border-t border-gray-200 py-4">
        <nav class="space-y-2">
          <router-link
            to="/"
            class="mobile-nav-link"
            :class="{ 'mobile-nav-link-active': $route.name === 'Dashboard' }"
            @click="showMobileMenu = false"
          >
            概览
          </router-link>
          <router-link
            to="/context"
            class="mobile-nav-link"
            :class="{ 'mobile-nav-link-active': $route.name === 'Context' }"
            @click="showMobileMenu = false"
          >
            上下文查看器
          </router-link>
          <router-link
            to="/evaluation"
            class="mobile-nav-link"
            :class="{ 'mobile-nav-link-active': $route.name === 'Evaluation' }"
            @click="showMobileMenu = false"
          >
            异步评估
          </router-link>
          <router-link
            to="/pipeline"
            class="mobile-nav-link"
            :class="{ 'mobile-nav-link-active': $route.name === 'Pipeline' }"
            @click="showMobileMenu = false"
          >
            流程可视化
          </router-link>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { useAppStore } from '@/stores/app'
import {
  CpuChipIcon,
  ArrowPathIcon,
  BellIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const monitoringStore = useMonitoringStore()
const appStore = useAppStore()

const showMobileMenu = ref(false)
const showNotifications = ref(false)
const isRefreshing = ref(false)

// 计算属性
const connectionStatusText = computed(() => monitoringStore.connectionStatusText)
const connectionStatusColor = computed(() => {
  const colorMap: Record<string, string> = {
    'text-green-500': 'bg-green-500',
    'text-yellow-500': 'bg-yellow-500',
    'text-red-500': 'bg-red-500',
    'text-gray-500': 'bg-gray-500',
  }
  
  return colorMap[monitoringStore.connectionStatusColor] || 'bg-gray-500'
})

const unreadNotifications = computed(() => appStore.notifications.length)

// 方法
const handleRefresh = async () => {
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
      duration: 5000
    })
  } finally {
    isRefreshing.value = false
  }
}
</script>

<style scoped>
.nav-link {
  @apply px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors;
}

.nav-link-active {
  @apply text-primary-600 bg-primary-50;
}

.mobile-nav-link {
  @apply block px-3 py-2 text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors;
}

.mobile-nav-link-active {
  @apply text-primary-600 bg-primary-50;
}
</style>