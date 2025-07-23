<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <DashboardHeader />
    
    <main class="container mx-auto px-4 py-6">
      <div class="mb-6">
        <button
          @click="$router.go(-1)"
          class="flex items-center space-x-2 text-gray-600 hover:text-gray-800 mb-4"
        >
          <ArrowLeftIcon class="w-4 h-4" />
          <span>返回</span>
        </button>
        
        <h1 class="text-2xl font-bold text-gray-900 mb-2">会话详情</h1>
        <p class="text-gray-600">{{ sessionId }}</p>
      </div>
      
      <!-- 功能开发中提示 -->
      <div class="card text-center py-12">
        <DocumentTextIcon class="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <h2 class="text-xl font-semibold text-gray-700 mb-2">会话详情页面开发中</h2>
        <p class="text-gray-600 mb-6 max-w-2xl mx-auto">
          此页面将提供指定会话的详细信息，包括完整的对话记录、性能统计、
          错误日志和相关分析等内容。
        </p>
        
        <button
          @click="$router.push('/')"
          class="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          返回仪表板
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DashboardHeader from '@/components/layout/DashboardHeader.vue'
import { ArrowLeftIcon, DocumentTextIcon } from '@heroicons/vue/24/outline'

const route = useRoute()

const sessionId = computed(() => {
  return route.params.sessionId as string
})
</script>