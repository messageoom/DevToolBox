# DevToolBox

一个面向开发者的**本地化安全工具箱**，基于 Flask + Vue 3 构建。所有数据处理均在本地完成，不上传、不外发、不留痕——你的数据永远不会离开你的电脑。

## 核心理念

- **本地处理**：所有计算在浏览器/本地服务完成，无需联网
- **隐私优先**：不上传任何数据到外部服务器，无用户追踪
- **开箱即用**：双击 exe 即可运行，无需安装 Python 或 Node.js
- **响应式设计**：桌面、平板、手机自适应布局
- **国际化**：中英双语实时切换，前端 + 原生 GUI + 锁页面全覆盖

## 功能一览

| 分类 | 工具 | 功能 |
|------|------|------|
| 文件工具 | 文件上传 | 多格式上传、分类管理、安全存储 |
| 数据工具 | JSON | 格式化、压缩、验证、转义 |
| 数据工具 | YAML | 格式化、压缩、验证、JSON 互转 |
| 数据工具 | Markdown 编辑器 | 实时预览、多主题、导出 HTML/PDF |
| 数据工具 | Markdown 工具 | 转 HTML、提取纯文本、语法验证、文档统计 |
| 数据工具 | 数据转换 | Markdown/HTML/PDF 互转 |
| 编码工具 | Base64 | 文本/文件编解码、URL 安全编码、校验 |
| 编码工具 | URL | 编解码、解析、构建、验证、链接提取、Query 编解码 |
| 加密工具 | 哈希 | MD5/SHA/HMAC/bcrypt/PBKDF2/Blake3 |
| 加密工具 | 加密解密 | RSA/ECC/Ed25519/AES/ChaCha20/SM2/SM4 |
| 时间工具 | 时间戳 | 转换、多时区、时间加减、批量计算、格式参考 |
| 时间工具 | 时间计算 | 日期差、工作日计算 |
| 其他工具 | 二维码 | 生成、美化 |
| 生成与调试 | UUID 生成器 | v1/v3/v4/v5 生成、验证、解析 |
| 生成与调试 | 密码生成器 | 自定义规则生成、强度检测、助记密码 |
| 生成与调试 | API Key 生成器 | 多格式生成、格式验证、Key 哈希 |
| 生成与调试 | JWT 调试器 | 解码 Header/Payload/Signature、过期检测 |
| 生成与调试 | 文本对比 | 统一视图、并排视图、差异统计 |

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+

### 从源码运行

```bash
# 克隆项目
git clone https://github.com/messageoom/DevToolBox.git
cd DevToolBox

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖并构建
cd frontend && npm install && npm run build && cd ..

# 启动
python backend/app.py
```

访问 http://localhost:5000 即可使用。

### 开发模式

```bash
# 终端 1：启动后端
python backend/app.py

# 终端 2：启动前端开发服务器
cd frontend && npm run dev
```

前端开发服务器访问 http://localhost:5173，支持热更新。

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | Flask 会话密钥 | 随机生成 |
| `FLASK_DEBUG` | 启用调试模式 | `false` |
| `CORS_ORIGINS` | 允许的前端源（逗号分隔） | `http://localhost:5173,http://127.0.0.1:5173` |

### 一键启动（Windows）

下载 `DevToolBox.exe`，双击运行即可，无需安装 Python 或 Node.js。

## 项目结构

```
DevToolBox/
├── backend/
│   ├── app.py                          # Flask 应用工厂
│   ├── modules/                        # 功能模块（14 个）
│   │   ├── file_upload.py              # 文件上传
│   │   ├── json_tools.py               # JSON 处理
│   │   ├── yaml_tools.py               # YAML 处理
│   │   ├── markdown_tools.py           # Markdown 工具
│   │   ├── base64_tools.py             # Base64 编解码
│   │   ├── url_tools.py                # URL 工具
│   │   ├── hash_tools.py               # 哈希工具
│   │   ├── crypto_tools.py             # 加密解密
│   │   ├── timestamp_tools.py          # 时间戳工具
│   │   ├── data_conversion.py          # 数据转换
│   │   ├── qr_tools.py                 # 二维码
│   │   ├── uuid_tools.py               # UUID 生成器
│   │   ├── password_tools.py           # 密码生成器
│   │   ├── apikey_tools.py             # API Key 生成器
│   │   └── data_conversion_styles.py   # 转换样式模板
│   └── utils/                          # 安全工具
│       ├── ssrf_protection.py          # SSRF 防护
│       ├── path_safety.py              # 路径安全
│       └── error_handler.py            # 错误脱敏
├── frontend/
│   └── src/
│       ├── stores/                     # Pinia 状态管理
│       │   ├── theme.js                # 暗黑模式
│       │   └── device.js               # 设备检测
│       ├── styles/                     # 全局样式 + 暗黑主题
│       ├── data/                       # 共享数据
│       │   └── toolCategories.js       # 工具分类
│       ├── views/                      # 页面组件（20 个）
│       ├── components/                 # 通用组件
│       ├── composables/                # 组合式函数
│       └── router/                     # 路由（懒加载）
├── requirements.txt                    # Python 依赖
├── app.spec                            # PyInstaller 打包配置
├── build.py                            # 构建脚本
└── README.md
```

