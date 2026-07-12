import { createApp } from 'vue'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './styles/variables.css'
import './styles/tool-layout.css'
import './styles/dark-theme.css'
import 'highlight.js/styles/github.css'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'
import i18n from './locales'

const app = createApp(App)

// 全局错误处理:捕获未处理的 Vue 运行时异常,避免单点错误导致白屏
app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue Error]', info, err)
  try {
    fetch('/api/frontend-log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        level: 'error',
        message: `[Vue ${info}] ${err && err.stack ? err.stack : err}`,
      }),
    }).catch(() => {})
  } catch (_) {
    // 忽略日志上报失败
  }
}

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
