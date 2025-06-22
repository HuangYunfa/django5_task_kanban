#!/usr/bin/env python
"""
Django 5 任务看板系统 - 完整的Playwright UI测试
包含登录功能和实际的工作流测试

运行方法：
    python test_ui_with_login.py
"""

import time
from playwright.sync_api import sync_playwright, expect
import requests


def check_server():
    """检查Django服务器状态"""
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        return response.status_code == 200
    except:
        return False


def run_full_ui_test(headless=False):
    """运行完整的UI测试，包含登录功能"""
    print(f"\n{'='*60}")
    print("Django 5 任务看板系统 - 完整UI测试（包含登录）")
    print(f"浏览器模式: {'无头模式' if headless else '可视模式'}")
    print(f"{'='*60}")
    
    if not check_server():
        print("✗ Django服务器未运行，请先启动：")
        print("  cd taskkanban && python manage.py runserver")
        return
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. 访问主页
            print("\n1. 访问主页...")
            page.goto("http://127.0.0.1:8000")
            page.wait_for_load_state('networkidle')
            print(f"   页面标题: {page.title()}")
            
            # 2. 尝试登录
            print("\n2. 尝试用户登录...")
            page.goto("http://127.0.0.1:8000/accounts/login/")
            page.wait_for_load_state('networkidle')
            
            # 检查是否有登录表单
            login_input = page.locator("input[name='login']")
            password_input = page.locator("input[name='password']")
            
            if login_input.count() > 0 and password_input.count() > 0:
                print("   ✓ 找到登录表单")
                
                # 尝试使用超级用户登录（假设已创建）
                login_input.fill("admin")
                password_input.fill("admin123")
                
                # 点击登录按钮
                login_button = page.locator("button[type='submit']")
                if login_button.count() > 0:
                    login_button.click()
                    page.wait_for_load_state('networkidle')
                    print(f"   登录后页面: {page.url}")
                    
                    # 检查是否登录成功
                    if "login" not in page.url:
                        print("   ✓ 登录成功")
                        is_logged_in = True
                    else:
                        print("   ⚠ 登录状态不确定")
                        is_logged_in = False
                else:
                    print("   ⚠ 未找到登录按钮")
                    is_logged_in = False
            else:
                print("   ⚠ 未找到登录表单")
                is_logged_in = False
            
            # 3. 测试任务列表页面
            print("\n3. 测试任务列表页面...")
            page.goto("http://127.0.0.1:8000/tasks/")
            page.wait_for_load_state('networkidle')
            print(f"   页面标题: {page.title()}")
            print(f"   页面URL: {page.url}")
            
            # 检查页面内容
            if "登录" not in page.title():
                print("   ✓ 成功访问任务页面")
                
                # 查找任务相关元素
                task_elements = page.locator(".task, .task-item, .task-card").all()
                print(f"   找到 {len(task_elements)} 个任务元素")
                
                # 查找创建任务的按钮
                create_buttons = page.locator("a[href*='create'], .btn-primary, text=创建").all()
                print(f"   找到 {len(create_buttons)} 个创建按钮")
                
            else:
                print("   ⚠ 需要登录才能访问任务页面")
                
            # 4. 测试看板页面
            print("\n4. 测试看板页面...")
            page.goto("http://127.0.0.1:8000/boards/")
            page.wait_for_load_state('networkidle')
            print(f"   页面标题: {page.title()}")
            
            if "登录" not in page.title():
                print("   ✓ 成功访问看板页面")
                
                # 查找看板元素
                board_elements = page.locator(".board, .board-item, .board-card").all()
                print(f"   找到 {len(board_elements)} 个看板元素")
                
                # 如果有看板，尝试访问第一个看板的工作流
                board_links = page.locator("a[href*='/boards/']").all()
                if len(board_links) > 0:
                    first_board_href = board_links[0].get_attribute('href')
                    print(f"   找到看板链接: {first_board_href}")
                    
                    # 提取看板slug（如果可能）
                    if '/boards/' in first_board_href:
                        # 假设URL格式为 /boards/board-slug/
                        board_slug = first_board_href.split('/boards/')[-1].rstrip('/')
                        if board_slug:
                            print(f"   看板Slug: {board_slug}")
                            
                            # 尝试访问工作流状态页面
                            print("\n5. 测试工作流状态页面...")
                            workflow_url = f"http://127.0.0.1:8000/tasks/workflow/boards/{board_slug}/workflow/statuses/"
                            page.goto(workflow_url)
                            page.wait_for_load_state('networkidle')
                            print(f"   工作流页面标题: {page.title()}")
                            print(f"   工作流页面URL: {page.url}")
                            
                            if "404" not in page.title() and "Not Found" not in page.title():
                                print("   ✓ 成功访问工作流状态页面")
                                
                                # 查找状态相关元素
                                status_elements = page.locator(".status, .workflow-status, tr").all()
                                print(f"   找到 {len(status_elements)} 个状态相关元素")
                            else:
                                print("   ⚠ 工作流状态页面未找到")
                        
            else:
                print("   ⚠ 需要登录才能访问看板页面")
            
            # 6. 测试Django管理后台
            print("\n6. 测试Django管理后台...")
            page.goto("http://127.0.0.1:8000/admin/")
            page.wait_for_load_state('networkidle')
            print(f"   管理后台标题: {page.title()}")
            
            if not headless:
                print("\n浏览器将保持打开状态，您可以手动浏览...")
                print("按Enter键关闭浏览器...")
                input()
                
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
            if not headless:
                print("按Enter键关闭浏览器...")
                input()
            
        finally:
            browser.close()
    
    print(f"\n{'='*60}")
    print("✓ 完整UI测试完成")
    print(f"{'='*60}")


def main():
    print("Django 5 任务看板系统 - 完整UI测试")
    print("1. 无头模式测试")
    print("2. 可视模式测试（推荐）")
    
    try:
        choice = input("\n请选择测试模式 [默认: 2]: ").strip()
        headless = choice == '1'
        run_full_ui_test(headless=headless)
    except KeyboardInterrupt:
        print("\n测试已取消")


if __name__ == "__main__":
    main()
