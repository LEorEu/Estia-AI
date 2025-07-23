<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <DashboardHeader />
    
    <main class="container mx-auto px-4 py-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">15步流程可视化</h1>
        <p class="text-gray-600">实时监控记忆处理流程，了解每个步骤的执行状态和性能</p>
      </div>
      
      <!-- 控制面板 -->
      <div class="mb-6">
        <div class="card p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="flex items-center space-x-2">
                <div :class="[
                  'w-3 h-3 rounded-full',
                  loading ? 'bg-yellow-500 animate-pulse' : 
                  pipelineData ? 'bg-green-500' : 'bg-red-500'
                ]"></div>
                <span class="text-sm font-medium">
                  {{ loading ? '加载中...' : pipelineData ? '数据已连接' : '连接失败' }}
                </span>
              </div>
              <div v-if="pipelineData" class="text-sm text-gray-600">
                活跃会话: {{ pipelineData.active_sessions }}
              </div>
            </div>
            <div class="flex space-x-2">
              <button
                @click="loadPipelineData"
                :disabled="loading"
                class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 transition-colors"
              >
                {{ loading ? '刷新中...' : '刷新数据' }}
              </button>
              <button
                @click="toggleAutoRefresh"
                :class="[
                  'px-4 py-2 rounded-md transition-colors',
                  autoRefresh ? 'bg-green-500 hover:bg-green-600 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                ]"
              >
                {{ autoRefresh ? '自动刷新: 开' : '自动刷新: 关' }}
              </button>
            </div>
          </div>
          <div v-if="error" class="mt-2 text-sm text-red-600">
            {{ error }}
          </div>
        </div>
      </div>

      <!-- 流程可视化 -->
      <div v-if="pipelineData" class="space-y-6">
        <!-- 三阶段概览 -->
        <div class="card p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">三阶段流程概览</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- 初始化阶段 -->
            <div class="text-center">
              <div class="mb-3">
                <div class="mx-auto w-20 h-20 rounded-full border-4 border-gray-200 flex items-center justify-center relative">
                  <div 
                    :class="[
                      'absolute inset-0 rounded-full transition-all duration-500',
                      getPhaseColor('initialization')
                    ]"
                    :style="{ 
                      background: `conic-gradient(${getPhaseColor('initialization')} ${pipelineData.phase_status.initialization.progress}%, transparent 0%)` 
                    }"
                  ></div>
                  <div class="bg-white rounded-full w-14 h-14 flex items-center justify-center z-10">
                    <CpuChipIcon class="w-6 h-6 text-gray-600" />
                  </div>
                </div>
              </div>
              <h4 class="font-medium text-gray-800">系统初始化</h4>
              <p class="text-sm text-gray-600">Steps 1-3</p>
              <div class="mt-2">
                <span :class="[
                  'px-2 py-1 text-xs rounded-full',
                  getPhaseStatusClass(pipelineData.phase_status.initialization.status)
                ]">
                  {{ getPhaseStatusText(pipelineData.phase_status.initialization.status) }}
                </span>
              </div>
            </div>

            <!-- 查询增强阶段 -->
            <div class="text-center">
              <div class="mb-3">
                <div class="mx-auto w-20 h-20 rounded-full border-4 border-gray-200 flex items-center justify-center relative">
                  <div 
                    :class="[
                      'absolute inset-0 rounded-full transition-all duration-500'
                    ]"
                    :style="{ 
                      background: `conic-gradient(${getPhaseColor('query_enhancement')} ${pipelineData.phase_status.query_enhancement.progress}%, transparent 0%)` 
                    }"
                  ></div>
                  <div class="bg-white rounded-full w-14 h-14 flex items-center justify-center z-10">
                    <MagnifyingGlassIcon class="w-6 h-6 text-gray-600" />
                  </div>
                </div>
              </div>
              <h4 class="font-medium text-gray-800">实时记忆增强</h4>
              <p class="text-sm text-gray-600">Steps 4-9</p>
              <div class="mt-2">
                <span :class="[
                  'px-2 py-1 text-xs rounded-full',
                  getPhaseStatusClass(pipelineData.phase_status.query_enhancement.status)
                ]">
                  {{ getPhaseStatusText(pipelineData.phase_status.query_enhancement.status) }}
                </span>
              </div>
            </div>

            <!-- 存储评估阶段 -->
            <div class="text-center">
              <div class="mb-3">
                <div class="mx-auto w-20 h-20 rounded-full border-4 border-gray-200 flex items-center justify-center relative">
                  <div 
                    :class="[
                      'absolute inset-0 rounded-full transition-all duration-500'
                    ]"
                    :style="{ 
                      background: `conic-gradient(${getPhaseColor('storage_evaluation')} ${pipelineData.phase_status.storage_evaluation.progress}%, transparent 0%)` 
                    }"
                  ></div>
                  <div class="bg-white rounded-full w-14 h-14 flex items-center justify-center z-10">
                    <ArchiveBoxIcon class="w-6 h-6 text-gray-600" />
                  </div>
                </div>
              </div>
              <h4 class="font-medium text-gray-800">存储与评估</h4>
              <p class="text-sm text-gray-600">Steps 10-15</p>
              <div class="mt-2">
                <span :class="[
                  'px-2 py-1 text-xs rounded-full',
                  getPhaseStatusClass(pipelineData.phase_status.storage_evaluation.status)
                ]">
                  {{ getPhaseStatusText(pipelineData.phase_status.storage_evaluation.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 当前执行步骤 -->
        <div v-if="pipelineData.current_step" class="card p-4 bg-blue-50 border-blue-200">
          <div class="flex items-center space-x-3">
            <div class="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
            <div>
              <span class="font-medium text-blue-800">当前执行步骤:</span>
              <span class="ml-2 text-blue-700">{{ formatStepName(pipelineData.current_step) }}</span>
            </div>
          </div>
        </div>

        <!-- 详细步骤状态 -->
        <div class="card p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">详细步骤状态</h3>
          <div class="space-y-4">
            <!-- 系统初始化步骤 -->
            <div>
              <h4 class="font-medium text-gray-800 mb-3">阶段一: 系统初始化 (Steps 1-3)</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div
                  v-for="step in initializationSteps"
                  :key="step.id"
                  class="p-3 rounded-lg border"
                  :class="getStepCardClass(step.id)"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium">{{ step.name }}</span>
                    <div :class="getStepStatusIcon(step.id)">
                      {{ getStepStatusEmoji(step.id) }}
                    </div>
                  </div>
                  <div class="text-xs text-gray-600">
                    <div v-if="pipelineData.step_status[step.id]">
                      平均耗时: {{ pipelineData.step_status[step.id].avg_duration }}s
                    </div>
                    <div v-else>暂无数据</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 实时记忆增强步骤 -->
            <div>
              <h4 class="font-medium text-gray-800 mb-3">阶段二: 实时记忆增强 (Steps 4-9)</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div
                  v-for="step in enhancementSteps"
                  :key="step.id"
                  class="p-3 rounded-lg border"
                  :class="getStepCardClass(step.id)"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium">{{ step.name }}</span>
                    <div :class="getStepStatusIcon(step.id)">
                      {{ getStepStatusEmoji(step.id) }}
                    </div>
                  </div>
                  <div class="text-xs text-gray-600">
                    <div v-if="pipelineData.step_status[step.id]">
                      平均耗时: {{ pipelineData.step_status[step.id].avg_duration }}s
                    </div>
                    <div v-else>暂无数据</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 存储与评估步骤 -->
            <div>
              <h4 class="font-medium text-gray-800 mb-3">阶段三: 存储与评估 (Steps 10-15)</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div
                  v-for="step in storageSteps"
                  :key="step.id"
                  class="p-3 rounded-lg border"
                  :class="getStepCardClass(step.id)"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium">{{ step.name }}</span>
                    <div :class="getStepStatusIcon(step.id)">
                      {{ getStepStatusEmoji(step.id) }}
                    </div>
                  </div>
                  <div class="text-xs text-gray-600">
                    <div v-if="pipelineData.step_status[step.id]">
                      平均耗时: {{ pipelineData.step_status[step.id].avg_duration }}s
                    </div>
                    <div v-else>暂无数据</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading" class="text-center py-12">
        <CpuChipIcon class="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <h2 class="text-xl font-semibold text-gray-700 mb-2">无法获取流程数据</h2>
        <p class="text-gray-600 mb-6">
          请确保后端服务正在运行，或点击刷新数据重试
        </p>
        <button
          @click="loadPipelineData"
          class="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          重试
        </button>
      </div>
    </main>
    
    <!-- 功能预览模态框 -->
    <div v-if="showFeaturePreview" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" @click="showFeaturePreview = false"></div>
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="relative w-full max-w-4xl bg-white rounded-xl shadow-2xl">
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">15步流程可视化 - 功能预览</h3>
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
                    <span>三阶段进度环形图</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>步骤状态实时指示器</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>性能指标实时监控</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>瓶颈自动识别</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <CheckIcon class="w-4 h-4 text-green-500" />
                    <span>流程执行动画</span>
                  </li>
                </ul>
              </div>
              
              <div class="space-y-4">
                <h4 class="font-medium text-gray-800">15步流程概览</h4>
                <div class="text-xs text-gray-600 space-y-1">
                  <div class="font-medium text-gray-700">Phase 1: 系统初始化 (1-3步)</div>
                  <div>• 数据库初始化</div>
                  <div>• 组件初始化</div>
                  <div>• 异步评估器初始化</div>
                  
                  <div class="font-medium text-gray-700 mt-2">Phase 2: 实时增强 (4-9步)</div>
                  <div>• 统一缓存向量化</div>
                  <div>• FAISS向量检索</div>
                  <div>• 关联网络拓展</div>
                  
                  <div class="font-medium text-gray-700 mt-2">Phase 3: 存储评估 (10-15步)</div>
                  <div>• LLM响应生成</div>
                  <div>• 异步评估处理</div>
                  <div>• 关联创建清理</div>
                </div>
              </div>
            </div>
            
            <div class="mt-6 p-4 bg-blue-50 rounded-lg">
              <div class="text-sm text-blue-800">
                <strong>预计开发时间：</strong> 3-4天
                <br>
                <strong>技术难点：</strong> 实时数据流处理、SVG动画效果、性能优化
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
import { 
  CpuChipIcon, 
  XMarkIcon, 
  CheckIcon, 
  MagnifyingGlassIcon, 
  ArchiveBoxIcon 
} from '@heroicons/vue/24/outline'

const notifications = useNotificationStore()
const { connect, disconnect, isConnected } = useWebSocket()

// 响应式数据
const pipelineData = ref(null)
const loading = ref(false)
const error = ref('')
const autoRefresh = ref(false)
const refreshInterval = ref(null)
const showFeaturePreview = ref(false)

// API基础URL
const API_BASE = 'http://localhost:5000/api'

// 步骤定义
const initializationSteps = [
  { id: 'step_1_database_initialization', name: '数据库初始化' },
  { id: 'step_2_component_initialization', name: '组件初始化' },
  { id: 'step_3_async_evaluator_initialization', name: '异步评估器初始化' }
]

const enhancementSteps = [
  { id: 'step_4_unified_cache_vectorization', name: '统一缓存向量化' },
  { id: 'step_5_faiss_vector_retrieval', name: 'FAISS向量检索' },
  { id: 'step_6_association_network_expansion', name: '关联网络拓展' },
  { id: 'step_7_history_dialogue_aggregation', name: '历史对话聚合' },
  { id: 'step_8_weight_ranking_deduplication', name: '权重排序去重' },
  { id: 'step_9_final_context_assembly', name: '最终上下文构建' }
]

const storageSteps = [
  { id: 'step_10_llm_response_generation', name: 'LLM响应生成' },
  { id: 'step_11_immediate_dialogue_storage', name: '即时对话存储' },
  { id: 'step_12_async_llm_evaluation', name: '异步LLM评估' },
  { id: 'step_13_save_evaluation_results', name: '保存评估结果' },
  { id: 'step_14_auto_association_creation', name: '自动关联创建' }
]

// 工具函数
const formatStepName = (stepId: string): string => {
  const stepMap: { [key: string]: string } = {
    'step_1_database_initialization': '数据库初始化',
    'step_2_component_initialization': '组件初始化',
    'step_3_async_evaluator_initialization': '异步评估器初始化',
    'step_4_unified_cache_vectorization': '统一缓存向量化',
    'step_5_faiss_vector_retrieval': 'FAISS向量检索',
    'step_6_association_network_expansion': '关联网络拓展',
    'step_7_history_dialogue_aggregation': '历史对话聚合',
    'step_8_weight_ranking_deduplication': '权重排序去重',
    'step_9_final_context_assembly': '最终上下文构建',
    'step_10_llm_response_generation': 'LLM响应生成',
    'step_11_immediate_dialogue_storage': '即时对话存储',
    'step_12_async_llm_evaluation': '异步LLM评估',
    'step_13_save_evaluation_results': '保存评估结果',
    'step_14_auto_association_creation': '自动关联创建'
  }
  return stepMap[stepId] || stepId
}

const getPhaseColor = (phase: string): string => {
  const colors = {
    'initialization': '#10b981', // green
    'query_enhancement': '#3b82f6', // blue
    'storage_evaluation': '#8b5cf6' // purple
  }
  return colors[phase] || '#6b7280'
}

const getPhaseStatusClass = (status: string): string => {
  const classes = {
    'completed': 'bg-green-100 text-green-800',
    'running': 'bg-blue-100 text-blue-800',
    'idle': 'bg-gray-100 text-gray-800',
    'failed': 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getPhaseStatusText = (status: string): string => {
  const texts = {
    'completed': '已完成',
    'running': '运行中',
    'idle': '空闲',
    'failed': '失败'
  }
  return texts[status] || status
}

const getStepCardClass = (stepId: string): string => {
  if (!pipelineData.value?.current_step) {
    return 'bg-gray-50 border-gray-200'
  }
  
  if (pipelineData.value.current_step === stepId) {
    return 'bg-blue-50 border-blue-300 shadow-md'
  }
  
  const stepData = pipelineData.value.step_status[stepId]
  if (stepData && stepData.success_rate > 0.8) {
    return 'bg-green-50 border-green-200'
  }
  
  return 'bg-gray-50 border-gray-200'
}

const getStepStatusIcon = (stepId: string): string => {
  if (pipelineData.value?.current_step === stepId) {
    return 'text-blue-600'
  }
  
  const stepData = pipelineData.value?.step_status[stepId]
  if (stepData && stepData.success_rate > 0.8) {
    return 'text-green-600'
  }
  
  return 'text-gray-400'
}

const getStepStatusEmoji = (stepId: string): string => {
  if (pipelineData.value?.current_step === stepId) {
    return '⚡'
  }
  
  const stepData = pipelineData.value?.step_status[stepId]
  if (stepData && stepData.success_rate > 0.8) {
    return '✅'
  }
  
  return '⭕'
}

// 加载流程数据
const loadPipelineData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch(`${API_BASE}/pipeline/status`)
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }
    
    const data = await response.json()
    pipelineData.value = data
    
    if (!autoRefresh.value) {
      notifications.add({
        type: 'success',
        title: '流程数据更新',
        message: `活跃会话: ${data.active_sessions}`
      })
    }
    
  } catch (err: any) {
    error.value = err.message || '加载失败'
    pipelineData.value = null
    
    if (!autoRefresh.value) {
      notifications.add({
        type: 'error',
        title: '加载失败',
        message: error.value
      })
    }
  } finally {
    loading.value = false
  }
}

// 切换自动刷新/WebSocket模式
const toggleAutoRefresh = async () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    // 开启WebSocket实时更新模式
    try {
      if (!isConnected()) {
        await connect()
      }
      
      // 订阅流程状态更新
      websocketManager.subscribePipeline()
      
      // 设置WebSocket事件监听
      websocketManager.on('pipeline_status_update', handleWebSocketUpdate)
      
      notifications.add({
        type: 'success',
        title: 'WebSocket实时更新已开启',
        message: '已连接到实时监控服务'
      })
      
    } catch (error) {
      // WebSocket连接失败，降级到轮询模式
      console.warn('WebSocket连接失败，降级到轮询模式:', error)
      autoRefresh.value = false
      startPollingMode()
    }
  } else {
    // 停止WebSocket监听
    websocketManager.off('pipeline_status_update', handleWebSocketUpdate)
    
    // 停止轮询模式
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
    
    notifications.add({
      type: 'info',
      title: '实时更新已关闭',
      message: '已停止自动更新'
    })
  }
}

// 启动轮询模式（降级方案）
const startPollingMode = () => {
  refreshInterval.value = setInterval(loadPipelineData, 3000)
  notifications.add({
    type: 'info',
    title: '轮询模式已启动',
    message: '每3秒自动更新流程数据'
  })
}

// WebSocket更新处理器
const handleWebSocketUpdate = (data: any) => {
  pipelineData.value = data
  console.log('📊 收到WebSocket流程状态更新:', data)
}

// 组件挂载和卸载
onMounted(async () => {
  console.log('PipelineViewer mounted')
  
  // 首次加载数据
  await loadPipelineData()
  
  // 尝试连接WebSocket
  try {
    await connect()
    console.log('✅ WebSocket连接成功')
  } catch (error) {
    console.warn('⚠️ WebSocket连接失败，将使用HTTP API:', error)
  }
})

onUnmounted(() => {
  // 清理定时器
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  
  // 移除WebSocket监听器
  websocketManager.off('pipeline_status_update', handleWebSocketUpdate)
  
  console.log('PipelineViewer unmounted')
})
</script>