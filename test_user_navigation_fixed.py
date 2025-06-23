#!/usr/bin/env python
"""
修复后的用户导航测试脚本
"""

import time
import asyncio
from playwright.sync_api import sync_playwright

def test_navigation():
    """测试导航和用户体验"""
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()
        
        print("======================================================================")
        print("Django 5 任务看板系统 - 用户界面导航测试")
        print("浏览器模式: 可视模式")
        print("======================================================================")
        
        try:
            # 1. 测试首页
            print("\n📋 1. 测试未登录状态的首页...")
            page.goto("http://127.0.0.1:8000/")
            print(f"   页面标题: {page.title()}")
            print(f"   当前URL: {page.url}")
            
            # 2. 登录测试
            print("\n🔐 2. 尝试用户登录...")
            login_link = page.locator("a:has-text('登录'), a:has-text('立即登录')").first
            login_link.click()
            
            # 填写登录表单
            page.fill("input[name='login']", "project_manager")
            page.fill("input[name='password']", "demo123456")
            page.click("button[type='submit']")
            
            page.wait_for_url("**/dashboard/")
            print(f"   登录后URL: {page.url}")
            print("   ✅ 登录成功")
            
            # 3. 测试导航栏
            print("\n🧭 3. 测试已登录状态的导航栏...")
            print(f"   工作台URL: {page.url}")
            print(f"   工作台标题: {page.title()}")
            
            nav_items = [
                "首页", "工作台", "看板", "任务", "团队", "报表", "API"
            ]
            
            print("   检查主导航菜单:")
            for item in nav_items:
                nav_link = page.locator(f"a:has-text('{item}')").first
                if nav_link.is_visible():
                    print(f"   ✅ 找到 {item} 链接")
                else:
                    print(f"   ❌ 未找到 {item} 链接")
            
            # 4. 测试用户下拉菜单
            print("\n👤 4. 测试用户下拉菜单...")
            user_dropdown = page.locator("#userDropdown, a:has-text('project_manager')")
            if user_dropdown.is_visible():
                print("   ✅ 找到用户菜单触发器")
                user_dropdown.click()
                time.sleep(1)
                
                menu_items = [
                    "个人资料", "账户设置", "通知设置", "切换账号", "退出登录"
                ]
                
                print("   查找用户菜单项:")
                for item in menu_items:
                    menu_item = page.locator(f".dropdown-menu a:has-text('{item}')").first
                    if menu_item.is_visible():
                        print(f"     ✅ 找到 {item}")
                    else:
                        print(f"     ❌ 未找到 {item}")
            else:
                print("   ❌ 未找到用户菜单触发器")
            
            # 5. 测试首页访问
            print("\n🏠 5. 测试已登录用户访问首页...")
            page.click("a:has-text('首页')")
            page.wait_for_load_state('networkidle')
            print(f"   首页URL: {page.url}")
            print(f"   首页标题: {page.title()}")
            
            if "dashboard" not in page.url:
                print("   ✅ 成功访问首页，没有被强制重定向")
            else:
                print("   ❌ 被重定向到工作台")
            
            # 6. 测试个人资料页面
            print("\n👤 6. 测试个人资料页面...")
            # 先点击用户菜单
            user_dropdown = page.locator("#userDropdown, a:has-text('project_manager')")
            user_dropdown.click()
            time.sleep(0.5)
            
            # 点击个人资料
            profile_link = page.locator(".dropdown-menu a:has-text('个人资料')").first
            profile_link.click()
            page.wait_for_load_state('networkidle')
            
            print(f"   个人资料URL: {page.url}")
            print(f"   个人资料标题: {page.title()}")
            
            # 检查侧边栏
            print("   检查侧边栏菜单:")
            sidebar_items = [
                "基本资料", "修改密码", "通知设置", "偏好设置", "退出登录"
            ]
            
            for item in sidebar_items:
                # 查找侧边栏中的链接
                sidebar_link = page.locator(f".profile-sidebar a:has-text('{item}'), .sidebar-menu a:has-text('{item}')").first
                if sidebar_link.is_visible():
                    print(f"     ✅ 找到 {item}")
                else:
                    print(f"     ❌ 未找到 {item}")
            
            # 7. 测试退出登录
            print("\n🚪 7. 测试退出登录功能...")
            logout_links = page.locator("a:has-text('退出登录'), a:has-text('logout')")
            count = logout_links.count()
            print(f"   找到 {count} 个退出登录链接")
            
            if count > 0:
                print("   尝试点击退出登录...")
                # 确保用户菜单是展开的
                user_dropdown = page.locator("#userDropdown, a:has-text('project_manager')")
                if user_dropdown.is_visible():
                    user_dropdown.click()
                    time.sleep(0.5)
                
                logout_link = page.locator(".dropdown-menu a:has-text('退出登录')").first
                if logout_link.is_visible():
                    logout_link.click()
                    page.wait_for_load_state('networkidle')
                    print("   ✅ 成功执行退出登录")
                else:
                    print("   ❌ 退出登录链接不可见")
            else:
                print("   ❌ 未找到退出登录链接")
                
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
        
        print("\n======================================================================")
        print("测试完成")
        print("======================================================================")
        
        input("按回车键关闭浏览器...")
        browser.close()

if __name__ == "__main__":
    test_navigation()
