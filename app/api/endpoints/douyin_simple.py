from typing import List
import sys
import os

from fastapi import APIRouter, Body, Query, Request, HTTPException
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel

from crawlers.douyin.web.web_crawler import DouyinWebCrawler

# 使用统一的路径配置
from path_config import setup_project_paths
setup_project_paths()

from database import db_manager

router = APIRouter()
douyin_crawler = DouyinWebCrawler()

async def fetch_all_videos_with_pagination(sec_user_id: str, fetch_method, max_count: int = None):
    """
    使用翻页获取用户的所有视频
    
    Args:
        sec_user_id: 用户sec_user_id
        fetch_method: 获取数据的方法
        max_count: 最大获取数量，None表示获取所有
    
    Returns:
        dict: 合并后的视频数据
    """
    all_videos = []
    max_cursor = 0
    has_more = True
    page_count = 0
    max_pages = 50  # 防止无限循环
    
    while has_more and page_count < max_pages:
        try:
            # 获取当前页数据
            page_data = await fetch_method(sec_user_id, max_cursor, 50)  # 每页50个，提高效率
            
            if not page_data or 'aweme_list' not in page_data:
                break
                
            videos = page_data.get('aweme_list', [])
            if not videos:
                break
                
            # 添加视频到总列表
            all_videos.extend(videos)
            
            # 检查是否达到最大数量
            if max_count and len(all_videos) >= max_count:
                all_videos = all_videos[:max_count]
                break
            
            # 获取下一页游标
            max_cursor = page_data.get('max_cursor', 0)
            has_more = page_data.get('has_more', 0) == 1
            
            page_count += 1
            
            # 防止无限循环
            if max_cursor == 0:
                break
                
        except Exception as e:
            print(f"翻页获取视频时出错: {e}")
            break
    
    # 构建返回数据
    if all_videos:
        # 使用第一页的用户信息
        first_page = await fetch_method(sec_user_id, 0, 50)
        user_info = first_page.get('user_info', {}) if first_page else {}
        
        return {
            'aweme_list': all_videos,
            'user_info': user_info,
            'total_fetched': len(all_videos),
            'page_count': page_count
        }
    else:
        return {
            'aweme_list': [],
            'user_info': {},
            'total_fetched': 0,
            'page_count': 0
        }

def create_simple_video_response(request: Request, videos_data: dict, endpoint_name: str, sec_user_id: str = None) -> ResponseModel:
    """
    创建简化格式的视频响应
    
    Args:
        request: FastAPI请求对象
        videos_data: 视频数据字典
        endpoint_name: 端点名称，用于错误信息
        sec_user_id: 用户sec_user_id，用于数据库查询
    
    Returns:
        ResponseModel: 标准化的响应模型
    """
    if not videos_data or 'aweme_list' not in videos_data:
        return ResponseModel(
            code=200,
            router=request.url.path,
            message="没有获取到视频数据",
            data={
                "message": "没有获取到视频数据",
                "videos": [],
                "total_fetched": 0
            }
        )
    
    all_videos = videos_data.get('aweme_list', [])
    total_fetched = len(all_videos)
    
    if total_fetched == 0:
        return ResponseModel(
            code=200,
            router=request.url.path,
            message="没有视频数据",
            data={
                "message": "没有视频数据",
                "videos": [],
                "total_fetched": 0
            }
        )
    
    # 获取用户信息
    user_info = videos_data.get('user_info', {})
    
    # 转换为简化格式
    videos = []
    for video in all_videos:
        video_url = video.get('video', {}).get('play_addr', {}).get('url_list', [''])[0] if video.get('video', {}).get('play_addr', {}).get('url_list') else ''
        
        # 优先从数据库获取用户昵称，如果没有则使用API返回的nickname
        blogger_name = '未知博主'
        
        # 尝试从数据库获取用户信息
        try:
            # 优先使用传入的sec_user_id查询数据库
            if sec_user_id:
                user_data = db_manager.get_user_info(sec_user_id)
                if user_data and user_data.get('nickname'):
                    blogger_name = user_data['nickname']
                else:
                    # 如果数据库中没有，使用API返回的nickname
                    blogger_name = user_info.get('nickname', '未知博主')
            else:
                # 如果没有sec_user_id，使用API返回的nickname
                blogger_name = user_info.get('nickname', '未知博主')
        except Exception as e:
            # 如果查询数据库出错，使用API返回的nickname
            blogger_name = user_info.get('nickname', '未知博主')
        
        videos.append({
            'Title': video.get('desc', ''),
            'URL': video_url,
            'Blogger': blogger_name
        })
    
    return ResponseModel(
        code=200,
        router=request.url.path,
        message=f"获取到 {total_fetched} 个视频",
        data={
            "message": f"获取到 {total_fetched} 个视频",
            "videos": videos,
            "total_fetched": total_fetched
        }
    )

async def handle_simple_video_endpoint(request: Request, sec_user_id: str, max_cursor: int, count: int, fetch_method, endpoint_name: str, auto_pagination: bool = False):
    """
    处理简化格式视频端点的通用函数
    
    Args:
        request: FastAPI请求对象
        sec_user_id: 用户sec_user_id
        max_cursor: 最大游标
        count: 每页数量
        fetch_method: 获取数据的方法
        endpoint_name: 端点名称
        auto_pagination: 是否启用自动翻页
    
    Returns:
        ResponseModel: 标准化的响应模型
    """
    try:
        if auto_pagination and max_cursor == 0:
            # 使用自动翻页获取所有视频
            all_videos_data = await fetch_all_videos_with_pagination(sec_user_id, fetch_method, count)
        else:
            # 获取单页视频数据
            all_videos_data = await fetch_method(sec_user_id, max_cursor, count)
        
        # 创建响应，传入sec_user_id用于数据库查询
        return create_simple_video_response(request, all_videos_data, endpoint_name, sec_user_id)
            
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())

