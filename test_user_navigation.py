#!/usr/bin/env python
"""
Django 5 任务看板系统 - 用户界面导航测试
专门测试用户菜单、导航栏、个人资料等功能

运行方法：
    python test_user_navigation.py
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


def run_navigation_test(headless=False):
    """运行用户导航测试"""
    print(f"\n{'='*70}")
    print("Django 5 任务看板系统 - 用户界面导航测试")
    print(f"浏览器模式: {'无头模式' if headless else '可视模式'}")
    print(f"{'='*70}")
    
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
            # 1. 测试未登录状态的首页
            print("\n📋 1. 测试未登录状态的首页...")
            page.goto("http://127.0.0.1:8000")
            page.wait_for_load_state('networkidle')
            print(f"   页面标题: {page.title()}")
            print(f"   当前URL: {page.url}")
            
            # 检查导航栏
            navbar = page.locator(".navbar")
            if navbar.count() > 0:
                print("   ✓ 找到导航栏")
                
                # 检查品牌链接
                brand_link = page.locator(".navbar-brand")
                if brand_link.count() > 0:
                    brand_text = brand_link.text_content()
                    print(f"   品牌链接文本: '{brand_text}'")
                
                # 检查登录链接
                login_links = page.locator("a:has-text('登录')")
                print(f"   找到 {login_links.count()} 个登录链接")
                
                # 检查注册链接
                signup_links = page.locator("a:has-text('注册')")
                print(f"   找到 {signup_links.count()} 个注册链接")
            else:
                print("   ❌ 未找到导航栏")
            
            # 2. 尝试登录
            print("\n🔐 2. 尝试用户登录...")
            page.goto("http://127.0.0.1:8000/accounts/login/")
            page.wait_for_load_state('networkidle')
            
            # 查找登录表单
            login_form = page.locator("form")
            if login_form.count() > 0:
                print("   ✓ 找到登录表单")
                
                # 尝试使用演示账号登录
                login_input = page.locator("input[name='login']")
                password_input = page.locator("input[name='password']")
                
                if login_input.count() > 0 and password_input.count() > 0:
                    # 使用演示数据中的用户
                    login_input.fill("project_manager")
                    password_input.fill("demo123456")
                    
                    # 点击登录按钮
                    submit_button = page.locator("button[type='submit'], input[type='submit']")
                    if submit_button.count() > 0:
                        submit_button.click()
                        page.wait_for_load_state('networkidle')
                        time.sleep(2)  # 等待重定向
                        
                        print(f"   登录后URL: {page.url}")
                        
                        # 检查是否登录成功
                        if "login" not in page.url:
                            print("   ✅ 登录成功")
                            is_logged_in = True
                        else:
                            print("   ❌ 登录失败")
                            is_logged_in = False
                    else:
                        print("   ❌ 未找到提交按钮")
                        is_logged_in = False
                else:
                    print("   ❌ 未找到登录输入框")
                    is_logged_in = False
            else:
                print("   ❌ 未找到登录表单")
                is_logged_in = False
            
            if not is_logged_in:
                print("⚠️  登录失败，无法测试已登录状态的功能")
                return
            
            # 3. 测试已登录状态的导航栏
            print("\n🧭 3. 测试已登录状态的导航栏...")
            page.goto("http://127.0.0.1:8000/dashboard/")
            page.wait_for_load_state('networkidle')
            print(f"   工作台URL: {page.url}")
            print(f"   工作台标题: {page.title()}")
            
            # 检查主导航菜单
            print("\n   检查主导航菜单:")
            nav_items = [
                ("首页", ["首页", "home"]),
                ("工作台", ["工作台", "dashboard"]),
                ("看板", ["看板", "boards"]),
                ("任务", ["任务", "tasks"]),
                ("团队", ["团队", "teams"]),
                ("报表", ["报表", "reports"]),
                ("API", ["API", "api"])
            ]
            
            for item_name, search_texts in nav_items:
                found = False
                for search_text in search_texts:
                    nav_link = page.locator(f".navbar a:has-text('{search_text}')")
                    if nav_link.count() > 0:
                        print(f"   ✅ 找到 {item_name} 链接")
                        found = True
                        break
                if not found:
                    print(f"   ❌ 未找到 {item_name} 链接")
            
            # 4. 测试用户下拉菜单
            print("\n👤 4. 测试用户下拉菜单...")
            
            # 查找用户菜单触发器
            user_dropdown_triggers = [
                f"a:has-text('project_manager')",
                ".nav-link.dropdown-toggle:has-text('project_manager')",
                "[data-bs-toggle='dropdown']:has-text('project_manager')",
                "a[id*='user']:has-text('project_manager')",
                "a[id*='User']:has-text('project_manager')",
                ".navbar a:has-text('project_manager')"
            ]
            
            user_menu_trigger = None
            for selector in user_dropdown_triggers:
                element = page.locator(selector)
                if element.count() > 0:
                    user_menu_trigger = element.first
                    print(f"   ✅ 找到用户菜单触发器: {selector}")
                    break
            
            if user_menu_trigger:
                # 点击用户菜单
                user_menu_trigger.click()
                time.sleep(1)  # 等待下拉菜单展开
                
                # 查找用户菜单项
                print("   查找用户菜单项:")
                menu_items = [
                    ("个人资料", ["个人资料", "profile"]),
                    ("账户设置", ["账户设置", "设置", "settings"]),
                    ("通知设置", ["通知设置", "通知"]),
                    ("切换账号", ["切换账号", "切换"]),
                    ("退出登录", ["退出登录", "退出", "logout"])
                ]
                
                for item_name, search_texts in menu_items:
                    found = False
                    for search_text in search_texts:
                        menu_item = page.locator(f".dropdown-menu a:has-text('{search_text}')")
                        if menu_item.count() > 0:
                            print(f"     ✅ 找到 {item_name}")
                            found = True
                            break
                    if not found:
                        print(f"     ❌ 未找到 {item_name}")
            else:
                print("   ❌ 未找到用户菜单触发器")
                print("   现有的所有链接:")
                all_links = page.locator(".navbar a").all()
                for i, link in enumerate(all_links):
                    link_text = link.text_content().strip()
                    if link_text:
                        print(f"     链接 {i+1}: '{link_text}'")
            
            # 5. 测试首页访问
            print("\n🏠 5. 测试已登录用户访问首页...")
            page.goto("http://127.0.0.1:8000/")
            page.wait_for_load_state('networkidle')
            print(f"   首页URL: {page.url}")
            print(f"   首页标题: {page.title()}")
            
            # 检查是否被重定向
            if page.url == "http://127.0.0.1:8000/":
                print("   ✅ 成功访问首页，没有被强制重定向")
                
                # 查找欢迎信息
                welcome_text = page.locator(".alert-info, .welcome, :has-text('欢迎回来')")
                if welcome_text.count() > 0:
                    print("   ✅ 找到欢迎信息")
                else:
                    print("   ⚠️  未找到欢迎信息")
                    
                # 查找进入工作台的按钮
                dashboard_links = page.locator("a:has-text('进入工作台'), a:has-text('工作台')")
                if dashboard_links.count() > 0:
                    print("   ✅ 找到进入工作台的链接")
                else:
                    print("   ⚠️  未找到进入工作台的链接")
            else:
                print(f"   ❌ 被重定向到: {page.url}")
            
            # 6. 测试个人资料页面
            print("\n👤 6. 测试个人资料页面...")
            page.goto("http://127.0.0.1:8000/users/profile/")
            page.wait_for_load_state('networkidle')
            print(f"   个人资料URL: {page.url}")
            print(f"   个人资料标题: {page.title()}")
            
            # 检查侧边栏功能
            sidebar_items = [
                "基本资料",
                "修改密码", 
                "通知设置",
                "偏好设置",
                "退出登录"
            ]
            
            print("   检查侧边栏菜单:")
            for item in sidebar_items:
                sidebar_link = page.locator(f".sidebar a:has-text('{item}'), .nav a:has-text('{item}')")
                if sidebar_link.count() > 0:
                    print(f"     ✅ 找到 {item}")
                else:
                    print(f"     ❌ 未找到 {item}")
            
            # 7. 测试退出登录功能
            print("\n🚪 7. 测试退出登录功能...")
            logout_links = page.locator("a:has-text('退出登录'), a:has-text('logout')")
            if logout_links.count() > 0:
                print(f"   找到 {logout_links.count()} 个退出登录链接")
                
                # 点击第一个退出登录链接
                logout_links.first.click()
                page.wait_for_load_state('networkidle')
                time.sleep(2)
                
                print(f"   退出后URL: {page.url}")
                
                # 检查是否成功退出
                if "login" in page.url or page.url == "http://127.0.0.1:8000/":
                    print("   ✅ 成功退出登录")
                else:
                    print("   ❌ 退出登录失败")
            else:
                print("   ❌ 未找到退出登录链接")
            
            print(f"\n{'='*70}")
            print("测试完成")
            print(f"{'='*70}")
            
        except Exception as e:
            print(f"\n❌ 测试过程中出现错误: {e}")
        finally:
            if not headless:
                input("\n按回车键关闭浏览器...")
            browser.close()


if __name__ == "__main__":
    # 运行测试，可视模式便于观察
    run_navigation_test(headless=False)
