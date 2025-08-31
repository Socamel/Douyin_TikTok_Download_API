# -*- coding: utf-8 -*-
"""
路径配置文件
统一管理项目路径，避免使用sys.path.append
"""

import os
import sys
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()

def setup_project_paths():
    """
    设置项目路径，将必要的目录添加到Python路径中
    """
    # 添加项目根目录到Python路径
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    
    # 添加其他必要的路径
    paths_to_add = [
        PROJECT_ROOT / "app",
        PROJECT_ROOT / "crawlers",
    ]
    
    for path in paths_to_add:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

def get_project_root():
    """
    获取项目根目录
    """
    return PROJECT_ROOT

def get_config_path():
    """
    获取配置文件路径
    """
    return PROJECT_ROOT / "config.yaml"

def get_database_path():
    """
    获取数据库文件路径
    """
    return PROJECT_ROOT / "douyin_data.db"

# 自动设置路径
setup_project_paths()
