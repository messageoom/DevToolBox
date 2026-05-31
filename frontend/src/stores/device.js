import { defineStore } from 'pinia'

const MOBILE_BREAKPOINT = 768

export const useDeviceStore = defineStore('device', {
  state: () => ({
    isMobile: window.innerWidth <= MOBILE_BREAKPOINT
  }),
  actions: {
    checkDevice() {
      this.isMobile = window.innerWidth <= MOBILE_BREAKPOINT
    }
  }
})

export { MOBILE_BREAKPOINT }
