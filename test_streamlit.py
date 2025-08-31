#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Streamlit测试应用
Simple Streamlit Test App
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    st.title("🧪 Streamlit测试应用")
    st.write("这是一个简单的测试页面，用于验证Streamlit是否正常工作")
    
    # 基本信息
    st.header("📋 基本信息")
    st.write(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"Streamlit版本: {st.__version__}")
    
    # 简单的表单测试
    st.header("📝 表单测试")
    with st.form("test_form"):
        name = st.text_input("输入您的姓名", placeholder="请输入姓名")
        age = st.number_input("输入您的年龄", min_value=0, max_value=120, value=25)
        favorite_color = st.selectbox("选择您喜欢的颜色", ["红色", "蓝色", "绿色", "黄色", "紫色"])
        is_student = st.checkbox("您是学生吗？")
        
        submitted = st.form_submit_button("提交信息")
        
        if submitted:
            if name:
                st.success(f"✅ 提交成功！")
                st.write(f"**姓名**: {name}")
                st.write(f"**年龄**: {age}")
                st.write(f"**喜欢的颜色**: {favorite_color}")
                st.write(f"**是否学生**: {'是' if is_student else '否'}")
            else:
                st.error("❌ 请填写姓名！")
    
    # 数据展示测试
    st.header("📊 数据展示测试")
    
    # 创建示例数据
    sample_data = {
        '姓名': ['张三', '李四', '王五', '赵六'],
        '年龄': [25, 30, 28, 35],
        '城市': ['北京', '上海', '广州', '深圳'],
        '分数': [85, 92, 78, 95]
    }
    
    df = pd.DataFrame(sample_data)
    st.write("示例数据表格:")
    st.dataframe(df, use_container_width=True)
    
    # 图表测试
    st.header("📈 图表测试")
    
    # 柱状图
    st.subheader("年龄分布")
    st.bar_chart(df.set_index('姓名')['年龄'])
    
    # 折线图
    st.subheader("分数趋势")
    st.line_chart(df.set_index('姓名')['分数'])
    
    # 交互式组件测试
    st.header("🎮 交互组件测试")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        slider_value = st.slider("滑动条", 0, 100, 50)
        st.write(f"滑动条值: {slider_value}")
    
    with col2:
        radio_choice = st.radio("单选按钮", ["选项A", "选项B", "选项C"])
        st.write(f"选择: {radio_choice}")
    
    with col3:
        multiselect_choices = st.multiselect("多选框", ["苹果", "香蕉", "橙子", "葡萄"])
        st.write(f"选择的水果: {multiselect_choices}")
    
    # 文件上传测试
    st.header("📁 文件上传测试")
    uploaded_file = st.file_uploader("选择一个文件", type=['txt', 'csv', 'json'])
    
    if uploaded_file is not None:
        st.write(f"文件名: {uploaded_file.name}")
        st.write(f"文件大小: {uploaded_file.size} 字节")
        
        # 如果是文本文件，显示内容
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode()
            st.text_area("文件内容:", content, height=200)
    
    # 侧边栏测试
    st.sidebar.header("⚙️ 设置")
    sidebar_option = st.sidebar.selectbox("选择主题", ["浅色", "深色", "自动"])
    st.sidebar.write(f"当前主题: {sidebar_option}")
    
    # 进度条测试
    st.header("⏳ 进度条测试")
    if st.button("开始进度"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(101):
            progress_bar.progress(i)
            status_text.text(f"进度: {i}%")
            import time
            time.sleep(0.01)
        
        st.success("✅ 进度完成！")
    
    # 代码显示测试
    st.header("💻 代码显示测试")
    code = '''
def hello_world():
    print("Hello, Streamlit!")
    return "Success"

result = hello_world()
print(result)
'''
    st.code(code, language='python')
    
    # 成功/错误消息测试
    st.header("🔔 消息测试")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("成功消息"):
            st.success("这是一条成功消息！")
    
    with col2:
        if st.button("错误消息"):
            st.error("这是一条错误消息！")
    
    with col3:
        if st.button("警告消息"):
            st.warning("这是一条警告消息！")
    
    with col4:
        if st.button("信息消息"):
            st.info("这是一条信息消息！")
    
    # 页面底部
    st.markdown("---")
    st.markdown("**🎉 测试完成！如果所有功能都正常显示，说明Streamlit环境配置成功。**")
    
    # 显示系统信息
    with st.expander("🔧 系统信息"):
        import sys
        import platform
        
        st.write(f"**Python版本**: {sys.version}")
        st.write(f"**操作系统**: {platform.system()} {platform.release()}")
        st.write(f"**Streamlit版本**: {st.__version__}")
        st.write(f"**Pandas版本**: {pd.__version__}")

if __name__ == "__main__":
    main()
