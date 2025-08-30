# DevToolBox - 开发工具箱

DevToolBox是一个功能强大的开发工具箱，基于Python Flask + Vue.js构建，专为开发者设计。提供文件上传、数据处理、编码解码、加密解密、时间处理等全方位开发工具支持。

## 🚀 项目特色

- **模块化设计**：每个功能模块独立处理，便于维护和扩展
- **现代化界面**：基于Vue.js + Element Plus的现代化Web界面
- **RESTful API**：提供完整的REST API接口，支持前后端分离
- **多功能集成**：涵盖开发过程中常用的各种工具
- **响应式设计**：支持桌面端和移动端访问

## 🛠️ 核心功能

### 📁 文件工具
- **文件上传服务**：支持多种文件类型上传和分类显示
  - 图片格式：png, jpg, jpeg, gif, bmp, webp, svg, ico
  - 文档格式：txt, pdf, doc, docx, xls, xlsx, ppt, pptx
  - 数据格式：csv, json, xml
  - 压缩文件：zip, rar, 7z
  - 音频格式：mp3, wav, flac, aac, ogg, m4a
  - 视频格式：mp4, avi, mov, wmv
  - 其他格式：exe, dll, iso, torrent
- 文件分类显示和管理
- 自动生成唯一文件名避免冲突

### 📊 数据工具
- **JSON工具**：格式化、压缩、验证、转义
- **YAML工具**：格式化、压缩、验证、JSON互转
- **Markdown工具**：HTML转换、纯文本提取、语法验证、文档统计

### 🔐 编码工具
- **Base64工具**：编码/解码、文件处理、URL安全编码
- **URL工具**：编码/解码、解析、构建、验证

### 🔒 加密工具
- **哈希工具**：MD5、SHA1、SHA256等多种算法
- HMAC生成、PBKDF2密钥派生、bcrypt哈希

### ⏰ 时间工具
- **时间戳工具**：转换、解析、计算、多时区显示
- 北京时间显示、时区转换
- 时间格式验证和转换

## 🎨 界面特性

- 现代化Web界面，基于Vue.js + Element Plus
- 响应式设计，支持桌面端和移动端
- 直观的侧边栏导航
- 实时预览和转换结果
- 详细的统计信息展示

## 📦 安装和运行

### 方法一：使用可执行文件（推荐）

1. 下载 `gui_app.exe` 文件
2. 双击运行即可启动服务
3. 无需安装Python或任何其他依赖

### 方法二：从源代码运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 运行服务

图形界面版本：
```bash
python gui_app.py
```

命令行版本：
```bash
python app.py
```

#### 3. 访问服务

运行后，程序界面会显示服务器的IP地址和端口，例如：
```
文件上传服务地址: http://192.168.1.100:5000
```

在同一局域网内的任何设备都可以通过这个地址访问上传服务。

## 🖥️ 图形界面说明

图形界面程序提供以下功能：
- 显示文件上传服务地址
- 显示当前文件存储路径
- 可更改文件存储路径（设置会自动保存）
- 可直接打开文件存储文件夹
- 可关闭服务并退出程序

## 📖 使用说明

1. 运行程序后，记下显示的服务地址
2. 在浏览器中访问该地址
3. 点击"选择文件"按钮选择要上传的文件
4. 点击"上传文件"按钮完成上传
5. 上传成功的文件会显示在页面下方的列表中，按文件类型分类
6. 点击文件可以查看或下载

## 🏗️ 项目结构

```
DevToolBox/
├── backend/                    # 后端服务
│   ├── app.py                 # Flask主应用
│   ├── modules/               # 功能模块
│   │   ├── __init__.py
│   │   ├── file_upload.py     # 文件上传模块
│   │   ├── json_tools.py      # JSON工具模块
│   │   ├── yaml_tools.py      # YAML工具模块
│   │   ├── markdown_tools.py  # Markdown工具模块
│   │   ├── base64_tools.py    # Base64工具模块
│   │   ├── hash_tools.py      # 哈希工具模块
│   │   ├── url_tools.py       # URL工具模块
│   │   └── timestamp_tools.py # 时间戳工具模块
│   ├── static/                # 静态文件
│   └── templates/             # HTML模板
├── frontend/                  # 前端应用
│   ├── package.json           # 前端依赖配置
│   ├── vite.config.js         # Vite构建配置
│   ├── index.html             # HTML入口
│   └── src/                   # 源代码
│       ├── main.js            # Vue应用入口
│       ├── App.vue            # 主应用组件
│       ├── router/            # 路由配置
│       │   └── index.js
│       └── views/             # 页面组件
│           ├── Home.vue
│           ├── FileUpload.vue
│           ├── JsonTools.vue
│           ├── YamlTools.vue
│           ├── MarkdownTools.vue
│           ├── Base64Tools.vue
│           ├── HashTools.vue
│           ├── UrlTools.vue
│           ├── TimestampTools.vue
│           └── TimeCalculator.vue
├── uploads/                   # 文件上传目录
├── requirements.txt           # Python依赖
└── README.md                  # 项目文档
```

## 📝 注意事项

- 上传的文件会保存在指定目录中（默认为`uploads`目录）
- 请定期备份文件存储目录以防止数据丢失
- 服务默认运行在5000端口
- 使用可执行文件时，所有设置会自动保存到同目录下的settings.json文件中
- 可执行文件可在任何Windows电脑上运行，无需安装Python或其他依赖
