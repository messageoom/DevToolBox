#!/usr/bin/env python3
"""
DevToolBox 一键打包脚本

功能：
1. 构建前端应用
2. 复制前端文件到后端
3. 使用PyInstaller打包后端
4. 生成最终的可执行文件
5. 支持版本号打包用于GitHub Releases

使用方法：
python build.py [--version VERSION]

参数：
--version VERSION  指定版本号，例如 v1.0.0

示例：
python build.py                    # 常规打包到 dist 目录
python build.py --version v1.0.0   # 带版本号打包到 dist_v1.0.0 目录
"""

import os
import sys
import subprocess
import shutil
import time
import argparse
from pathlib import Path

class DevToolBoxBuilder:
    def __init__(self, version=None):
        self.project_root = Path(__file__).parent
        self.version = version
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        # 如果指定了版本号，则使用版本号作为目录名
        if version:
            self.dist_dir = self.project_root / "dist" / f"CLI_{version}"
        else:
            self.dist_dir = self.project_root / "dist" / "CLI"
        self.frontend_dist = self.frontend_dir / "dist"

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

        # 检查Node.js (如果需要前端构建)
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
        """构建前端"""
        if self.skip_frontend:
            print("⏭️  跳过前端构建")
            return True

        print("🎨 构建前端应用...")

        # 检查前端目录
        if not self.frontend_dir.exists():
            print("   ⚠ 前端目录不存在，跳过前端构建")
            return True

        # 运行前端构建脚本
        build_script = self.frontend_dir / "build.py"
        if build_script.exists():
            print(f"   执行: python {build_script}")
            try:
                result = subprocess.run(
                    f"python {build_script}",
                    shell=True,
                    cwd=self.frontend_dir,
                    check=True
                )
                print("   ✓ 前端构建脚本执行成功")
            except subprocess.CalledProcessError as e:
                print(f"   ✗ 前端构建脚本执行失败 (退出码: {e.returncode})")
                return False
        else:
            # 直接使用npm构建
            if not self.run_command("npm install", cwd=self.frontend_dir, description="安装前端依赖"):
                return False

            if not self.run_command("npm run build", cwd=self.frontend_dir, description="构建前端应用"):
                return False

        # 检查构建结果
        if not self.frontend_dist.exists():
            print("   ✗ 前端构建失败，未找到dist目录")
            return False

        print(f"   ✓ 前端构建完成: {self.frontend_dist}")
        return True

    def prepare_backend(self):
        """准备后端打包环境"""
        print("📦 准备后端打包环境...")

        # 复制前端文件到后端
        if self.frontend_dist.exists():
            backend_static = self.backend_dir / "static"
            backend_static.mkdir(exist_ok=True)

            # 复制前端dist到后端static
            frontend_dest = backend_static / "frontend"
            if frontend_dest.exists():
                shutil.rmtree(frontend_dest)

            print(f"   复制前端文件: {self.frontend_dist} -> {frontend_dest}")
            shutil.copytree(self.frontend_dist, frontend_dest)
            print("   ✓ 前端文件复制完成")

        # 确保uploads目录存在
        uploads_dir = self.backend_dir / "uploads"
        uploads_dir.mkdir(exist_ok=True)

        return True

    def build_backend(self):
        """构建后端可执行文件"""
        print("🏗️  构建后端可执行文件...")

        # 检查app.spec文件
        spec_file = self.project_root / "app.spec"
        if not spec_file.exists():
            print("   ✗ 未找到app.spec文件")
            return False

        # 使用PyInstaller打包
        if not self.run_command(f"python -c \"import PyInstaller.__main__; PyInstaller.__main__.run(['--clean', '{spec_file.name}'])\"", description="运行PyInstaller打包"):
            return False

        # PyInstaller默认输出到dist目录，需要移动到目标目录
        default_dist_dir = self.project_root / "dist"
        exe_name = "DevToolBox"
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
            print(f"   ✓ 生成可执行文件: {exe_name} ({file_size:.2f} MB)")
            
            # 如果指定了版本号，在可执行文件名中包含版本号
            if self.version:
                versioned_exe_name = f"DevToolBox_{self.version}"
                if sys.platform == "win32":
                    versioned_exe_name += ".exe"
                versioned_exe_path = self.dist_dir / versioned_exe_name
                
                # 复制文件并重命名
                shutil.copy2(str(target_exe_path), str(versioned_exe_path))
                print(f"   ✓ 创建带版本号的可执行文件: {versioned_exe_name}")
            
            return True
        else:
            print("   ✗ 可执行文件生成失败")
            return False

    def cleanup(self):
        """清理临时文件"""
        print("🧹 清理临时文件...")

        # 删除build目录
        build_dir = self.project_root / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print("   ✓ 删除build目录")

        # 删除前端dist目录（保留在backend/static中的副本）
        if self.frontend_dist.exists():
            shutil.rmtree(self.frontend_dist)
            print("   ✓ 删除前端dist目录")

    def create_shortcut_script(self):
        """创建启动脚本"""
        print("📝 创建启动脚本...")

        if sys.platform == "win32":
            # Windows批处理文件
            script_content = '''@echo off
echo ========================================
echo    DevToolBox - 开发工具箱
echo ========================================
echo.
echo 正在启动服务...
echo.
cd /d "%~dp0"
start "" "DevToolBox.exe"
echo.
echo 服务已启动，请在浏览器中访问:
echo http://localhost:5000
echo.
pause
'''
            script_name = "启动DevToolBox.bat"
        else:
            # Linux/Mac脚本
            script_content = '''#!/bin/bash
echo "========================================"
echo "    DevToolBox - 开发工具箱"
echo "========================================"
echo ""
echo "正在启动服务..."
echo ""
./DevToolBox &
echo ""
echo "服务已启动，请在浏览器中访问:"
echo "http://localhost:5000"
echo ""
read -p "按回车键退出..."
'''
            script_name = "启动DevToolBox.sh"

        script_path = self.dist_dir / script_name
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        if sys.platform != "win32":
            script_path.chmod(0o755)

        print(f"   ✓ 创建启动脚本: {script_name}")

    def create_readme(self):
        """创建使用说明"""
        print("📖 创建使用说明...")

        readme_content = '''# DevToolBox - 开发工具箱

## 🚀 快速开始

### 方法1：运行启动脚本
双击运行 `启动DevToolBox.bat` (Windows) 或 `启动DevToolBox.sh` (Linux/Mac)

### 方法2：直接运行
```bash
# Windows
DevToolBox.exe

# Linux/Mac
./DevToolBox
```

### 访问应用
启动后，在浏览器中访问：http://localhost:5000

## 🛠️ 功能介绍

DevToolBox 集成了以下8大工具模块：

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
- 无需额外安装Python或其他依赖

## 🆘 故障排除

### 服务无法启动
- 检查端口5000是否被占用
- 尝试以管理员权限运行

### 无法访问网页
- 确认服务已正常启动
- 检查防火墙设置
- 尝试使用 http://127.0.0.1:5000

### 文件上传失败
- 检查uploads目录权限
- 确认文件大小不超过限制

## 📞 技术支持

如遇到问题，请查看项目GitHub页面获取帮助。

---

**DevToolBox** - 让开发更简单！🚀
'''

        readme_path = self.dist_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print("   ✓ 创建使用说明: README.md")

    def build(self):
        """执行完整打包流程"""
        print("🚀 开始打包 DevToolBox...")
        print("=" * 50)

        start_time = time.time()

        try:
            # 1. 检查依赖
            if not self.check_dependencies():
                return False

            # 2. 构建前端
            if not self.build_frontend():
                return False

            # 3. 准备后端
            if not self.prepare_backend():
                return False

            # 4. 构建后端
            if not self.build_backend():
                return False

            # 5. 创建启动脚本
            self.create_shortcut_script()

            # 6. 创建说明文档
            self.create_readme()

            # 7. 清理临时文件
            self.cleanup()

            # 计算耗时
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
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='DevToolBox 打包工具')
    parser.add_argument('--version', type=str, help='指定版本号，例如 v1.0.0')
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
