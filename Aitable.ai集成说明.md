# Aitable.ai 集成说明

## 概述

这个增强版定时任务系统支持将抖音新视频数据直接存储到 **Aitable.ai** 数据库中，每个视频会创建单独的一行记录。

## 功能特性

- 🕐 **定时执行**: 每天北京时间 12:00、17:00、20:00、22:00 自动执行
- 👥 **博主管理**: 支持添加、删除、查看关注的博主
- 🔄 **自动去重**: 只获取数据库中不存在的新视频
- 📊 **Aitable.ai存储**: 每个新视频创建单独的行记录
- ⚡ **并发处理**: 支持并发抓取多个博主的新视频

## 工作流程

```
定时任务 → 调用API → 获取新视频 → 解析数据 → 存储到Aitable.ai
```

## 配置步骤

### 1. 设置 Aitable.ai 配置

编辑 `config.yaml` 文件：

```yaml
# Aitable.ai Configuration
Aitable:
  api_key: "uskIZVNT6ybBEQxO5cTPcCa"    # 你的Aitable.ai API Key
  base_id: "dstGGELxSrPMb0kRWa"         # 你的Aitable.ai Datasheet ID
  table_name: "viwMgMZrxb1Zv"           # View ID
```

### 2. 获取 Aitable.ai 配置信息

#### 获取 API Key (Bearer Token)
1. 登录 [Aitable.ai](https://aitable.ai)
2. 进入开发者设置
3. 创建新的 API Key

#### 获取 Datasheet ID
1. 打开你的 Aitable.ai 数据表
2. 查看 URL: `https://aitable.ai/datasheet/DATASHEET_ID`
3. `DATASHEET_ID` 就是你的 Datasheet ID

#### 获取 View ID
1. 在数据表中选择对应的视图
2. 查看 URL 中的 `viewId` 参数
3. 或者使用默认视图

### 3. 创建表结构

在 Aitable.ai 中创建一个数据表，包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| Title | Text | 视频标题 |
| URL | URL | 视频链接 |
| Blogger | Text | 博主昵称 |

## 使用方法

### 1. 启动 API 服务器

```bash
python start.py
```

### 2. 添加关注的博主

通过 Aitable.ai 的 webhook 接口自动添加博主：

1. **在 Aitable.ai 中设置 webhook**:
   - 将 webhook URL 设置为: `http://your-server:80/api/aitable/blogger_cookie`
   - 当在 Aitable.ai 中添加新博主时，会自动同步到系统

2. **或者直接调用 API**:
   ```bash
   curl -X POST "http://localhost:80/api/aitable/add_user" \
        -H "Content-Type: application/json" \
        -d '{
          "user_id": "MS4wLjABAAAAzdUNicnvSbYj3AfLtAhThVtATHyveJSaAE9hm0ul1_w",
          "username": "博主用户名",
          "nickname": "博主昵称"
        }'
   ```

### 3. 启动增强版定时任务

```bash
python enhanced_scheduler.py
```

## 管理命令

### 配置 Aitable.ai

```bash
# 测试连接
curl -X GET "http://localhost:80/api/aitable/test_connection"
```

### 管理关注博主

#### 通过 Aitable.ai Webhook (推荐)
1. **设置 webhook URL**: `http://your-server:80/api/aitable/blogger_cookie`
2. **在 Aitable.ai 中操作**:
   - 添加博主: 在 Aitable.ai 中添加新记录，设置 `Status` 为 `Add user_id`
   - 删除博主: 在 Aitable.ai 中设置 `Status` 为 `Delete user_id`
   - 更新 Cookie: 在 Aitable.ai 中设置 `Status` 为 `Refresh Cookie`

#### 通过 API 接口
```bash
# 添加博主
curl -X POST "http://localhost:80/api/aitable/add_user" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user_id", "username": "username", "nickname": "nickname"}'

# 查看博主列表
curl -X GET "http://localhost:80/api/aitable/get_users"

# 删除博主
curl -X DELETE "http://localhost:80/api/aitable/delete_user/user_id"
```

## 数据存储示例

当发现新视频时，系统会为每个视频创建一条记录：

```
视频1: "有趣的视频标题1" → Aitable.ai 第1行
  - Title: "有趣的视频标题1"
  - URL: "https://www.douyin.com/video/7372484719365098803"
  - Blogger: "博主昵称"

视频2: "有趣的视频标题2" → Aitable.ai 第2行
  - Title: "有趣的视频标题2"
  - URL: "https://www.douyin.com/video/7372484719365098804"
  - Blogger: "博主昵称"

视频3: "有趣的视频标题3" → Aitable.ai 第3行
  - Title: "有趣的视频标题3"
  - URL: "https://www.douyin.com/video/7372484719365098805"
  - Blogger: "博主昵称"
```

## 日志文件

- `enhanced_scheduler.log` - 增强版定时任务执行日志
- 包含执行时间、处理结果、Aitable.ai 存储状态等

## 注意事项

1. **API 限制**: Aitable.ai 可能有 API 调用频率限制
2. **网络连接**: 确保能够访问 Aitable.ai API
3. **权限设置**: 确保 API Key 有写入权限
4. **表结构**: 确保 Aitable.ai 中的表字段与代码匹配

## 故障排除

### 常见问题

1. **API Key 无效**
   - 错误: "API Key无效"
   - 解决: 检查 API Key 是否正确

2. **表不存在**
   - 错误: "表不存在"
   - 解决: 检查表名是否正确

3. **权限不足**
   - 错误: "没有访问权限"
   - 解决: 检查 API Key 权限

4. **字段不匹配**
   - 错误: "字段验证失败"
   - 解决: 确保 Aitable.ai 表字段与代码匹配

### 查看日志

```bash
# 查看实时日志
tail -f enhanced_scheduler.log

# 查看最近的日志
tail -n 100 enhanced_scheduler.log
```

## 扩展功能

### 自定义字段映射

可以在 `enhanced_scheduler.py` 中修改 `parse_video_data` 方法来调整字段映射：

```python
def parse_video_data(self, video_info: Dict[str, Any], user_info: Dict[str, Any]) -> Dict[str, Any]:
    # 自定义字段映射逻辑
    video_data = {
        'Video ID': video_info.get('aweme_id', ''),
        'Title': video_info.get('desc', '无标题'),
        # 添加更多自定义字段
    }
    return video_data
```

### 批量存储优化

如果需要提高存储效率，可以修改代码支持批量存储：

```python
async def store_videos_batch(self, session: aiohttp.ClientSession, videos_data: List[Dict[str, Any]]) -> bool:
    # 批量存储多个视频
    pass
```

## 技术支持

如果遇到问题：

1. 测试连接: `curl -X GET "http://localhost:80/api/aitable/test_connection"`
2. 查看日志: `enhanced_scheduler.log`
3. 检查配置: `config.yaml`
4. 验证表结构: 确保 Aitable.ai 表字段正确

---

这个增强版系统为你提供了一个完整的解决方案，可以自动监控关注博主的新视频并将数据存储到 Aitable.ai 中，每个视频都会创建独立的记录行。
