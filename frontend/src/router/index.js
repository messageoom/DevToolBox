import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const JsonTools = () => import(/* webpackChunkName: "data-tools" */ '../views/JsonTools.vue')
const YamlTools = () => import(/* webpackChunkName: "data-tools" */ '../views/YamlTools.vue')
const MarkdownTools = () => import(/* webpackChunkName: "data-tools" */ '../views/MarkdownTools.vue')
const MarkdownEditor = () => import(/* webpackChunkName: "data-tools" */ '../views/MarkdownEditor.vue')

const HashTools = () => import(/* webpackChunkName: "crypto-tools" */ '../views/HashTools.vue')
const CryptoTools = () => import(/* webpackChunkName: "crypto-tools" */ '../views/CryptoTools.vue')

const Base64Tools = () => import(/* webpackChunkName: "encoding-tools" */ '../views/Base64Tools.vue')
const UrlTools = () => import(/* webpackChunkName: "encoding-tools" */ '../views/UrlTools.vue')

const TimestampTools = () => import(/* webpackChunkName: "time-tools" */ '../views/TimestampTools.vue')
const TimeCalculator = () => import(/* webpackChunkName: "time-tools" */ '../views/TimeCalculator.vue')

const FileUpload = () => import(/* webpackChunkName: "file-tools" */ '../views/FileUpload.vue')
const FileCategory = () => import(/* webpackChunkName: "file-tools" */ '../views/FileCategory.vue')

const DataConversion = () => import(/* webpackChunkName: "misc-tools" */ '../views/DataConversion.vue')
const QrTools = () => import(/* webpackChunkName: "misc-tools" */ '../views/QrTools.vue')

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/file-upload', name: 'FileUpload', component: FileUpload },
  { path: '/file-category/:category', name: 'FileCategory', component: FileCategory, props: true },
  { path: '/json-tools', name: 'JsonTools', component: JsonTools },
  { path: '/yaml-tools', name: 'YamlTools', component: YamlTools },
  { path: '/base64-tools', name: 'Base64Tools', component: Base64Tools },
  { path: '/hash-tools', name: 'HashTools', component: HashTools },
  { path: '/url-tools', name: 'UrlTools', component: UrlTools },
  { path: '/timestamp-tools', name: 'TimestampTools', component: TimestampTools },
  { path: '/time-calculator', name: 'TimeCalculator', component: TimeCalculator },
  { path: '/markdown-tools', name: 'MarkdownTools', component: MarkdownTools },
  { path: '/markdown-editor', name: 'MarkdownEditor', component: MarkdownEditor },
  { path: '/data-conversion', name: 'DataConversion', component: DataConversion },
  { path: '/qr-tools', name: 'QrTools', component: QrTools },
  { path: '/crypto-tools', name: 'CryptoTools', component: CryptoTools },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
