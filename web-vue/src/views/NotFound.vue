<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
    <div class="text-center">
      <div class="mb-8">
        <div class="text-6xl font-bold text-gray-300 mb-4">404</div>
        <ExclamationTriangleIcon class="w-24 h-24 mx-auto text-gray-400 mb-4" />
      </div>
      
      <h1 class="text-2xl font-bold text-gray-900 mb-2">页面未找到</h1>
      <p class="text-gray-600 mb-8 max-w-md mx-auto">
        抱歉，您访问的页面不存在。可能是URL输入错误或页面已被移除。
      </p>
      
      <div class="flex justify-center space-x-4">
        <button
          @click="$router.push('/')"
          class="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          返回首页
        </button>
        <button
          @click="$router.go(-1)"
          class="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
        >
          返回上一页
        </button>
      </div>
      
      <div class="mt-8 text-sm text-gray-500">
        如果问题持续存在，请联系技术支持
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
</script>