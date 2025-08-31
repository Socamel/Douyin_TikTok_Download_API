# 如何获取抖音（Douyin）和 TikTok �?Cookie

本项目部分功能需要配置抖音或 TikTok �?Cookie，以下是详细获取步骤�?

---

## 1. 获取抖音（Douyin）Cookie

1. 使用 Chrome �?Edge 浏览器访�?https://www.douyin.com/
2. 登录你的抖音账号�?
3. �?F12 打开开发者工具，切换到「应用程序�?Application) 或「存储�?Storage)�?
4. 在左侧找到「Cookies」→ 选择 `https://www.douyin.com`�?
5. 复制所�?Cookie 内容（如 `Cookie: ...`），粘贴�?`crawlers/douyin/web/config.yaml` 文件对应�?`Cookie:` 字段�?

---

## 2. 获取 TikTok Cookie

1. 使用 Chrome �?Edge 浏览器访�?https://www.tiktok.com/
2. 登录你的 TikTok 账号�?
3. �?F12 打开开发者工具，切换到「应用程序�?Application) 或「存储�?Storage)�?
4. 在左侧找到「Cookies」→ 选择 `https://www.tiktok.com`�?
5. 复制所�?Cookie 内容，粘贴到 `crawlers/tiktok/web/config.yaml` 文件对应�?`Cookie:` 字段�?

---

## 3. 注意事项
- 建议使用已登录账号的 Cookie，且 Cookie 需要定期更新�?
- 修改完配置文件后需重启服务�?
- 不要随意修改 User-Agent 字段，否则可能导致请求失败�?
- 仅用于学习和交流，禁止用于非法用途�?

---

如需图文教程或遇到问题，可参考项�?README 或联系开发者�?
