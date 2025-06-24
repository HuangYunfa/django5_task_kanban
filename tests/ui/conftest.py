"""
UI测试的特定配置和fixtures
"""
import os
import sys
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright, Browser, Page
from django.conf import settings
from typing import AsyncGenerator

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')

import django
django.setup()

import threading
from django.core.management import call_command
from django.core.servers.basehttp import WSGIServer
from django.core.wsgi import get_wsgi_application

@pytest_asyncio.fixture(scope="session", autouse=True)
def django_server(django_db_blocker):
    """启动Django测试服务器"""
    def run_server():
        with django_db_blocker.unblock():
            call_command('runserver', '127.0.0.1:8000', '--noreload', '--skip-checks')

    server_thread = threading.Thread(
        target=run_server,
        daemon=True
    )
    server_thread.start()
    yield
    # 服务器线程是守护线程，会在主线程结束时自动终止

@pytest_asyncio.fixture(scope="session")
async def browser() -> AsyncGenerator[Browser, None]:
    """创建浏览器实例"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # 在CI环境中使用无头模式
        yield browser
        await browser.close()

@pytest_asyncio.fixture
async def page(browser) -> AsyncGenerator[Page, None]:
    """创建新的浏览器页面"""
    context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = await context.new_page()
    yield page
    await page.close()
    await context.close()

@pytest.fixture(scope='session')
def django_db_setup():
    """设置测试数据库"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'NAME': ':memory:',
            'MIRROR': False
        }
    }

@pytest.fixture(scope='session', autouse=True)
def setup_test_data(django_db_setup, django_db_blocker):
    """初始化测试数据"""
    from .test_data import create_test_user
    with django_db_blocker.unblock():
        create_test_user()

@pytest_asyncio.fixture
async def login(page: Page):
    """执行登录流程"""
    async def _login(username: str = "project_manager", password: str = "demo123456") -> Page:
        await page.goto("http://127.0.0.1:8000/accounts/login/")
        await page.fill('input[name="login"]', username)
        await page.fill('input[name="password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        
        # 验证登录成功
        await page.wait_for_selector('.user-menu')  # 等待用户菜单出现
        assert await page.get_by_role('link', name=username).is_visible(), "用户名未显示，登录可能失败"
        return page
    
    return _login
