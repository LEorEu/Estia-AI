<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <DashboardHeader />
    
    <main class="container mx-auto px-4 py-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">异步评估展示</h1>
        <p class="text-gray-600">监控异步评估过程和结果，了解系统如何评价对话质量</p>
      </div>
      
      <!-- 会话选择器 -->
      <div class="mb-6">
        <div class="card p-4">
          <div class="flex items-center space-x-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-2">选择会话ID</label>
              <input
                v-model="selectedSessionId"
                @keyup.enter="loadEvaluationData"
                type="text"
                placeholder="输入会话ID (例如: user123_20250123_140500)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div class="flex space-x-2 pt-6">
              <button
                @click="loadEvaluationData"
                :disabled="!selectedSessionId || loading"
                class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="loading">加载中...</span>
                <span v-else>查看评估</span>
              </button>
            </div>
          </div>
          <div v-if="error" class="mt-2 text-sm text-red-600">
            {{ error }}
          </div>
        </div>
      </div>

      <!-- 评估内容 -->
      <div v-if="evaluationData" class="space-y-6">
        <!-- 标签页导航 -->
        <div class="card">
          <div class="border-b border-gray-200">
            <nav class="-mb-px flex space-x-8">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                :class="[
                  'py-2 px-1 border-b-2 font-medium text-sm',
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                {{ tab.name }}
              </button>
            </nav>
          </div>
          
          <div class="p-6">
            <!-- 评估上下文标签页 -->
            <div v-if="activeTab === 'context'" class="space-y-4">
              <h3 class="text-lg font-medium text-gray-900">评估上下文构建</h3>
              <div class="space-y-6">
                <!-- 评估基本信息 -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">用户输入</label>
                      <div class="p-3 bg-blue-50 rounded-md border">
                        {{ evaluationData.evaluation_context.user_input || '暂无数据' }}
                      </div>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">AI回复</label>
                      <div class="p-3 bg-green-50 rounded-md border max-h-32 overflow-y-auto">
                        {{ evaluationData.evaluation_context.assistant_response || '暂无数据' }}
                      </div>
                    </div>
                  </div>
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">评估配置</label>
                      <div class="grid grid-cols-2 gap-4">
                        <div class="p-3 bg-gray-50 rounded-md">
                          <div class="text-sm text-gray-600">使用模型</div>
                          <div class="text-lg font-semibold text-gray-800">
                            {{ evaluationData.evaluation_context.model_used || '未知' }}
                          </div>
                        </div>
                        <div class="p-3 bg-purple-50 rounded-md">
                          <div class="text-sm text-gray-600">评估耗时</div>
                          <div class="text-lg font-semibold text-purple-600">
                            {{ formatDuration(evaluationData.evaluation_context.evaluation_time) }}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">评估提示词</label>
                      <div class="p-3 bg-yellow-50 rounded-md border max-h-32 overflow-y-auto text-sm font-mono">
                        {{ evaluationData.evaluation_context.evaluation_prompt || '暂无评估提示词' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 评估结果标签页 -->
            <div v-if="activeTab === 'results'" class="space-y-4">
              <h3 class="text-lg font-medium text-gray-900">评估结果详情</h3>
              <div class="space-y-6">
                <!-- 重要性评分 -->
                <div class="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                  <div class="flex items-center justify-between mb-4">
                    <h4 class="text-lg font-medium text-gray-800">记忆重要性评分</h4>
                    <div class="text-3xl font-bold text-blue-600">
                      {{ evaluationData.evaluation_results.importance_score || 0 }}/10
                    </div>
                  </div>
                  <div class="mb-4">
                    <!-- 评分可视化条 -->
                    <div class="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        class="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500"
                        :style="{ width: `${(evaluationData.evaluation_results.importance_score || 0) * 10}%` }"
                      ></div>
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">评分理由</label>
                    <div class="text-sm text-gray-700 bg-white p-3 rounded-md border">
                      {{ evaluationData.evaluation_results.importance_reason || '暂无评分理由' }}
                    </div>
                  </div>
                </div>

                <!-- 情感分析 -->
                <div class="p-4 bg-pink-50 rounded-lg border border-pink-200">
                  <h4 class="font-medium text-gray-800 mb-3">情感分析</h4>
                  <div v-if="evaluationData.evaluation_results.emotion_analysis && Object.keys(evaluationData.evaluation_results.emotion_analysis).length">
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div
                        v-for="(value, emotion) in evaluationData.evaluation_results.emotion_analysis"
                        :key="emotion"
                        class="text-center"
                      >
                        <div class="text-2xl mb-1">
                          {{ getEmotionEmoji(emotion) }}
                        </div>
                        <div class="text-xs text-gray-600 capitalize">{{ emotion }}</div>
                        <div class="text-sm font-medium">{{ (value * 100).toFixed(1) }}%</div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-sm text-gray-500 text-center py-4">
                    暂无情感分析数据
                  </div>
                </div>

                <!-- 主题标签 -->
                <div>
                  <h4 class="font-medium text-gray-800 mb-3">主题标签</h4>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="tag in evaluationData.evaluation_results.topic_tags"
                      :key="tag"
                      class="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full border border-green-200"
                    >
                      #{{ tag }}
                    </span>
                    <span v-if="!evaluationData.evaluation_results.topic_tags?.length" class="text-gray-500 text-sm">
                      暂无主题标签
                    </span>
                  </div>
                </div>

                <!-- 知识提取 -->
                <div>
                  <h4 class="font-medium text-gray-800 mb-3">知识提取</h4>
                  <div class="space-y-2">
                    <div
                      v-for="(knowledge, index) in evaluationData.evaluation_results.knowledge_extracted"
                      :key="index"
                      class="p-3 bg-yellow-50 rounded-md border border-yellow-200 text-sm"
                    >
                      <div class="flex items-start space-x-2">
                        <div class="w-5 h-5 bg-yellow-500 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0 mt-0.5">
                          {{ index + 1 }}
                        </div>
                        <div>{{ knowledge }}</div>
                      </div>
                    </div>
                    <div v-if="!evaluationData.evaluation_results.knowledge_extracted?.length" class="text-center py-8 text-gray-500">
                      暂无提取的知识
                    </div>
                  </div>
                </div>

                <!-- 关联建议 -->
                <div>
                  <h4 class="font-medium text-gray-800 mb-3">关联建议</h4>
                  <div class="space-y-2">
                    <div
                      v-for="(suggestion, index) in evaluationData.evaluation_results.association_suggestions"
                      :key="index"
                      class="p-3 bg-indigo-50 rounded-md border border-indigo-200 text-sm"
                    >
                      <div class="flex items-start space-x-2">
                        <div class="w-5 h-5 bg-indigo-500 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0 mt-0.5">
                          💡
                        </div>
                        <div>{{ suggestion }}</div>
                      </div>
                    </div>
                    <div v-if="!evaluationData.evaluation_results.association_suggestions?.length" class="text-center py-8 text-gray-500">
                      暂无关联建议
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 关联创建标签页 -->
            <div v-if="activeTab === 'associations'" class="space-y-4">
              <h3 class="text-lg font-medium text-gray-900">自动关联创建</h3>
              <div class="space-y-6">
                <!-- 关联统计 -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div class="p-4 bg-teal-50 rounded-lg">
                    <div class="text-sm text-gray-600">新建关联数</div>
                    <div class="text-2xl font-bold text-teal-600">
                      {{ evaluationData.association_creation.association_count || 0 }}
                    </div>
                  </div>
                  <div class="p-4 bg-orange-50 rounded-lg">
                    <div class="text-sm text-gray-600">关联类型数</div>
                    <div class="text-2xl font-bold text-orange-600">
                      {{ evaluationData.association_creation.association_types?.length || 0 }}
                    </div>
                  </div>
                  <div class="p-4 bg-purple-50 rounded-lg">
                    <div class="text-sm text-gray-600">创建耗时</div>
                    <div class="text-2xl font-bold text-purple-600">
                      {{ formatDuration(evaluationData.association_creation.creation_time) }}
                    </div>
                  </div>
                </div>

                <!-- 关联类型 -->
                <div v-if="evaluationData.association_creation.association_types?.length">
                  <h4 class="font-medium text-gray-800 mb-3">关联类型</h4>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="type in evaluationData.association_creation.association_types"
                      :key="type"
                      class="px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full border border-orange-200"
                    >
                      {{ type }}
                    </span>
                  </div>
                </div>

                <!-- 新建关联列表 -->
                <div>
                  <h4 class="font-medium text-gray-800 mb-3">新建关联</h4>
                  <div class="space-y-3">
                    <div
                      v-for="(association, index) in evaluationData.association_creation.new_associations"
                      :key="index"
                      class="p-4 bg-white border border-gray-200 rounded-lg"
                    >
                      <div class="flex justify-between items-start mb-2">
                        <span class="text-sm font-medium text-gray-700">关联 #{{ index + 1 }}</span>
                        <span class="px-2 py-1 bg-teal-100 text-teal-800 text-xs rounded-full">
                          {{ association.type || '未知类型' }}
                        </span>
                      </div>
                      <div class="text-gray-600 text-sm">
                        <div><strong>源:</strong> {{ association.source || '未知' }}</div>
                        <div><strong>目标:</strong> {{ association.target || '未知' }}</div>
                        <div v-if="association.strength"><strong>强度:</strong> {{ (association.strength * 100).toFixed(1) }}%</div>
                      </div>
                    </div>
                    <div v-if="!evaluationData.association_creation.new_associations?.length" class="text-center py-8 text-gray-500">
                      暂无新建关联
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading" class="text-center py-12">
        <ChartBarIcon class="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <h2 class="text-xl font-semibold text-gray-700 mb-2">选择一个会话查看评估结果</h2>
        <p class="text-gray-600 mb-6">
          输入会话ID查看完整的异步评估过程和结果
        </p>
      </div>
    </main>
    
    <!-- 功能预览模态框 -->
    <div v-if="showFeaturePreview" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" @click="showFeaturePreview = false"></div>
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="relative w-full max-w-4xl bg-white rounded-xl shadow-2xl">
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">异步评估展示 - 功能预览</h3>
              <button @click="showFeaturePreview = false" class="text-gray-400 hover:text-gray-600">
                <XMarkIcon class="w-6 h-6" />
              </button>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <h4 class="font-medium text-gray-800">核心功能</h4>
                <ul class="space-y-2 text-sm text-gray-600">
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>评估触发条件监控</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>评估上下文构建展示</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>评估结果详情</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>自动关联创建</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>评估历史记录</span>
                  </li>
                </ul>
              </div>
              
              <div class="space-y-4">
                <h4 class="font-medium text-gray-800">预计开发时间</h4>
                <div class="text-sm text-gray-600 space-y-2">
                  <div class="flex justify-between">
                    <span>后端API扩展</span>
                    <span>2-3天</span>
                  </div>
                  <div class="flex justify-between">
                    <span>前端组件开发</span>
                    <span>2-3天</span>
                  </div>
                  <div class="flex justify-between">
                    <span>实时数据展示</span>
                    <span>1-2天</span>
                  </div>
                  <div class="flex justify-between border-t pt-2 font-medium">
                    <span>总计</span>
                    <span>5-8天</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import DashboardHeader from '@/components/layout/DashboardHeader.vue'
import { ChartBarIcon, XMarkIcon, CheckIcon } from '@heroicons/vue/24/outline'

const notifications = useNotificationStore()

// 响应式数据
const selectedSessionId = ref('')
const evaluationData = ref(null)
const loading = ref(false)
const error = ref('')
const activeTab = ref('context')
const showFeaturePreview = ref(false)

// 标签页定义
const tabs = [
  { id: 'context', name: '评估上下文' },
  { id: 'results', name: '评估结果' },
  { id: 'associations', name: '关联创建' }
]

// API基础URL
const API_BASE = 'http://localhost:5000/api'

// 工具函数
const formatDuration = (duration: number | null | undefined): string => {
  if (!duration && duration !== 0) return '未知'
  if (duration < 0.001) return '<1ms'
  if (duration < 1) return `${(duration * 1000).toFixed(1)}ms`
  return `${duration.toFixed(3)}s`
}

// 获取情感emoji
const getEmotionEmoji = (emotion: string): string => {
  const emotionMap: { [key: string]: string } = {
    'joy': '😊',
    'sadness': '😢',
    'anger': '😠',
    'fear': '😨',
    'surprise': '😮',
    'disgust': '🤢',
    'positive': '😊',
    'negative': '😔',
    'neutral': '😐',
    'happy': '😄',
    'excited': '🤩',
    'calm': '😌',
    'confused': '😕',
    'frustrated': '😤'
  }
  return emotionMap[emotion.toLowerCase()] || '😐'
}

// 加载评估数据
const loadEvaluationData = async () => {
  if (!selectedSessionId.value.trim()) {
    error.value = '请输入会话ID'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch(`${API_BASE}/session/${selectedSessionId.value}/evaluation`)
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }
    
    const data = await response.json()
    evaluationData.value = data
    
    notifications.add({
      type: 'success',
      title: '评估数据加载成功',
      message: `已加载会话 ${selectedSessionId.value} 的评估数据`
    })
    
  } catch (err: any) {
    error.value = err.message || '加载失败'
    evaluationData.value = null
    
    notifications.add({
      type: 'error',
      title: '加载失败',
      message: error.value
    })
  } finally {
    loading.value = false
  }
}

// 组件挂载时的初始化
onMounted(() => {
  console.log('EvaluationViewer mounted')
})
</script>