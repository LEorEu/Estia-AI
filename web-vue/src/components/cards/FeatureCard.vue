<template>
  <div 
    class="card cursor-pointer transition-all duration-300 hover:shadow-xl hover:scale-105"
    :class="{ 'opacity-50 cursor-not-allowed': !available }"
    @click="handleClick"
  >
    <div class="flex items-start space-x-4">
      <!-- 图标 -->
      <div :class="[
        'p-3 rounded-lg',
        available ? 'bg-primary-100' : 'bg-gray-100'
      ]">
        <component 
          :is="iconComponent" 
          :class="[
            'w-6 h-6',
            available ? 'text-primary-600' : 'text-gray-400'
          ]"
        />
      </div>
      
      <!-- 内容 -->
      <div class="flex-1">
        <div class="flex items-center justify-between mb-2">
          <h3 :class="[
            'font-semibold',
            available ? 'text-gray-900' : 'text-gray-500'
          ]">
            {{ title }}
          </h3>
          
          <!-- 状态指示器 -->
          <span 
            v-if="available"
            class="inline-flex items-center px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full"
          >
            可用
          </span>
          <span 
            v-else
            class="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-500 rounded-full"
          >
            开发中
          </span>
        </div>
        
        <p :class="[
          'text-sm leading-relaxed',
          available ? 'text-gray-600' : 'text-gray-400'
        ]">
          {{ description }}
        </p>
        
        <!-- 功能特性 -->
        <div v-if="features && features.length > 0" class="mt-3">
          <div class="flex flex-wrap gap-1">
            <span 
              v-for="feature in features"
              :key="feature"
              :class="[
                'inline-flex items-center px-2 py-1 text-xs rounded-full',
                available 
                  ? 'bg-blue-50 text-blue-700' 
                  : 'bg-gray-50 text-gray-400'
              ]"
            >
              {{ feature }}
            </span>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="mt-4 flex items-center justify-between">
          <div class="flex items-center space-x-2 text-xs text-gray-500">
            <ClockIcon class="w-4 h-4" />
            <span>预计开发时间: {{ estimatedTime || '待定' }}</span>
          </div>
          
          <ChevronRightIcon 
            :class="[
              'w-5 h-5 transition-transform',
              available ? 'text-primary-500' : 'text-gray-300'
            ]"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import {
  EyeIcon,
  ChartBarIcon,
  CpuChipIcon,
  ClockIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

interface Props {
  title: string
  description: string
  icon: 'eye' | 'chart' | 'flow' | 'settings'
  route?: string
  available?: boolean
  features?: string[]
  estimatedTime?: string
}

const props = withDefaults(defineProps<Props>(), {
  available: false,
  features: () => [],
  estimatedTime: '待定'
})

const router = useRouter()
const appStore = useAppStore()

// 图标映射
const iconComponent = computed(() => {
  switch (props.icon) {
    case 'eye':
      return EyeIcon
    case 'chart':
      return ChartBarIcon
    case 'flow':
      return CpuChipIcon
    default:
      return ChartBarIcon
  }
})

const handleClick = () => {
  if (!props.available) {
    appStore.addNotification({
      type: 'info',
      title: '功能开发中',
      message: `${props.title} 功能正在开发中，敬请期待！`,
      duration: 3000
    })
    return
  }
  
  if (props.route) {
    router.push(props.route)
  }
}
</script>

<style scoped>
.card:hover .ChevronRightIcon {
  transform: translateX(4px);
}
</style>