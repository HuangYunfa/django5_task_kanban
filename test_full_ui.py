#!/usr/bin/env python3
"""
全面的UI测试脚本 - 测试所有页面和链接
"""

import time
from playwright.sync_api import sync_playwright

def comprehensive_ui_test():
    """全面的UI测试"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 80)
        print("Django 5 任务看板系统 - 全面UI测试")
        print("=" * 80)
        
        test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # 1. 登录
            print("🔐 执行登录...")
            if login(page):
                test_results['passed'] += 1
                print("✅ 登录成功")
            else:
                test_results['failed'] += 1
                test_results['errors'].append("登录失败")
                return
            
            # 2. 测试主要页面
            pages_to_test = [
                ("首页", "http://127.0.0.1:8000/"),
                ("工作台", "http://127.0.0.1:8000/dashboard/"),
                ("个人资料", "http://127.0.0.1:8000/users/profile/"),
                ("用户设置", "http://127.0.0.1:8000/users/settings/"),
                ("看板列表", "http://127.0.0.1:8000/boards/"),
                ("任务列表", "http://127.0.0.1:8000/tasks/"),
                ("团队列表", "http://127.0.0.1:8000/teams/"),
                ("报表页面", "http://127.0.0.1:8000/reports/"),
                ("通知设置", "http://127.0.0.1:8000/notifications/preferences/"),
            ]
            
            print("🏠 测试主要页面...")
            for name, url in pages_to_test:
                if test_page_access(page, name, url):
                    test_results['passed'] += 1
                else:
                    test_results['failed'] += 1
                    test_results['errors'].append(f"{name} 页面访问失败")
            
            # 3. 测试导航链接
            print("🧭 测试主导航链接...")
            navigation_links = [
                ("首页导航", "a[href='/']"),
                ("工作台导航", "a[href='/dashboard/']"),
                ("看板导航", "a[href='/boards/']"),
                ("任务导航", "a[href='/tasks/']"),
                ("团队导航", "a[href='/teams/']"),
                ("报表导航", "a[href='/reports/']"),
            ]
            
            page.goto("http://127.0.0.1:8000/dashboard/")
            page.wait_for_load_state()
            
            for name, selector in navigation_links:
                if test_navigation_link(page, name, selector):
                    test_results['passed'] += 1
                else:
                    test_results['failed'] += 1
                    test_results['errors'].append(f"{name} 链接测试失败")
            
            # 4. 测试下拉菜单
            print("👤 测试下拉菜单...")
            dropdown_tests = [
                ("用户下拉菜单", "#userDropdown"),
                ("API下拉菜单", "#apiDropdown"),
                ("通知下拉菜单", "#notificationDropdown"),
            ]
            
            for name, selector in dropdown_tests:
                if test_dropdown_menu(page, name, selector):
                    test_results['passed'] += 1
                else:
                    test_results['failed'] += 1
                    test_results['errors'].append(f"{name} 测试失败")
            
            # 5. 测试具体功能页面
            print("🔧 测试具体功能页面...")
            
            # 测试任务详情页面
            if test_task_detail_page(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("任务详情页面测试失败")
            
            # 测试看板详情页面
            if test_board_detail_page(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("看板详情页面测试失败")
            
            # 6. 测试响应式设计
            print("📱 测试响应式设计...")
            if test_responsive_design(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("响应式设计测试失败")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            test_results['failed'] += 1
            test_results['errors'].append(f"测试异常: {e}")
        
        # 输出测试结果
        print_test_results(test_results)
        
        input("按回车键关闭浏览器...")
        browser.close()

def login(page):
    """执行登录"""
    try:
        page.goto("http://127.0.0.1:8000/accounts/login/")
        page.fill("#id_login", "project_manager")
        page.fill("#id_password", "demo123456")
        page.click("button[type=submit]")
        page.wait_for_load_state()
        return "dashboard" in page.url
    except Exception as e:
        print(f"   ❌ 登录错误: {e}")
        return False

def test_page_access(page, name, url):
    """测试页面访问"""
    try:
        print(f"   测试 {name} ({url})...")
        page.goto(url, timeout=10000)
        page.wait_for_load_state()
        
        # 检查是否是错误页面
        title = page.title()
        if "error" in title.lower() or "404" in title or "500" in title:
            print(f"   ❌ {name} 访问错误 - 标题: {title}")
            return False
        
        print(f"   ✅ {name} 访问成功 - 标题: {title}")
        return True
    except Exception as e:
        print(f"   ❌ {name} 访问失败: {e}")
        return False

def test_navigation_link(page, name, selector):
    """测试导航链接"""
    try:
        link = page.locator(selector).first
        if link.is_visible():
            print(f"   ✅ {name} 链接可见")
            link.click()
            page.wait_for_load_state()
            print(f"   ✅ {name} 链接功能正常")
            return True
        else:
            print(f"   ❌ {name} 链接不可见")
            return False
    except Exception as e:
        print(f"   ❌ {name} 链接测试错误: {e}")
        return False

def test_dropdown_menu(page, name, selector):
    """测试下拉菜单"""
    try:
        page.goto("http://127.0.0.1:8000/dashboard/")
        page.wait_for_load_state()
        
        dropdown = page.locator(selector)
        if dropdown.is_visible():
            print(f"   ✅ 找到{name}触发器")
            dropdown.click()
            time.sleep(0.5)
            
            # 检查菜单项
            menu_selector = f"{selector} + .dropdown-menu .dropdown-item"
            items = page.locator(menu_selector)
            count = items.count()
            print(f"   📋 {name}项数量: {count}")
            
            visible_count = 0
            for i in range(count):
                item = items.nth(i)
                if item.is_visible():
                    visible_count += 1
                    text = item.inner_text().strip()
                    print(f"   ✅ {name}项: '{text}'")
            
            if visible_count > 0:
                print(f"   ✅ {name} 功能正常 ({visible_count}/{count} 项可见)")
                return True
            else:
                print(f"   ❌ {name} 无可见菜单项")
                return False
        else:
            print(f"   ❌ 未找到{name}触发器")
            return False
    except Exception as e:
        print(f"   ❌ {name} 测试错误: {e}")
        return False

def test_task_detail_page(page):
    """测试任务详情页面"""
    try:
        print("   测试任务详情页面...")
        page.goto("http://127.0.0.1:8000/tasks/")
        page.wait_for_load_state()
        
        # 查找第一个任务链接
        task_links = page.locator("a[href*='/tasks/'][href$='/']")
        if task_links.count() > 0:
            first_task = task_links.first
            task_url = first_task.get_attribute("href")
            page.goto(f"http://127.0.0.1:8000{task_url}")
            page.wait_for_load_state()
            
            title = page.title()
            if "error" not in title.lower():
                print(f"   ✅ 任务详情页面访问成功 - {title}")
                return True
            else:
                print(f"   ❌ 任务详情页面错误 - {title}")
                return False
        else:
            print("   ⚠️ 未找到任务链接，跳过测试")
            return True
    except Exception as e:
        print(f"   ❌ 任务详情页面测试错误: {e}")
        return False

def test_board_detail_page(page):
    """测试看板详情页面"""
    try:
        print("   测试看板详情页面...")
        page.goto("http://127.0.0.1:8000/boards/")
        page.wait_for_load_state()
        
        # 查找第一个看板链接
        board_links = page.locator("a[href*='/boards/'][href$='/']")
        if board_links.count() > 0:
            first_board = board_links.first
            board_url = first_board.get_attribute("href")
            page.goto(f"http://127.0.0.1:8000{board_url}")
            page.wait_for_load_state()
            
            title = page.title()
            if "error" not in title.lower():
                print(f"   ✅ 看板详情页面访问成功 - {title}")
                return True
            else:
                print(f"   ❌ 看板详情页面错误 - {title}")
                return False
        else:
            print("   ⚠️ 未找到看板链接，跳过测试")
            return True
    except Exception as e:
        print(f"   ❌ 看板详情页面测试错误: {e}")
        return False

def test_responsive_design(page):
    """测试响应式设计"""
    try:
        print("   测试移动端响应式...")
        page.goto("http://127.0.0.1:8000/dashboard/")
        
        # 设置移动端视口
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_load_state()
        
        # 检查移动端导航
        mobile_toggle = page.locator(".navbar-toggler")
        if mobile_toggle.is_visible():
            print("   ✅ 移动端导航切换按钮可见")
            mobile_toggle.click()
            time.sleep(0.5)
            
            mobile_menu = page.locator(".navbar-collapse")
            if mobile_menu.is_visible():
                print("   ✅ 移动端导航菜单可以展开")
                return True
            else:
                print("   ❌ 移动端导航菜单无法展开")
                return False
        else:
            print("   ❌ 移动端导航切换按钮不可见")
            return False
    except Exception as e:
        print(f"   ❌ 响应式设计测试错误: {e}")
        return False
    finally:
        # 恢复桌面端视口
        page.set_viewport_size({"width": 1280, "height": 720})

def print_test_results(results):
    """输出测试结果"""
    print("=" * 80)
    print("测试完成 - 结果汇总")
    print("=" * 80)
    
    total = results['passed'] + results['failed']
    success_rate = (results['passed'] / total * 100) if total > 0 else 0
    
    print(f"📊 测试统计:")
    print(f"   - 总测试项: {total}")
    print(f"   - 通过: {results['passed']} 项")
    print(f"   - 失败: {results['failed']} 项")
    print(f"   - 成功率: {success_rate:.1f}%")
    
    if results['errors']:
        print(f"❌ 发现的问题:")
        for i, error in enumerate(results['errors'], 1):
            print(f"   {i}. {error}")
    else:
        print("🎉 所有测试都通过了！")

if __name__ == "__main__":
    comprehensive_ui_test()
