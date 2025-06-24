"""
测试登录流程的基本UI测试
"""
import pytest
from playwright.async_api import expect, Page

pytestmark = [
    pytest.mark.ui,  # 标记为UI测试
    pytest.mark.asyncio  # 标记为异步测试
]

async def test_login_success(page: Page, login):
    """测试正常登录流程"""
    page = await login()  # 使用默认用户名密码
    # 验证重定向到看板页面
    assert page.url.endswith('/boards/'), "登录后未重定向到看板页面"
    # 验证用户菜单存在
    await expect(page.get_by_role('button', name='用户菜单')).to_be_visible()

async def test_login_failed(page: Page):
    """测试登录失败场景"""
    await page.goto("http://127.0.0.1:8000/accounts/login/")
    await page.fill('input[name="login"]', "wrong_user")
    await page.fill('input[name="password"]', "wrong_pass")
    await page.click('button[type="submit"]')
    
    # 等待错误消息出现
    await page.wait_for_load_state('networkidle')
    error_msg = page.get_by_text("请输入正确的用户名和密码")
    await expect(error_msg).to_be_visible()
    # 确认未重定向
    assert "login" in page.url, "错误登录不应重定向"
