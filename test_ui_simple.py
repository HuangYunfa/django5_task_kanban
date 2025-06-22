#!/usr/bin/env python
"""
Django 5 任务看板系统 - 简化的Playwright UI测试
用于演示和验证前端功能

运行方法：
    python test_ui_simple.py
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


def run_ui_test(headless=False):
    """运行UI测试"""
    print(f"\n{'='*60}")
    print("Django 5 任务看板系统 - Playwright UI测试")
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
            print("\n1. 测试主页访问...")
            page.goto("http://127.0.0.1:8000")
            page.wait_for_load_state('networkidle')
            print(f"   页面标题: {page.title()}")
            print(f"   页面URL: {page.url}")
            
            print("\n2. 测试登录页面...")
            page.goto("http://127.0.0.1:8000/accounts/login/")
            page.wait_for_load_state('networkidle')
            print(f"   页面标题: {page.title()}")
            
            # 检查登录表单元素
            if page.locator("input[name='login']").count() > 0:
                print("   ✓ 找到登录用户名输入框")
            if page.locator("input[name='password']").count() > 0:
                print("   ✓ 找到密码输入框")
                
            print("\n3. 测试Django管理后台...")
            page.goto("http://127.0.0.1:8000/admin/")
            page.wait_for_load_state('networkidle')
            print(f"   页面标题: {page.title()}")
            
            print("\n4. 测试任务应用...")
            page.goto("http://127.0.0.1:8000/tasks/")
            page.wait_for_load_state('networkidle')
            print(f"   页面标题: {page.title()}")
            print(f"   页面URL: {page.url}")
            
            print("\n5. 测试工作流状态页面...")
            page.goto("http://127.0.0.1:8000/tasks/workflow/status/")
            page.wait_for_load_state('networkidle')
            print(f"   页面标题: {page.title()}")
            print(f"   页面URL: {page.url}")
            
            print("\n6. 测试看板页面...")
            page.goto("http://127.0.0.1:8000/boards/")
            page.wait_for_load_state('networkidle')
            print(f"   页面标题: {page.title()}")
            
            if not headless:
                print("\n按Enter键继续并关闭浏览器...")
                input()
                
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
            
        finally:
            browser.close()
    
    print(f"\n{'='*60}")
    print("✓ UI测试完成")
    print(f"{'='*60}")


def main():
    print("Playwright UI测试启动器")
    print("1. 无头模式测试")
    print("2. 可视模式测试（推荐）")
    
    try:
        choice = input("\n请选择测试模式 [默认: 2]: ").strip()
        headless = choice == '1'
        run_ui_test(headless=headless)
    except KeyboardInterrupt:
        print("\n测试已取消")


if __name__ == "__main__":
    main()
