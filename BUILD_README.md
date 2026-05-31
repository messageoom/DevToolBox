# 构建与发布指南

## 自动构建（GitHub Actions）

项目已配置 GitHub Actions CI/CD（`.github/workflows/ci.yml`），包含三个自动化流程：

### 持续集成

每次推送到 `master` 分支或创建 PR 时自动运行：

| Job | 说明 |
|-----|------|
| `backend-check` | Python 语法检查 + Flask 应用导入验证 |
| `frontend-build` | npm ci + 生产构建 + 上传构建产物 |

### 发布构建

推送 `v*` 格式的 tag 时自动触发：

```bash
git tag v1.0.0
git push origin v1.0.0
```

流程：
1. 运行 CI 检查（backend-check + frontend-build 通过后继续）
2. 在 Windows 环境中构建前端并嵌入后端
3. 使用 PyInstaller 打包为 `DevToolBox.exe`
4. 自动创建 GitHub Release 并附带可执行文件

---

## 手动构建

### 环境要求

- Python 3.8+
- Node.js 16+

### 一键构建

```bash
python build.py
```

此脚本会依次：安装依赖 → 构建前端 → 复制到后端 → PyInstaller 打包 → 生成启动脚本。

支持带版本号构建：
```bash
python build.py --version v1.0.0
```

### 手动分步构建

```bash
# 1. 安装后端依赖
pip install -r requirements.txt

# 2. 安装前端依赖并构建
cd frontend && npm ci && npm run build -- --outDir ../backend/static/frontend && cd ..

# 3. 打包
pip install pyinstaller
python build.py
```

### 构建产物

```
dist/
├── DevToolBox.exe          # 可执行文件
├── 启动DevToolBox.bat      # Windows 启动脚本
├── README.md               # 使用说明
└── uploads/                # 上传目录
```

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| PyInstaller 未安装 | `pip install pyinstaller` |
| 前端构建失败 | 确认 Node.js 已安装：`node --version` |
| 模块导入错误 | 在 `app.spec` 的 `hiddenimports` 中添加缺失模块 |
| 打包文件过大 | 使用 UPX 压缩（已在 app.spec 中启用） |
| CI 构建失败 | 检查 GitHub Actions 日志，确认 requirements.txt 和 package-lock.json 是否最新 |

调试打包：
```bash
pyinstaller --debug=all --clean app.spec
```
