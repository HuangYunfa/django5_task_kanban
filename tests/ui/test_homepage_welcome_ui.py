"""
首页欢迎提示与待办/通知UI自动化测试（Playwright）
"""
import time
from playwright.sync_api import sync_playwright, expect

class HomePageWelcomeUITest:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.base_url = "http://127.0.0.1:8000"

    def setup(self, headless=True):
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def teardown(self):
        if self.browser:
            self.browser.close()

    def wait_for_load(self, timeout=5000):
        self.page.wait_for_load_state('networkidle', timeout=timeout)
        time.sleep(0.5)

    def login(self, username, password):
        """自动登录"""
        self.page.goto(f"{self.base_url}/users/login/")
        self.wait_for_load()
        self.page.fill("input[name='username']", username)
        self.page.fill("input[name='password']", password)
        self.page.click("button[type='submit']")
        self.wait_for_load()

    def test_homepage_welcome_message(self):
        print("\n=== 测试首页欢迎提示自动淡出 ===")
        # 先登录
        self.login("admin", "admin123")  # 请替换为实际测试账号
        self.page.goto(f"{self.base_url}/?welcome=1")
        self.wait_for_load()
        # 检查欢迎提示是否出现
        alert = self.page.locator("#login-welcome-alert")
        expect(alert).to_be_visible()
        print("✓ 欢迎提示已显示")
        # 等待3.5秒后检查是否自动消失
        time.sleep(3.5)
        expect(alert).not_to_be_visible()
        print("✓ 欢迎提示已自动淡出")

    def test_homepage_todo_and_notifications(self):
        print("\n=== 测试首页待办与通知展示 ===")
        # 假设已登录，直接访问首页
        self.page.goto(f"{self.base_url}/")
        self.wait_for_load()
        # 检查待办任务区块
        todo_title = self.page.locator("text=我的待办任务")
        expect(todo_title).to_be_visible()
        print("✓ 待办任务区块可见")
        # 检查重要通知区块
        notice_title = self.page.locator("text=重要通知")
        expect(notice_title).to_be_visible()
        print("✓ 重要通知区块可见")

if __name__ == "__main__":
    test = HomePageWelcomeUITest()
    test.setup(headless=True)
    try:
        test.test_homepage_welcome_message()
        test.test_homepage_todo_and_notifications()
    finally:
        test.teardown()
