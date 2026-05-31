# Changelog

All notable changes to this project will be documented in this file.

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
