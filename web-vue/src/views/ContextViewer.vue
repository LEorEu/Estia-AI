<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <DashboardHeader />
    
    <main class="container mx-auto px-4 py-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">上下文查看器</h1>
        <p class="text-gray-600">查看完整的对话上下文构建过程，了解系统如何处理用户输入</p>
      </div>
      
      <!-- 会话选择器 -->
      <div class="mb-6">
        <div class="card p-4">
          <div class="flex items-center space-x-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-2">选择会话ID</label>
              <input
                v-model="selectedSessionId"
                @keyup.enter="loadContextData"
                type="text"
                placeholder="输入会话ID (例如: user123_20250123_140500)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div class="flex space-x-2 pt-6">
              <button
                @click="loadContextData"
                :disabled="!selectedSessionId || loading"
                class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="loading">加载中...</span>
                <span v-else>查看上下文</span>
              </button>
              <button
                @click="loadCurrentContext"
                :disabled="loading"
                class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                实时上下文
              </button>
            </div>
          </div>
          <div v-if="error" class="mt-2 text-sm text-red-600">
            {{ error }}
          </div>
        </div>
      </div>

      <!-- 上下文内容 -->
      <div v-if="contextData" class="space-y-6">
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
            <!-- 预处理标签页 -->
            <div v-if="activeTab === 'preprocessing'" class="space-y-4">
              <h3 class="text-lg font-medium text-gray-900">用户输入预处理</h3>
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">处理后的查询文本</label>
                    <div class="p-3 bg-gray-50 rounded-md border">
                      {{ contextData.preprocessing.query_processed || '暂无数据' }}
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">提取的关键词</label>
                    <div class="flex flex-wrap gap-2">
                      <span
                        v-for="keyword in contextData.preprocessing.keywords_extracted"
                        :key="keyword"
                        class="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                      >
                        {{ keyword }}
                      </span>
                      <span v-if="!contextData.preprocessing.keywords_extracted?.length" class="text-gray-500 text-sm">
                        暂无关键词
                      </span>
                    </div>
                  </div>
                </div>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">处理性能</label>
                    <div class="grid grid-cols-2 gap-4">
                      <div class="p-3 bg-green-50 rounded-md">
                        <div class="text-sm text-gray-600">向量维度</div>
                        <div class="text-lg font-semibold text-green-600">
                          {{ contextData.preprocessing.vector_dimension || 0 }}
                        </div>
                      </div>
                      <div class="p-3 bg-blue-50 rounded-md">
                        <div class="text-sm text-gray-600">处理耗时</div>
                        <div class="text-lg font-semibold text-blue-600">
                          {{ formatDuration(contextData.preprocessing.processing_time) }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 记忆检索标签页 -->
            <div v-if="activeTab === 'retrieval'" class="space-y-4">
              <h3 class="text-lg font-medium text-gray-900">记忆检索结果</h3>
              <div class="space-y-6">
                <!-- 检索统计 -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div class="p-4 bg-blue-50 rounded-lg">
                    <div class="text-sm text-gray-600">检索数量</div>
                    <div class="text-2xl font-bold text-blue-600">
                      {{ contextData.memory_retrieval.retrieval_count || 0 }}
                    </div>
                  </div>
                  <div class="p-4 bg-green-50 rounded-lg">
                    <div class="text-sm text-gray-600">平均相似度</div>
                    <div class="text-2xl font-bold text-green-600">
                      {{ (contextData.memory_retrieval.avg_similarity * 100).toFixed(1) }}%
                    </div>
                  </div>
                  <div class="p-4 bg-purple-50 rounded-lg">
                    <div class="text-sm text-gray-600">搜索耗时</div>
                    <div class="text-2xl font-bold text-purple-600">
                      {{ formatDuration(contextData.memory_retrieval.search_time) }}
                    </div>
                  </div>
                </div>

                <!-- 检索到的记忆列表 -->
                <div>
                  <h4 class="font-medium text-gray-800 mb-3">检索到的记忆</h4>
                  <div class="space-y-3">
                    <div
                      v-for="(memory, index) in contextData.memory_retrieval.retrieved_memories"
                      :key="index"
                      class="p-4 bg-white border border-gray-200 rounded-lg"
                    >
                      <div class="flex justify-between items-start mb-2">
                        <span class="text-sm font-medium text-gray-700">记忆 #{{ index + 1 }}</span>
                        <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          相似度: {{ ((contextData.memory_retrieval.similarity_scores?.[index] || 0) * 100).toFixed(1) }}%
                        </span>
                      </div>
                      <div class="text-gray-600 text-sm">{{ memory || '记忆内容不可用' }}</div>
                    </div>
                    <div v-if="!contextData.memory_retrieval.retrieved_memories?.length" class="text-center py-8 text-gray-500">
                      暂无检索到的记忆
                    </div>
                  </div>
                </div>

                <!-- 关联拓展 -->
                <div v-if="contextData.memory_retrieval.associations">
                  <h4 class="font-medium text-gray-800 mb-3">关联网络拓展</h4>
                  <div class="p-4 bg-gray-50 rounded-lg">
                    <div class="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <span class="text-sm text-gray-600">拓展数量:</span>
                        <span class="ml-2 font-medium">{{ contextData.memory_retrieval.associations.association_count || 0 }}</span>
                      </div>
                      <div>
                        <span class="text-sm text-gray-600">平均强度:</span>
                        <span class="ml-2 font-medium">{{ (contextData.memory_retrieval.associations.association_strength * 100).toFixed(1) }}%</span>
                      </div>
                    </div>
                    <div v-if="contextData.memory_retrieval.associations.expanded_memories?.length" class="space-y-2">
                      <div
                        v-for="(memory, index) in contextData.memory_retrieval.associations.expanded_memories"
                        :key="index"
                        class="p-2 bg-white rounded border text-sm"
                      >
                        {{ memory }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 历史聚合标签页 -->
            <div v-if="activeTab === 'history'" class="space-y-4">
              <h3 class="text-lg font-medium text-gray-900">历史对话聚合</h3>
              <div class="space-y-6">
                <!-- 聚合统计 -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="p-4 bg-yellow-50 rounded-lg">
                    <div class="text-sm text-gray-600">历史对话数量</div>
                    <div class="text-2xl font-bold text-yellow-600">
                      {{ contextData.history_aggregation.dialogue_count || 0 }}
                    </div>
                  </div>
                  <div class="p-4 bg-indigo-50 rounded-lg">
                    <div class="text-sm text-gray-600">聚合耗时</div>
                    <div class="text-2xl font-bold text-indigo-600">
                      {{ formatDuration(contextData.history_aggregation.aggregation_time) }}
                    </div>
                  </div>
                </div>

                <!-- 历史对话列表 -->
                <div>
                  <h4 class="font-medium text-gray-800 mb-3">相关历史对话</h4>
                  <div class="space-y-3">
                    <div
                      v-for="(dialogue, index) in contextData.history_aggregation.historical_dialogues"
                      :key="index"
                      class="p-4 bg-white border border-gray-200 rounded-lg"
                    >
                      <div class="flex justify-between items-start mb-2">
                        <span class="text-sm font-medium text-gray-700">对话 #{{ index + 1 }}</span>
                        <span class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                          相关度: {{ ((contextData.history_aggregation.relevance_scores?.[index] || 0) * 100).toFixed(1) }}%
                        </span>
                      </div>
                      <div class="text-gray-600 text-sm">{{ dialogue || '对话内容不可用' }}</div>
                    </div>
                    <div v-if="!contextData.history_aggregation.historical_dialogues?.length" class="text-center py-8 text-gray-500">
                      暂无相关历史对话
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 最终上下文标签页 -->
            <div v-if="activeTab === 'final'" class="space-y-4">
              <h3 class="text-lg font-medium text-gray-900">最终上下文构建</h3>
              <div class="space-y-6">
                <!-- 上下文统计 -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div class="p-3 bg-red-50 rounded-lg">
                    <div class="text-xs text-gray-600">上下文长度</div>
                    <div class="text-lg font-bold text-red-600">
                      {{ contextData.final_context.context_length || 0 }}
                    </div>
                  </div>
                  <div class="p-3 bg-orange-50 rounded-lg">
                    <div class="text-xs text-gray-600">Token数量</div>
                    <div class="text-lg font-bold text-orange-600">
                      {{ contextData.final_context.token_count || 0 }}
                    </div>
                  </div>
                  <div class="p-3 bg-teal-50 rounded-lg">
                    <div class="text-xs text-gray-600">记忆数量</div>
                    <div class="text-lg font-bold text-teal-600">
                      {{ contextData.final_context.memory_count || 0 }}
                    </div>
                  </div>
                  <div class="p-3 bg-pink-50 rounded-lg">
                    <div class="text-xs text-gray-600">构建耗时</div>
                    <div class="text-lg font-bold text-pink-600">
                      {{ formatDuration(contextData.final_context.build_time) }}
                    </div>
                  </div>
                </div>

                <!-- 上下文结构 -->
                <div>
                  <h4 class="font-medium text-gray-800 mb-3">上下文结构</h4>
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">系统提示词</label>
                      <div class="p-3 bg-gray-50 rounded-md border text-sm font-mono">
                        {{ contextData.final_context.context_structure?.system_prompt || '暂无系统提示词' }}
                      </div>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">格式化记忆</label>
                      <div class="p-3 bg-blue-50 rounded-md border max-h-40 overflow-y-auto">
                        <div
                          v-for="(memory, index) in contextData.final_context.context_structure?.retrieved_memories"
                          :key="index"
                          class="text-sm mb-2 pb-2 border-b border-blue-200 last:border-b-0"
                        >
                          {{ memory }}
                        </div>
                        <div v-if="!contextData.final_context.context_structure?.retrieved_memories?.length" class="text-sm text-gray-500">
                          暂无格式化记忆
                        </div>
                      </div>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">历史上下文</label>
                      <div class="p-3 bg-yellow-50 rounded-md border text-sm">
                        {{ contextData.final_context.context_structure?.historical_context || '暂无历史上下文' }}
                      </div>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">用户输入</label>
                      <div class="p-3 bg-green-50 rounded-md border text-sm font-medium">
                        {{ contextData.final_context.context_structure?.user_input || '暂无用户输入' }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 完整上下文 -->
                <div>
                  <h4 class="font-medium text-gray-800 mb-3">完整上下文内容</h4>
                  <div class="p-4 bg-gray-50 rounded-md border max-h-96 overflow-y-auto">
                    <pre class="text-sm text-gray-700 whitespace-pre-wrap">{{ contextData.final_context.complete_context || '暂无完整上下文' }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading" class="text-center py-12">
        <EyeIcon class="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <h2 class="text-xl font-semibold text-gray-700 mb-2">选择一个会话查看上下文</h2>
        <p class="text-gray-600 mb-6">
          输入会话ID或点击"实时上下文"查看当前正在处理的上下文构建过程
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
              <h3 class="text-lg font-semibold text-gray-900">上下文查看器 - 功能预览</h3>
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
                    <span>用户输入预处理展示</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>记忆检索结果详情</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>关联网络拓展展示</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>历史对话聚合</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>最终上下文构建</span>
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
                    <span>数据可视化</span>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '@/stores/notifications'
import { websocketManager, useWebSocket } from '@/services/websocket'
import DashboardHeader from '@/components/layout/DashboardHeader.vue'
import { EyeIcon, XMarkIcon, CheckIcon } from '@heroicons/vue/24/outline'

const notifications = useNotificationStore()
const { connect, isConnected } = useWebSocket()

// 响应式数据
const selectedSessionId = ref('')
const contextData = ref(null)
const loading = ref(false)
const error = ref('')
const activeTab = ref('preprocessing')
const showFeaturePreview = ref(false)

// 标签页定义
const tabs = [
  { id: 'preprocessing', name: '预处理' },
  { id: 'retrieval', name: '记忆检索' }, 
  { id: 'history', name: '历史聚合' },
  { id: 'final', name: '最终上下文' }
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

// 加载会话上下文数据
const loadContextData = async () => {
  if (!selectedSessionId.value.trim()) {
    error.value = '请输入会话ID'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch(`${API_BASE}/session/${selectedSessionId.value}/context`)
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }
    
    const data = await response.json()
    contextData.value = data
    
    notifications.add({
      type: 'success',
      title: '上下文加载成功',
      message: `已加载会话 ${selectedSessionId.value} 的上下文数据`
    })
    
  } catch (err: any) {
    error.value = err.message || '加载失败'
    contextData.value = null
    
    notifications.add({
      type: 'error', 
      title: '加载失败',
      message: error.value
    })
  } finally {
    loading.value = false
  }
}

// 加载当前实时上下文
const loadCurrentContext = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 优先尝试WebSocket实时获取
    if (isConnected()) {
      // 订阅上下文更新
      websocketManager.subscribeContext()
      
      // 设置WebSocket监听器
      websocketManager.on('context_status_update', handleContextWebSocketUpdate)
      
      notifications.add({
        type: 'info',
        title: '已启用实时上下文监控',
        message: '通过WebSocket获取实时上下文更新'
      })
      
      loading.value = false
      return
    }
    
    // 降级到HTTP API
    const response = await fetch(`${API_BASE}/current_context`)
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }
    
    const data = await response.json()
    
    if (!data.active) {
      // 没有活跃会话，显示提示
      notifications.add({
        type: 'info',
        title: '暂无活跃上下文',
        message: data.message || '当前没有正在处理的上下文构建过程'
      })
      contextData.value = null
      return
    }
    
    // 有活跃会话，显示部分上下文
    contextData.value = {
      session_id: data.session_id,
      timestamp: data.timestamp,
      preprocessing: data.partial_context?.preprocessing || {},
      memory_retrieval: data.partial_context?.memory_retrieval || {},
      history_aggregation: {},
      final_context: {}
    }
    
    selectedSessionId.value = data.session_id
    
    notifications.add({
      type: 'success',
      title: '实时上下文加载成功',
      message: `当前正在处理会话: ${data.session_id}`
    })
    
  } catch (err: any) {
    error.value = err.message || '加载实时上下文失败'
    contextData.value = null
    
    notifications.add({
      type: 'error',
      title: '加载失败', 
      message: error.value
    })
  } finally {
    loading.value = false
  }
}

// WebSocket上下文更新处理器
const handleContextWebSocketUpdate = (data: any) => {
  console.log('📝 收到WebSocket上下文更新:', data)
  
  if (!data.active) {
    contextData.value = null
    notifications.add({
      type: 'info',
      title: '上下文状态更新',
      message: data.message || '当前没有活跃的上下文构建过程'
    })
    return
  }
  
  // 更新上下文数据
  contextData.value = {
    session_id: data.session_id,
    timestamp: data.timestamp,
    preprocessing: data.partial_context?.preprocessing || {},
    memory_retrieval: data.partial_context?.memory_retrieval || {},
    history_aggregation: {},
    final_context: {}
  }
  
  selectedSessionId.value = data.session_id
}

// 组件挂载时的初始化
onMounted(async () => {
  console.log('ContextViewer mounted')
  
  // 尝试连接WebSocket
  try {
    await connect()
    console.log('✅ ContextViewer WebSocket连接成功')
  } catch (error) {
    console.warn('⚠️ ContextViewer WebSocket连接失败:', error)
  }
})

onUnmounted(() => {
  // 移除WebSocket监听器
  websocketManager.off('context_status_update', handleContextWebSocketUpdate)
  console.log('ContextViewer unmounted')
})
</script>