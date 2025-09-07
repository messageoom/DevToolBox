#!/usr/bin/env python3
"""
DevToolBox GUI版本一键打包脚本

功能：
1. 检查GUI应用依赖
2. 创建GUI版本的PyInstaller配置
3. 使用PyInstaller打包GUI应用
4. 生成最终的可执行文件
5. 支持版本号打包用于GitHub Releases

使用方法：
python gui_build.py [--version VERSION]

参数：
--version VERSION  指定版本号，例如 v1.0.0

示例：
python gui_build.py                    # 常规打包到 dist_gui 目录
python gui_build.py --version v1.0.0   # 带版本号打包到 dist_gui_v1.0.0 目录
"""

import os
import sys
import subprocess
import shutil
import time
import argparse
from pathlib import Path

class DevToolBoxGUIBuilder:
    def __init__(self, version=None):
        self.project_root = Path(__file__).parent
        self.version = version
        # 如果指定了版本号，则使用版本号作为目录名
        if version:
            self.dist_dir = self.project_root / "dist" / f"GUI_{version}"
        else:
            self.dist_dir = self.project_root / "dist" / "GUI"
        self.spec_file = self.project_root / "gui_app.spec"

    def run_command(self, command, cwd=None, description=""):
        """运行命令"""
        try:
            print(f"🔧 {description}")
            print(f"   执行: {command}")

            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                print("   ✓ 成功")
                if result.stdout.strip():
                    print(f"   输出: {result.stdout.strip()}")
                return True
            else:
                print(f"   ✗ 失败 (退出码: {result.returncode})")
                if result.stderr.strip():
                    print(f"   错误: {result.stderr.strip()}")
                return False

        except Exception as e:
            print(f"   ✗ 异常: {str(e)}")
            return False

    def check_dependencies(self):
        """检查依赖"""
        print("🔍 检查依赖...")

        # 检查Python
        if not self.run_command("python --version", description="检查Python"):
            return False

        # 检查pip
        if not self.run_command("python -m pip --version", description="检查pip"):
            return False

        # 检查PyInstaller
        try:
            import PyInstaller
            print("   ✓ PyInstaller 已安装")
        except ImportError:
            print("   ⚠ PyInstaller 未安装，正在安装...")
            if not self.run_command("pip install pyinstaller", description="安装PyInstaller"):
                return False

        # 检查tkinter
        try:
            import tkinter
            print("   ✓ tkinter 已安装")
        except ImportError:
            print("   ✗ tkinter 未安装")
            print("   💡 请安装Python时包含tkinter，或使用以下命令安装:")
            print("      Windows: pip install tk")
            print("      Linux: sudo apt-get install python3-tk")
            print("      macOS: 通常Python已包含tkinter")
            return False

        # 检查其他依赖
        required_modules = [
            'flask', 'flask_cors', 'yaml', 'bcrypt', 'pytz', 'tzlocal',
            'markdown', 'bs4', 'blake3', 'gmssl', 'qrcode', 'PIL',
            'html2text', 'lxml', 'Crypto', 'markdown_it'
        ]

        optional_modules = ['fitz', 'pdfkit']

        missing_required = []
        missing_optional = []

        for module in required_modules:
            try:
                __import__(module)
                print(f"   ✓ {module} 已安装")
            except ImportError:
                missing_required.append(module)
                print(f"   ⚠ {module} 未安装")

        for module in optional_modules:
            try:
                __import__(module)
                print(f"   ✓ {module} 已安装")
            except ImportError:
                missing_optional.append(module)
                print(f"   ⚠ {module} 未安装 (可选)")

        if missing_required:
            print(f"   📦 正在安装缺失的必需依赖: {', '.join(missing_required)}")
            if not self.run_command(f"pip install {' '.join(missing_required)}", description="安装缺失依赖"):
                return False

        if missing_optional:
            print(f"   📦 正在尝试安装可选依赖: {', '.join(missing_optional)}")
            if not self.run_command(f"pip install {' '.join(missing_optional)}", description="安装可选依赖"):
                print("   ⚠ 可选依赖安装失败，但将继续打包过程")

        return True

    def create_spec_file(self):
        """创建GUI版本的PyInstaller spec文件"""
        print("📝 创建PyInstaller配置...")

        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

