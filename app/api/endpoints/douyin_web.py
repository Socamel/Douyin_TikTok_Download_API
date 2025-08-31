# -*- coding: utf-8 -*-
from typing import List
import sys
import os

from fastapi import APIRouter, Body, Query, Request, HTTPException
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel

from crawlers.douyin.web.web_crawler import DouyinWebCrawler

from path_config import setup_project_paths
setup_project_paths()

from database import db_manager

router = APIRouter()
douyin_crawler = DouyinWebCrawler()

@router.get("/fetch_one_video", response_model=ResponseModel, summary="获取单个作品数据/Get single video data")
async def fetch_one_video(request: Request,
                          aweme_id: str = Query(example="7372484719365098803", description="作品id/Video id")):
    try:
        data = await douyin_crawler.fetch_one_video(aweme_id)
        return ResponseModel(code=200, router=request.url.path, data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code, router=request.url.path, params=dict(request.query_params))
        raise HTTPException(status_code=status_code, detail=detail.dict())

@router.get("/fetch_user_post_videos", response_model=ResponseModel, summary="获取用户主页作品数据/Get user homepage video data")
async def fetch_user_post_videos(request: Request,
                                 sec_user_id: str = Query(example="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE", description="用户sec_user_id/User sec_user_id"),
                                 max_cursor: int = Query(default=0, description="最大游标/Maximum cursor"),
                                 count: int = Query(default=20, description="每页数量/Number per page")):
    try:
        data = await douyin_crawler.fetch_user_post_videos(sec_user_id, max_cursor, count)
        return ResponseModel(code=200, router=request.url.path, data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code, router=request.url.path, params=dict(request.query_params))
        raise HTTPException(status_code=status_code, detail=detail.dict())

@router.get("/fetch_user_like_videos", response_model=ResponseModel, summary="获取用户喜欢作品数据/Get user like video data")
async def fetch_user_like_videos(request: Request,
                                 sec_user_id: str = Query(example="MS4wLjABAAAAW9FWcqS7RdQAWPd2AA5fL_ilmqsIFUCQ_Iym6Yh9_cUa6ZRqVLjVQSUjlHrfXY1Y", description="用户sec_user_id/User sec_user_id"),
                                 max_cursor: int = Query(default=0, description="最大游标/Maximum cursor"),
                                 counts: int = Query(default=20, description="每页数量/Number per page")):
    try:
        data = await douyin_crawler.fetch_user_like_videos(sec_user_id, max_cursor, counts)
        return ResponseModel(code=200, router=request.url.path, data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code, router=request.url.path, params=dict(request.query_params))
        raise HTTPException(status_code=status_code, detail=detail.dict())

@router.get("/fetch_user_collection_videos", response_model=ResponseModel, summary="获取用户收藏作品数据/Get user collection video data")
async def fetch_user_collection_videos(request: Request,
                                       cookie: str = Query(example="YOUR_COOKIE", description="用户网页版抖音Cookie/Your web version of Douyin Cookie"),
                                       max_cursor: int = Query(default=0, description="最大游标/Maximum cursor"),
                                       counts: int = Query(default=20, description="每页数量/Number per page")):
    try:
        data = await douyin_crawler.fetch_user_collection_videos(cookie, max_cursor, counts)
        return ResponseModel(code=200, router=request.url.path, data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code, router=request.url.path, params=dict(request.query_params))
        raise HTTPException(status_code=status_code, detail=detail.dict())

