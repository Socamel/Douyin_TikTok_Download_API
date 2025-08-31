#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aitable.ai集成API端点
Aitable.ai Integration API Endpoints
"""

import sys
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import BaseModel

from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from database import db_manager
from cookie_manager import cookie_manager

router = APIRouter()

# 数据模型
class CookieData(BaseModel):
    cookie_data: str
    platform: str = "douyin"
    expires_at: Optional[str] = None

class UserData(BaseModel):
    user_id: str
    username: str
    nickname: str
    avatar_url: Optional[str] = None
    follower_count: Optional[int] = 0
    following_count: Optional[int] = 0
    video_count: Optional[int] = 0

class AitableSyncRequest(BaseModel):
    cookies: Optional[List[CookieData]] = []
    users: Optional[List[UserData]] = []

# Aitable.ai Automation 数据模型
class AitableAutomationData(BaseModel):
    record_id: str
    action: str  # "create", "update", "delete"
    fields: Dict[str, Any]
    table_name: Optional[str] = "博主管理"
    timestamp: Optional[str] = None

class AitableAutomationRequest(BaseModel):
    data: List[AitableAutomationData]
    source: str = "aitable_automation"
    trigger_type: Optional[str] = "record_change"

@router.post("/sync_data", response_model=ResponseModel)
async def sync_aitable_data(request: Request):
    """
    从Aitable.ai同步数据到本地数据库
    Sync data from Aitable.ai to local database
    """
    try:
        # Aitable.ai API配置
        api_token = "uskIZVNT6ybBEQxO5cTPcCa"
        base_url = "https://aitable.ai/fusion/v1"
        datasheet_id = "dst9PG5TJZc6hRQ3U7"
        view_id = "viwYZCShcEicA"
        
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # 获取Aitable.ai数据
        endpoint = f"datasheets/{datasheet_id}/records"
        params = {
            "viewId": view_id,
            "fieldKey": "name",
            "pageSize": 100
        }
        
        url = f"{base_url}/{endpoint}"
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success') or data.get('code') != 200:
            raise Exception(f"Aitable.ai API错误: {data.get('message', '未知错误')}")
        
        records = data.get('data', {}).get('records', [])
        
        sync_results = {
            "cookies_synced": 0,
            "users_synced": 0,
            "errors": []
        }
        
        # 处理每条记录
        for record in records:
            fields = record.get('fields', {})
            record_id = record.get('recordId')
            
            try:
                # 提取Cookie数据
                if 'cookie' in fields and fields['cookie']:
                    # 验证Cookie
                    validation = cookie_manager.validate_cookie(fields['cookie'])
                    if not validation['valid']:
                        sync_results["errors"].append(f"Cookie验证失败 ({fields.get('Blogger', '未知')}): {validation['message']}")
                        continue
                    
                    # 保存Cookie
                    success = db_manager.save_cookie(
                        cookie_data=fields['cookie'],
                        platform='douyin'
                    )
                    
                    if success:
                        sync_results["cookies_synced"] += 1
                    else:
                        sync_results["errors"].append(f"Cookie保存失败: {fields.get('Blogger', '未知')}")
                
                # 提取用户数据
                if 'user_id' in fields and fields['user_id']:
                    # 保存用户信息
                    success = db_manager.save_user({
                        'user_id': fields['user_id'],
                        'username': fields.get('Blogger', ''),
                        'nickname': fields.get('Blogger', ''),
                        'avatar_url': '',
                        'follower_count': 0,
                        'following_count': 0,
                        'video_count': 0
                    })
                    
                    if success:
                        sync_results["users_synced"] += 1
                    else:
                        sync_results["errors"].append(f"用户保存失败: {fields.get('Blogger', '未知')}")
                        
            except Exception as e:
                sync_results["errors"].append(f"处理记录失败 {record_id}: {str(e)}")
        
        # 生成响应消息
        message = f"同步完成: {sync_results['cookies_synced']} 个Cookie, {sync_results['users_synced']} 个用户"
        if sync_results["errors"]:
            message += f", {len(sync_results['errors'])} 个错误"
        
        return ResponseModel(
            code=200,
            message=message,
            data={
                "total_records": len(records),
                "cookies_synced": sync_results["cookies_synced"],
                "users_synced": sync_results["users_synced"],
                "errors": sync_results["errors"]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"数据同步失败: {str(e)}"
        )

@router.get("/get_users", response_model=ResponseModel)
async def get_all_users():
    """
    获取所有博主信息
    Get all user information
    """
    try:
        # 从数据库获取所有用户
        users = db_manager.get_all_users()
        
        return ResponseModel(
            code=200,
            message=f"获取到 {len(users)} 个用户",
            data={
                "users": users,
                "total_count": len(users)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取用户信息失败: {str(e)}"
        )

@router.put("/update_user", response_model=ResponseModel)
async def update_user(user_data: UserData = Body(...)):
    """
    更新博主信息
    Update user information
    """
    try:
        # 更新用户信息
        success = db_manager.update_user({
            'user_id': user_data.user_id,
            'username': user_data.username,
            'nickname': user_data.nickname,
            'avatar_url': user_data.avatar_url,
            'follower_count': user_data.follower_count,
            'following_count': user_data.following_count,
            'video_count': user_data.video_count
        })
        
        if success:
            return ResponseModel(
                code=200,
                message="用户信息更新成功",
                data={"user_id": user_data.user_id}
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="用户信息更新失败"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新用户信息失败: {str(e)}"
        )

@router.get("/get_cookies", response_model=ResponseModel)
async def get_all_cookies():
    """
    获取所有Cookie信息
    Get all cookie information
    """
    try:
        # 从数据库获取所有Cookie
        cookies = db_manager.get_all_cookies()
        
        return ResponseModel(
            code=200,
            message=f"获取到 {len(cookies)} 个Cookie",
            data={
                "cookies": cookies,
                "total_count": len(cookies)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取Cookie信息失败: {str(e)}"
        )

@router.post("/sync_status", response_model=ResponseModel)
async def get_sync_status():
    """
    获取同步状态信息
    Get synchronization status
    """
    try:
        # 获取数据库统计信息
        stats = db_manager.get_database_stats()
        
        # 获取Cookie状态
        cookie_status = cookie_manager.get_cookie_status()
        
        return ResponseModel(
            code=200,
            message="获取同步状态成功",
            data={
                "database_stats": stats,
                "cookie_status": cookie_status,
                "last_sync": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取同步状态失败: {str(e)}"
        )

@router.post("/automation", response_model=ResponseModel)
async def handle_aitable_automation(request: AitableAutomationRequest):
    """
    处理Aitable.ai Automation数据
    Handle Aitable.ai automation data
    """
    try:
        results = {
            "processed": 0,
            "cookies_updated": 0,
            "users_updated": 0,
            "errors": []
        }
        
        for automation_data in request.data:
            try:
                fields = automation_data.fields
                record_id = automation_data.record_id
                action = automation_data.action
                
                if action == "create" or action == "update":
                    # 处理Cookie数据
                    if 'cookie' in fields and fields['cookie']:
                        # 验证Cookie
                        validation = cookie_manager.validate_cookie(fields['cookie'])
                        if not validation['valid']:
                            results["errors"].append(f"Cookie验证失败 (Record {record_id}): {validation['message']}")
                            continue
                        
                        # 保存Cookie
                        success = db_manager.save_cookie(
                            cookie_data=fields['cookie'],
                            platform='douyin'
                        )
                        
                        if success:
                            results["cookies_updated"] += 1
                            results["processed"] += 1
                        else:
                            results["errors"].append(f"Cookie保存失败: Record {record_id}")
                    
                    # 处理用户数据
                    if 'user_id' in fields and fields['user_id']:
                        # 保存用户信息
                        success = db_manager.save_user({
                            'user_id': fields['user_id'],
                            'username': fields.get('博主', ''),
                            'nickname': fields.get('博主', ''),
                            'avatar_url': '',
                            'follower_count': 0,
                            'following_count': 0,
                            'video_count': 0
                        })
                        
                        if success:
                            results["users_updated"] += 1
                            results["processed"] += 1
                        else:
                            results["errors"].append(f"用户保存失败: Record {record_id}")
                
                elif action == "delete":
                    # 处理删除操作
                    if 'user_id' in fields and fields['user_id']:
                        # 这里可以添加删除用户的逻辑
                        results["processed"] += 1
                        results["errors"].append(f"删除操作暂未实现: Record {record_id}")
                
            except Exception as e:
                results["errors"].append(f"处理记录失败 {record_id}: {str(e)}")
        
        # 生成响应消息
        message = f"自动化处理完成: {results['processed']} 条记录"
        if results["cookies_updated"] > 0 or results["users_updated"] > 0:
            message += f", {results['cookies_updated']} 个Cookie, {results['users_updated']} 个用户"
        if results["errors"]:
            message += f", {len(results['errors'])} 个错误"
        
        return ResponseModel(
            code=200,
            message=message,
            data={
                "automation_results": results,
                "source": request.source,
                "trigger_type": request.trigger_type,
                "processed_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"自动化处理失败: {str(e)}"
        )

@router.post("/blogger_cookie", response_model=ResponseModel)
async def handle_aitable_blogger_cookie(request: Request):
    """
    处理Aitable.ai博主Cookie数据
    Handle Aitable.ai blogger and cookie data
    """
    try:
        # 获取请求体数据
        webhook_data = await request.json()
        
        # 解析webhook数据
        results = {
            "processed": 0,
            "cookies_updated": 0,
            "users_updated": 0,
            "errors": []
        }
        
        # 尝试解析不同格式的webhook数据
        if isinstance(webhook_data, dict):
            # 格式1: 直接包含记录数据
            if 'fields' in webhook_data:
                fields = webhook_data['fields']
                record_id = webhook_data.get('recordId', 'unknown')
                status = fields.get('Status', '').strip()
                
                # 根据Status字段处理不同操作
                if status == 'Refresh Cookie':
                    # 更新Cookie操作
                    if 'cookie' in fields and fields['cookie']:
                        validation = cookie_manager.validate_cookie(fields['cookie'])
                        if validation['valid']:
                            success = db_manager.save_cookie(
                                cookie_data=fields['cookie'],
                                platform='douyin'
                            )
                            if success:
                                results["cookies_updated"] += 1
                                results["processed"] += 1
                        else:
                            results["errors"].append(f"Cookie验证失败: {validation.get('error', '未知错误')}")
                
                elif status == 'Add user_id':
                    # 新增博主操作
                    if 'user_id' in fields and fields['user_id']:
                        success = db_manager.save_user({
                            'user_id': fields['user_id'],
                            'username': fields.get('Blogger', ''),
                            'nickname': fields.get('Blogger', ''),
                            'avatar_url': '',
                            'follower_count': 0,
                            'following_count': 0,
                            'video_count': 0
                        })
                        if success:
                            results["users_updated"] += 1
                            results["processed"] += 1
                        else:
                            results["errors"].append(f"用户保存失败: {fields['user_id']}")
                
                elif status == 'Delete user_id':
                    # 删除博主操作
                    if 'user_id' in fields and fields['user_id']:
                        success = db_manager.delete_user(fields['user_id'])
                        if success:
                            results["users_updated"] += 1
                            results["processed"] += 1
                        else:
                            results["errors"].append(f"用户删除失败: {fields['user_id']}")
                
                else:
                    # 兼容旧格式：没有Status字段时的处理
                    # 处理Cookie
                    if 'cookie' in fields and fields['cookie']:
                        validation = cookie_manager.validate_cookie(fields['cookie'])
                        if validation['valid']:
                            success = db_manager.save_cookie(
                                cookie_data=fields['cookie'],
                                platform='douyin'
                            )
                            if success:
                                results["cookies_updated"] += 1
                                results["processed"] += 1
                    
                    # 处理用户
                    if 'user_id' in fields and fields['user_id']:
                        success = db_manager.save_user({
                            'user_id': fields['user_id'],
                            'username': fields.get('Blogger', ''),
                            'nickname': fields.get('Blogger', ''),
                            'avatar_url': '',
                            'follower_count': 0,
                            'following_count': 0,
                            'video_count': 0
                        })
                        if success:
                            results["users_updated"] += 1
                            results["processed"] += 1
            
            # 格式2: 包含多条记录
            elif 'records' in webhook_data:
                for record in webhook_data['records']:
                    fields = record.get('fields', {})
                    record_id = record.get('recordId', 'unknown')
                    status = fields.get('Status', '').strip()
                    
                    # 根据Status字段处理不同操作
                    if status == 'Refresh Cookie':
                        # 更新Cookie操作
                        if 'cookie' in fields and fields['cookie']:
                            validation = cookie_manager.validate_cookie(fields['cookie'])
                            if validation['valid']:
                                success = db_manager.save_cookie(
                                    cookie_data=fields['cookie'],
                                    platform='douyin'
                                )
                                if success:
                                    results["cookies_updated"] += 1
                                    results["processed"] += 1
                            else:
                                results["errors"].append(f"Cookie验证失败: {validation.get('error', '未知错误')}")
                    
                    elif status == 'Add user_id':
                        # 新增博主操作
                        if 'user_id' in fields and fields['user_id']:
                            success = db_manager.save_user({
                                'user_id': fields['user_id'],
                                'username': fields.get('Blogger', ''),
                                'nickname': fields.get('Blogger', ''),
                                'avatar_url': '',
                                'follower_count': 0,
                                'following_count': 0,
                                'video_count': 0
                            })
                            if success:
                                results["users_updated"] += 1
                                results["processed"] += 1
                            else:
                                results["errors"].append(f"用户保存失败: {fields['user_id']}")
                    
                    elif status == 'Delete user_id':
                        # 删除博主操作
                        if 'user_id' in fields and fields['user_id']:
                            success = db_manager.delete_user(fields['user_id'])
                            if success:
                                results["users_updated"] += 1
                                results["processed"] += 1
                            else:
                                results["errors"].append(f"用户删除失败: {fields['user_id']}")
                    
                    else:
                        # 兼容旧格式：没有Status字段时的处理
                        # 处理Cookie
                        if 'cookie' in fields and fields['cookie']:
                            validation = cookie_manager.validate_cookie(fields['cookie'])
                            if validation['valid']:
                                success = db_manager.save_cookie(
                                    cookie_data=fields['cookie'],
                                    platform='douyin'
                                )
                                if success:
                                    results["cookies_updated"] += 1
                                    results["processed"] += 1
                        
                        # 处理用户
                        if 'user_id' in fields and fields['user_id']:
                            success = db_manager.save_user({
                                'user_id': fields['user_id'],
                                'username': fields.get('博主', ''),
                                'nickname': fields.get('博主', ''),
                                'avatar_url': '',
                                'follower_count': 0,
                                'following_count': 0,
                                'video_count': 0
                            })
                            if success:
                                results["users_updated"] += 1
                                results["processed"] += 1
        
        message = f"博主Cookie同步完成: {results['processed']} 条记录"
        if results["cookies_updated"] > 0 or results["users_updated"] > 0:
            message += f", {results['cookies_updated']} 个Cookie, {results['users_updated']} 个用户"
        if results["errors"]:
            message += f", {len(results['errors'])} 个错误"
        
        return ResponseModel(
            code=200,
            message=message,
            data={
                "webhook_results": results,
                "received_data": webhook_data,
                "processed_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"博主Cookie同步失败: {str(e)}"
        )