## 技术栈

**后端**：Flask 2.3 · Flask-CORS · PyYAML · markdown-it-py · PyCryptodome · cryptography · bcrypt · PyMuPDF · WeasyPrint · Pillow · qrcode

**前端**：Vue 3.4 · Vue Router 4 · Element Plus 2.4 · Pinia · vue-i18n 9 · Axios · Vite 5

**安全**：SSRF 防护 · 路径穿越防护 · XSS 过滤 · 输入参数边界校验 · 错误响应脱敏 · 速率限制

## API 端点

所有端点前缀：`/api`

| 模块 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 文件上传 | POST | `/file-upload/upload` | 上传文件（最大 50MB） |
| | GET | `/file-upload/files` | 获取文件列表 |
| | GET | `/file-upload/files/{name}` | 下载文件 |
| | DELETE | `/file-upload/files/{name}` | 删除文件 |
| JSON | POST | `/json-tools/format` | 格式化 |
| | POST | `/json-tools/minify` | 压缩 |
| | POST | `/json-tools/validate` | 验证 |
| | POST | `/json-tools/escape` | 转义 |
| YAML | POST | `/yaml-tools/format` | 格式化 |
| | POST | `/yaml-tools/to-json` | YAML → JSON |
| | POST | `/yaml-tools/validate` | 验证 |
| Base64 | POST | `/base64-tools/encode` | 编码 |
| | POST | `/base64-tools/decode` | 解码 |
| | POST | `/base64-tools/url-safe-encode` | URL 安全编码 |
| | POST | `/base64-tools/url-safe-decode` | URL 安全解码 |
| | POST | `/base64-tools/validate` | 校验 |
| | POST | `/base64-tools/encode-file` | 文件编码 |
| | POST | `/base64-tools/decode-file` | 文件解码 |
| URL | POST | `/url-tools/encode` | URL 编码 |
| | POST | `/url-tools/decode` | URL 解码 |
| | POST | `/url-tools/parse` | 解析 URL |
| | POST | `/url-tools/build` | 构建 URL |
| | POST | `/url-tools/validate` | 验证 URL |
| | POST | `/url-tools/extract-links` | 提取链接 |
| | POST | `/url-tools/query-encode` | Query 编码 |
| | POST | `/url-tools/query-decode` | Query 解码 |
| 哈希 | POST | `/hash-tools/generate` | 生成哈希 |
| | POST | `/hash-tools/verify` | 验证哈希 |
| | POST | `/hash-tools/hmac` | HMAC |
| | POST | `/hash-tools/bcrypt` | bcrypt 哈希 |
| | POST | `/hash-tools/pbkdf2` | PBKDF2 密钥派生 |
| 加密 | POST | `/crypto-tools/{algo}/generate` | 生成密钥对 |
| | POST | `/crypto-tools/{algo}/encrypt` | 加密 |
| | POST | `/crypto-tools/{algo}/decrypt` | 解密 |
| | POST | `/crypto-tools/{algo}/sign` | 签名 |
| | POST | `/crypto-tools/{algo}/verify` | 验签 |
| 时间戳 | GET | `/timestamp-tools/current` | 当前时间戳 |
| | POST | `/timestamp-tools/convert` | 时间戳转换 |
| | POST | `/timestamp-tools/calculate` | 时间计算 |
| | POST | `/timestamp-tools/batch` | 批量计算 |
| | POST | `/timestamp-tools/add-time` | 时间加减 |
| 数据转换 | POST | `/data-conversion/md-to-html` | Markdown → HTML |
| | POST | `/data-conversion/md-to-pdf` | Markdown → PDF |
| | POST | `/data-conversion/html-to-md` | HTML → Markdown |
| | POST | `/data-conversion/pdf-to-md` | PDF → Markdown |
| Markdown | POST | `/markdown-tools/to-html` | 转 HTML |
| | POST | `/markdown-tools/to-plain` | 提取纯文本 |
| | POST | `/markdown-tools/validate` | 语法验证 |
| | POST | `/markdown-tools/stats` | 文档统计 |
| 二维码 | POST | `/qr-tools/generate` | 生成二维码 |
| | POST | `/qr-tools/beautify` | 美化二维码 |
| UUID | POST | `/uuid-tools/generate` | 生成 UUID |
| | POST | `/uuid-tools/validate` | 验证 UUID |
| | POST | `/uuid-tools/parse` | 解析 UUID |
| 密码 | POST | `/password-tools/generate` | 生成密码 |
| | POST | `/password-tools/strength` | 密码强度检测 |
| | POST | `/password-tools/passphrase` | 生成助记密码 |
| API Key | POST | `/apikey-tools/generate` | 生成 API Key |
| | POST | `/apikey-tools/validate` | 验证 API Key |
| | POST | `/apikey-tools/hash-key` | Key 哈希 |

## 贡献

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 联系

- 项目主页：https://github.com/messageoom/DevToolBox
- 问题反馈：https://github.com/messageoom/DevToolBox/issues
