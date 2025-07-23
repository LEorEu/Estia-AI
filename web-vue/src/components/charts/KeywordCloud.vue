<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title flex items-center">
        <HashtagIcon class="w-5 h-5 mr-2 text-primary-500" />
        关键词分析
      </h3>
      <div class="text-xs text-gray-500">
        {{ totalKeywords }} 个关键词
      </div>
    </div>
    
    <div class="relative h-64">
      <!-- 关键词云 -->
      <div v-if="hasKeywords" class="h-full flex flex-wrap content-center justify-center p-4 space-x-2 space-y-2 overflow-hidden">
        <span
          v-for="(keyword, index) in displayKeywords"
          :key="keyword.word"
          :class="[
            'inline-block px-3 py-1 rounded-full transition-all duration-300 cursor-pointer hover:scale-110',
            getKeywordClass(keyword.frequency),
            'animate-fade-in'
          ]"
          :style="{
            fontSize: getKeywordSize(keyword.frequency),
            animationDelay: `${index * 100}ms`
          }"
          @click="selectKeyword(keyword)"
          :title="`出现 ${keyword.count} 次，频率 ${(keyword.frequency * 100).toFixed(1)}%`"
        >
          {{ keyword.word }}
        </span>
      </div>
      
      <!-- 无数据状态 -->
      <div v-else class="h-full flex items-center justify-center">
        <div class="text-center text-gray-500">
          <HashtagIcon class="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p class="text-sm">暂无关键词数据</p>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div 
        v-if="isLoading" 
        class="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm"
      >
        <div class="flex items-center space-x-2 text-gray-600">
          <div class="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-sm">分析中...</span>
        </div>
      </div>
    </div>
    
    <!-- 关键词统计 -->
    <div class="mt-4 pt-4 border-t border-gray-200">
      <div class="flex items-center justify-between mb-3">
        <span class="text-sm font-medium text-gray-700">热门关键词</span>
        <button
          @click="refreshKeywords"
          :disabled="isRefreshing"
          class="text-xs text-primary-600 hover:text-primary-700 disabled:opacity-50"
        >
          {{ isRefreshing ? '刷新中...' : '刷新' }}
        </button>
      </div>
      
      <div class="space-y-2">
        <div
          v-for="(keyword, index) in topKeywords"
          :key="keyword.word"
          class="flex items-center justify-between text-sm"
        >
          <div class="flex items-center space-x-2">
            <span class="w-4 h-4 text-xs bg-gray-100 rounded-full flex items-center justify-center">
              {{ index + 1 }}
            </span>
            <span class="text-gray-700">{{ keyword.word }}</span>
          </div>
          
          <div class="flex items-center space-x-2">
            <div class="w-16 bg-gray-200 rounded-full h-1.5">
              <div 
                class="bg-primary-500 h-1.5 rounded-full transition-all duration-500"
                :style="{ width: `${(keyword.frequency / maxFrequency) * 100}%` }"
              ></div>
            </div>
            <span class="text-xs text-gray-500 w-8 text-right">{{ keyword.count }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 选中关键词详情 -->
    <div v-if="selectedKeyword" class="mt-4 p-3 bg-blue-50 rounded-lg">
      <div class="flex items-center justify-between mb-2">
        <h4 class="font-medium text-blue-900">{{ selectedKeyword.word }}</h4>
        <button
          @click="selectedKeyword = null"
          class="text-blue-600 hover:text-blue-800"
        >
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
      <div class="text-sm text-blue-700 space-y-1">
        <div>出现次数: {{ selectedKeyword.count }}</div>
        <div>出现频率: {{ (selectedKeyword.frequency * 100).toFixed(1) }}%</div>
        <div>相关度: {{ getRelevanceLevel(selectedKeyword.frequency) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { HashtagIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import type { KeywordData } from '@/types'

const monitoringStore = useMonitoringStore()

const isLoading = ref(false)
const isRefreshing = ref(false)
const selectedKeyword = ref<KeywordData | null>(null)

// 模拟关键词数据
const mockKeywords = ref<KeywordData[]>([
  { word: '监控', count: 45, frequency: 0.8 },
  { word: '性能', count: 38, frequency: 0.68 },
  { word: '数据', count: 32, frequency: 0.57 },
  { word: '系统', count: 28, frequency: 0.5 },
  { word: '实时', count: 25, frequency: 0.45 },
  { word: '分析', count: 22, frequency: 0.39 },
  { word: '会话', count: 20, frequency: 0.36 },
  { word: '缓存', count: 18, frequency: 0.32 },
  { word: '优化', count: 15, frequency: 0.27 },
  { word: '响应', count: 12, frequency: 0.21 },
  { word: '查询', count: 10, frequency: 0.18 },
  { word: '记忆', count: 8, frequency: 0.14 },
  { word: '流程', count: 6, frequency: 0.11 },
  { word: '评估', count: 5, frequency: 0.09 },
  { word: '上下文', count: 4, frequency: 0.07 }
])

// 计算属性
const keywords = computed(() => {
  return monitoringStore.keywords?.top_keywords || mockKeywords.value
})

const hasKeywords = computed(() => keywords.value.length > 0)

const totalKeywords = computed(() => {
  return monitoringStore.keywords?.total_unique_keywords || keywords.value.length
})

const displayKeywords = computed(() => {
  return keywords.value.slice(0, 15) // 最多显示15个关键词
})

const topKeywords = computed(() => {
  return keywords.value.slice(0, 8) // 显示前8个关键词的统计
})

const maxFrequency = computed(() => {
  return Math.max(...keywords.value.map(k => k.frequency))
})

// 方法
const getKeywordSize = (frequency: number): string => {
  const baseSize = 12
  const maxSize = 20
  const size = baseSize + (frequency * (maxSize - baseSize))
  return `${Math.round(size)}px`
}

const getKeywordClass = (frequency: number): string => {
  if (frequency >= 0.6) {
    return 'bg-red-100 text-red-800 hover:bg-red-200'
  } else if (frequency >= 0.4) {
    return 'bg-orange-100 text-orange-800 hover:bg-orange-200'
  } else if (frequency >= 0.2) {
    return 'bg-blue-100 text-blue-800 hover:bg-blue-200'
  } else {
    return 'bg-gray-100 text-gray-800 hover:bg-gray-200'
  }
}

const getRelevanceLevel = (frequency: number): string => {
  if (frequency >= 0.6) return '高'
  if (frequency >= 0.3) return '中'
  return '低'
}

const selectKeyword = (keyword: KeywordData) => {
  selectedKeyword.value = keyword
}

const refreshKeywords = async () => {
  if (isRefreshing.value) return
  
  try {
    isRefreshing.value = true
    
    // 模拟数据刷新
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟关键词数据更新
    mockKeywords.value = mockKeywords.value.map(keyword => ({
      ...keyword,
      count: keyword.count + Math.floor(Math.random() * 5),
      frequency: Math.min(1, keyword.frequency + (Math.random() - 0.5) * 0.1)
    }))
    
    // 按频率重新排序
    mockKeywords.value.sort((a, b) => b.frequency - a.frequency)
    
  } finally {
    isRefreshing.value = false
  }
}

onMounted(() => {
  // 初始化时可以从监控存储中获取真实数据
  if (!hasKeywords.value) {
    // 使用模拟数据
    console.log('使用模拟关键词数据')
  }
})
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out forwards;
  opacity: 0;
}

/* 关键词悬停效果 */
.keyword-cloud span:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px) scale(1.05);
}

/* 进度条动画 */
.h-1\.5 {
  transition: width 0.5s ease-in-out;
}
</style>