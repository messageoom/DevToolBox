# DevToolBox - 开发工具箱

## 🎯 项目简介

**DevToolBox** 是一个功能强大的开发工具箱，专为开发者打造的综合性工具平台。基于现代Web技术栈构建，提供从文件处理到数据转换，从编码解码到加密解密的全方位开发工具支持。

## 🌟 核心特色

### 🏗️ 架构设计
- **模块化架构**：每个功能独立模块，便于维护和扩展
- **前后端分离**：RESTful API设计，支持灵活部署
- **现代化技术栈**：Vue.js + Flask + Element Plus

### 🎨 用户体验
- **直观界面**：简洁明了的现代化Web界面
- **响应式设计**：完美适配桌面端和移动端
- **实时反馈**：即时预览和转换结果

### 🔧 功能丰富
- **8大工具模块**：涵盖开发全流程需求
- **专业功能**：每项工具都提供专业级功能
- **易于使用**：傻瓜式操作，无需复杂配置

## 📋 功能概览

| 工具分类 | 具体工具 | 主要功能 |
|---------|---------|---------|
| 📁 文件工具 | 文件上传 | 多格式支持、分类显示、安全存储 |
| 📊 数据工具 | JSON/YAML/Markdown | 格式化、转换、验证、统计 |
| 🔐 编码工具 | Base64/URL | 编解码、解析、构建 |
| 🔒 加密工具 | 哈希算法 | MD5/SHA256/HMAC/PBKDF2/bcrypt |
| ⏰ 时间工具 | 时间戳转换 | 多时区支持、北京时间显示 |

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- 现代浏览器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd DevToolBox
```

2. **安装后端依赖**
```bash
cd backend
pip install -r ../requirements.txt
```

3. **安装前端依赖**
```bash
cd ../frontend
npm install
```

4. **启动服务**
```bash
# 后端服务
cd ../backend
python app.py

# 前端服务（新终端）
cd ../frontend
npm run dev
```

5. **访问应用**
打开浏览器访问：http://localhost:5173

## 📖 使用指南

### 文件上传
- 支持多种文件格式上传
- 自动分类显示
- 安全的文件存储机制

### 数据处理
- **JSON工具**：格式化、压缩、验证、转义
- **YAML工具**：格式化、压缩、JSON互转
- **Markdown工具**：HTML转换、语法验证、文档统计

### 编码解码
- **Base64工具**：文本和文件编解码
- **URL工具**：编码解码、链接解析

### 加密安全
- 多算法哈希生成
- HMAC签名
- 密码哈希（bcrypt）

### 时间处理
- 时间戳转换
- 多时区显示
- 北京时间支持

## 🏗️ 项目结构

```
DevToolBox/
├── backend/                    # 后端服务 (Flask)
│   ├── app.py                 # 主应用入口
│   ├── modules/               # 功能模块
│   │   ├── file_upload.py     # 文件上传模块
│   │   ├── json_tools.py      # JSON处理模块
│   │   ├── yaml_tools.py      # YAML处理模块
│   │   ├── markdown_tools.py  # Markdown处理模块
│   │   ├── base64_tools.py    # Base64编解码模块
│   │   ├── hash_tools.py      # 哈希加密模块
│   │   ├── url_tools.py       # URL处理模块
│   │   └── timestamp_tools.py # 时间戳处理模块
│   ├── static/                # 静态资源
│   └── templates/             # HTML模板
├── frontend/                  # 前端应用 (Vue.js)
│   ├── src/
│   │   ├── components/        # 通用组件
│   │   ├── views/            # 页面组件
│   │   ├── router/           # 路由配置
│   │   └── App.vue           # 主应用组件
│   ├── package.json          # 项目配置
│   └── vite.config.js        # 构建配置
├── uploads/                   # 文件上传目录
├── requirements.txt           # Python依赖
└── README.md                  # 项目文档
```

## 🔧 技术栈

### 后端技术栈
- **Flask** - 轻量级Web框架
- **Flask-CORS** - 跨域资源共享
- **Werkzeug** - WSGI工具包
- **PyYAML** - YAML处理
- **Markdown** - Markdown解析
- **bcrypt** - 密码哈希
- **pytz** - 时区处理

### 前端技术栈
- **Vue.js 3** - 渐进式JavaScript框架
- **Element Plus** - Vue 3组件库
- **Vue Router 4** - 官方路由管理器
- **Axios** - HTTP客户端
- **Vite** - 下一代前端构建工具

## 🌐 API文档

### 基础信息
- **Base URL**: `http://localhost:5000/api`
- **认证方式**: 无需认证
- **数据格式**: JSON

### 主要接口

#### 文件上传
```
POST /api/file-upload/upload          # 上传文件
GET  /api/file-upload/files           # 获取文件列表
GET  /api/file-upload/files/{id}      # 下载文件
```

#### 数据工具
```
POST /api/json-tools/format           # JSON格式化
POST /api/yaml-tools/to-json          # YAML转JSON
POST /api/markdown-tools/to-html      # Markdown转HTML
```

#### 编码工具
```
POST /api/base64-tools/encode         # Base64编码
POST /api/url-tools/encode           # URL编码
```

#### 加密工具
```
POST /api/hash-tools/generate         # 生成哈希
POST /api/hash-tools/hmac            # HMAC签名
```

#### 时间工具
```
GET  /api/timestamp-tools/current     # 当前时间戳
POST /api/timestamp-tools/convert     # 时间戳转换
```

## 🤝 贡献指南

欢迎为 DevToolBox 贡献代码！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

**DevToolBox Team**

- 项目维护者: [Your Name]
- 贡献者: 欢迎加入！

## 🙏 致谢

感谢所有为这个项目贡献代码和建议的开发者！

## 📞 联系我们

- 项目主页: https://github.com/messageoom/DevToolBox
- 问题反馈: https://github.com/messageoom/DevToolBox/issues
- 邮箱: [messageoom@gmail.com]

---

**DevToolBox** - 让开发更简单！🚀
