import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import socket
import os
import sys
import json
import argparse
import subprocess
import time
from backend.app import create_app

class DevToolBoxGUI:
    def __init__(self, root, backend_port=5000, frontend_port=5173):
        self.root = root
        self.root.title("DevToolBox - 开发工具箱")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        # 设置窗口图标（如果有的话）
        try:
            # 尝试设置窗口图标
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except:
            pass

        # 获取本机IP地址
        hostname = socket.gethostname()
        self.local_ip = socket.gethostbyname(hostname)
        self.backend_port = backend_port
        self.frontend_port = frontend_port
        self.backend_address = f"http://{self.local_ip}:{self.backend_port}"
        self.frontend_address = f"http://localhost:{self.frontend_port}"

        # 服务进程
        self.backend_process = None
        self.frontend_process = None

        # 创建Flask应用实例
        self.app = create_app()

        # 获取文件存储地址
        self.load_settings()

        # 创建UI
        self.create_widgets()

        # 启动服务
        self.start_services()
        
    def load_settings(self):
        """加载用户设置"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe文件
            application_path = os.path.dirname(sys.executable)
        else:
            # 如果是python脚本
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        self.settings_file = os.path.join(application_path, "settings.json")
        
        # 默认存储路径
        self.storage_path = os.path.join(application_path, "uploads")
        
        # 确保默认的uploads目录存在
        if not os.path.exists(self.storage_path):
            try:
                os.makedirs(self.storage_path)
            except Exception as e:
                print(f"创建默认上传目录时出错: {e}")
        
        # 如果设置文件存在，加载设置
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'storage_path' in settings:
                        self.storage_path = settings['storage_path']
                        # 确保用户设置的存储路径存在
                        if not os.path.exists(self.storage_path):
                            try:
                                os.makedirs(self.storage_path)
                            except Exception as e:
                                print(f"创建用户设置的上传目录时出错: {e}")
                                # 如果创建失败，回退到默认路径
                                self.storage_path = os.path.join(application_path, "uploads")
            except:
                pass
        
        # 更新Flask应用的上传目录
        self.app.config['UPLOAD_FOLDER'] = self.storage_path
        
    def create_widgets(self):
        # 设置样式
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 16, "bold"), foreground="#2c3e50")
        style.configure("Section.TLabel", font=("Arial", 10, "bold"), foreground="#34495e")
        style.configure("Status.TLabel", font=("Arial", 10))
        style.configure("Action.TButton", font=("Arial", 10, "bold"))
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重，使窗口可调整大小
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="DevToolBox - 开发工具箱", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 30), sticky=tk.W)
        
        # 服务地址框架
        service_frame = ttk.LabelFrame(main_frame, text="服务信息", padding="10")
        service_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        service_frame.columnconfigure(1, weight=1)
        
        # 服务地址
        service_label = ttk.Label(service_frame, text="后端地址:", style="Section.TLabel")
        service_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.service_address_var = tk.StringVar(value=self.backend_address)
        service_entry = ttk.Entry(service_frame, textvariable=self.service_address_var, state="readonly", font=("Consolas", 10))
        service_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 文件存储地址框架
        storage_frame = ttk.LabelFrame(main_frame, text="存储设置", padding="10")
        storage_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        storage_frame.columnconfigure(1, weight=1)
        
        # 文件存储地址
        storage_label = ttk.Label(storage_frame, text="存储路径:", style="Section.TLabel")
        storage_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.storage_path_var = tk.StringVar(value=self.storage_path)
        storage_entry = ttk.Entry(storage_frame, textvariable=self.storage_path_var, state="readonly", font=("Consolas", 10))
        storage_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 更改路径按钮
        change_path_button = ttk.Button(storage_frame, text="更改存储路径", command=self.change_storage_path, style="Action.TButton")
        change_path_button.grid(row=2, column=0, pady=(0, 5), sticky=tk.W)
        
        # 状态框架
        status_frame = ttk.LabelFrame(main_frame, text="服务状态", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 状态标签
        self.status_label = ttk.Label(status_frame, text="服务运行中...", foreground="green", style="Status.TLabel")
        self.status_label.grid(row=0, column=0, pady=(5, 5), sticky=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 20))
        
        # 关闭按钮
        close_button = ttk.Button(button_frame, text="关闭服务", command=self.close_service, style="Action.TButton")
        close_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 打开存储文件夹按钮
        open_folder_button = ttk.Button(button_frame, text="打开存储文件夹", command=self.open_storage_folder, style="Action.TButton")
        open_folder_button.pack(side=tk.RIGHT)
        
        # 添加一些间距
        main_frame.rowconfigure(5, weight=1)
        
        # 底部信息
        info_label = ttk.Label(main_frame, text="DevToolBox v1.0 - 开发工具箱", font=("Arial", 8), foreground="#7f8c8d")
        info_label.grid(row=6, column=0, columnspan=3, pady=(0, 10), sticky=tk.S)
        
    def start_services(self):
        """启动前后端服务"""
        print("🚀 启动 DevToolBox 服务...")

        # 启动前端服务
        self.start_frontend_service()

        # 启动后端服务
        self.start_backend_service()

    def start_frontend_service(self):
        """启动前端服务"""
        try:
            print(f"正在启动前端服务 (端口 {self.frontend_port})...")
            frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

            if not os.path.exists(frontend_dir):
                print("⚠️ 前端目录不存在，跳过前端服务启动")
                self.update_status("后端服务运行中 (前端未启动)")
                return

            # 检查 package.json 是否存在
            package_json = os.path.join(frontend_dir, 'package.json')
            if not os.path.exists(package_json):
                print("⚠️ 前端 package.json 不存在，跳过前端服务启动")
                self.update_status("后端服务运行中 (前端未启动)")
                return

            # 尝试多种方式启动前端服务
            commands = [
                ['npm', 'run', 'dev', '--', '--port', str(self.frontend_port), '--host'],
                ['npx', 'vite', '--port', str(self.frontend_port), '--host'],
            ]

            for cmd in commands:
                try:
                    print(f"尝试命令: {' '.join(cmd)}")
                    self.frontend_process = subprocess.Popen(
                        cmd,
                        cwd=frontend_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        shell=True  # 在 Windows 上可能需要 shell=True
                    )

                    # 等待前端服务启动
                    time.sleep(5)

                    if self.frontend_process.poll() is None:
                        print(f"✓ 前端服务已启动: {self.frontend_address}")
                        self.update_status("前后端服务运行中...")
                        return
                    else:
                        stdout, stderr = self.frontend_process.communicate()
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
            print(f"   cd frontend && npm run dev -- --port {self.frontend_port} --host")
            self.update_status("后端服务运行中 (前端启动失败)")

        except Exception as e:
            print(f"启动前端服务时出错: {e}")
            self.update_status("前端服务启动出错")

    def start_backend_service(self):
        """启动后端服务"""
        try:
            print(f"正在启动后端服务 (端口 {self.backend_port})...")

            def run_flask():
                try:
                    self.app.run(host='0.0.0.0', port=self.backend_port, debug=False, use_reloader=False)
                except Exception as e:
                    print(f"后端服务运行出错: {e}")

            backend_thread = threading.Thread(target=run_flask, daemon=True)
            backend_thread.start()

            print(f"✓ 后端服务已启动: {self.backend_address}")
            print("API 端点:")
            print(f"  - 文件上传: {self.backend_address}/api/file-upload")
            print(f"  - JSON工具: {self.backend_address}/api/json-tools")
            print(f"  - YAML工具: {self.backend_address}/api/yaml-tools")
            print(f"  - 时间戳工具: {self.backend_address}/api/timestamp-tools")
            print(f"  - Base64工具: {self.backend_address}/api/base64-tools")
            print(f"  - 哈希工具: {self.backend_address}/api/hash-tools")
            print(f"  - URL工具: {self.backend_address}/api/url-tools")
            print(f"  - Markdown工具: {self.backend_address}/api/markdown-tools")

        except Exception as e:
            print(f"启动后端服务时出错: {e}")
            self.update_status("后端服务启动出错")

    def update_status(self, status):
        """更新状态显示"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status)
        
    def save_settings(self):
        """保存用户设置"""
        settings = {
            'storage_path': self.storage_path
        }
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置时出错: {e}")
    
    def change_storage_path(self):
        """更改文件存储路径"""
        new_path = filedialog.askdirectory(
            title="选择文件存储路径",
            initialdir=self.storage_path
        )
        
        if new_path:
            # 检查路径是否有效
            if os.path.exists(new_path) or messagebox.askyesno("创建目录", f"目录 {new_path} 不存在，是否创建？"):
                try:
                    # 如果目录不存在则创建
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
                    
                    # 更新存储路径
                    self.storage_path = new_path
                    self.storage_path_var.set(new_path)
                    
                    # 保存设置
                    self.save_settings()
                    
                    # 更新Flask应用的上传目录
                    self.app.config['UPLOAD_FOLDER'] = new_path
                    
                    messagebox.showinfo("成功", "存储路径已更新！")
                except Exception as e:
                    messagebox.showerror("错误", f"无法设置存储路径: {e}")
    
    def open_storage_folder(self):
        """打开存储文件夹"""
        try:
            if os.path.exists(self.storage_path):
                os.startfile(self.storage_path)
            else:
                # 如果目录不存在则创建
                os.makedirs(self.storage_path)
                os.startfile(self.storage_path)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")
    
    def close_service(self):
        """关闭服务"""
        self.status_label.config(text="服务已停止", foreground="red")
        # 这里可以添加更多清理代码
        self.root.after(1000, self.root.destroy)  # 1秒后关闭窗口

def main(backend_port=5000, frontend_port=5173):
    root = tk.Tk()
    app = DevToolBoxGUI(root, backend_port, frontend_port)
    root.mainloop()

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='DevToolBox - 开发工具箱 GUI')
    parser.add_argument('--backend-port', type=int, default=5000, help='指定后端服务器端口 (默认: 5000)')
    parser.add_argument('--frontend-port', type=int, default=5173, help='指定前端服务器端口 (默认: 5173)')
    args = parser.parse_args()

    main(args.backend_port, args.frontend_port)
