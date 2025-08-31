# 简化格式API说明

## 概述

为了适配 Aitable.ai 存储需求，项目新增了简化格式的API接口，所有视频信息API都输出统一的 `Title`、`URL`、`Blogger` 三个字段格式。

## 新增的简化格式API

### 1. 获取用户新视频（简化格式）
```
GET /api/douyin/simple/fetch_user_new_videos_simple
```

**参数：**
- `sec_user_id`: 用户sec_user_id
- `max_cursor`: 最大游标（可选，默认0）
- `count`: 每页数量（可选，默认20）

**返回格式：**
```json
{
  "code": 200,
  "message": "获取到 5 个视频",
  "data": {
    "message": "获取到 5 个视频",
    "videos": [
      {
        "Title": "有趣的视频标题",
        "URL": "https://www.douyin.com/video/7372484719365098803",
        "Blogger": "博主昵称"
      },
      {
        "Title": "另一个视频标题",
        "URL": "https://www.douyin.com/video/7372484719365098804",
        "Blogger": "博主昵称"
      }
    ],
    "total_fetched": 5
  }
}
```

### 2. 获取用户发布视频（简化格式）
```
GET /api/douyin/simple/fetch_user_post_videos_simple
```

**参数：**
- `sec_user_id`: 用户sec_user_id
- `max_cursor`: 最大游标（可选，默认0）
- `count`: 每页数量（可选，默认20）

### 3. 获取用户喜欢视频（简化格式）
```
GET /api/douyin/simple/fetch_user_like_videos_simple
```

**参数：**
- `sec_user_id`: 用户sec_user_id
- `max_cursor`: 最大游标（可选，默认0）
- `counts`: 每页数量（可选，默认20）

### 4. 获取用户收藏视频（简化格式）
```
GET /api/douyin/simple/fetch_user_collection_videos_simple
```

**参数：**
- `cookie`: 用户网页版抖音Cookie
- `max_cursor`: 最大游标（可选，默认0）
- `counts`: 每页数量（可选，默认20）

### 5. 获取用户合辑视频（简化格式）
```
GET /api/douyin/simple/fetch_user_mix_videos_simple
```

**参数：**
- `mix_id`: 合辑id
- `max_cursor`: 最大游标（可选，默认0）
- `counts`: 每页数量（可选，默认20）

## 数据格式说明

所有简化格式API都返回相同的数据结构：

### 视频记录格式
每个视频记录包含以下三个字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| Title | String | 视频标题 |
| URL | String | 视频链接 |
| Blogger | String | 博主昵称 |

### 响应格式
```json
{
  "code": 200,
  "message": "操作结果描述",
  "data": {
    "message": "详细结果描述",
    "videos": [
      {
        "Title": "视频标题",
        "URL": "视频链接",
        "Blogger": "博主昵称"
      }
    ],
    "total_fetched": 视频数量
  }
}
```

## 使用示例

### 1. 获取用户新视频
```bash
curl -X GET "http://localhost:80/api/douyin/simple/fetch_user_new_videos_simple?sec_user_id=MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE&count=10"
```

### 2. 获取用户发布视频
```bash
curl -X GET "http://localhost:80/api/douyin/simple/fetch_user_post_videos_simple?sec_user_id=MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE&count=20"
```

### 3. 获取用户喜欢视频
```bash
curl -X GET "http://localhost:80/api/douyin/simple/fetch_user_like_videos_simple?sec_user_id=MS4wLjABAAAAW9FWcqS7RdQAWPd2AA5fL_ilmqsIFUCQ_Iym6Yh9_cUa6ZRqVLjVQSUjlHrfXY1Y&counts=15"
```

## 与Aitable.ai集成

这些简化格式API专门为 Aitable.ai 存储设计，每个视频记录都可以直接存储为 Aitable.ai 中的一行数据：

```json
{
  "records": [
    {
      "fields": {
        "Title": "视频标题",
        "URL": "视频链接",
        "Blogger": "博主昵称"
      }
    }
  ],
  "fieldKey": "name"
}
```

## 优势

1. **统一格式**: 所有视频API都使用相同的输出格式
2. **简化存储**: 只需要三个字段，减少存储复杂度
3. **Aitable.ai友好**: 直接适配 Aitable.ai 的数据结构
4. **易于处理**: 简化的数据结构便于后续处理和分析

## 注意事项

1. 简化格式API与原有API并存，不影响现有功能
2. 简化格式API专门用于 Aitable.ai 存储场景
3. 如果需要完整视频信息，仍可使用原有的详细格式API
4. 所有简化格式API都支持分页和游标功能
