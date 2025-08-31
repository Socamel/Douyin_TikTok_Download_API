from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import sys
import os

# 使用统一的路径配置
from path_config import setup_project_paths
setup_project_paths()

import sys
from pathlib import Path

# 确保项目根目录在路径中
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from cookie_manager import cookie_manager
from database import db_manager

router = APIRouter()

class CookieUpdateRequest(BaseModel):
    cookie_data: str
    source: Optional[str] = "api"

class AitableRequest(BaseModel):
    cookies: List[Dict[str, str]]
    users: List[Dict[str, Any]] = []

@router.get("/status")
async def get_cookie_status():
    """获取cookie状态"""
    try:
        status = cookie_manager.get_cookie_status()
        return {
            "code": 200,
            "message": "获取成功",
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": f"获取cookie状态失败: {str(e)}"})

@router.post("/update_cookie")
async def update_cookie(request: CookieUpdateRequest):
    """更新cookie"""
    try:
        result = cookie_manager.update_cookie(
            cookie_data=request.cookie_data,
            source=request.source
        )
        
        if result['success']:
            return {
                "code": 200,
                "message": "Cookie更新成功",
                "data": {
                    "expires_at": result['expires_at']
                }
            }
        else:
            raise HTTPException(status_code=400, detail={"message": result['message']})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": f"更新cookie失败: {str(e)}"})

@router.post("/aitable/cookie")
async def aitable_update_cookie(request: AitableRequest):
    """通过Aitable.ai更新cookie"""
    try:
        aitable_data = {
            "cookies": request.cookies,
            "users": request.users
        }
        
        result = cookie_manager.process_aitable_update(aitable_data)
        
        if result['success']:
            return {
                "code": 200,
                "message": "Aitable.ai处理成功",
                "data": {
                    "source": result['source'],
                    "expires_at": result['expires_at']
                }
            }
        else:
            raise HTTPException(status_code=400, detail={"message": result['message']})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": f"Aitable.ai处理失败: {str(e)}"})

@router.get("/test")
async def test_cookie():
    """测试cookie有效性"""
    try:
        cookie_data = cookie_manager.get_cookie()
        if not cookie_data:
            raise HTTPException(status_code=404, detail={"message": "未找到Cookie"})
        
        # 这里可以添加实际的cookie测试逻辑
        # 比如发送一个简单的请求到抖音API
        
        return {
            "code": 200,
            "message": "Cookie测试成功",
            "data": {
                "has_cookie": True,
                "is_expired": cookie_manager.is_cookie_expired()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": f"Cookie测试失败: {str(e)}"})

@router.delete("/clear")
async def clear_cookie():
    """清除所有cookie"""
    try:
        # 将所有cookie设为非活跃
        with db_manager.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE cookies SET is_active = 0 WHERE platform = 'douyin'")
            conn.commit()
        
        return {
            "code": 200,
            "message": "Cookie清除成功",
            "data": {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": f"清除cookie失败: {str(e)}"})

@router.get("/history")
async def get_cookie_history():
    """获取cookie历史记录"""
    try:
        with db_manager.db_path as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, platform, created_at, updated_at, expires_at, is_active 
                FROM cookies 
                WHERE platform = 'douyin' 
                ORDER BY updated_at DESC 
                LIMIT 10
            """)
            
            columns = [description[0] for description in cursor.description]
            history = []
            for row in cursor.fetchall():
                history.append(dict(zip(columns, row)))
        
        return {
            "code": 200,
            "message": "获取历史记录成功",
            "data": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": f"获取历史记录失败: {str(e)}"})
