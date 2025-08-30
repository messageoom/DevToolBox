#!/usr/bin/env python3
"""
DevToolBox 前端打包脚本
"""

import os
import subprocess
import shutil
import sys

def run_command(command, cwd=None):
    """运行命令"""
    try:
        print(f"执行命令: {command}")
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:
            print("[OK] 命令执行成功")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"[ERROR] 命令执行失败 (退出码: {result.returncode})")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            return False

        return True
    except Exception as e:
        print(f"[ERROR] 命令执行异常: {str(e)}")
        return False

def build_frontend():
    """打包前端"""
    print("开始打包前端...")

    frontend_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(frontend_dir)
    dist_dir = os.path.join(frontend_dir, "dist")

    # 检查Node.js和npm
    if not run_command("node --version"):
        print("[ERROR] Node.js 未安装或不可用")
        return False

    if not run_command("npm --version"):
        print("[ERROR] npm 未安装或不可用")
        return False

    # 检查是否已安装依赖
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("安装前端依赖...")
        if not run_command("npm install", cwd=frontend_dir):
            return False
    else:
        print("前端依赖已存在，跳过安装")

    # 检查是否已构建
    if not os.path.exists(dist_dir):
        print("构建前端应用...")
        if not run_command("npm run build", cwd=frontend_dir):
            return False
    else:
        print("前端已构建，跳过构建步骤")

    # 检查构建结果
    dist_dir = os.path.join(frontend_dir, "dist")
    if not os.path.exists(dist_dir):
        print("[ERROR] 前端构建失败，未找到dist目录")
        return False

    print(f"[OK] 前端构建完成，输出目录: {dist_dir}")
    return True

if __name__ == "__main__":
    success = build_frontend()
    if success:
        print("前端打包成功！")
        sys.exit(0)
    else:
        print("前端打包失败！")
        sys.exit(1)
