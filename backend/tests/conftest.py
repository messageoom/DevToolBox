import os
import sys

# 让测试可以用 `from utils.xxx` / `from modules.xxx` 导入后端模块
# (与后端从 backend/ 目录运行时的 import 路径一致)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
