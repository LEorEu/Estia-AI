import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

// 创建Vue应用
const app = createApp(App)

// 注册Pinia状态管理
const pinia = createPinia()
app.use(pinia)

// 注册路由
app.use(router)

// 挂载应用
app.mount('#app')

// 开发环境下的调试工具
if (import.meta.env.DEV) {
  console.log('🚀 Estia AI 监控仪表板已启动')
  console.log('📦 Vue版本:', app.version)
}