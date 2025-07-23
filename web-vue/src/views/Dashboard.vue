<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- 头部 -->
    <DashboardHeader />
    
    <!-- 主要内容区域 -->
    <main class="container mx-auto px-4 py-6">
      <!-- 系统状态概览 -->
      <section class="mb-8">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <SystemStatusCard />
          <PerformanceMetricsCard />
          <ConnectionStatusCard />
          <QuickActionsCard />
        </div>
      </section>
      
      <!-- 增强监控面板 -->
      <section class="mb-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SystemHealthCard />
          <AlertsManagementCard />
        </div>
      </section>
      
      <!-- 核心监控面板 -->
      <section class="mb-8">
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <!-- 实时性能图表 -->
          <PerformanceChart />
          
          <!-- 关键词云 -->
          <KeywordCloud />
        </div>
      </section>
      
      <!-- 详细数据展示 -->
      <section class="mb-8">
        <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <!-- 会话列表 -->
          <div class="xl:col-span-2">
            <SessionList />
          </div>
          
          <!-- 记忆分析 -->
          <MemoryAnalysis />
        </div>
      </section>
      
      <!-- 新功能入口 -->
      <section>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            title="上下文查看器"
            description="查看完整的对话上下文构建过程"
            icon="eye"
            route="/context"
            :available="hasData"
          />
          
          <FeatureCard
            title="异步评估展示"
            description="监控异步评估过程和结果"
            icon="chart"
            route="/evaluation"
            :available="hasData"
          />
          
          <FeatureCard
            title="15步流程可视化"
            description="实时监控记忆处理流程"
            icon="flow"
            route="/pipeline"
            :available="true"
          />
        </div>
      </section>
    </main>
    
    <!-- 页脚 -->
    <DashboardFooter />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { useWebSocket } from '@/services/websocket'

// 组件导入
import DashboardHeader from '@/components/layout/DashboardHeader.vue'
import DashboardFooter from '@/components/layout/DashboardFooter.vue'
import SystemStatusCard from '@/components/cards/SystemStatusCard.vue'
import PerformanceMetricsCard from '@/components/cards/PerformanceMetricsCard.vue'
import ConnectionStatusCard from '@/components/cards/ConnectionStatusCard.vue'
import QuickActionsCard from '@/components/cards/QuickActionsCard.vue'
import PerformanceChart from '@/components/charts/PerformanceChart.vue'
import KeywordCloud from '@/components/charts/KeywordCloud.vue'
import SessionList from '@/components/data/SessionList.vue'
import MemoryAnalysis from '@/components/data/MemoryAnalysis.vue'
import FeatureCard from '@/components/cards/FeatureCard.vue'
import SystemHealthCard from '@/components/cards/SystemHealthCard.vue'
import AlertsManagementCard from '@/components/cards/AlertsManagementCard.vue'

const monitoringStore = useMonitoringStore()
const { connect, disconnect } = useWebSocket()

// 计算属性
const hasData = computed(() => monitoringStore.hasData)

// 初始化数据获取
const initializeDashboard = async () => {
  try {
    // 获取初始数据
    await monitoringStore.fetchDashboardData()
    
    // 建立WebSocket连接
    await connect()
    
  } catch (error) {
    console.error('仪表板初始化失败:', error)
  }
}

// 生命周期钩子
onMounted(() => {
  initializeDashboard()
})

onUnmounted(() => {
  disconnect()
})
</script>