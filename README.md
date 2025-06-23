# django5_task_kanban

## 项目简介
本项目是一个基于 Django 5 的任务看板系统，旨在为团队提供敏捷、高效的任务/项目管理解决方案。系统支持任务分组、看板视图、多团队协作、通知提醒、报表分析等多项功能。

## 主要特性
- 灵活的任务管理与看板视图
- 多团队协作支持
- 实时通知与邮件提醒
- 丰富的数据报表与进度追踪
- 模块化设计，方便扩展与二次开发
- 前端用户体验持续优化

## 目录结构简述
- `taskkanban/`：主应用代码，包含核心模块、API、团队、任务、报表等子模块
- `docs/`：项目文档，包含开发计划、环境搭建、功能报告、用例说明等
- `requirements/`：依赖配置
- `screenshots/`：界面截图，将后续补上

## 快速开始
1. 克隆仓库
   ```shell
   git clone https://github.com/HuangYunfa/django5_task_kanban.git
   ```
2. 安装依赖
   ```shell
   pip install -r requirements/requirements.txt
   ```
3. 数据库迁移
   ```shell
   python manage.py migrate
   ```
4. 启动服务
   ```shell
   python manage.py runserver
   ```

## 文档与资源
- [开发环境搭建文档](https://github.com/HuangYunfa/django5_task_kanban/blob/main/docs/开发环境搭建文档.md)
- [快速启动指南](https://github.com/HuangYunfa/django5_task_kanban/blob/main/docs/快速启动指南.md)
- [API模块开发完成报告](https://github.com/HuangYunfa/django5_task_kanban/blob/main/docs/API模块开发完成报告.md)
- [看板多视图功能完成报告](https://github.com/HuangYunfa/django5_task_kanban/blob/main/docs/看板多视图功能完成报告.md)
- 其余详细文档见 [docs 目录](https://github.com/HuangYunfa/django5_task_kanban/tree/main/docs)

## 参与贡献
欢迎提交 issue 或 PR，一起完善系统功能！

## License
MIT
