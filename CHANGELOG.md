# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2026-06-08

### Added

- 文本传输：局域网设备间实时文本传输与群聊（SocketIO + WebRTC）
- 全工具页面交互优化：14 个工具页统一添加复制按钮、示例数据、字符/行数统计、一键清空
- 页面路由过渡动画：slide+fade 替代简单 fade，切换更有层次感
- 工具区段入场动画：input/action/output 依次淡入上滑（staggered delay）
- Tab 内容切换过渡动画：淡入+微上滑
- 输出区域加载态 shimmer 动画
- 文件上传页 UI/UX 全面打磨：上传进度条、文件卡片 hover 抬升、拖拽视觉反馈、分类折叠过渡、自适应预览高度、文件搜索、新文件高亮脉冲、空状态浮动动画
- 全局微交互：自定义滚动条、input 聚焦光晕、Alert 入场动画、文本选中色、Tab 指示条贝塞尔曲线过渡
- 暗色模式下所有交互效果同步适配
- GUI 打包输出目录改为 `dist/GUI_vX.Y.Z/`，exe 名含版本+平台后缀

### Changed

- 编码工具分类图标：swap_horiz → code（花括号风格）
- 数据工具分类图标：data_object → database（数据库风格）
- 路由过渡名：page-fade → page-slide
- ToolSection 组件支持 `aria-busy` 属性配合加载态

## [2.0.2] - 2026-06-01

### Added

- 国际化 (i18n)：中英双语实时切换，覆盖前端 33 个文件、后端 GUI + 锁页面
- vue-i18n 集成：Element Plus 组件跟随语言切换
- 语言切换 UI：顶部下拉菜单，选择保存到 localStorage
- 原生 GUI 中英文切换：pywebview 控制面板支持语言切换
- 锁页面双语：根据用户语言设置显示中文或英文
- 移动端底部导航：8 个入口（新增文件上传、二维码），图标/文字紧凑排列
- 移动端首页：列表式分类布局，替代卡片网格，节省屏幕空间
- 移动端工具页：去除 el-card 嵌套，内容铺满屏宽，padding 最小化
- 页面切换过渡动画：200ms fade 淡入淡出
- 按钮/导航触摸反馈：active 缩放、背景高亮

### Changed

- deviceStore 简化为两档（mobile ≤768px / desktop >768px），统一全局 resize 监听
- tool-layout.css 移动端 padding 从 16-20px 缩减至 4-8px
- 9 个视图补充 `@media` 响应式 CSS
- FileUpload、TimestampTools、FileCategory 去除重复 resize 监听，复用 deviceStore
- CryptoTools 移动端去除额外 padding wrapper

### Fixed

- UuidTools、PasswordTools 标签页标题显示英文（`tabs` → `tab` 键名拼写错误）
- Web 页面出现多余滚动条（html/body overflow 修正）

## [2.0.1] - 2025-06-01

### Added

- pywebview 原生桌面 GUI 窗口：macOS 风格暗色 UI，双击 exe 即弹出控制面板
- GUI 概览页：服务器状态、局域网地址、一键打开浏览器/复制 URL/打开存储目录
- GUI 安全页：Token 启用/禁用/刷新、临时令牌管理
- GUI 存储页：自定义存储路径（原生文件夹选择器）、文件大小限制、自动清理
- GUI 网络页：端口/绑定地址配置
- GUI 关于页：版本、Python、运行时长等信息
- UUID 安全 Token 访问控制 + macOS 风格锁页面板
- 系统托盘集成（pystray），pywebview 不可用时自动降级
- Settings API（`/api/settings`）：配置管理、Token 操作、运行状态
- Settings 前端页面：Web 端配置管理（供局域网访问使用）
- JSON 配置持久化（`devtoolbox_config.json`）
- 智能局域网 IP 检测：自动绕过 VPN/虚拟网卡，获取真实物理网卡 IP

### Changed

- 存储路径统一：`file_upload`、`data_conversion` 均读取 `config_manager`，GUI 修改全局生效
- 启动流程：pywebview GUI 优先 → system tray 降级 → console 降级
- CI 支持 `DEVTOOLBOX_NO_GUI=1` 环境变量跳过 GUI 模式

### Removed

- 旧 tkinter GUI（`gui_app.py`），由 pywebview 替代

## [2.0.0] - 2025-05-31

### Added

- UUID 生成器：支持 v1/v3/v4/v5 生成、批量生成、格式验证、UUID 解析
- 密码生成器：自定义规则生成、强度检测（0-100 评分）、助记密码
- API Key 生成器：Random/Base64/UUID/Hex 多格式、格式验证、SHA-256/512 哈希
- JWT 调试器（纯前端）：自动解码 Header/Payload/Signature、过期检测、特殊声明解析
- 文本对比工具（纯前端）：LCS 差异算法、统一视图、并排视图、差异统计
- Base64 工具新增 5 个 Tab：URL 安全编码、URL 安全解码、校验、文件编码、文件解码
- URL 工具新增 5 个 Tab：解析 URL、构建 URL、验证 URL、提取链接、Query 编解码
- 时间戳工具新增 3 个 Tab：时间加减、批量计算、格式参考

### Fixed

- 加密工具路由错误：`/crypto-main-menu` → `/crypto-tools`
- 哈希工具：从 3 个按钮占位改为完整实现（生成/验证/HMAC/密码哈希 4 个 Tab）
- Markdown 转 HTML：后端返回 JSON 而非 HTML 字符串
- 加密工具：移除 RSA 1024-bit 选项，新增 3072-bit
- 文件上传：大小限制从 100MB 校正为 50MB（与后端一致）
- 时间计算器：移除后端不支持的 weeks/months/years 选项

### Changed

- README 全面更新：反映 20 个工具、本地安全理念、完整 API 端点
- 项目结构更新：14 个后端模块、20 个前端页面
- 响应式布局：桌面/平板/手机三端自适应
- 暗黑模式完善

### Removed

- 废弃的 `frontend/src/api/` 目录（11 个文件）
- 废弃的 `MobileMenu.vue` 组件

## [1.0.1] - 2025-05-20

### Added

- 二维码工具：生成、美化
- 数据转换工具：Markdown/HTML/PDF 互转
- 加密工具：RSA/ECC/AES/ChaCha20/SM2/SM4
- 哈希工具：MD5/SHA 系列

### Changed

- UI/UX 全面重构：设计体系、响应式布局、组件拆分
- 安全加固：SSRF 防护、路径穿越防护、XSS 过滤、错误脱敏
- CI/CD 集成

### Fixed

- PyInstaller 打包配置完善
- 前端 SPA 路由支持
- exe 图标多尺寸支持

## [1.0.0] - 2025-05-10

### Added

- 初始版本发布
- 文件上传工具
- JSON 工具：格式化、压缩、验证
- YAML 工具：格式化、JSON 互转
- Base64 编解码
- URL 编解码
- 时间戳转换
- Markdown 编辑器（沉浸式）
- 移动端适配
