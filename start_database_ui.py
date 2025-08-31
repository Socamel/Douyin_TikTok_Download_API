#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动数据库管理界面
Start Database Management UI
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """启动Streamlit数据库管理界面"""
    
    print("🚀 启动数据库管理界面...")
    print("📱 界面将在浏览器中打开: http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止服务")
    
    # 运行streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "streamlit_database_ui.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    main()
