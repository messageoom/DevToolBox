#!/usr/bin/env python3
"""
DevToolBox 一键打包脚本

使用方法：
python build.py                    # 常规打包到 dist/CLI 目录
python build.py --version v2.0.0   # 带版本号打包到 dist/CLI_v2.0.0 目录
"""

import os
import sys
import io
import subprocess

# Fix Windows console encoding for emoji/CJK output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import shutil
import time
import argparse
import platform
from pathlib import Path


def get_platform_suffix():
    """Return platform suffix like '-windows-x64', '-macos-arm64', '-linux-x64'"""
    os_map = {'win32': 'windows', 'darwin': 'macos', 'linux': 'linux'}
    arch = platform.machine().lower()
    arch_map = {'x86_64': 'x64', 'amd64': 'x64', 'arm64': 'arm64', 'aarch64': 'arm64'}
    os_name = os_map.get(sys.platform, sys.platform)
    arch_name = arch_map.get(arch, arch)
    return f"-{os_name}-{arch_name}"


class DevToolBoxBuilder:
    def __init__(self, version=None):
        self.project_root = Path(__file__).parent
        self.version = version
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        if version:
            self.dist_dir = self.project_root / "dist" / f"CLI_{version}"
        else:
            self.dist_dir = self.project_root / "dist" / "CLI"
        self.frontend_dist = self.frontend_dir / "dist"

    def run_command(self, command, cwd=None, description=""):
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
        print("🔍 检查依赖...")
        if not self.run_command("python --version", description="检查Python"):
            return False
        if not self.run_command("python -m pip --version", description="检查pip"):
            return False
        try:
            import PyInstaller
            print("   ✓ PyInstaller 已安装")
        except ImportError:
            print("   ⚠ PyInstaller 未安装，正在安装...")
            if not self.run_command("pip install pyinstaller", description="安装PyInstaller"):
                return False
        if self.frontend_dir.exists():
            if not self.run_command("node --version", description="检查Node.js"):
                print("   ⚠ Node.js 未找到，将跳过前端构建")
                self.skip_frontend = True
            else:
                self.skip_frontend = False
        else:
            self.skip_frontend = True
        return True

    def build_frontend(self):
        if self.skip_frontend:
            print("⏭️  跳过前端构建")
            return True
        print("🎨 构建前端应用...")
        if not self.frontend_dir.exists():
            print("   ⚠ 前端目录不存在，跳过前端构建")
            return True
        build_script = self.frontend_dir / "build.py"
        if build_script.exists():
            try:
                subprocess.run(f"python {build_script}", shell=True, cwd=self.frontend_dir, check=True)
                print("   ✓ 前端构建脚本执行成功")
            except subprocess.CalledProcessError as e:
                print(f"   ✗ 前端构建脚本执行失败 (退出码: {e.returncode})")
                return False
        else:
            if not self.run_command("npm install", cwd=self.frontend_dir, description="安装前端依赖"):
                return False
            if not self.run_command("npm run build", cwd=self.frontend_dir, description="构建前端应用"):
                return False
        if not self.frontend_dist.exists():
            print("   ✗ 前端构建失败，未找到dist目录")
            return False
        print(f"   ✓ 前端构建完成: {self.frontend_dist}")
        return True

    def prepare_backend(self):
        print("📦 准备后端打包环境...")
        if self.frontend_dist.exists():
            backend_static = self.backend_dir / "static"
            backend_static.mkdir(exist_ok=True)
            frontend_dest = backend_static / "frontend"
            if frontend_dest.exists():
                shutil.rmtree(frontend_dest)
            print(f"   复制前端文件: {self.frontend_dist} -> {frontend_dest}")
            shutil.copytree(self.frontend_dist, frontend_dest)
            print("   ✓ 前端文件复制完成")
        uploads_dir = self.backend_dir / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        return True

    def build_backend(self):
        print("🏗️  构建后端可执行文件...")
        spec_file = self.project_root / "app.spec"
        if not spec_file.exists():
            print("   ✗ 未找到app.spec文件")
            return False
        if not self.run_command(
            f'python -c "import PyInstaller.__main__; PyInstaller.__main__.run([\'--clean\', \'{spec_file.name}\'])"',
            description="运行PyInstaller打包"
        ):
            return False

        default_dist_dir = self.project_root / "dist"
        pyinstaller_name = "DevToolBox.exe" if sys.platform == "win32" else "DevToolBox"

        # Target name with platform suffix
        platform_suffix = get_platform_suffix()
        ext = ".exe" if sys.platform == "win32" else ""
        final_name = f"DevToolBox{platform_suffix}{ext}"

        default_exe_path = default_dist_dir / pyinstaller_name
        target_exe_path = self.dist_dir / final_name

        if default_exe_path.exists():
            self.dist_dir.mkdir(exist_ok=True)
            if target_exe_path.exists():
                target_exe_path.unlink()
            shutil.move(str(default_exe_path), str(target_exe_path))
            file_size = target_exe_path.stat().st_size / (1024 * 1024)
            print(f"   ✓ 生成可执行文件: {final_name} ({file_size:.2f} MB)")
            return True
        else:
            print("   ✗ 可执行文件生成失败")
            return False

    def cleanup(self):
        print("🧹 清理临时文件...")
        build_dir = self.project_root / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print("   ✓ 删除build目录")
        if self.frontend_dist.exists():
            shutil.rmtree(self.frontend_dist)
            print("   ✓ 删除前端dist目录")

    def create_shortcut_script(self):
        print("📝 创建启动脚本...")
        exe_files = list(self.dist_dir.glob("DevToolBox*"))
        exe_name = exe_files[0].name if exe_files else "DevToolBox"

        if sys.platform == "win32":
            script_content = (
                '@echo off\n'
                'cd /d "%~dp0"\n'
                f'start "" "{exe_name}"\n'
            )
            script_name = "启动DevToolBox.bat"
        else:
            script_content = (
                '#!/bin/bash\n'
                'cd "$(dirname "$0")"\n'
                f'chmod +x "{exe_name}"\n'
                f'./"{exe_name}" &\n'
            )
            script_name = "启动DevToolBox.sh"

        script_path = self.dist_dir / script_name
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        if sys.platform != "win32":
            script_path.chmod(0o755)
        print(f"   ✓ 创建启动脚本: {script_name}")

    def create_readme(self):
        print("📖 创建使用说明...")
        readme_content = """# DevToolBox - 开发工具箱

## 快速开始

双击运行可执行文件，浏览器将自动打开。
首次访问会自动生成安全 Token，确保只有本机用户可以访问。

### 系统托盘
启动后最小化到系统托盘，右键菜单：
- 打开浏览器
- 复制访问地址
- 退出

### 手动运行
```bash
# Windows
DevToolBox-windows-x64.exe

# macOS
./DevToolBox-macos-arm64

# Linux
./DevToolBox-linux-x64
```

## 功能介绍

DevToolBox 集成了 20 个开发工具：

- 文件上传 | JSON/YAML/Markdown | Base64/URL 编码
- 哈希/加密解密 | 时间戳/时间计算 | 二维码
- UUID/密码/API Key 生成 | JWT 调试器 | 文本对比

## 系统要求

- Windows 7+ / macOS 10.12+ / Ubuntu 16.04+
- 无需额外安装 Python 或其他依赖

## 故障排除

- 服务无法启动：检查端口 5000 是否被占用
- 无法访问网页：通过托盘菜单"复制访问地址"获取带 Token 的完整 URL

## 技术支持

https://github.com/messageoom/DevToolBox/issues
"""
        readme_path = self.dist_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("   ✓ 创建使用说明: README.md")

    def build(self):
        print("🚀 开始打包 DevToolBox...")
        print("=" * 50)
        start_time = time.time()
        try:
            if not self.check_dependencies():
                return False
            if not self.build_frontend():
                return False
            if not self.prepare_backend():
                return False
            if not self.build_backend():
                return False
            self.create_shortcut_script()
            self.create_readme()
            self.cleanup()
            end_time = time.time()
            duration = end_time - start_time
            print("=" * 50)
            print("🎉 打包完成！")
            print(f"⏱️  总耗时: {duration:.2f} 秒")
            print(f"📁 输出目录: {self.dist_dir}")
            print("\n📋 下一步操作:")
            print("1. 进入dist目录")
            print("2. 运行启动脚本或直接运行DevToolBox可执行文件")
            print("3. 在浏览器中访问 http://localhost:5000")
            return True
        except Exception as e:
            print(f"❌ 打包过程中发生错误: {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(description='DevToolBox 打包工具')
    parser.add_argument('--version', type=str, help='指定版本号，例如 v2.0.0')
    args = parser.parse_args()
    builder = DevToolBoxBuilder(version=args.version)
    success = builder.build()
    if success:
        print("\n✅ DevToolBox 打包成功完成！")
        sys.exit(0)
    else:
        print("\n❌ DevToolBox 打包失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
