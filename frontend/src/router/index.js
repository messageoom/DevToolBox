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
import MarkdownEditor from '../views/MarkdownEditor.vue'
import DataConversion from '../views/DataConversion.vue'
import QrTools from '../views/QrTools.vue'
import CryptoTools from '../views/CryptoTools.vue'
import CryptoMainMenu from '../views/CryptoMainMenu.vue'
import TestCryptoAPI from '../views/TestCryptoAPI.vue'
// 导入PDF帮助页面
import PdfHelp from '../views/PdfHelp.vue'

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
  },
  {
    path: '/markdown-editor',
    name: 'MarkdownEditor',
    component: MarkdownEditor
  },
  {
    path: '/data-conversion',
    name: 'DataConversion',
    component: DataConversion
  },
  {
    path: '/qr-tools',
    name: 'QrTools',
    component: QrTools
  },
  {
    path: '/crypto-tools',
    name: 'CryptoTools',
    component: CryptoTools
  },
  {
    path: '/crypto-main-menu',
    name: 'CryptoMainMenu',
    component: CryptoMainMenu
  },
  {
    path: '/test-crypto-api',
    name: 'TestCryptoAPI',
    component: TestCryptoAPI
  },
  // 添加PDF帮助页面路由
  {
    path: '/pdf-help',
    name: 'PdfHelp',
    component: PdfHelp
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router