# DevToolBox GUI版本打包配置
a = Analysis(
    ['gui_app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('backend', 'backend'),
        ('frontend', 'frontend'),
        ('templates', 'templates'),
        ('uploads', 'uploads'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'threading',
        'socket',
        'json',
        'argparse',
        'subprocess',
        'time',
        'backend.app',
        'backend.modules.file_upload',
        'backend.modules.json_tools',
        'backend.modules.yaml_tools',
        'backend.modules.markdown_tools',
        'backend.modules.base64_tools',
        'backend.modules.hash_tools',
        'backend.modules.url_tools',
        'backend.modules.timestamp_tools',
        'backend.modules.data_conversion',
        'backend.modules.qr_tools',
        'backend.modules.crypto_tools',
        'flask',
        'flask_cors',
        'yaml',
        'bcrypt',
        'pytz',
        'tzlocal',
        'bs4',
        'cryptography',
        'cryptography.hazmat.primitives.asymmetric',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.serialization',
        'cryptography.hazmat.primitives.hashes',
        'cryptography.hazmat.primitives.asymmetric.padding',
        'cryptography.hazmat.primitives.ciphers.algorithms',
        'cryptography.hazmat.primitives.ciphers.modes',
        'cryptography.hazmat.primitives.padding',
        'pycryptodome',
        'Crypto',
        'Crypto.Cipher',
        'Crypto.Hash',
        'Crypto.PublicKey',
        'Crypto.Signature',
        'Crypto.Util',
        'Crypto.Random',
        'Crypto.Protocol',
        'gmssl',
        'gmssl.func',
        'gmssl.sm2',
        'gmssl.sm4',
        'blake3',
        'qrcode',
        'qrcode.image',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'html2text',
        'lxml',
        'lxml.etree',
        'lxml.html',
        'markdown_it',
        'requests',
        'requests.adapters',
        'urllib3',
        'urllib3.util',
        'urllib3.poolmanager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DevToolBox_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''

        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)

        print(f"   ✓ 创建spec文件: {self.spec_file}")
        return True

    def build_gui(self):
        """构建GUI可执行文件"""
        print("🏗️  构建GUI可执行文件...")

        # 检查gui_app.py是否存在
        gui_app_file = self.project_root / "gui_app.py"
        if not gui_app_file.exists():
            print("   ✗ 未找到gui_app.py文件")
            return False

        # 使用PyInstaller打包
        if not self.run_command(f"python -c \"import PyInstaller.__main__; PyInstaller.__main__.run(['--clean', '{self.spec_file.name}'])\"", description="运行PyInstaller打包GUI应用"):
            return False

        # PyInstaller默认输出到dist目录，需要移动到dist_gui目录
        default_dist_dir = self.project_root / "dist"
        exe_name = "DevToolBox_GUI"
        if sys.platform == "win32":
            exe_name += ".exe"

        default_exe_path = default_dist_dir / exe_name
        target_exe_path = self.dist_dir / exe_name

        if default_exe_path.exists():
            # 确保目标目录存在
            self.dist_dir.mkdir(exist_ok=True)
            
            # 移动文件
            if target_exe_path.exists():
                target_exe_path.unlink()
            shutil.move(str(default_exe_path), str(target_exe_path))
            
            file_size = target_exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   ✓ 生成GUI可执行文件: {exe_name} ({file_size:.2f} MB)")
            
            # 如果指定了版本号，在可执行文件名中包含版本号
            if self.version:
                versioned_exe_name = f"DevToolBox_GUI_{self.version}"
                if sys.platform == "win32":
                    versioned_exe_name += ".exe"
                versioned_exe_path = self.dist_dir / versioned_exe_name
                
                # 复制文件并重命名
                shutil.copy2(str(target_exe_path), str(versioned_exe_path))
                print(f"   ✓ 创建带版本号的可执行文件: {versioned_exe_name}")
            
            return True
        else:
            print("   ✗ GUI可执行文件生成失败")
            return False

    def create_shortcut_script(self):
        """创建启动脚本"""
        print("📝 创建启动脚本...")

        if sys.platform == "win32":
            # Windows批处理文件
            script_content = '''@echo off
echo ========================================
echo    DevToolBox GUI - 开发工具箱
echo ========================================
echo.
echo 正在启动GUI应用...
echo.
cd /d "%~dp0"
start "" "DevToolBox_GUI.exe"
echo.
echo GUI应用已启动
echo.
pause
'''
            script_name = "启动DevToolBox_GUI.bat"
        else:
            # Linux/Mac脚本
            script_content = '''#!/bin/bash
echo "========================================"
echo "    DevToolBox GUI - 开发工具箱"
echo "========================================"
echo ""
echo "正在启动GUI应用..."
echo ""
./DevToolBox_GUI &
echo ""
echo "GUI应用已启动"
echo ""
read -p "按回车键退出..."
'''
            script_name = "启动DevToolBox_GUI.sh"

        script_path = self.dist_dir / script_name
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        if sys.platform != "win32":
            script_path.chmod(0o755)

        print(f"   ✓ 创建启动脚本: {script_name}")

    def create_readme(self):
        """创建GUI版本使用说明"""
        print("📖 创建GUI版本使用说明...")

        readme_content = '''# DevToolBox GUI - 开发工具箱 (桌面版)

## 🚀 快速开始

### 方法1：运行启动脚本
双击运行 `启动DevToolBox_GUI.bat` (Windows) 或 `启动DevToolBox_GUI.sh` (Linux/Mac)

### 方法2：直接运行
```bash
# Windows
DevToolBox_GUI.exe

# Linux/Mac
./DevToolBox_GUI
```

## 🖥️ GUI界面功能

DevToolBox GUI版本提供直观的桌面界面，包含以下功能：

### 📊 服务管理
- 实时显示服务状态
- 自动启动前后端服务
- 本地网络访问地址显示

### 📁 存储管理
- 可自定义文件存储路径
- 一键打开存储文件夹
- 自动创建必要的目录

### 🌐 网络服务
- 自动检测本机IP地址
- 支持局域网访问
- 显示前后端服务地址

## 🛠️ 集成的工具模块

GUI版本集成了完整的DevToolBox工具集：

### 📁 文件工具
- 文件上传和下载
- 多格式文件支持
- 文件分类管理

### 📊 数据工具
- JSON格式化/压缩/验证
- YAML格式化/压缩/验证
- Markdown转HTML/纯文本/语法验证

### 🔐 编码工具
- Base64编解码
- URL编解码
- 文件Base64处理

### 🔒 加密工具
- MD5/SHA256哈希生成
- HMAC签名
- PBKDF2密钥派生
- bcrypt密码哈希

### ⏰ 时间工具
- 时间戳转换
- 多时区显示
- 北京时间支持

## 📋 系统要求

- Windows 7+ / macOS 10.12+ / Ubuntu 16.04+
- Python 3.7+ (打包后无需Python环境)
- 至少512MB可用内存
- 至少100MB可用磁盘空间

## ⚙️ 配置说明

### 存储路径设置
1. 启动GUI应用
2. 点击"更改存储路径"按钮
3. 选择新的存储目录
4. 设置将自动保存

### 网络访问
- 本地访问: http://localhost:5000
- 网络访问: http://本机IP:5000
- 前端开发服务器: http://localhost:5173

## 🆘 故障排除

### GUI应用无法启动
- 检查是否所有依赖都已正确安装
- 确认Python版本兼容性
- 查看控制台错误信息

### 服务启动失败
- 检查端口5000和5173是否被占用
- 尝试以管理员权限运行
- 查看防火墙设置

### 前端服务启动失败
- 确认Node.js和npm已安装
- 检查frontend目录是否存在
- 手动运行: `cd frontend && npm install && npm run dev`

### 文件上传失败
- 检查存储目录权限
- 确认目录存在且可写
- 查看GUI界面中的存储路径设置

## 🔧 开发模式

如果需要开发模式运行：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行GUI应用
python gui_app.py
```

## 📞 技术支持

如遇到问题，请查看项目GitHub页面获取帮助。

---

**DevToolBox GUI** - 让开发更简单！🚀
'''

        readme_path = self.dist_dir / "README_GUI.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print("   ✓ 创建GUI版本使用说明: README_GUI.md")

    def cleanup(self):
        """清理临时文件"""
        print("🧹 清理临时文件...")

        # 删除build目录
        build_dir = self.project_root / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print("   ✓ 删除build目录")

        # 删除spec文件（保留在dist中）
        if self.spec_file.exists():
            self.spec_file.unlink()
            print("   ✓ 删除临时spec文件")

    def build(self):
        """执行完整GUI打包流程"""
        print("🚀 开始打包 DevToolBox GUI版本...")
        print("=" * 50)

        start_time = time.time()

        try:
            # 1. 检查依赖
            if not self.check_dependencies():
                return False

            # 2. 创建spec文件
            if not self.create_spec_file():
                return False

            # 3. 构建GUI应用
            if not self.build_gui():
                return False

            # 4. 创建启动脚本
            self.create_shortcut_script()

            # 5. 创建说明文档
            self.create_readme()

            # 6. 清理临时文件
            self.cleanup()

            # 计算耗时
            end_time = time.time()
            duration = end_time - start_time

            print("=" * 50)
            print("🎉 GUI版本打包完成！")
            print(f"⏱️  总耗时: {duration:.2f} 秒")
            print(f"📁 输出目录: {self.dist_dir}")
            print("\n📋 下一步操作:")
            print("1. 进入dist_gui目录")
            print("2. 运行启动脚本或直接运行DevToolBox_GUI可执行文件")
            print("3. 享受桌面版DevToolBox！")

            return True

        except Exception as e:
            print(f"❌ 打包过程中发生错误: {str(e)}")
            return False

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='DevToolBox GUI版本打包工具')
    parser.add_argument('--version', type=str, help='指定版本号，例如 v1.0.0')
    args = parser.parse_args()
    
    builder = DevToolBoxGUIBuilder(version=args.version)
    success = builder.build()

    if success:
        print("\n✅ DevToolBox GUI版本打包成功完成！")
        sys.exit(0)
    else:
        print("\n❌ DevToolBox GUI版本打包失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
