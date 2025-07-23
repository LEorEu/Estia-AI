import { format, formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

/**
 * 格式化时间长度（秒）为可读字符串
 */
export function formatDuration(seconds: number): string {
  if (seconds < 1) {
    return `${Math.round(seconds * 1000)}毫秒`
  }
  
  if (seconds < 60) {
    return `${Math.round(seconds)}秒`
  }
  
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.round(seconds % 60)
  
  if (minutes < 60) {
    return remainingSeconds > 0 
      ? `${minutes}分${remainingSeconds}秒`
      : `${minutes}分钟`
  }
  
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  
  if (hours < 24) {
    return remainingMinutes > 0 
      ? `${hours}小时${remainingMinutes}分钟`
      : `${hours}小时`
  }
  
  const days = Math.floor(hours / 24)
  const remainingHours = hours % 24
  
  return remainingHours > 0 
    ? `${days}天${remainingHours}小时`
    : `${days}天`
}

/**
 * 格式化字节大小
 */
export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

/**
 * 格式化百分比
 */
export function formatPercentage(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`
}

/**
 * 格式化数字，添加千分位分隔符
 */
export function formatNumber(num: number, decimals = 0): string {
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num)
}

/**
 * 格式化大数字为紧凑格式 (1000 -> 1K)
 */
export function formatCompactNumber(num: number): string {
  return new Intl.NumberFormat('zh-CN', {
    notation: 'compact',
    compactDisplay: 'short',
  }).format(num)
}

/**
 * 格式化日期时间
 */
export function formatDateTime(date: Date | string | number): string {
  const dateObj = typeof date === 'string' || typeof date === 'number' 
    ? new Date(date) 
    : date
    
  return format(dateObj, 'yyyy-MM-dd HH:mm:ss', { locale: zhCN })
}

/**
 * 格式化相对时间 (2小时前)
 */
export function formatRelativeTime(date: Date | string | number): string {
  const dateObj = typeof date === 'string' || typeof date === 'number' 
    ? new Date(date) 
    : date
    
  return formatDistanceToNow(dateObj, { 
    addSuffix: true, 
    locale: zhCN 
  })
}

/**
 * 格式化时间戳为简短格式
 */
export function formatShortTime(timestamp: number): string {
  const date = new Date(timestamp)
  const now = new Date()
  
  // 如果是今天，只显示时间
  if (date.toDateString() === now.toDateString()) {
    return format(date, 'HH:mm', { locale: zhCN })
  }
  
  // 如果是今年，显示月日时间
  if (date.getFullYear() === now.getFullYear()) {
    return format(date, 'MM-dd HH:mm', { locale: zhCN })
  }
  
  // 否则显示完整日期
  return format(date, 'yy-MM-dd HH:mm', { locale: zhCN })
}

/**
 * 截断文本并添加省略号
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

/**
 * 格式化JSON为可读格式
 */
export function formatJSON(obj: any): string {
  try {
    return JSON.stringify(obj, null, 2)
  } catch (error) {
    return String(obj)
  }
}

/**
 * 高亮搜索关键词
 */
export function highlightSearchTerms(text: string, searchTerms: string[]): string {
  if (!searchTerms.length) return text
  
  let highlighted = text
  searchTerms.forEach(term => {
    const regex = new RegExp(`(${term})`, 'gi')
    highlighted = highlighted.replace(regex, '<mark class="bg-yellow-200 px-1 rounded">$1</mark>')
  })
  
  return highlighted
}

/**
 * 生成随机颜色（用于图表等）
 */
export function generateRandomColor(alpha = 1): string {
  const hue = Math.floor(Math.random() * 360)
  const saturation = Math.floor(Math.random() * 30) + 70 // 70-100%
  const lightness = Math.floor(Math.random() * 20) + 45  // 45-65%
  
  return `hsla(${hue}, ${saturation}%, ${lightness}%, ${alpha})`
}

/**
 * 生成预定义的颜色调色板
 */
export function getColorPalette(index: number): string {
  const colors = [
    '#3B82F6', // blue
    '#10B981', // green
    '#F59E0B', // yellow
    '#EF4444', // red
    '#8B5CF6', // purple
    '#06B6D4', // cyan
    '#F97316', // orange
    '#84CC16', // lime
    '#EC4899', // pink
    '#6B7280', // gray
  ]
  
  return colors[index % colors.length]
}

/**
 * 计算文本的哈希值（用于生成一致的颜色）
 */
export function hashStringToColor(str: string): string {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // 32位整数
  }
  
  const hue = Math.abs(hash) % 360
  return `hsl(${hue}, 70%, 50%)`
}

/**
 * 深拷贝对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime()) as any
  if (obj instanceof Array) return obj.map(item => deepClone(item)) as any
  if (typeof obj === 'object') {
    const cloned: any = {}
    Object.keys(obj).forEach(key => {
      cloned[key] = deepClone((obj as any)[key])
    })
    return cloned
  }
  return obj
}

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 等待指定时间
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 检查是否为有效的URL
 */
export function isValidUrl(string: string): boolean {
  try {
    new URL(string)
    return true
  } catch (_) {
    return false
  }
}

/**
 * 将驼峰命名转换为短横线命名
 */
export function camelToKebab(str: string): string {
  return str.replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`)
}

/**
 * 将短横线命名转换为驼峰命名
 */
export function kebabToCamel(str: string): string {
  return str.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())
}