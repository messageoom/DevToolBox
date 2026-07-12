import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

// 注:原 webpackChunkName 魔法注释在 Vite/Rollup 下不生效(只在 webpack 下有效),
// 已移除以避免误导。如需控制 chunk 分组,在 vite.config.js 配置
// build.rollupOptions.output.manualChunks。
const JsonTools = () => import('../views/JsonTools.vue')
const YamlTools = () => import('../views/YamlTools.vue')
const MarkdownTools = () => import('../views/MarkdownTools.vue')
const MarkdownEditor = () => import('../views/MarkdownEditor.vue')
const JsonToTs = () => import('../views/JsonToTs.vue')

const HashTools = () => import('../views/HashTools.vue')
const CryptoTools = () => import('../views/CryptoTools.vue')

const Base64Tools = () => import('../views/Base64Tools.vue')
const UrlTools = () => import('../views/UrlTools.vue')
const BaseConverter = () => import('../views/BaseConverter.vue')

const TimestampTools = () => import('../views/TimestampTools.vue')
const TimeCalculator = () => import('../views/TimeCalculator.vue')
const CronParser = () => import('../views/CronParser.vue')

const FileUpload = () => import('../views/FileUpload.vue')
const FileCategory = () => import('../views/FileCategory.vue')
const ImageTools = () => import('../views/ImageTools.vue')

const DataConversion = () => import('../views/DataConversion.vue')
const QrTools = () => import('../views/QrTools.vue')
const ColorTools = () => import('../views/ColorTools.vue')
const CaseConverter = () => import('../views/CaseConverter.vue')
const SqlFormatter = () => import('../views/SqlFormatter.vue')

const UuidTools = () => import('../views/UuidTools.vue')
const PasswordTools = () => import('../views/PasswordTools.vue')
const ApiKeyTools = () => import('../views/ApiKeyTools.vue')
const DummyDataGenerator = () => import('../views/DummyDataGenerator.vue')
const RegexTester = () => import('../views/RegexTester.vue')

const JwtDebugger = () => import('../views/JwtDebugger.vue')
const DiffTool = () => import('../views/DiffTool.vue')

const TextTransfer = () => import('../views/TextTransfer.vue')

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
  { path: '/uuid-tools', name: 'UuidTools', component: UuidTools },
  { path: '/password-tools', name: 'PasswordTools', component: PasswordTools },
  { path: '/apikey-tools', name: 'ApiKeyTools', component: ApiKeyTools },
  { path: '/jwt-debugger', name: 'JwtDebugger', component: JwtDebugger },
  { path: '/diff-tool', name: 'DiffTool', component: DiffTool },
  { path: '/text-transfer', name: 'TextTransfer', component: TextTransfer },
  { path: '/case-converter', name: 'CaseConverter', component: CaseConverter },
  { path: '/sql-formatter', name: 'SqlFormatter', component: SqlFormatter },
  { path: '/base-converter', name: 'BaseConverter', component: BaseConverter },
  { path: '/dummy-data', name: 'DummyDataGenerator', component: DummyDataGenerator },
  { path: '/regex-tester', name: 'RegexTester', component: RegexTester },
  { path: '/cron-parser', name: 'CronParser', component: CronParser },
  { path: '/json-to-ts', name: 'JsonToTs', component: JsonToTs },
  { path: '/image-tools', name: 'ImageTools', component: ImageTools },
  { path: '/color-tools', name: 'ColorTools', component: ColorTools },
  // 404 兜底:未匹配的路由回到首页
  { path: '/:pathMatch(.*)*', name: 'NotFound', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // 切换路由后回到顶部(原来会停留在上次滚动位置)
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
