#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
Database initialization script
"""

import os
import sys
import sqlite3
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(__file__))

from database import db_manager

def init_database():
    """初始化数据库"""
    print("=" * 50)
    print("数据库初始化")
    print("=" * 50)
    
    try:
        # 检查数据库文件是否存在
        if os.path.exists("douyin_data.db"):
            print("✅ 数据库文件已存在")
        else:
            print("📝 创建新的数据库文件...")
        
        # 初始化数据库（这会创建所有必要的表）
        db_manager.init_database()
        print("✅ 数据库表初始化完成")
        
        # 验证表是否创建成功
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"📊 数据库包含 {len(tables)} 个表:")
            for table in tables:
                print(f"  - {table[0]}")
        
        print("\n✅ 数据库初始化完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def reset_database():
    """重置数据库（删除所有数据）"""
    print("=" * 50)
    print("重置数据库")
    print("=" * 50)
    
    try:
        # 删除数据库文件
        if os.path.exists("douyin_data.db"):
            os.remove("douyin_data.db")
            print("🗑️  已删除旧数据库文件")
        
        # 重新初始化
        success = init_database()
        if success:
            print("✅ 数据库重置完成！")
        return success
        
    except Exception as e:
        print(f"❌ 数据库重置失败: {e}")
        return False

def show_database_info():
    """显示数据库信息"""
    print("=" * 50)
    print("数据库信息")
    print("=" * 50)
    
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取表信息
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"📊 数据库表数量: {len(tables)}")
            
            for table in tables:
                table_name = table[0]
                print(f"\n📋 表: {table_name}")
                
                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"  列数: {len(columns)}")
                
                # 获取记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  记录数: {count}")
                
                # 显示列信息
                for col in columns:
                    col_name, col_type, not_null, default_val, pk = col[1:6]
                    pk_str = " (主键)" if pk else ""
                    print(f"    - {col_name}: {col_type}{pk_str}")
        
        print("\n✅ 数据库信息显示完成！")
        return True
        
    except Exception as e:
        print(f"❌ 获取数据库信息失败: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库初始化工具")
    parser.add_argument("--reset", action="store_true", help="重置数据库（删除所有数据）")
    parser.add_argument("--info", action="store_true", help="显示数据库信息")
    
    args = parser.parse_args()
    
    if args.reset:
        success = reset_database()
    elif args.info:
        success = show_database_info()
    else:
        success = init_database()
    
    if success:
        print("\n✨ 操作完成！")
        return 0
    else:
        print("\n💥 操作失败！")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