@router.get("/fetch_user_new_videos_simple", response_model=ResponseModel,
            summary="获取用户新视频（简化格式）/Get user new videos (simplified format)")
async def fetch_user_new_videos_simple(request: Request,
                                      sec_user_id: str = Query(
                                          example="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE",
                                          description="用户sec_user_id/User sec_user_id"),
                                      max_cursor: int = Query(default=0, description="最大游标/Maximum cursor"),
                                      count: int = Query(default=1000, description="每页数量/Number per page"),
                                      auto_pagination: bool = Query(default=False, description="自动翻页获取所有视频/Auto pagination to get all videos")):
    """
    # [中文]
    ### 用途:
    - 获取用户新视频（简化格式，专门为Aitable.ai存储优化）
    - 只返回 Title、URL、Blogger 三个字段
    - 每个视频在Aitable.ai中创建独立的一行记录
    ### 参数:
    - sec_user_id: 用户sec_user_id
    - max_cursor: 最大游标
    - count: 每页数量
    - auto_pagination: 自动翻页（当max_cursor=0时生效）
    ### 返回:
    - 简化格式的视频数据

    # [English]
    ### Purpose:
    - Get user new videos (simplified format, optimized for Aitable.ai storage)
    - Only returns Title, URL, Blogger fields
    - Each video creates a separate row in Aitable.ai
    ### Parameters:
    - sec_user_id: User sec_user_id
    - max_cursor: Maximum cursor
    - count: Number per page
    - auto_pagination: Auto pagination (effective when max_cursor=0)
    ### Return:
    - Simplified video data
    """
    return await handle_simple_video_endpoint(
        request, sec_user_id, max_cursor, count, 
        douyin_crawler.fetch_user_new_videos, 
        "fetch_user_new_videos_simple",
        auto_pagination
    )

@router.get("/fetch_user_post_videos_simple", response_model=ResponseModel,
            summary="获取用户发布视频（简化格式）/Get user post videos (simplified format)")
async def fetch_user_post_videos_simple(request: Request,
                                       sec_user_id: str = Query(
                                           example="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE",
                                           description="用户sec_user_id/User sec_user_id"),
                                       max_cursor: int = Query(default=0, description="最大游标/Maximum cursor"),
                                       count: int = Query(default=1000, description="每页数量/Number per page"),
                                       auto_pagination: bool = Query(default=False, description="自动翻页获取所有视频/Auto pagination to get all videos")):
    """
    # [中文]
    ### 用途:
    - 获取用户发布视频（简化格式，专门为Aitable.ai存储优化）
    - 只返回 Title、URL、Blogger 三个字段
    ### 参数:
    - sec_user_id: 用户sec_user_id
    - max_cursor: 最大游标
    - count: 每页数量
    - auto_pagination: 自动翻页（当max_cursor=0时生效）
    ### 返回:
    - 简化格式的视频数据

    # [English]
    ### Purpose:
    - Get user post videos (simplified format, optimized for Aitable.ai storage)
    - Only returns Title, URL, Blogger fields
    ### Parameters:
    - sec_user_id: User sec_user_id
    - max_cursor: Maximum cursor
    - count: Number per page
    - auto_pagination: Auto pagination (effective when max_cursor=0)
    ### Return:
    - Simplified video data
    """
    return await handle_simple_video_endpoint(
        request, sec_user_id, max_cursor, count, 
        douyin_crawler.fetch_user_post_videos, 
        "fetch_user_post_videos_simple",
        auto_pagination
    )

@router.get("/fetch_user_like_videos_simple", response_model=ResponseModel,
            summary="获取用户喜欢视频（简化格式）/Get user like videos (simplified format)")
async def fetch_user_like_videos_simple(request: Request,
                                       sec_user_id: str = Query(
                                           example="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE",
                                           description="用户sec_user_id/User sec_user_id"),
                                       max_cursor: int = Query(default=0, description="最大游标/Maximum cursor"),
                                       count: int = Query(default=1000, description="每页数量/Number per page"),
                                       auto_pagination: bool = Query(default=False, description="自动翻页获取所有视频/Auto pagination to get all videos")):
    """
    # [中文]
    ### 用途:
    - 获取用户喜欢视频（简化格式，专门为Aitable.ai存储优化）
    - 只返回 Title、URL、Blogger 三个字段
    ### 参数:
    - sec_user_id: 用户sec_user_id
    - max_cursor: 最大游标
    - count: 每页数量
    - auto_pagination: 自动翻页（当max_cursor=0时生效）
    ### 返回:
    - 简化格式的视频数据

    # [English]
    ### Purpose:
    - Get user like videos (simplified format, optimized for Aitable.ai storage)
    - Only returns Title, URL, Blogger fields
    ### Parameters:
    - sec_user_id: User sec_user_id
    - max_cursor: Maximum cursor
    - count: Number per page
    - auto_pagination: Auto pagination (effective when max_cursor=0)
    ### Return:
    - Simplified video data
    """
    return await handle_simple_video_endpoint(
        request, sec_user_id, max_cursor, count, 
        douyin_crawler.fetch_user_like_videos, 
        "fetch_user_like_videos_simple",
        auto_pagination
    )
