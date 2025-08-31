import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database import db_manager

class CookieManager:
    def __init__(self):
        self.db_manager = db_manager
    
    def parse_cookie(self, cookie_data: str) -> Dict[str, str]:
        """解析cookie字符串为字典"""
        cookie_dict = {}
        if not cookie_data:
            return cookie_dict
        
        # 处理不同格式的cookie
        if '=' in cookie_data and ';' in cookie_data:
            # 标准cookie格式: name=value; name2=value2
            pairs = cookie_data.split(';')
            for pair in pairs:
                pair = pair.strip()
                if '=' in pair:
                    name, value = pair.split('=', 1)
                    cookie_dict[name.strip()] = value.strip()
        elif cookie_data.startswith('{') and cookie_data.endswith('}'):
            # JSON格式
            try:
                cookie_dict = json.loads(cookie_data)
            except json.JSONDecodeError:
                pass
        
        return cookie_dict
    
    def extract_expiry_from_cookie(self, cookie_data: str) -> Optional[str]:
        """从cookie中提取过期时间"""
        cookie_dict = self.parse_cookie(cookie_data)
        
        # 检查常见的过期时间字段
        expiry_fields = ['expires', 'Expires', 'max-age', 'Max-Age']
        for field in expiry_fields:
            if field in cookie_dict:
                expiry_value = cookie_dict[field]
                try:
                    # 尝试解析不同的时间格式
                    if field.lower() == 'max-age':
                        # max-age是秒数
                        expiry_time = datetime.now() + timedelta(seconds=int(expiry_value))
                        return expiry_time.isoformat()
                    else:
                        # 尝试解析日期字符串
                        expiry_time = datetime.fromisoformat(expiry_value.replace('Z', '+00:00'))
                        return expiry_time.isoformat()
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def validate_cookie(self, cookie_data: str) -> Dict[str, Any]:
        """验证cookie有效性"""
        result = {
            'valid': False,
            'message': '',
            'expires_at': None
        }
        
        if not cookie_data or not cookie_data.strip():
            result['message'] = 'Cookie数据为空'
            return result
        
        cookie_dict = self.parse_cookie(cookie_data)
        
        # 检查必要的字段
        required_fields = ['sessionid', 'passport_csrf_token']
        missing_fields = [field for field in required_fields if field not in cookie_dict]
        
        if missing_fields:
            result['message'] = f'缺少必要字段: {", ".join(missing_fields)}'
            return result
        
        # 提取过期时间
        expires_at = self.extract_expiry_from_cookie(cookie_data)
        result['expires_at'] = expires_at
        
        # 检查是否已过期
        if expires_at:
            try:
                expiry_time = datetime.fromisoformat(expires_at)
                if datetime.now() > expiry_time:
                    result['message'] = 'Cookie已过期'
                    return result
            except ValueError:
                pass
        
        result['valid'] = True
        result['message'] = 'Cookie有效'
        return result
    
    def update_cookie(self, cookie_data: str, source: str = "manual") -> Dict[str, Any]:
        """更新cookie"""
        result = {
            'success': False,
            'message': '',
            'expires_at': None
        }
        
        # 验证cookie
        validation = self.validate_cookie(cookie_data)
        if not validation['valid']:
            result['message'] = validation['message']
            return result
        
        # 保存到数据库
        success = self.db_manager.save_cookie(
            cookie_data=cookie_data,
            platform="douyin",
            expires_at=validation['expires_at']
        )
        
        if success:
            result['success'] = True
            result['message'] = 'Cookie更新成功'
            result['expires_at'] = validation['expires_at']
        else:
            result['message'] = '保存Cookie失败'
        
        return result
    
    def get_cookie(self) -> Optional[str]:
        """获取当前活跃的cookie"""
        return self.db_manager.get_active_cookie("douyin")
    
    def is_cookie_expired(self) -> bool:
        """检查cookie是否过期"""
        return self.db_manager.is_cookie_expired("douyin")
    
    def get_cookie_status(self) -> Dict[str, Any]:
        """获取cookie状态"""
        cookie_data = self.get_cookie()
        
        status = {
            'has_cookie': cookie_data is not None,
            'is_expired': False,
            'expires_at': None,
            'last_updated': None
        }
        
        if cookie_data:
            status['is_expired'] = self.is_cookie_expired()
            # 这里可以添加获取最后更新时间的逻辑
            validation = self.validate_cookie(cookie_data)
            status['expires_at'] = validation['expires_at']
        
        return status
    
    def process_aitable_update(self, aitable_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理Aitable.ai更新请求"""
        result = {
            'success': False,
            'message': '',
            'source': 'aitable'
        }
        
        # 从Aitable.ai数据中提取cookie
        cookies = aitable_data.get('cookies', [])
        if not cookies:
            result['message'] = 'Aitable.ai数据中缺少cookies字段'
            return result
        
        # 更新第一个cookie
        cookie_data = cookies[0].get('cookie_data')
        if not cookie_data:
            result['message'] = 'Aitable.ai数据中缺少cookie_data字段'
            return result
        
        # 更新cookie
        update_result = self.update_cookie(cookie_data, source="aitable")
        
        result['success'] = update_result['success']
        result['message'] = update_result['message']
        result['expires_at'] = update_result['expires_at']
        
        return result
    
    def format_cookie_for_request(self, cookie_data: str) -> Dict[str, str]:
        """格式化cookie用于HTTP请求"""
        cookie_dict = self.parse_cookie(cookie_data)
        
        # 添加常用的请求头
        headers = {
            'Cookie': cookie_data,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.douyin.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 如果有csrf token，添加到请求头
        if 'passport_csrf_token' in cookie_dict:
            headers['X-CSRF-Token'] = cookie_dict['passport_csrf_token']
        
        return headers

# 全局cookie管理器实例
cookie_manager = CookieManager()
