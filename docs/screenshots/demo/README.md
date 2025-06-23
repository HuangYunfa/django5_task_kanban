# 产品演示截图

本目录包含了系统主要功能模块的演示截图，这些截图是通过自动化测试脚本生成的，用于产品展示和文档说明。

## 截图列表

1. `homepage.png` - 系统首页
2. `dashboard.png` - 用户工作台
3. `boards.png` - 看板管理页面（优化版，使用自定义CSS样式）
4. `board_detail.png` - 看板详情视图
5. `tasks.png` - 任务管理页面
6. `teams.png` - 团队管理页面
7. `reports.png` - 报表分析页面
8. `api_docs.png` - API文档页面
9. `user_profile.png` - 用户资料页面

## 如何生成

这些截图可以通过项目中的自动化脚本生成：

1. 确保系统已启动：
   ```
   cd taskkanban
   python manage.py runserver
   ```

2. 在另一个终端中运行截图生成脚本：
   ```
   python tools/demo/create_screenshots.py
   ```

3. 脚本会自动使用测试账号登录系统并为主要功能模块生成截图。

4. 对于看板管理页面，我们提供了优化样式的专用脚本：
   ```
   python tools/demo/fix_board_cards_style.py
   ```
   该脚本会注入自定义CSS，改进看板卡片的样式和用户体验，然后生成优化版的截图。

## 测试账号信息

- 用户名: `project_manager`
- 密码: `demo123456`

## 注意事项

- 截图生成需要安装 Playwright
- 生成的截图会根据屏幕分辨率有所不同
- 数据内容可能会根据系统中的实际数据而变化
