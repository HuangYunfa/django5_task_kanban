# UI自动化测试运行指南

## 🚀 快速开始

### 方法1: 使用批处理脚本 (推荐)
```bash
# 在项目根目录双击运行
run_ui_tests.bat
```

### 方法2: 手动运行
```bash
# 1. 启动Django服务器
cd taskkanban
python manage.py runserver

# 2. 新开终端，运行UI测试
cd tests\ui
python test_reports_playwright_enhanced.py
```

## 📋 测试内容

### 🎯 主要测试功能
- ✅ 用户登录和认证
- ✅ 报表分析页面导航
- ✅ 图表渲染和数据显示
- ✅ 报表导出功能
- ✅ 筛选和搜索功能
- ✅ 响应式设计 (桌面/平板/手机)
- ✅ 图表交互 (悬停/点击/类型切换)

### 📊 报表模块测试
1. **仪表板页面** - 总览图表和KPI指标
2. **任务完成率报表** - 任务统计和趋势分析
3. **用户工作负载报表** - 用户任务分配情况
4. **团队绩效报表** - 团队协作效率
5. **项目进度报表** - 项目整体进展

## 🎭 测试特性

### 🌟 可视化测试
- Chrome浏览器以**可见模式**启动
- 每个操作都有**慢动作展示** (1.5秒间隔)
- 实时观察测试执行过程

### 📸 自动截图
测试过程中会自动保存截图到 `screenshots/` 目录：
- `reports_main.png` - 报表主页
- `reports_dashboard.png` - 仪表板
- `task_completion_report.png` - 任务完成率报表
- `user_workload_report.png` - 用户工作负载报表
- `team_performance_report.png` - 团队绩效报表
- `project_progress_report.png` - 项目进度报表
- `reports_responsive_*.png` - 响应式设计截图
- `chart_interaction_*.png` - 图表交互截图

### 🔧 错误处理
- 测试失败时自动保存错误截图
- 详细的错误日志输出
- 优雅的异常处理机制

## 🛠️ 技术栈

- **Playwright** - 浏览器自动化
- **Django** - Web应用框架
- **Chart.js** - 数据可视化
- **Bootstrap** - UI框架
- **pytest** - 测试框架

## 📈 测试结果解读

### ✅ 成功指标
- 所有页面正常加载
- 图表正确渲染
- 交互功能响应正常
- 导出功能工作正常
- 响应式设计适配良好

### ⚠️ 注意事项
- 确保Django服务器在8000端口运行
- 确保测试用户 'huangyunfa' 存在且密码正确
- 首次运行可能需要安装Playwright浏览器: `playwright install`

## 🚨 故障排除

### 常见问题

1. **浏览器无法启动**
   ```bash
   # 安装Playwright浏览器
   playwright install
   ```

2. **Django服务器连接失败**
   ```bash
   # 检查服务器是否运行
   curl http://127.0.0.1:8000/
   ```

3. **登录失败**
   - 检查用户名密码是否正确
   - 确认测试用户已创建

4. **图表不显示**
   - 检查Chart.js是否正确加载
   - 确认报表数据已生成

## 📞 技术支持

如有问题，请查看以下文档：
- `docs/Playwright_UI自动化测试完成报告.md` - 详细技术报告
- `docs/TODO.md` - 项目开发计划
- `tests/ui/` - 测试源代码

---

*最后更新: 2025年6月24日*
