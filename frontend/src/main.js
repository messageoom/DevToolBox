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

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
