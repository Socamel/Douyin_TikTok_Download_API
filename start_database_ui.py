#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理界面 - Streamlit版本
Database Management UI using Streamlit
"""

import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="数据库管理界面",
    page_icon="🗄️",
    layout="wide"
)

# 设置项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import db_manager

def main():
    st.title("🗄️ SQLite数据库管理界面")
    st.markdown("---")
    
    # 侧边栏导航
    st.sidebar.title("功能导航")
    page = st.sidebar.selectbox(
        "选择功能",
        ["📊 数据概览", "👥 用户管理", "🍪 Cookie管理", "🎥 视频管理", "🔧 数据库维护"]
    )
    
    if page == "📊 数据概览":
        show_dashboard()
    elif page == "👥 用户管理":
        show_users_management()
    elif page == "🍪 Cookie管理":
        show_cookies_management()
    elif page == "🎥 视频管理":
        show_videos_management()
    elif page == "🔧 数据库维护":
        show_database_maintenance()

def show_dashboard():
    """显示数据概览"""
    st.header("📊 数据概览")
    
    # 获取数据库统计
    stats = db_manager.get_database_stats()
    
    # 显示统计指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("用户数量", stats['user_count'])
    
    with col2:
        st.metric("视频数量", stats['video_count'])
    
    with col3:
        st.metric("活跃Cookie", stats['active_cookie_count'])
    
    with col4:
        st.metric("总Cookie数", stats['total_cookie_count'])
    
    st.markdown("---")
    
    # 显示最近用户
    st.subheader("👥 最近用户")
    users = db_manager.get_all_users()[:10]
    if users:
        users_df = pd.DataFrame(users)
        st.dataframe(users_df, width='stretch')
    else:
        st.info("暂无用户数据")

def show_users_management():
    """显示用户管理"""
    st.header("👥 用户管理")
    
    # 添加用户
    with st.expander("➕ 添加用户"):
        with st.form("add_user_form"):
            user_id = st.text_input("用户ID *", placeholder="MS4wLjABAAAA...")
            nickname = st.text_input("昵称", placeholder="用户昵称")
            follower_count = st.number_input("粉丝数", min_value=0, value=0)
            video_count = st.number_input("视频数", min_value=0, value=0)
            
            submitted = st.form_submit_button("添加用户")
            
            if submitted and user_id:
                user_data = {
                    'user_id': user_id,
                    'username': nickname,
                    'nickname': nickname,
                    'follower_count': follower_count,
                    'video_count': video_count
                }
                
                success = db_manager.save_user(user_data)
                if success:
                    st.success(f"用户 {nickname} 添加成功！")
                    st.rerun()
                else:
                    st.error("添加用户失败！")
            elif submitted:
                st.error("用户ID不能为空！")
    
    # 用户列表
    st.subheader("用户列表")
    users = db_manager.get_all_users()
    
    if users:
        users_df = pd.DataFrame(users)
        st.dataframe(users_df, width='stretch')
        
        # 删除用户
        selected_user_id = st.selectbox(
            "选择要删除的用户",
            [user['user_id'] for user in users]
        )
        
        if st.button("🗑️ 删除用户"):
            success = db_manager.delete_user(selected_user_id)
            if success:
                st.success("用户删除成功！")
                st.rerun()
            else:
                st.error("删除失败！")
    else:
        st.info("暂无用户数据")

def show_cookies_management():
    """显示Cookie管理"""
    st.header("🍪 Cookie管理")
    
    # 添加Cookie
    with st.expander("➕ 添加Cookie"):
        with st.form("add_cookie_form"):
            cookie_data = st.text_area("Cookie内容 *", placeholder="请输入完整的Cookie内容...")
            platform = st.selectbox("平台", ["douyin", "tiktok", "bilibili"])
            
            submitted = st.form_submit_button("添加Cookie")
            
            if submitted and cookie_data:
                success = db_manager.save_cookie(
                    cookie_data=cookie_data,
                    platform=platform
                )
                
                if success:
                    st.success("Cookie添加成功！")
                    st.rerun()
                else:
                    st.error("添加Cookie失败！")
            elif submitted:
                st.error("Cookie内容不能为空！")
    
    # Cookie列表
    st.subheader("Cookie列表")
    cookies = db_manager.get_all_cookies()
    
    if cookies:
        cookies_df = pd.DataFrame(cookies)
        st.dataframe(cookies_df, width='stretch')
    else:
        st.info("暂无Cookie数据")

def show_videos_management():
    """显示视频管理"""
    st.header("🎥 视频管理")
    
    # 视频列表
    st.subheader("视频列表")
    
    # 获取所有视频（这里需要添加get_all_videos方法到database.py）
    try:
        videos = db_manager.get_all_videos()
        if videos:
            videos_df = pd.DataFrame(videos)
            st.dataframe(videos_df, width='stretch')
            
            # 删除视频
            if st.button("🗑️ 清空所有视频"):
                if st.checkbox("确认删除所有视频？"):
                    success = db_manager.clear_all_videos()
                    if success:
                        st.success("所有视频已删除！")
                        st.rerun()
                    else:
                        st.error("删除失败！")
        else:
            st.info("暂无视频数据")
    except Exception as e:
        st.error(f"获取视频数据失败: {str(e)}")
        st.info("请确保数据库中有videos表")

def show_database_maintenance():
    """显示数据库维护"""
    st.header("🔧 数据库维护")
    
    # 数据库统计
    st.subheader("数据库统计")
    stats = db_manager.get_database_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("用户数量", stats['user_count'])
        st.metric("视频数量", stats['video_count'])
    
    with col2:
        st.metric("活跃Cookie", stats['active_cookie_count'])
        st.metric("总Cookie数", stats['total_cookie_count'])
    
    st.markdown("---")
    
    # 数据清理
    st.subheader("数据清理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ 清空所有用户"):
            if st.checkbox("确认删除所有用户？"):
                success = db_manager.clear_all_users()
                if success:
                    st.success("所有用户已删除！")
                    st.rerun()
                else:
                    st.error("删除失败！")
    
    with col2:
        if st.button("🗑️ 清空所有Cookie"):
            if st.checkbox("确认删除所有Cookie？"):
                success = db_manager.clear_all_cookies()
                if success:
                    st.success("所有Cookie已删除！")
                    st.rerun()
                else:
                    st.error("删除失败！")
    
    # 数据库备份
    st.markdown("---")
    st.subheader("数据库备份")
    
    if st.button("💾 导出数据库"):
        try:
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_douyin_data_{timestamp}.db"
            
            shutil.copy2("douyin_data.db", backup_path)
            st.success(f"数据库已备份到: {backup_path}")
        except Exception as e:
            st.error(f"备份失败: {str(e)}")

if __name__ == "__main__":
    main()
