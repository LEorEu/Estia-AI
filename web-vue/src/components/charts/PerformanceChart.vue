<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title flex items-center">
        <ChartBarIcon class="w-5 h-5 mr-2 text-primary-500" />
        性能趋势
      </h3>
      <div class="flex items-center space-x-2">
        <select
          v-model="selectedMetric"
          class="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="response_time">响应时间</option>
          <option value="qps">QPS</option>
          <option value="success_rate">成功率</option>
          <option value="cache_hit">缓存命中率</option>
        </select>
        
        <button
          @click="refreshChart"
          :disabled="isRefreshing"
          class="text-xs text-primary-600 hover:text-primary-700 disabled:opacity-50"
        >
          {{ isRefreshing ? '刷新中...' : '刷新' }}
        </button>
      </div>
    </div>
    
    <div class="relative">
      <!-- 图表容器 -->
      <div ref="chartContainer" class="h-64 w-full">
        <canvas ref="chartCanvas"></canvas>
      </div>
      
      <!-- 加载状态 -->
      <div 
        v-if="isLoading" 
        class="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm"
      >
        <div class="flex items-center space-x-2 text-gray-600">
          <div class="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-sm">加载中...</span>
        </div>
      </div>
      
      <!-- 无数据状态 -->
      <div 
        v-if="!isLoading && !hasData" 
        class="absolute inset-0 flex items-center justify-center"
      >
        <div class="text-center text-gray-500">
          <ChartBarIcon class="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p class="text-sm">暂无性能数据</p>
        </div>
      </div>
    </div>
    
    <!-- 统计信息 -->
    <div class="mt-4 pt-4 border-t border-gray-200">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div>
          <div class="text-lg font-semibold text-gray-900">{{ currentValue }}</div>
          <div class="text-xs text-gray-600">当前值</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-green-600">{{ maxValue }}</div>
          <div class="text-xs text-gray-600">最高值</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-blue-600">{{ avgValue }}</div>
          <div class="text-xs text-gray-600">平均值</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-red-600">{{ minValue }}</div>
          <div class="text-xs text-gray-600">最低值</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { ChartBarIcon } from '@heroicons/vue/24/outline'
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'

// 注册Chart.js组件
Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const monitoringStore = useMonitoringStore()

const chartContainer = ref<HTMLDivElement>()
const chartCanvas = ref<HTMLCanvasElement>()
const chart = ref<Chart | null>(null)

const selectedMetric = ref('response_time')
const isLoading = ref(false)
const isRefreshing = ref(false)

// 模拟历史数据
const historicalData = ref([
  { time: '10:00', response_time: 1.2, qps: 645, success_rate: 96, cache_hit: 98 },
  { time: '10:30', response_time: 1.8, qps: 520, success_rate: 94, cache_hit: 95 },
  { time: '11:00', response_time: 1.1, qps: 780, success_rate: 98, cache_hit: 99 },
  { time: '11:30', response_time: 0.9, qps: 892, success_rate: 99, cache_hit: 100 },
  { time: '12:00', response_time: 1.3, qps: 756, success_rate: 97, cache_hit: 97 },
  { time: '12:30', response_time: 1.49, qps: 671, success_rate: 98, cache_hit: 100 }
])

// 计算属性
const hasData = computed(() => historicalData.value.length > 0)

const currentData = computed(() => {
  const data = historicalData.value
  return data.map(item => item[selectedMetric.value as keyof typeof item])
})

const currentValue = computed(() => {
  const data = currentData.value
  return data.length > 0 ? formatValue(data[data.length - 1]) : '--'
})

const maxValue = computed(() => {
  const data = currentData.value
  return data.length > 0 ? formatValue(Math.max(...data)) : '--'
})

const minValue = computed(() => {
  const data = currentData.value
  return data.length > 0 ? formatValue(Math.min(...data)) : '--'
})

const avgValue = computed(() => {
  const data = currentData.value
  if (data.length === 0) return '--'
  const avg = data.reduce((sum, val) => sum + val, 0) / data.length
  return formatValue(avg)
})

// 方法
const formatValue = (value: number): string => {
  switch (selectedMetric.value) {
    case 'response_time':
      return `${value.toFixed(2)}ms`
    case 'qps':
      return Math.round(value).toString()
    case 'success_rate':
    case 'cache_hit':
      return `${Math.round(value)}%`
    default:
      return value.toString()
  }
}

const getChartConfig = () => {
  const labels = historicalData.value.map(item => item.time)
  const data = currentData.value
  
  const colors = {
    response_time: { bg: 'rgba(59, 130, 246, 0.1)', border: 'rgb(59, 130, 246)' },
    qps: { bg: 'rgba(16, 185, 129, 0.1)', border: 'rgb(16, 185, 129)' },
    success_rate: { bg: 'rgba(245, 158, 11, 0.1)', border: 'rgb(245, 158, 11)' },
    cache_hit: { bg: 'rgba(139, 92, 246, 0.1)', border: 'rgb(139, 92, 246)' }
  }
  
  const color = colors[selectedMetric.value as keyof typeof colors]
  
  return {
    type: 'line' as const,
    data: {
      labels,
      datasets: [{
        label: getMetricLabel(),
        data,
        backgroundColor: color.bg,
        borderColor: color.border,
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: color.border,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: false
        },
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index' as const,
          intersect: false,
          callbacks: {
            label: (context: any) => {
              return `${getMetricLabel()}: ${formatValue(context.parsed.y)}`
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          grid: {
            display: false
          },
          ticks: {
            font: {
              size: 11
            }
          }
        },
        y: {
          display: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            font: {
              size: 11
            },
            callback: (value: any) => formatValue(value)
          }
        }
      },
      interaction: {
        mode: 'nearest' as const,
        axis: 'x' as const,
        intersect: false
      },
      animation: {
        duration: 750,
        easing: 'easeInOutQuart'
      }
    }
  }
}

const getMetricLabel = (): string => {
  switch (selectedMetric.value) {
    case 'response_time':
      return '响应时间'
    case 'qps':
      return 'QPS'
    case 'success_rate':
      return '成功率'
    case 'cache_hit':
      return '缓存命中率'
    default:
      return '未知指标'
  }
}

const initChart = async () => {
  if (!chartCanvas.value) return
  
  await nextTick()
  
  // 销毁现有图表
  if (chart.value) {
    chart.value.destroy()
  }
  
  // 创建新图表
  chart.value = new Chart(chartCanvas.value, getChartConfig())
}

const refreshChart = async () => {
  if (isRefreshing.value) return
  
  try {
    isRefreshing.value = true
    
    // 模拟数据刷新
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 添加新的数据点
    const now = new Date()
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    
    const newDataPoint = {
      time: timeStr,
      response_time: 1.2 + (Math.random() - 0.5) * 0.8,
      qps: 650 + (Math.random() - 0.5) * 200,
      success_rate: 95 + Math.random() * 5,
      cache_hit: 95 + Math.random() * 5
    }
    
    historicalData.value.push(newDataPoint)
    
    // 保持最近10个数据点
    if (historicalData.value.length > 10) {
      historicalData.value.shift()
    }
    
    // 更新图表
    await initChart()
    
  } finally {
    isRefreshing.value = false
  }
}

// 监听选中指标变化
watch(selectedMetric, () => {
  initChart()
})

// 生命周期
onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chart.value) {
    chart.value.destroy()
  }
})
</script>

<style scoped>
canvas {
  max-height: 256px;
}
</style>