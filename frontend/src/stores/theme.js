import { defineStore } from 'pinia'

// 共享的偏好读取逻辑(原来在 state 初始化器和 initTheme 里各写一遍)
function readThemePref() {
  const saved = localStorage.getItem('devtoolbox-theme')
  if (saved) return saved === 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    // 创建时即读取正确值——子组件可能在 App.vue onMounted(initTheme) 之前就用 isDark,
    // 因此不能延迟到 initTheme 才设值,否则会短暂为 false。
    isDark: readThemePref(),
  }),
  actions: {
    _apply() {
      document.documentElement.classList.toggle('dark', this.isDark)
      localStorage.setItem('devtoolbox-theme', this.isDark ? 'dark' : 'light')
    },
    toggleTheme() {
      this.isDark = !this.isDark
      this._apply()
    },
    initTheme() {
      this.isDark = readThemePref()
      this._apply()
    }
  }
})
