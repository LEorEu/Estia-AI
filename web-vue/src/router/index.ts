import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      title: 'Estia AI 监控仪表板'
    }
  },
  {
    path: '/context',
    name: 'Context',
    component: () => import('@/views/ContextViewer.vue'),
    meta: {
      title: '上下文查看器'
    }
  },
  {
    path: '/evaluation',
    name: 'Evaluation', 
    component: () => import('@/views/EvaluationViewer.vue'),
    meta: {
      title: '异步评估展示'
    }
  },
  {
    path: '/pipeline',
    name: 'Pipeline',
    component: () => import('@/views/PipelineViewer.vue'),
    meta: {
      title: '15步流程可视化'
    }
  },
  {
    path: '/session/:sessionId',
    name: 'SessionDetail',
    component: () => import('@/views/SessionDetail.vue'),
    meta: {
      title: '会话详情'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面未找到'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = to.meta.title as string
  }
  
  next()
})

export default router