from fastapi import APIRouter
from app.api.endpoints import (
    tiktok_web,
    tiktok_app,
    douyin_web,
    douyin_simple,
    bilibili_web,
    hybrid_parsing, ios_shortcut, download,
    cookie_manager, aitable_integration,
)

router = APIRouter()

# TikTok routers
router.include_router(tiktok_web.router, prefix="/tiktok/web", tags=["TikTok-Web-API"])
router.include_router(tiktok_app.router, prefix="/tiktok/app", tags=["TikTok-App-API"])

# Douyin routers
router.include_router(douyin_web.router, prefix="/douyin/web", tags=["Douyin-Web-API"])
router.include_router(douyin_simple.router, prefix="/douyin/simple", tags=["Douyin-Simple-API"])

# Bilibili routers
router.include_router(bilibili_web.router, prefix="/bilibili/web", tags=["Bilibili-Web-API"])

# Hybrid routers
router.include_router(hybrid_parsing.router, prefix="/hybrid", tags=["Hybrid-API"])

# iOS_Shortcut routers
router.include_router(ios_shortcut.router, prefix="/ios", tags=["iOS-Shortcut"])

# Download routers
router.include_router(download.router, tags=["Download"])

# Cookie management routers
router.include_router(cookie_manager.router, prefix="/cookie", tags=["Cookie-Management"])

# Aitable.ai integration routers
router.include_router(aitable_integration.router, prefix="/aitable", tags=["Aitable-Integration"])

# Health check routers (已移动到根路径)
# 健康检查路由已移动到 app/main.py 中直接注册
