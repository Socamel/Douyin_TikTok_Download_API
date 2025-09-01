#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版定时任务程序
支持将多个视频分别存储到Airtable的不同行中
"""

import asyncio
import aiohttp
import logging
import yaml
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pytz
from database import db_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedVideoScheduler:
    def __init__(self):
        self.config = self.load_config()
        self.api_base_url = f"http://{self.config['API']['Host_IP']}:{self.config['API']['Host_Port']}"
        self.beijing_tz = pytz.timezone('Asia/Shanghai')
        
        # Aitable.ai配置
        self.aitable_config = self.config.get('Aitable', {})
        self.aitable_api_key = self.aitable_config.get('api_key')
        self.aitable_base_id = self.aitable_config.get('base_id')
        self.aitable_table_name = self.aitable_config.get('table_name', 'Videos')
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {
                'API': {
                    'Host_IP': 'localhost',
                    'Host_Port': 8501
                },
                'Aitable': {
                    'api_key': '',
                    'base_id': '',
                    'table_name': 'Videos'
                }
            }
    
    async def fetch_user_new_videos(self, session: aiohttp.ClientSession, sec_user_id: str, count: int = 10) -> Dict[str, Any]:
        """调用API获取用户新视频（简化格式）"""
        try:
            url = f"{self.api_base_url}/api/douyin/simple/fetch_user_new_videos_simple"
            params = {
                'sec_user_id': sec_user_id,
                'count': count
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"API请求失败: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"获取用户新视频失败 {sec_user_id}: {e}")
            return None
    
    def parse_video_data(self, video_info: Dict[str, Any], user_info: Dict[str, Any]) -> Dict[str, Any]:
        """解析视频数据，准备存储到Airtable"""
        try:
            aweme_detail = video_info.get('aweme_detail', {})
            
            # 提取视频信息
            video_data = {
                'video_id': aweme_detail.get('aweme_id', ''),
                'title': aweme_detail.get('desc', '无标题'),
                'description': aweme_detail.get('desc', ''),
                'video_url': aweme_detail.get('video', {}).get('play_addr', {}).get('url_list', [''])[0],
                'cover_url': aweme_detail.get('video', {}).get('cover', {}).get('url_list', [''])[0],
                'duration': aweme_detail.get('video', {}).get('duration', 0),
                'play_count': aweme_detail.get('statistics', {}).get('play_count', 0),
                'like_count': aweme_detail.get('statistics', {}).get('digg_count', 0),
                'comment_count': aweme_detail.get('statistics', {}).get('comment_count', 0),
                'share_count': aweme_detail.get('statistics', {}).get('share_count', 0),
                'user_id': user_info.get('user_id', ''),
                'user_nickname': user_info.get('nickname', ''),
                'user_username': user_info.get('username', ''),
                'created_time': aweme_detail.get('create_time', 0),
                'fetch_time': datetime.now().isoformat(),
                'platform': 'douyin'
            }
            
            return video_data
            
        except Exception as e:
            logger.error(f"解析视频数据失败: {e}")
            return {}
    
    async def store_video_to_aitable(self, session: aiohttp.ClientSession, video_data: Dict[str, Any]) -> bool:
        """将单个视频存储到Aitable.ai"""
        try:
            if not self.aitable_api_key or not self.aitable_base_id:
                logger.warning("Aitable.ai配置不完整，跳过存储")
                return False
            
            # 数据已经是简化格式，直接使用 - 只使用nickname
            aitable_record = {
                "Title": video_data.get('Title', ''),
                "URL": video_data.get('URL', ''),
                "Blogger": video_data.get('Blogger', '未知博主')
            }
            
            # 发送到Aitable.ai (使用Fusion API格式)
            url = f"https://aitable.ai/fusion/v1/datasheets/{self.aitable_base_id}/records"
            params = {
                'viewId': self.aitable_table_name,  # 使用viewId作为表名
                'fieldKey': 'name'
            }
            headers = {
                'Authorization': f'Bearer {self.aitable_api_key}',
                'Content-Type': 'application/json'
            }
            
            # 使用正确的Aitable.ai Fusion API格式
            aitable_payload = {
                "records": [
                    {
                        "fields": aitable_record
                    }
                ],
                "fieldKey": "name"
            }
            
            async with session.post(url, headers=headers, params=params, json=aitable_payload) as response:
                if response.status == 200 or response.status == 201:
                    result = await response.json()
                    logger.info(f"✅ 视频 {video_data.get('Title', '')[:30]}... 成功存储到Aitable.ai")
                    return True
                else:
                    logger.error(f"❌ 存储视频到Aitable.ai失败: {response.status} - {await response.text()}")
                    return False
                    
        except Exception as e:
            logger.error(f"存储视频到Aitable.ai时出错: {e}")
            return False
    
    async def process_user_videos(self, session: aiohttp.ClientSession, user: Dict[str, Any]) -> None:
        """处理单个用户的新视频"""
        try:
            logger.info(f"开始处理用户: {user.get('nickname', user.get('username', user['user_id']))}")
            
            # 调用API获取新视频
            result = await self.fetch_user_new_videos(session, user['user_id'], count=20)
            
            if result and result.get('code') == 200:
                data = result.get('data', {})
                
                if data.get('message') == "没有视频" or data.get('message') == "没有获取到视频数据":
                    logger.info(f"用户 {user.get('nickname', user.get('username', user['user_id']))} 没有新视频")
                else:
                    # 处理新视频数据（简化格式）
                    videos = data.get('videos', [])
                    if videos:
                        logger.info(f"用户 {user.get('nickname', user.get('username', user['user_id']))} 发现 {len(videos)} 个新视频")
                        
                        # 为每个视频创建单独的行存储到Aitable.ai
                        success_count = 0
                        for video in videos:
                            # 直接存储简化格式的视频数据
                            if await self.store_video_to_aitable(session, video):
                                success_count += 1
                                logger.info(f"✅ 视频 - {video.get('Title', '')[:30]}... 已存储")
                            else:
                                logger.error(f"❌ 视频存储失败")
                            
                            # 避免请求过于频繁
                            await asyncio.sleep(0.5)
                        
                        logger.info(f"📊 用户 {user.get('nickname', user.get('username', user['user_id']))} 处理完成: {success_count}/{len(videos)} 个视频成功存储")
                    else:
                        logger.info(f"用户 {user.get('nickname', user.get('username', user['user_id']))} 没有新视频")
                
                # 更新最后抓取时间（可选）
                # db_manager.update_followed_user_fetch_time(user['user_id'])
            else:
                logger.error(f"处理用户 {user.get('nickname', user.get('username', user['user_id']))} 失败")
                
        except Exception as e:
            logger.error(f"处理用户视频时出错 {user.get('nickname', user.get('username', user['user_id']))}: {e}")
    
    async def fetch_all_followed_users_videos(self) -> None:
        """抓取所有关注博主的新视频"""
        try:
            logger.info("开始抓取所有关注博主的新视频")
            
            # 获取所有关注的博主
            followed_users = db_manager.get_all_users()
            
            if not followed_users:
                logger.info("没有关注的博主，请先添加关注的博主")
                return
            
            logger.info(f"找到 {len(followed_users)} 个关注的博主")
            
            # 创建HTTP会话
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # 并发处理所有用户，但限制并发数量避免API限制
                semaphore = asyncio.Semaphore(2)  # 降低并发数，避免Aitable.ai限制
                
                async def process_with_semaphore(user):
                    async with semaphore:
                        await self.process_user_videos(session, user)
                
                # 创建所有任务
                tasks = [process_with_semaphore(user) for user in followed_users]
                
                # 等待所有任务完成
                await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info("所有关注博主的新视频抓取完成")
            
        except Exception as e:
            logger.error(f"抓取关注博主视频时出错: {e}")
    
    def get_next_run_time(self, target_hours: List[int]) -> datetime:
        """获取下次运行时间"""
        now = datetime.now(self.beijing_tz)
        
        # 找到下一个目标时间
        for hour in sorted(target_hours):
            next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        
        # 如果没有找到，返回明天的第一个时间
        next_run = now.replace(hour=target_hours[0], minute=0, second=0, microsecond=0)
        return next_run + timedelta(days=1)
    
    async def run_scheduler(self) -> None:
        """运行定时调度器"""
        # 每天运行的时间点（北京时间）
        target_hours = [12, 17, 20, 22]  # 12点、17点、20点、22点
        
        logger.info("增强版定时调度器启动")
        logger.info(f"将在每天 {', '.join(map(str, target_hours))} 点执行抓取任务")
        logger.info("新视频将分别存储到Aitable.ai的不同行中")
        
        while True:
            try:
                # 获取下次运行时间
                next_run = self.get_next_run_time(target_hours)
                logger.info(f"下次执行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 等待到下次运行时间
                now = datetime.now(self.beijing_tz)
                wait_seconds = (next_run - now).total_seconds()
                
                if wait_seconds > 0:
                    logger.info(f"等待 {wait_seconds:.0f} 秒后执行...")
                    await asyncio.sleep(wait_seconds)
                
                # 执行抓取任务
                logger.info("开始执行定时抓取任务")
                await self.fetch_all_followed_users_videos()
                logger.info("定时抓取任务完成")
                
            except Exception as e:
                logger.error(f"调度器运行出错: {e}")
                # 出错后等待5分钟再继续
                await asyncio.sleep(300)

async def main():
    """主函数"""
    scheduler = EnhancedVideoScheduler()
    await scheduler.run_scheduler()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
