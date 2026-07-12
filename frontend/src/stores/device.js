import { defineStore } from 'pinia'

const MOBILE_BREAKPOINT = 768

// 防抖后的 resize handler(模块级引用,便于 removeEventListener)
let _resizeHandler = null

export const useDeviceStore = defineStore('device', {
  state: () => ({
    isMobile: window.innerWidth <= MOBILE_BREAKPOINT,
  }),
  actions: {
    updateDevice() {
      this.isMobile = window.innerWidth <= MOBILE_BREAKPOINT
    },
    initListener() {
      // 防抖:拖拽窗口时避免每像素都触发响应式重渲染(isMobile 被几乎所有布局组件依赖)
      let timer = null
      _resizeHandler = () => {
        clearTimeout(timer)
        timer = setTimeout(() => this.updateDevice(), 150)
      }
      window.addEventListener('resize', _resizeHandler)
    },
    cleanupListener() {
      if (_resizeHandler) {
        window.removeEventListener('resize', _resizeHandler)
        _resizeHandler = null
      }
    },
  }
})

export { MOBILE_BREAKPOINT }
