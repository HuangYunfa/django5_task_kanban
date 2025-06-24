@echo off
echo ================================================
echo    Django 企业级任务看板 - UI自动化测试
echo ================================================
echo.

cd /d "%~dp0"

echo 🔍 检查当前目录...
echo 当前目录: %CD%

echo.
echo 🚀 启动Django开发服务器...
cd taskkanban
start "Django Server" cmd /c "python manage.py runserver --noreload"

echo ⏳ 等待Django服务器启动...
timeout /t 8 /nobreak >nul

echo.
echo 🎭 启动Playwright UI自动化测试...
echo 💡 Chrome浏览器将以可视模式启动，请观察测试过程
echo.

cd ..\tests\ui
python test_reports_playwright_enhanced.py

echo.
echo 📊 UI自动化测试完成！
echo 📸 测试截图已保存到 screenshots\ 目录
echo.

pause
