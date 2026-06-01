import { defineStore } from 'pinia'

const MOBILE_BREAKPOINT = 768

export const useDeviceStore = defineStore('device', {
  state: () => ({
    isMobile: window.innerWidth <= MOBILE_BREAKPOINT,
  }),
  actions: {
    updateDevice() {
      this.isMobile = window.innerWidth <= MOBILE_BREAKPOINT
    },
    initListener() {
      window.addEventListener('resize', this.updateDevice)
    },
    cleanupListener() {
      window.removeEventListener('resize', this.updateDevice)
    },
  }
})

export { MOBILE_BREAKPOINT }
