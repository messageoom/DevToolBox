import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const JsonTools = () => import(/* webpackChunkName: "data-tools" */ '../views/JsonTools.vue')
const YamlTools = () => import(/* webpackChunkName: "data-tools" */ '../views/YamlTools.vue')
const MarkdownTools = () => import(/* webpackChunkName: "data-tools" */ '../views/MarkdownTools.vue')
const MarkdownEditor = () => import(/* webpackChunkName: "data-tools" */ '../views/MarkdownEditor.vue')
const JsonToTs = () => import(/* webpackChunkName: "data-tools" */ '../views/JsonToTs.vue')

const HashTools = () => import(/* webpackChunkName: "crypto-tools" */ '../views/HashTools.vue')
const CryptoTools = () => import(/* webpackChunkName: "crypto-tools" */ '../views/CryptoTools.vue')

const Base64Tools = () => import(/* webpackChunkName: "encoding-tools" */ '../views/Base64Tools.vue')
const UrlTools = () => import(/* webpackChunkName: "encoding-tools" */ '../views/UrlTools.vue')
const BaseConverter = () => import(/* webpackChunkName: "encoding-tools" */ '../views/BaseConverter.vue')

const TimestampTools = () => import(/* webpackChunkName: "time-tools" */ '../views/TimestampTools.vue')
const TimeCalculator = () => import(/* webpackChunkName: "time-tools" */ '../views/TimeCalculator.vue')
const CronParser = () => import(/* webpackChunkName: "time-tools" */ '../views/CronParser.vue')

const FileUpload = () => import(/* webpackChunkName: "file-tools" */ '../views/FileUpload.vue')
const FileCategory = () => import(/* webpackChunkName: "file-tools" */ '../views/FileCategory.vue')
const ImageTools = () => import(/* webpackChunkName: "file-tools" */ '../views/ImageTools.vue')

const DataConversion = () => import(/* webpackChunkName: "misc-tools" */ '../views/DataConversion.vue')
const QrTools = () => import(/* webpackChunkName: "misc-tools" */ '../views/QrTools.vue')
const ColorTools = () => import(/* webpackChunkName: "misc-tools" */ '../views/ColorTools.vue')
const CaseConverter = () => import(/* webpackChunkName: "misc-tools" */ '../views/CaseConverter.vue')
const SqlFormatter = () => import(/* webpackChunkName: "misc-tools" */ '../views/SqlFormatter.vue')

const UuidTools = () => import(/* webpackChunkName: "generator-tools" */ '../views/UuidTools.vue')
const PasswordTools = () => import(/* webpackChunkName: "generator-tools" */ '../views/PasswordTools.vue')
const ApiKeyTools = () => import(/* webpackChunkName: "generator-tools" */ '../views/ApiKeyTools.vue')
const DummyDataGenerator = () => import(/* webpackChunkName: "generator-tools" */ '../views/DummyDataGenerator.vue')
const RegexTester = () => import(/* webpackChunkName: "generator-tools" */ '../views/RegexTester.vue')

const JwtDebugger = () => import(/* webpackChunkName: "dev-tools" */ '../views/JwtDebugger.vue')
const DiffTool = () => import(/* webpackChunkName: "dev-tools" */ '../views/DiffTool.vue')

const TextTransfer = () => import(/* webpackChunkName: "transfer-tools" */ '../views/TextTransfer.vue')

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
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
