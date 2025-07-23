// 基础类型定义
export interface ApiResponse<T = any> {
  data?: T
  error?: string
  timestamp: string
}

// 系统状态类型
export type SystemStatus = 'running' | 'idle' | 'error' | 'offline'

// 步骤状态类型  
export type StepStatus = 'pending' | 'running' | 'success' | 'failed' | 'skipped'

// 监控数据接口
export interface SystemStatusData {
  status: SystemStatus
  session_id: string | null
  running_time: number
  progress_percentage: number
}

export interface PerformanceSummary {
  total_sessions: number
  average_duration: number
  success_rate: number
  slowest_step?: {
    step: string
    avg_duration: number
  }
}

export interface StatusResponse {
  status: SystemStatusData
  summary: PerformanceSummary
  timestamp: string
}

// 关键词分析接口
export interface KeywordData {
  word: string
  count: number
  frequency: number
}

export interface KeywordAnalysis {
  top_keywords: KeywordData[]
  total_unique_keywords: number
  keyword_distribution: Record<string, number>
}

// 会话数据接口
export interface SessionData {
  session_id: string
  start_time: string
  duration: number
  success_count: number
  failed_count: number
  user_input: string
  ai_response: string
}

export interface SessionListResponse {
  sessions: SessionData[]
  total: number
  timestamp: string
}

// 记忆分析接口
export interface MemoryAnalysis {
  average_similarity: number
  memory_usage_stats: {
    retrieved: number
    associations: number
    context_memories: number
  }
  total_retrievals: number
  similarity_distribution: {
    '高 (>0.8)': number
    '中 (0.6-0.8)': number
    '低 (<0.6)': number
  }
}

// 仪表板批量数据接口
export interface DashboardData {
  timestamp: string
  has_data: boolean
  data_source?: string
  live_mode?: boolean
  test_mode?: boolean
  status: StatusResponse
  keywords: KeywordAnalysis
  sessions: SessionListResponse
  memory: MemoryAnalysis
}

// 15步流程监控接口
export interface PipelineStep {
  id: string
  name: string
  status: StepStatus
  duration?: number
  start_time?: number
  end_time?: number
  progress?: number
  metadata?: Record<string, any>
}

export interface PipelinePhase {
  id: string
  name: string
  steps: PipelineStep[]
  status: StepStatus
  progress: number
}

export interface PipelineStatus {
  session_id: string | null
  current_step: string | null
  phase: string
  phases: PipelinePhase[]
  overall_progress: number
  timestamp: number
}

// 上下文查看器接口
export interface ContextStep {
  step_name: string
  input_data: any
  output_data: any
  processing_details: any
}

export interface SessionContext {
  session_id: string
  user_input: string
  preprocessed_query: string
  extracted_keywords: string[]
  retrieved_memories: Array<{
    content: string
    similarity: number
    weight: number
    created_at: string
  }>
  association_memories: Array<{
    content: string
    association_strength: number
    level: number
  }>
  historical_context: Array<{
    content: string
    timestamp: string
    relevance_score: number
  }>
  final_context: {
    system_prompt: string
    context_structure: string
    token_count: number
    context_length: number
  }
  steps: ContextStep[]
}

// 异步评估接口
export interface EvaluationContext {
  user_input: string
  assistant_response: string
  retrieved_memories: string[]
  session_context: string
  evaluation_prompt: string
}

export interface EvaluationResults {
  importance_score: number
  importance_reason: string
  emotion_analysis: {
    emotion: string
    confidence: number
  }
  topic_tags: string[]
  association_suggestions: Array<{
    target: string
    strength: number
    reason: string
  }>
  knowledge_extraction: string[]
}

export interface SessionEvaluation {
  session_id: string
  evaluation_context: EvaluationContext
  evaluation_results: EvaluationResults
  associations_created: Array<{
    source: string
    target: string
    strength: number
    type: string
    created_at: string
  }>
  timestamp: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
}

// 通知系统接口
export interface Notification {
  id: string
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  timestamp: number
  duration?: number
  persistent?: boolean
}

// WebSocket事件接口
export interface WebSocketEvents {
  'status_update': StatusResponse
  'pipeline_status_update': PipelineStatus
  'new_session': SessionData
  'evaluation_complete': SessionEvaluation
  'monitoring_error': { error: string; timestamp: string }
  'system_alert': Notification
}

// Chart.js数据接口
export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor?: string | string[]
  borderColor?: string
  tension?: number
}

export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

export interface ChartOptions {
  responsive: boolean
  maintainAspectRatio: boolean
  plugins?: {
    title?: {
      display: boolean
      text: string
    }
    legend?: {
      display: boolean
      position: 'top' | 'bottom' | 'left' | 'right'
    }
  }
  scales?: any
}