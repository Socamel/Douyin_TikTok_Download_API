# 简化格式API说明

## 概述

为了适配 Aitable.ai 存储需求，项目新增了简化格式的API接口，所有视频信息API都输出统一的 `Title`、`URL`、`Blogger` 三个字段格式。

**重要说明**：简化格式API会优先从本地数据库获取用户昵称，确保Blogger字段显示正确的博主名称。API会使用传入的 `sec_user_id` 参数查询数据库中的用户信息。如果数据库中还没有该用户信息，建议先通过Aitable.ai集成或手动添加用户信息。

**新增功能**：现在支持自动翻页功能，可以一次性获取用户的所有视频，解决翻页问题。

## 新增的简化格式API

### 1. 获取用户新视频（简化格式）
```
GET /api/douyin/simple/fetch_user_new_videos_simple
```

**参数：**
- `sec_user_id`: 用户sec_user_id
- `max_cursor`: 最大游标（可选，默认0）
- `count`: 每页数量（可选，默认1000）
- `auto_pagination`: 自动翻页（可选，默认false，当max_cursor=0时生效）

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
- `count`: 每页数量（可选，默认1000）
- `auto_pagination`: 自动翻页（可选，默认false，当max_cursor=0时生效）

### 3. 获取用户喜欢视频（简化格式）
```
GET /api/douyin/simple/fetch_user_like_videos_simple
```

**参数：**
- `sec_user_id`: 用户sec_user_id
- `max_cursor`: 最大游标（可选，默认0）
- `count`: 每页数量（可选，默认1000）
- `auto_pagination`: 自动翻页（可选，默认false，当max_cursor=0时生效）

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

### 1. 获取用户新视频（单页）
```bash
curl -X GET "http://localhost:8501/api/douyin/simple/fetch_user_new_videos_simple?sec_user_id=MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
```

### 2. 获取用户发布视频（自动翻页，获取所有视频）
```bash
curl -X GET "http://localhost:8501/api/douyin/simple/fetch_user_post_videos_simple?sec_user_id=MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE&auto_pagination=true"
```

### 3. 获取用户喜欢视频（自动翻页，限制数量）
```bash
curl -X GET "http://localhost:8501/api/douyin/simple/fetch_user_like_videos_simple?sec_user_id=MS4wLjABAAAAW9FWcqS7RdQAWPd2AA5fL_ilmqsIFUCQ_Iym6Yh9_cUa6ZRqVLjVQSUjlHrfXY1Y&auto_pagination=true&count=500"
```

### 4. 手动翻页获取视频
```bash
# 第一页
curl -X GET "http://localhost:8501/api/douyin/simple/fetch_user_post_videos_simple?sec_user_id=MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE&max_cursor=0"

# 第二页（使用返回的max_cursor值）
curl -X GET "http://localhost:8501/api/douyin/simple/fetch_user_post_videos_simple?sec_user_id=MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE&max_cursor=1234567890"
```

## 自动翻页功能

### 功能说明
为了解决抖音API的翻页限制问题，新增了自动翻页功能：

- **自动翻页**：当 `auto_pagination=true` 且 `max_cursor=0` 时，API会自动获取用户的所有视频
- **数量限制**：可以通过 `count` 参数限制最大获取数量
- **安全保护**：最多获取50页数据，防止无限循环

### 使用场景
1. **获取所有视频**：`auto_pagination=true`
2. **限制数量**：`auto_pagination=true&count=500`
3. **单页获取**：`auto_pagination=false`（默认）

### 注意事项
- 自动翻页会增加请求时间，建议合理设置count值
- 当用户视频数量很多时，建议分批获取
- 自动翻页功能仅在 `max_cursor=0` 时生效

## 与Aitable.ai集成

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
5. **自动翻页**: 支持自动获取所有视频，解决翻页问题

## 注意事项

1. 简化格式API与原有API并存，不影响现有功能
2. 简化格式API专门用于 Aitable.ai 存储场景
3. 如果需要完整视频信息，仍可使用原有的详细格式API
4. 所有简化格式API都支持分页和游标功能
5. **Blogger字段优化**：API会优先从本地数据库获取用户昵称，如果数据库中没有该用户信息，会显示"未知博主"
6. **建议流程**：首次使用某个sec_user_id时，建议先通过Aitable.ai集成或Streamlit数据库界面添加用户信息
7. **自动翻页**：使用 `auto_pagination=true` 可以自动获取所有视频，但会增加请求时间
8. **数量限制**：建议合理设置count值，避免一次性获取过多数据
