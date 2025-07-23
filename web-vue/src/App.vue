<template>
  <div id="app" class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <router-view />
    
    <!-- 全局加载指示器 -->
    <LoadingOverlay v-if="appStore.isLoading" />
    
    <!-- 全局通知系统 -->
    <NotificationSystem />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import LoadingOverlay from '@/components/common/LoadingOverlay.vue'
import NotificationSystem from '@/components/common/NotificationSystem.vue'

const appStore = useAppStore()

onMounted(() => {
  // 应用初始化
  appStore.initialize()
})
</script>

<style>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>