@router.get("/fetch_user_new_videos", response_model=ResponseModel, summary="获取用户新视频（去重）/Get user new videos (deduplication)")
async def fetch_user_new_videos(request: Request,
                               sec_user_id: str = Query(example="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE", description="用户sec_user_id/User sec_user_id"),
                               max_cursor: int = Query(default=0, description="最大游标/Maximum cursor"),
                               count: int = Query(default=20, description="每页数量/Number per page")):
    try:
        all_videos_data = await douyin_crawler.fetch_user_post_videos(sec_user_id, max_cursor, count)
        
        if not all_videos_data or 'aweme_list' not in all_videos_data:
            return ResponseModel(
                code=200,
                router=request.url.path,
                message="没有获取到视频数据",
                data={
                    "message": "没有获取到视频数据",
                    "new_videos": [],
                    "total_fetched": 0,
                    "new_count": 0
                }
            )
        
        all_videos = all_videos_data.get('aweme_list', [])
        total_fetched = len(all_videos)
        
        if total_fetched == 0:
            return ResponseModel(
                code=200,
                router=request.url.path,
                message="没有新视频",
                data={
                    "message": "没有新视频",
                    "new_videos": [],
                    "total_fetched": 0,
                    "new_count": 0
                }
            )
        
        user_info = all_videos_data.get('user_info', {})
        if user_info:
            db_manager.save_user({
                'user_id': sec_user_id,
                'username': user_info.get('nickname', '未知博主'),
                'nickname': user_info.get('nickname', '未知博主'),
                'avatar_url': user_info.get('avatar_larger', {}).get('url_list', [''])[0] if user_info.get('avatar_larger', {}).get('url_list') else '',
                'follower_count': user_info.get('follower_count', 0),
                'following_count': user_info.get('following_count', 0),
                'video_count': user_info.get('aweme_count', 0)
            })
        
        new_videos = []
        existing_video_ids = []
        
        for video in all_videos:
            video_id = video.get('aweme_id', '')
            if video_id:
                if not db_manager.video_exists(video_id):
                    video_data = {
                        'video_id': video_id,
                        'user_id': sec_user_id,
                        'title': video.get('desc', ''),
                        'description': video.get('desc', ''),
                        'video_url': video.get('video', {}).get('play_addr', {}).get('url_list', [''])[0] if video.get('video', {}).get('play_addr', {}).get('url_list') else '',
                        'cover_url': video.get('video', {}).get('cover', {}).get('url_list', [''])[0] if video.get('video', {}).get('cover', {}).get('url_list') else '',
                        'duration': video.get('video', {}).get('duration', 0),
                        'play_count': video.get('statistics', {}).get('play_count', 0),
                        'like_count': video.get('statistics', {}).get('digg_count', 0),
                        'comment_count': video.get('statistics', {}).get('comment_count', 0),
                        'share_count': video.get('statistics', {}).get('share_count', 0),
                        'douyin_created_at': video.get('create_time', 0)
                    }
                    
                    if db_manager.save_video(video_data):
                        # 确保Blogger字段有值 - 只使用nickname
                        blogger_name = user_info.get('nickname', '未知博主')
                        
                        new_videos.append({
                            'Title': video.get('desc', ''),
                            'URL': video_data['video_url'],
                            'Blogger': blogger_name
                        })
                else:
                    existing_video_ids.append(video_id)
        
        new_count = len(new_videos)
        
        if new_count == 0:
            return ResponseModel(
                code=200,
                router=request.url.path,
                message="没有新视频",
                data={
                    "message": "没有新视频",
                    "new_videos": [],
                    "total_fetched": total_fetched,
                    "new_count": 0
                }
            )
        else:
            return ResponseModel(
                code=200,
                router=request.url.path,
                message=f"发现 {new_count} 个新视频",
                data={
                    "message": f"发现 {new_count} 个新视频",
                    "new_videos": new_videos,
                    "total_fetched": total_fetched,
                    "new_count": new_count
                }
            )
            
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code, router=request.url.path, params=dict(request.query_params))
        raise HTTPException(status_code=status_code, detail=detail.dict())

@router.get("/generate_real_msToken", response_model=ResponseModel, summary="生成真实msToken/Generate real msToken")
async def generate_real_msToken(request: Request):
    try:
        data = await douyin_crawler.gen_real_msToken()
        return ResponseModel(code=200, router=request.url.path, data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code, router=request.url.path, params=dict(request.query_params))
        raise HTTPException(status_code=status_code, detail=detail.dict())

@router.get("/generate_ttwid", response_model=ResponseModel, summary="生成ttwid/Generate ttwid")
async def generate_ttwid(request: Request):
    try:
        data = await douyin_crawler.gen_ttwid()
        return ResponseModel(code=200, router=request.url.path, data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code, router=request.url.path, params=dict(request.query_params))
        raise HTTPException(status_code=status_code, detail=detail.dict())

@router.get("/get_sec_user_id", response_model=ResponseModel, summary="提取单个用户id/Extract single user id")
async def get_sec_user_id(request: Request,
                          url: str = Query(example="https://www.douyin.com/user/MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE")):
    try:
        data = await douyin_crawler.get_sec_user_id(url)
        return ResponseModel(code=200, router=request.url.path, data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code, router=request.url.path, params=dict(request.query_params))
        raise HTTPException(status_code=status_code, detail=detail.dict())

@router.get("/get_aweme_id", response_model=ResponseModel, summary="提取单个作品id/Extract single video id")
async def get_aweme_id(request: Request,
                       url: str = Query(example="https://www.douyin.com/video/7298145681699622182")):
    try:
        data = await douyin_crawler.get_aweme_id(url)
        return ResponseModel(code=200, router=request.url.path, data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code, router=request.url.path, params=dict(request.query_params))
        raise HTTPException(status_code=status_code, detail=detail.dict())
