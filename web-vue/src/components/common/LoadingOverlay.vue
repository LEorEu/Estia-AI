<template>
  <div 
    class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center"
    :class="{ 'animate-fade-in': visible }"
  >
    <div class="bg-white rounded-2xl p-8 shadow-2xl max-w-sm mx-4">
      <div class="flex flex-col items-center">
        <!-- 加载动画 -->
        <div class="relative mb-6">
          <div class="w-16 h-16 border-4 border-gray-200 border-t-primary-500 rounded-full animate-spin"></div>
          <div class="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-primary-300 rounded-full animate-spin animation-delay-150"></div>
        </div>
        
        <!-- 加载文本 -->
        <h3 class="text-lg font-semibold text-gray-800 mb-2">
          {{ title }}
        </h3>
        <p class="text-sm text-gray-600 text-center leading-relaxed">
          {{ message }}
        </p>
        
        <!-- 进度条（可选） -->
        <div v-if="showProgress && progress >= 0" class="w-full mt-4">
          <div class="flex justify-between text-xs text-gray-500 mb-1">
            <span>进度</span>
            <span>{{ Math.round(progress) }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div 
              class="bg-primary-500 h-2 rounded-full transition-all duration-300 ease-out"
              :style="{ width: `${Math.min(100, Math.max(0, progress))}%` }"
            ></div>
          </div>
        </div>
        
        <!-- 取消按钮（可选） -->
        <button 
          v-if="showCancel" 
          @click="handleCancel"
          class="mt-6 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Props {
  title?: string
  message?: string
  progress?: number
  showProgress?: boolean
  showCancel?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '加载中...',
  message: '请稍候，系统正在处理您的请求',
  progress: -1,
  showProgress: false,
  showCancel: false,
})

const emit = defineEmits<{
  cancel: []
}>()

const visible = ref(false)

const handleCancel = () => {
  emit('cancel')
}

onMounted(() => {
  // 延迟显示动画
  setTimeout(() => {
    visible.value = true
  }, 10)
})
</script>

<style scoped>
.animation-delay-150 {
  animation-delay: 150ms;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
</style>