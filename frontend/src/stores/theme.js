import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => {
    const saved = localStorage.getItem('devtoolbox-theme')
    return {
      isDark: saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches
    }
  },
  actions: {
    toggleTheme() {
      this.isDark = !this.isDark
      localStorage.setItem('devtoolbox-theme', this.isDark ? 'dark' : 'light')
      document.documentElement.classList.toggle('dark', this.isDark)
    },
    initTheme() {
      const saved = localStorage.getItem('devtoolbox-theme')
      if (saved) {
        this.isDark = saved === 'dark'
      } else {
        this.isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      document.documentElement.classList.toggle('dark', this.isDark)
    }
  }
})
