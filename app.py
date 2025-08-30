# DevToolBox - 开发工具箱主应用
# 一键启动前后端服务

from backend.app import create_app
import argparse
import socket
import subprocess
import sys
import os
import threading
import time

def start_frontend(port=5173):
    """启动前端服务"""
    try:
        print(f"正在启动前端服务 (端口 {port})...")
        frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')

        # 检查前端目录是否存在
        if not os.path.exists(frontend_dir):
            print("⚠️ 前端目录不存在，跳过前端服务启动")
            return False

        # 检查 package.json 是否存在
        package_json = os.path.join(frontend_dir, 'package.json')
        if not os.path.exists(package_json):
            print("⚠️ 前端 package.json 不存在，跳过前端服务启动")
            return False

        # 尝试多种方式启动前端服务
        commands = [
            ['npm', 'run', 'dev', '--', '--port', str(port), '--host'],
            ['npx', 'vite', '--port', str(port), '--host'],
        ]

        for cmd in commands:
            try:
                print(f"尝试命令: {' '.join(cmd)}")
                process = subprocess.Popen(
                    cmd,
                    cwd=frontend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True  # 在 Windows 上可能需要 shell=True
                )

                # 等待前端服务启动
                time.sleep(5)

                if process.poll() is None:
                    print(f"✓ 前端服务已启动: http://localhost:{port}")
                    return True
                else:
                    stdout, stderr = process.communicate()
                    print(f"命令失败: {stderr}")
                    continue

            except FileNotFoundError:
                print(f"命令不可用: {' '.join(cmd)}")
                continue
            except Exception as e:
                print(f"启动失败: {e}")
                continue

        print("❌ 所有前端启动方式都失败了")
        print("💡 提示: 请手动启动前端服务")
        print(f"   cd frontend && npm run dev -- --port {port} --host")
        return False

    except Exception as e:
        print(f"启动前端服务时出错: {e}")
        return False

def start_backend(host='0.0.0.0', port=5000, debug=False):
    """启动后端服务"""
    try:
        print(f"正在启动后端服务 (端口 {port})...")

        # 创建应用实例
        app = create_app()

        # 获取本机IP地址
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        print("=== DevToolBox - 开发工具箱 ===")
        print(f"后端服务器将在以下地址运行: http://{local_ip}:{port}")
        print("API 端点:")
        print(f"  - 文件上传: http://{local_ip}:{port}/api/file-upload")
        print(f"  - JSON工具: http://{local_ip}:{port}/api/json-tools")
        print(f"  - YAML工具: http://{local_ip}:{port}/api/yaml-tools")
        print(f"  - 时间戳工具: http://{local_ip}:{port}/api/timestamp-tools")
        print(f"  - Base64工具: http://{local_ip}:{port}/api/base64-tools")
        print(f"  - 哈希工具: http://{local_ip}:{port}/api/hash-tools")
        print(f"  - URL工具: http://{local_ip}:{port}/api/url-tools")
        print(f"  - Markdown工具: http://{local_ip}:{port}/api/markdown-tools")
        print("=" * 50)

        # 启动服务器
        app.run(host=host, port=port, debug=debug)

    except Exception as e:
        print(f"启动后端服务时出错: {e}")

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='DevToolBox - 开发工具箱')
    parser.add_argument('--backend-port', type=int, default=5000, help='指定后端服务器端口 (默认: 5000)')
    parser.add_argument('--frontend-port', type=int, default=5173, help='指定前端服务器端口 (默认: 5173)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='指定后端服务器主机 (默认: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='启用后端调试模式')
    parser.add_argument('--no-frontend', action='store_true', help='不启动前端服务')
    args = parser.parse_args()

    print("🚀 启动 DevToolBox - 开发工具箱")
    print("=" * 50)

    # 启动前端服务（在新线程中）
    if not args.no_frontend:
        frontend_thread = threading.Thread(
            target=start_frontend,
            args=(args.frontend_port,),
            daemon=True
        )
        frontend_thread.start()
        time.sleep(1)  # 给前端一点启动时间

    # 启动后端服务（在主线程中）
    try:
        start_backend(args.host, args.backend_port, args.debug)
    except KeyboardInterrupt:
        print("\n👋 DevToolBox 已停止")
    except Exception as e:
        print(f"运行时出错: {e}")
