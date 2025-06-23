"""
UI测试的特定配置和fixtures
"""
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    """创建浏览器实例"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    """创建新的浏览器页面"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    page.close()
    context.close()

@pytest.fixture
def login(page):
    """执行登录流程"""
    def _login(username="project_manager", password="demo123456"):
        page.goto("http://127.0.0.1:8000/accounts/login/")
        page.fill('input[name="login"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        return "dashboard" in page.url
    
    return _login
