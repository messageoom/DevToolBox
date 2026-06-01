import { createI18n } from 'vue-i18n'
import zh from './zh.json'
import en from './en.json'

const saved = localStorage.getItem('dt-lang') || 'zh'

const i18n = createI18n({
  legacy: false,
  locale: saved,
  fallbackLocale: 'en',
  messages: { zh, en },
})

export default i18n
