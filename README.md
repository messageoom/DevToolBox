# DevToolBox

一个面向开发者的全能工具箱，基于 Flask + Vue 3 构建，提供文件处理、数据转换、编码解码、加密解密、时间处理等一站式开发工具。

## 功能一览

| 分类 | 工具 | 功能 |
|------|------|------|
| 文件工具 | 文件上传 | 多格式上传、分类管理、安全存储 |
| 数据工具 | JSON | 格式化、压缩、验证、转义 |
| 数据工具 | YAML | 格式化、压缩、验证、JSON 互转 |
| 数据工具 | Markdown 编辑器 | 实时预览、多主题、导出 HTML/PDF |
| 数据工具 | 数据转换 | Markdown/HTML/PDF 互转 |
| 编码工具 | Base64 | 文本/文件编解码、URL 安全编码 |
| 编码工具 | URL | 编解码、解析、构建、HAR 转换、Curl 执行 |
| 编码工具 | 二维码 | 生成、美化 |
| 加密工具 | 哈希 | MD5/SHA/HMAC/PBKDF2/bcrypt/Blake3 |
| 加密工具 | 加密解密 | RSA/ECC/Ed25519/AES/ChaCha20/SM2/SM4 |
| 时间工具 | 时间戳 | 转换、多时区、批量计算 |
| 时间工具 | 时间计算 | 日期差、工作日计算 |

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

# 安装前端依赖
cd frontend && npm install && cd ..

# 启动（同时启动前后端）
python app.py
```

访问 http://localhost:5173 即可使用。

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | Flask 会话密钥 | 随机生成 |
| `FLASK_DEBUG` | 启用调试模式 | `false` |
| `FLASK_HOST` | 后端监听地址 | `127.0.0.1` |
| `CORS_ORIGINS` | 允许的前端源（逗号分隔） | `http://localhost:5173,http://127.0.0.1:5173` |

### 一键启动（Windows）

下载 `DevToolBox.exe`，双击运行即可，无需安装 Python 或 Node.js。

## 项目结构

```
DevToolBox/
├── backend/
│   ├── app.py                          # Flask 应用工厂
│   ├── modules/                        # 功能模块（11 个）
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
│   │   └── data_conversion_styles.py   # 转换样式模板
│   └── utils/                          # 安全工具
│       ├── ssrf_protection.py          # SSRF 防护
│       ├── path_safety.py              # 路径安全
│       └── error_handler.py            # 错误脱敏
├── frontend/
│   └── src/
│       ├── api/                        # 统一 API 层（11 个模块）
│       ├── stores/                     # Pinia 状态管理
│       │   ├── theme.js                # 暗黑模式
│       │   └── device.js               # 设备检测
│       ├── styles/                     # 全局样式
│       │   └── dark-theme.css          # 暗黑主题
│       ├── data/                       # 共享数据
│       │   └── toolCategories.js       # 工具分类
│       ├── views/                      # 页面组件（17 个）
│       ├── components/                 # 通用组件
│       ├── composables/                # 组合式函数
│       └── router/                     # 路由（懒加载）
├── .github/workflows/ci.yml            # CI/CD 配置
├── requirements.txt                    # Python 依赖
└── app.py                              # 启动入口
```

## 技术栈

**后端**：Flask 2.3 · Flask-CORS · PyYAML · markdown-it-py · PyCryptodome · cryptography · bcrypt · PyMuPDF · WeasyPrint · Pillow · qrcode

**前端**：Vue 3.4 · Vue Router 4 · Element Plus 2.4 · Pinia · Axios · Vite 5

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
| YAML | POST | `/yaml-tools/format` | 格式化 |
| | POST | `/yaml-tools/to-json` | YAML → JSON |
| Base64 | POST | `/base64-tools/encode` | 编码 |
| | POST | `/base64-tools/decode` | 解码 |
| URL | POST | `/url-tools/encode` | URL 编码 |
| | POST | `/url-tools/decode` | URL 解码 |
| | POST | `/url-tools/send-request` | 发送 HTTP 请求 |
| | POST | `/url-tools/parse-curl` | 解析 Curl |
| | POST | `/url-tools/execute-curl` | 执行 Curl |
| | POST | `/url-tools/to-har` | URL → HAR |
| 哈希 | POST | `/hash-tools/generate` | 生成哈希 |
| | POST | `/hash-tools/verify` | 验证哈希 |
| | POST | `/hash-tools/pbkdf2` | PBKDF2 密钥派生 |
| | POST | `/hash-tools/bcrypt` | bcrypt 哈希 |
| 加密 | POST | `/crypto-tools/{algo}/generate` | 生成密钥对 |
| | POST | `/crypto-tools/{algo}/encrypt` | 加密 |
| | POST | `/crypto-tools/{algo}/decrypt` | 解密 |
| | POST | `/crypto-tools/{algo}/sign` | 签名 |
| | POST | `/crypto-tools/{algo}/verify` | 验签 |
| 时间戳 | GET | `/timestamp-tools/current` | 当前时间戳 |
| | POST | `/timestamp-tools/convert` | 时间戳转换 |
| | POST | `/timestamp-tools/calculate` | 时间计算 |
| 数据转换 | POST | `/data-conversion/md-to-html` | Markdown → HTML |
| | POST | `/data-conversion/md-to-pdf` | Markdown → PDF |
| | POST | `/data-conversion/html-to-md` | HTML → Markdown |
| | POST | `/data-conversion/pdf-to-md` | PDF → Markdown |
| 二维码 | POST | `/qr-tools/generate` | 生成二维码 |
| | POST | `/qr-tools/beautify` | 美化二维码 |
| Markdown | POST | `/markdown-tools/to-html` | 转 HTML |
| | POST | `/markdown-tools/to-plain` | 提取纯文本 |
| | POST | `/markdown-tools/validate` | 语法验证 |
| | POST | `/markdown-tools/stats` | 文档统计 |

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
