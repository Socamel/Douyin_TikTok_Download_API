# Aitable.ai 集成说明

## 📊 端口配置表

| 服务 | 端口 | 用途 |
|------|------|------|
| **FastAPI** | **8501** | 主API服务 |
| **Streamlit** | **8502** | 数据库管理界面 |
| **Streamlit** | **8503** | 备用端口 |
| **Streamlit** | **8504** | 故障排除端口 |
| **Streamlit** | **8505** | HTTPS生产环境 |

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

#### 方法一：通过 Aitable.ai 自动化功能（推荐）

1. **在 Aitable.ai 中设置自动化规则**:
   - 进入你的数据表
   - 点击"自动化"标签
   - 创建新的自动化规则
   - 选择触发条件（如：新增记录、字段更新等）
   - 选择动作类型：**HTTP 请求**
   - 设置请求方法：**POST** 或 **GET**
       - 设置请求URL：`http://your-server:8501/api/aitable/blogger_cookie`
   - 设置请求头：`Content-Type: application/json`
   - 设置请求体（POST方法）：
   ```json
   {
     "recordId": "{{recordId}}",
     "fields": {
       "Blogger": "{{Blogger}}",
       "Status": "{{Status}}",
       "user_id": "{{user_id}}",
       "cookie": "{{cookie}}"
     }
   }
   ```

2. **自动化触发示例**:
   - 当在 Aitable.ai 中添加新博主时，自动化会发送POST请求到API
   - 当更新博主状态时，自动化会发送GET请求到API
   - API会自动处理博主信息的同步

#### 方法二：直接调用 API

```bash
curl -X POST "http://localhost:8501/api/aitable/add_user" \
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
curl -X GET "http://localhost:8501/api/aitable/test_connection"
```

### 管理关注博主

#### 通过 Aitable.ai 自动化（推荐）

1. **设置自动化规则**:
   - 进入 Aitable.ai 数据表
   - 点击"自动化" → "创建规则"
   - 设置触发条件：
     - **新增记录**：当添加新博主时
     - **字段更新**：当更新Status字段时
   - 设置动作：**HTTP 请求**
       - 请求URL：`http://your-server:8501/api/aitable/blogger_cookie`
   - 请求方法：**POST**（新增）或 **GET**（查询）
   - 请求体（POST）：
   ```json
   {
     "recordId": "{{recordId}}",
     "fields": {
       "Blogger": "{{Blogger}}",
       "Status": "{{Status}}",
       "user_id": "{{user_id}}",
       "cookie": "{{cookie}}"
     }
   }
   ```

2. **在 Aitable.ai 中操作**:
   - **添加博主**: 在数据表中添加新记录，设置 `Status` 为 `Add user_id`
   - **删除博主**: 在数据表中设置 `Status` 为 `Delete user_id`
   - **更新 Cookie**: 在数据表中设置 `Status` 为 `Refresh Cookie`
   - **查询博主**: 设置 `Status` 为 `Get user info`

3. **自动化触发流程**:
   ```
   用户在Aitable.ai中操作 → 自动化规则触发 → 发送HTTP请求到API → API处理数据 → 返回结果
   ```

#### 通过 API 接口
```bash
# 添加博主
curl -X POST "http://localhost:8501/api/aitable/add_user" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user_id", "username": "username", "nickname": "nickname"}'

# 查看博主列表
curl -X GET "http://localhost:8501/api/aitable/get_users"

# 删除博主
curl -X DELETE "http://localhost:8501/api/aitable/delete_user/user_id"
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

## 自动化配置详解

### Aitable.ai 自动化设置步骤

#### 1. 创建自动化规则

1. **进入自动化设置**:
   - 打开你的 Aitable.ai 数据表
   - 点击左侧菜单的"自动化"
   - 点击"创建规则"

2. **设置触发条件**:
   - **触发类型**: 选择"记录变更"
   - **触发条件**: 
     - 新增记录时
     - 字段更新时（选择Status字段）
   - **过滤条件**: 可选，如 `Status` 不为空

3. **设置动作**:
   - **动作类型**: 选择"发送HTTP请求"
   - **请求方法**: 
     - POST（用于新增、更新操作）
     - GET（用于查询操作）
       - **请求URL**: `http://your-server:8501/api/aitable/blogger_cookie`
   - **请求头**:
     ```
     Content-Type: application/json
     ```
   - **请求体**（POST方法）:
     ```json
     {
       "recordId": "{{recordId}}",
       "fields": {
         "Blogger": "{{Blogger}}",
         "Status": "{{Status}}",
         "user_id": "{{user_id}}",
         "cookie": "{{cookie}}"
       }
     }
     ```

#### 2. 自动化规则示例

##### 规则1：新增博主
- **触发条件**: 新增记录
- **动作**: POST 请求
- **用途**: 自动添加新博主到系统

##### 规则2：更新状态
- **触发条件**: Status 字段更新
- **动作**: POST 请求
- **用途**: 处理博主状态变更

##### 规则3：查询信息
- **触发条件**: Status 字段更新为 "Get user info"
- **动作**: GET 请求
- **用途**: 获取博主详细信息

#### 3. 字段映射说明

| Aitable字段 | API字段 | 说明 |
|-------------|---------|------|
| `{{recordId}}` | recordId | 记录ID，自动生成 |
| `{{Blogger}}` | fields.Blogger | 博主昵称 |
| `{{Status}}` | fields.Status | 操作状态 |
| `{{user_id}}` | fields.user_id | 用户ID |
| `{{cookie}}` | fields.cookie | Cookie数据 |

#### 4. 状态值说明

| Status值 | 操作类型 | 说明 |
|----------|----------|------|
| `Add user_id` | 添加用户 | 新增博主到系统 |
| `Delete user_id` | 删除用户 | 从系统删除博主 |
| `Refresh Cookie` | 更新Cookie | 更新博主Cookie |
| `Get user info` | 查询信息 | 获取博主详细信息 |

### 自动化测试

#### 测试自动化规则

1. **测试新增博主**:
   - 在 Aitable.ai 中添加新记录
   - 设置 `Blogger` 为 "测试博主"
   - 设置 `Status` 为 "Add user_id"
   - 观察自动化是否触发

2. **测试状态更新**:
   - 更新现有记录的 `Status` 字段
   - 检查API是否收到请求
   - 验证处理结果

3. **查看自动化日志**:
   - 在 Aitable.ai 中查看自动化执行历史
   - 检查请求是否成功发送
   - 查看API响应结果

## 注意事项

1. **API 限制**: Aitable.ai 可能有 API 调用频率限制
2. **网络连接**: 确保能够访问 Aitable.ai API
3. **权限设置**: 确保 API Key 有写入权限
4. **表结构**: 确保 Aitable.ai 中的表字段与代码匹配
5. **自动化配置**: 确保自动化规则正确设置，包括触发条件和请求格式
6. **服务器可访问性**: 确保你的服务器可以被 Aitable.ai 访问（公网IP或域名）
7. **请求格式**: 确保自动化中的请求体格式与API期望的格式一致
8. **错误处理**: 监控自动化执行日志，及时处理失败请求

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

1. 测试连接: `curl -X GET "http://localhost:8501/api/aitable/test_connection"`
2. 查看日志: `enhanced_scheduler.log`
3. 检查配置: `config.yaml`
4. 验证表结构: 确保 Aitable.ai 表字段正确

---

这个增强版系统为你提供了一个完整的解决方案，可以自动监控关注博主的新视频并将数据存储到 Aitable.ai 中，每个视频都会创建独立的记录行。
