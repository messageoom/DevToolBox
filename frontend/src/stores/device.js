import { defineStore } from 'pinia'

const MOBILE_BREAKPOINT = 480
const TABLET_BREAKPOINT = 768

export const useDeviceStore = defineStore('device', {
  state: () => ({
    width: window.innerWidth,
  }),
  getters: {
    isMobile: (state) => state.width <= MOBILE_BREAKPOINT,
    isTablet: (state) => state.width > MOBILE_BREAKPOINT && state.width <= TABLET_BREAKPOINT,
    isDesktop: (state) => state.width > TABLET_BREAKPOINT,
  },
  actions: {
    checkDevice() {
      this.width = window.innerWidth
    }
  }
})

export { MOBILE_BREAKPOINT, TABLET_BREAKPOINT }
