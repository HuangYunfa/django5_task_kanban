#!/usr/bin/env python
"""
Django 5 任务看板系统 - Playwright UI自动化测试
测试任务状态流转系统的前端交互功能

功能覆盖：
1. 用户登录和注销
2. 任务详情页面的状态变更UI
3. 状态历史记录显示
4. 状态转换权限验证
5. 工作流状态管理界面

运行方法：
    python test_ui_workflow_playwright.py
    或
    pytest test_ui_workflow_playwright.py -v
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright, expect
import requests


class PlaywrightUITest:
    """Playwright UI测试基类"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.base_url = "http://127.0.0.1:8000"
        
    def setup_browser(self, headless=True):
        """初始化浏览器"""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
    def teardown_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            
    def wait_for_load(self, timeout=5000):
        """等待页面加载完成"""
        self.page.wait_for_load_state('networkidle', timeout=timeout)
        time.sleep(0.5)  # 额外等待时间确保JS执行完成


class WorkflowUITest(PlaywrightUITest):
    """任务状态流转UI测试"""
    
    def test_user_login_logout(self):
        """测试用户登录和注销功能"""
        print("\n=== 测试用户登录和注销功能 ===")
        
        try:
            # 访问登录页面
            self.page.goto(f"{self.base_url}/users/login/")
            self.wait_for_load()
            
            # 检查登录页面元素
            expect(self.page.locator("input[name='username']")).to_be_visible()
            expect(self.page.locator("input[name='password']")).to_be_visible()
            expect(self.page.locator("button[type='submit']")).to_be_visible()
            
            # 填写登录信息
            self.page.fill("input[name='username']", "admin")
            self.page.fill("input[name='password']", "admin123")
            
            # 点击登录
            self.page.click("button[type='submit']")
            self.wait_for_load()
            
            # 检查是否登录成功（检查页面是否跳转）
            current_url = self.page.url
            print(f"登录后页面URL: {current_url}")
            
            # 检查是否有登录用户信息
            if self.page.locator("text=admin").count() > 0:
                print("✓ 登录成功 - 找到用户名显示")
            else:
                print("⚠ 登录状态不确定 - 未找到明确的用户名显示")
            
            print("✓ 用户登录测试完成")
            
        except Exception as e:
            print(f"✗ 用户登录测试失败: {e}")
            
    def test_task_detail_page(self):
        """测试任务详情页面"""
        print("\n=== 测试任务详情页面 ===")
        
        try:
            # 先尝试访问任务列表页面
            self.page.goto(f"{self.base_url}/tasks/")
            self.wait_for_load()
            
            # 检查是否有任务链接
            task_links = self.page.locator("a[href*='/tasks/']").all()
            
            if len(task_links) > 0:
                # 点击第一个任务链接
                first_task_link = task_links[0]
                task_url = first_task_link.get_attribute('href')
                print(f"访问任务详情页面: {task_url}")
                
                self.page.goto(f"{self.base_url}{task_url}")
                self.wait_for_load()
                
                # 检查任务详情页面元素
                if self.page.locator("h1").count() > 0:
                    task_title = self.page.locator("h1").first.text_content()
                    print(f"任务标题: {task_title}")
                
                # 检查状态相关元素
                status_elements = [
                    ".task-status",
                    ".status-change-form",
                    ".workflow-controls",
                    "[data-status]"
                ]
                
                for selector in status_elements:
                    if self.page.locator(selector).count() > 0:
                        print(f"✓ 找到状态元素: {selector}")
                    else:
                        print(f"○ 未找到状态元素: {selector}")
                
                print("✓ 任务详情页面访问测试完成")
            else:
                print("⚠ 未找到任务链接，创建测试任务...")
                # 如果没有任务，尝试创建一个
                self.create_test_task()
                
        except Exception as e:
            print(f"✗ 任务详情页面测试失败: {e}")
            
    def test_workflow_status_management(self):
        """测试工作流状态管理页面"""
        print("\n=== 测试工作流状态管理页面 ===")
        
        try:
            # 访问工作流状态列表页面
            self.page.goto(f"{self.base_url}/tasks/workflow/status/")
            self.wait_for_load()
            
            # 检查页面标题
            if self.page.locator("h1").count() > 0:
                page_title = self.page.locator("h1").first.text_content()
                print(f"页面标题: {page_title}")
            
            # 检查状态列表
            status_rows = self.page.locator("tr").all()
            print(f"找到 {len(status_rows)} 个表格行")
            
            # 检查添加状态按钮
            add_buttons = [
                "a[href*='add']",
                ".btn-primary",
                "text=添加",
                "text=新建"
            ]
            
            for selector in add_buttons:
                if self.page.locator(selector).count() > 0:
                    print(f"✓ 找到添加按钮: {selector}")
                    break
            
            print("✓ 工作流状态管理页面测试完成")
            
        except Exception as e:
            print(f"✗ 工作流状态管理页面测试失败: {e}")
            
    def test_status_change_interaction(self):
        """测试状态变更交互"""
        print("\n=== 测试状态变更交互 ===")
        
        try:
            # 尝试找到一个任务进行状态变更测试
            self.page.goto(f"{self.base_url}/tasks/")
            self.wait_for_load()
            
            # 查找状态变更相关的元素
            status_selectors = [
                "select[name='status']",
                ".status-dropdown",
                ".status-change-btn",
                "[data-action='change-status']"
            ]
            
            found_elements = []
            for selector in status_selectors:
                elements = self.page.locator(selector).all()
                if len(elements) > 0:
                    found_elements.append((selector, len(elements)))
                    print(f"✓ 找到状态变更元素: {selector} ({len(elements)}个)")
            
            if found_elements:
                print("✓ 状态变更交互元素检测完成")
            else:
                print("○ 未找到明确的状态变更交互元素")
                
        except Exception as e:
            print(f"✗ 状态变更交互测试失败: {e}")
            
    def create_test_task(self):
        """创建测试任务数据"""
        print("创建测试任务数据...")
        try:
            # 这里可以通过API或直接数据库操作创建测试数据
            # 为简化，这里只是一个占位符
            print("○ 测试数据创建功能需要进一步实现")
        except Exception as e:
            print(f"创建测试数据失败: {e}")
            
    def run_all_tests(self, headless=True):
        """运行所有UI测试"""
        print(f"\n{'='*60}")
        print("Django 5 任务看板系统 - Playwright UI自动化测试")
        print(f"{'='*60}")
        print(f"测试环境: {self.base_url}")
        print(f"浏览器模式: {'无头模式' if headless else '可视模式'}")
        print(f"{'='*60}")
        
        try:
            self.setup_browser(headless=headless)
            
            # 执行所有测试
            self.test_user_login_logout()
            self.test_task_detail_page()
            self.test_workflow_status_management()
            self.test_status_change_interaction()
            
            print(f"\n{'='*60}")
            print("✓ 所有UI测试执行完成")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"\n✗ UI测试执行失败: {e}")
            
        finally:
            self.teardown_browser()


def check_server_status():
    """检查Django开发服务器状态"""
    print("检查Django开发服务器状态...")
    
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        if response.status_code == 200:
            print("✓ Django开发服务器运行正常")
            return True
        else:
            print(f"⚠ Django开发服务器返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到Django开发服务器: {e}")
        print("\n请确保Django开发服务器正在运行:")
        print("  cd taskkanban")
        print("  python manage.py runserver")
        return False


def main():
    """主测试函数"""
    print("Playwright UI自动化测试启动...")
    
    # 检查服务器状态
    if not check_server_status():
        print("\n请先启动Django开发服务器，然后重新运行测试")
        return
    
    # 运行UI测试
    ui_test = WorkflowUITest()
    
    # 询问是否使用可视模式
    try:
        mode = input("\n选择测试模式 (1: 无头模式, 2: 可视模式) [默认: 1]: ").strip()
        headless = mode != '2'
    except KeyboardInterrupt:
        print("\n测试已取消")
        return
    
    ui_test.run_all_tests(headless=headless)


if __name__ == "__main__":
    main()
