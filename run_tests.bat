@echo off
rem 设置Python路径
set PYTHONPATH=%CD%;%CD%\taskkanban;%CD%\tests
set DJANGO_SETTINGS_MODULE=taskkanban.settings

rem 切换到Django项目目录
cd taskkanban

rem 运行测试
python manage.py test tests.ui.test_reports_analysis_playwright -v 2
