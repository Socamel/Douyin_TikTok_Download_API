import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

class DatabaseManager:
    def __init__(self, db_path: str = "douyin_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建cookie表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cookies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cookie_data TEXT NOT NULL,
                    platform VARCHAR(50) DEFAULT 'douyin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    expires_at TIMESTAMP NULL
                )
            """)
            
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(100) UNIQUE NOT NULL,
                    username VARCHAR(100),
                    nickname VARCHAR(100),
                    avatar_url TEXT,
                    follower_count INTEGER DEFAULT 0,
                    following_count INTEGER DEFAULT 0,
                    video_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建视频表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id VARCHAR(100) UNIQUE NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    title TEXT,
                    description TEXT,
                    video_url TEXT,
                    cover_url TEXT,
                    duration INTEGER,
                    play_count INTEGER DEFAULT 0,
                    like_count INTEGER DEFAULT 0,
                    comment_count INTEGER DEFAULT 0,
                    share_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    douyin_created_at TIMESTAMP NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos (created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cookies_active ON cookies (is_active)")
            
            conn.commit()
    
    def save_cookie(self, cookie_data: str, platform: str = "douyin", expires_at: Optional[str] = None) -> bool:
        """保存cookie"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 将之前的cookie设为非活跃
                cursor.execute("UPDATE cookies SET is_active = 0 WHERE platform = ?", (platform,))
                
                # 插入新cookie
                cursor.execute("""
                    INSERT INTO cookies (cookie_data, platform, expires_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (cookie_data, platform, expires_at, datetime.now()))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"保存cookie失败: {e}")
            return False
    
    def get_active_cookie(self, platform: str = "douyin") -> Optional[str]:
        """获取活跃的cookie"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT cookie_data FROM cookies 
                    WHERE platform = ? AND is_active = 1 
                    ORDER BY updated_at DESC LIMIT 1
                """, (platform,))
                
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"获取cookie失败: {e}")
            return None
    
    def is_cookie_expired(self, platform: str = "douyin") -> bool:
        """检查cookie是否过期"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT expires_at FROM cookies 
                    WHERE platform = ? AND is_active = 1 
                    ORDER BY updated_at DESC LIMIT 1
                """, (platform,))
                
                result = cursor.fetchone()
                if not result or not result[0]:
                    return False  # 没有设置过期时间，认为未过期
                
                expires_at = datetime.fromisoformat(result[0])
                return datetime.now() > expires_at
        except Exception as e:
            print(f"检查cookie过期失败: {e}")
            return False
    
    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """保存用户信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, username, nickname, avatar_url, follower_count, following_count, video_count, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data.get('user_id'),
                    user_data.get('username'),
                    user_data.get('nickname'),
                    user_data.get('avatar_url'),
                    user_data.get('follower_count', 0),
                    user_data.get('following_count', 0),
                    user_data.get('video_count', 0),
                    datetime.now()
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"保存用户失败: {e}")
            return False
    
    def save_video(self, video_data: Dict[str, Any]) -> bool:
        """保存视频信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO videos 
                    (video_id, user_id, title, description, video_url, cover_url, duration, 
                     play_count, like_count, comment_count, share_count, douyin_created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    video_data.get('video_id'),
                    video_data.get('user_id'),
                    video_data.get('title'),
                    video_data.get('description'),
                    video_data.get('video_url'),
                    video_data.get('cover_url'),
                    video_data.get('duration', 0),
                    video_data.get('play_count', 0),
                    video_data.get('like_count', 0),
                    video_data.get('comment_count', 0),
                    video_data.get('share_count', 0),
                    video_data.get('douyin_created_at')
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"保存视频失败: {e}")
            return False
    
    def get_user_videos(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户的所有视频"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM videos WHERE user_id = ? ORDER BY created_at DESC
                """, (user_id,))
                
                columns = [description[0] for description in cursor.description]
                videos = []
                for row in cursor.fetchall():
                    video_dict = dict(zip(columns, row))
                    videos.append(video_dict)
                
                return videos
        except Exception as e:
            print(f"获取用户视频失败: {e}")
            return []
    
    def get_new_videos(self, user_id: str, existing_video_ids: List[str]) -> List[Dict[str, Any]]:
        """获取新视频（不在现有列表中的视频）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if existing_video_ids:
                    placeholders = ','.join(['?' for _ in existing_video_ids])
                    cursor.execute(f"""
                        SELECT * FROM videos 
                        WHERE user_id = ? AND video_id NOT IN ({placeholders})
                        ORDER BY created_at DESC
                    """, (user_id,) + tuple(existing_video_ids))
                else:
                    cursor.execute("""
                        SELECT * FROM videos 
                        WHERE user_id = ? 
                        ORDER BY created_at DESC
                    """, (user_id,))
                
                columns = [description[0] for description in cursor.description]
                videos = []
                for row in cursor.fetchall():
                    video_dict = dict(zip(columns, row))
                    videos.append(video_dict)
                
                return videos
        except Exception as e:
            print(f"获取新视频失败: {e}")
            return []
    
    def video_exists(self, video_id: str) -> bool:
        """检查视频是否已存在"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM videos WHERE video_id = ?", (video_id,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"检查视频存在失败: {e}")
            return False
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                
                result = cursor.fetchone()
                if result:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, result))
                return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, username, nickname, avatar_url, 
                           follower_count, following_count, video_count,
                           created_at, updated_at
                    FROM users 
                    ORDER BY created_at DESC
                """)
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'user_id': row[0],
                        'username': row[1],
                        'nickname': row[2],
                        'avatar_url': row[3],
                        'follower_count': row[4],
                        'following_count': row[5],
                        'video_count': row[6],
                        'created_at': row[7],
                        'updated_at': row[8]
                    })
                return users
                
        except Exception as e:
            print(f"获取所有用户信息失败: {e}")
            return []
    
    def update_user(self, user_data: Dict[str, Any]) -> bool:
        """更新用户信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET username = ?, nickname = ?, avatar_url = ?,
                        follower_count = ?, following_count = ?, video_count = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (
                    user_data['username'],
                    user_data['nickname'],
                    user_data.get('avatar_url'),
                    user_data.get('follower_count', 0),
                    user_data.get('following_count', 0),
                    user_data.get('video_count', 0),
                    user_data['user_id']
                ))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"更新用户信息失败: {e}")
            return False
    
    def get_all_cookies(self) -> List[Dict[str, Any]]:
        """获取所有Cookie信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, cookie_data, platform, created_at, 
                           updated_at, is_active, expires_at
                    FROM cookies 
                    ORDER BY created_at DESC
                """)
                
                cookies = []
                for row in cursor.fetchall():
                    cookies.append({
                        'id': row[0],
                        'cookie_data': row[1],
                        'platform': row[2],
                        'created_at': row[3],
                        'updated_at': row[4],
                        'is_active': bool(row[5]),
                        'expires_at': row[6]
                    })
                return cookies
                
        except Exception as e:
            print(f"获取所有Cookie信息失败: {e}")
            return []
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"删除用户失败: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 统计用户数量
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                
                # 统计视频数量
                cursor.execute("SELECT COUNT(*) FROM videos")
                video_count = cursor.fetchone()[0]
                
                # 统计活跃Cookie数量
                cursor.execute("SELECT COUNT(*) FROM cookies WHERE is_active = 1")
                active_cookie_count = cursor.fetchone()[0]
                
                # 统计总Cookie数量
                cursor.execute("SELECT COUNT(*) FROM cookies")
                total_cookie_count = cursor.fetchone()[0]
                
                return {
                    'user_count': user_count,
                    'video_count': video_count,
                    'active_cookie_count': active_cookie_count,
                    'total_cookie_count': total_cookie_count
                }
                
        except Exception as e:
            print(f"获取数据库统计信息失败: {e}")
            return {
                'user_count': 0,
                'video_count': 0,
                'active_cookie_count': 0,
                'total_cookie_count': 0
            }

# 全局数据库管理器实例
db_manager = DatabaseManager()
