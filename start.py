# -*- coding: utf-8 -*-
# ==============================================================================
# Copyright (C) 2021 Evil0ctal
#
# This file is part of the Douyin_TikTok_Download_API project.
#
# This project is licensed under the Apache License 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
# 　　　　 　　  ＿＿
# 　　　 　　 ／＞　　フ
# 　　　 　　| 　_　 _ l
# 　 　　 　／` ミ＿xノ
# 　　 　 /　　　 　 |       Feed me Stars ⭐
# 　　　 /　 ヽ　　 ﾉ
# 　 　 │　　|　|　|
# 　／￣|　　 |　|　|
# 　| (￣ヽ＿_ヽ_)__)
# 　＼二つ
# ==============================================================================
#
# Contributor Link, Thanks for your contribution:
# - https://github.com/Evil0ctal
# - https://github.com/Johnserf-Seed
# - https://github.com/Evil0ctal/Douyin_TikTok_Download_API/graphs/contributors
#
# ==============================================================================

import sys
import os
import uvicorn
from pathlib import Path

# 导入路径配置
from path_config import setup_project_paths, get_config_path

def main():
    """
    主启动函数
    """
    try:
        # 设置项目路径
        setup_project_paths()
        
        # 检查配置文件
        config_path = get_config_path()
        if not config_path.exists():
            print(f"错误: 配置文件不存在: {config_path}")
            sys.exit(1)
        
        # 从配置文件读取配置
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        host = config['API']['Host_IP']
        port = config['API']['Host_Port']
        
        print(f"启动服务器: {host}:{port}")
        print(f"API文档: http://{host}:{port}/docs")
        print(f"ReDoc文档: http://{host}:{port}/redoc")
        
        # 启动服务器
        uvicorn.run(
            "app.main:app",  # 使用导入字符串方式
            host=host,
            port=port,
            reload=True,
            log_level="warning",  # 改为warning级别，减少日志输出
            # 添加连接复用配置
            limit_concurrency=1000,
            limit_max_requests=1000,
            timeout_keep_alive=5,
            access_log=False  # 禁用访问日志
        )
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"启动错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
