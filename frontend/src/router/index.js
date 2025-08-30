import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import FileUpload from '../views/FileUpload.vue'
import FileCategory from '../views/FileCategory.vue'
import JsonTools from '../views/JsonTools.vue'
import YamlTools from '../views/YamlTools.vue'
import Base64Tools from '../views/Base64Tools.vue'
import HashTools from '../views/HashTools.vue'
import UrlTools from '../views/UrlTools.vue'
import TimestampTools from '../views/TimestampTools.vue'
import TimeCalculator from '../views/TimeCalculator.vue'
import MarkdownTools from '../views/MarkdownTools.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/file-upload',
    name: 'FileUpload',
    component: FileUpload
  },
  {
    path: '/file-category/:category',
    name: 'FileCategory',
    component: FileCategory,
    props: true
  },
  {
    path: '/json-tools',
    name: 'JsonTools',
    component: JsonTools
  },
  {
    path: '/yaml-tools',
    name: 'YamlTools',
    component: YamlTools
  },
  {
    path: '/base64-tools',
    name: 'Base64Tools',
    component: Base64Tools
  },
  {
    path: '/hash-tools',
    name: 'HashTools',
    component: HashTools
  },
  {
    path: '/url-tools',
    name: 'UrlTools',
    component: UrlTools
  },
  {
    path: '/timestamp-tools',
    name: 'TimestampTools',
    component: TimestampTools
  },
  {
    path: '/time-calculator',
    name: 'TimeCalculator',
    component: TimeCalculator
  },
  {
    path: '/markdown-tools',
    name: 'MarkdownTools',
    component: MarkdownTools
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
