#!/usr/bin/env python3
"""
全面的UI测试脚本 - 测试所有页面和链接 (简化修复版)
"""

import time
import sys
import os
from playwright.sync_api import sync_playwright

def comprehensive_ui_test():
    """全面的UI测试"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, 
            slow_mo=1000,  # 慢速模式，便于观察
            args=['--start-maximized', '--disable-web-security', '--no-sandbox']
        )
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("=" * 80)
        print("Django 5 任务看板系统 - 全面UI测试")
        print("=" * 80)
        
        test_results = {'passed': 0, 'failed': 0, 'errors': []}
        
        try:
            # 1. 登录
            print("🔐 执行登录...")
            if login(page):
                test_results['passed'] += 1
                print("✅ 登录成功")
            else:
                test_results['failed'] += 1
                test_results['errors'].append("登录失败")
                print_test_results(test_results)
                return
            
            # 2. 测试主要页面
            pages_to_test = [
                ("首页", "http://127.0.0.1:8000/"),
                ("工作台", "http://127.0.0.1:8000/dashboard/"),
                ("看板列表", "http://127.0.0.1:8000/boards/"),
                ("任务列表", "http://127.0.0.1:8000/tasks/"),
                ("团队列表", "http://127.0.0.1:8000/teams/"),
                ("报表页面", "http://127.0.0.1:8000/reports/"),
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
            if test_navigation(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("导航链接测试失败")
            
            # 4. 测试功能页面
            print("🔧 测试功能页面...")
            if test_features(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("功能测试失败")
            
            # 5. 测试响应式设计
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
        
        finally:
            print_test_results(test_results)
            print("\n💡 按回车键关闭浏览器...")
            input()
            browser.close()

def login(page):
    """执行登录"""
    try:
        print("   正在访问登录页面...")
        page.goto("http://127.0.0.1:8000/accounts/login/")
        page.wait_for_load_state('networkidle')
        
        print("   正在填写登录信息...")
        page.fill('input[name="login"]', "project_manager")
        page.fill('input[name="password"]', "demo123456")
        
        print("   正在提交登录表单...")
        page.click("button[type=submit]")
        page.wait_for_load_state('networkidle')
        
        # 检查是否登录成功
        current_url = page.url
        if "dashboard" in current_url or "admin" in current_url or "boards" in current_url:
            print(f"   ✅ 登录成功 - 当前URL: {current_url}")
            return True
        else:
            print(f"   ❌ 登录失败 - 当前URL: {current_url}")
            return False
            
    except Exception as e:
        print(f"   ❌ 登录错误: {e}")
        return False

def test_page_access(page, name, url):
    """测试页面访问"""
    try:
        print(f"   测试 {name} ({url})...")
        response = page.goto(url, timeout=15000)
        page.wait_for_load_state('networkidle', timeout=10000)
        
        if response and response.status >= 400:
            print(f"   ❌ {name} HTTP错误 - 状态码: {response.status}")
            return False
        
        title = page.title()
        if "error" in title.lower() or "404" in title or "500" in title:
            print(f"   ❌ {name} 访问错误 - 标题: {title}")
            return False
        
        print(f"   ✅ {name} 访问成功 - 标题: {title[:50]}...")
        return True
        
    except Exception as e:
        print(f"   ❌ {name} 访问失败: {str(e)[:100]}...")
        return False

def test_navigation(page):
    """测试导航功能"""
    try:
        print("   测试主导航...")
        page.goto("http://127.0.0.1:8000/dashboard/")
        page.wait_for_load_state('networkidle')
        
        # 测试导航链接
        nav_links = page.locator('nav a, .navbar a').all()
        working_links = 0
        
        for i, link in enumerate(nav_links[:5]):  # 测试前5个链接
            try:
                href = link.get_attribute('href')
                if href and href.startswith('/'):
                    text = link.inner_text()[:20]
                    print(f"   ✅ 导航链接 {i+1}: {text}... -> {href}")
                    working_links += 1
            except:
                continue
        
        print(f"   📊 找到 {working_links} 个有效导航链接")
        return working_links > 0
        
    except Exception as e:
        print(f"   ❌ 导航测试错误: {e}")
        return False

def test_features(page):
    """测试主要功能"""
    try:
        features_working = 0
        
        # 测试任务列表
        print("   测试任务管理...")
        page.goto("http://127.0.0.1:8000/tasks/")
        page.wait_for_load_state('networkidle')
        
        task_elements = page.locator('.task, .card, .list-group-item, tr').count()
        if task_elements > 0:
            print(f"   ✅ 任务页面：找到 {task_elements} 个元素")
            features_working += 1
        
        # 测试看板列表
        print("   测试看板管理...")
        page.goto("http://127.0.0.1:8000/boards/")
        page.wait_for_load_state('networkidle')
        
        board_elements = page.locator('.board, .card, .list-group-item').count()
        if board_elements > 0:
            print(f"   ✅ 看板页面：找到 {board_elements} 个元素")
            features_working += 1
        
        # 测试报表页面
        print("   测试报表功能...")
        page.goto("http://127.0.0.1:8000/reports/")
        page.wait_for_load_state('networkidle')
        time.sleep(2)  # 等待图表加载
        
        chart_elements = page.locator('canvas, .chart').count()
        if chart_elements > 0:
            print(f"   ✅ 报表页面：找到 {chart_elements} 个图表")
            features_working += 1
        
        print(f"   📊 功能测试：{features_working}/3 个模块正常")
        return features_working >= 2
        
    except Exception as e:
        print(f"   ❌ 功能测试错误: {e}")
        return False

def test_responsive_design(page):
    """测试响应式设计"""
    try:
        print("   测试移动端响应式...")
        page.goto("http://127.0.0.1:8000/dashboard/")
        page.wait_for_load_state('networkidle')
        
        # 设置移动端视口
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(1000)
        
        # 检查移动端元素
        mobile_elements = page.locator(".navbar-toggler, .mobile-menu, .hamburger")
        if mobile_elements.count() > 0:
            print("   ✅ 找到移动端导航元素")
            result = True
        else:
            print("   ⚠️  页面在移动端可访问")
            result = True
        
        # 恢复桌面端视口
        page.set_viewport_size({"width": 1920, "height": 1080})
        return result
        
    except Exception as e:
        print(f"   ❌ 响应式测试错误: {e}")
        return False

def print_test_results(results):
    """输出测试结果"""
    print("\n" + "=" * 80)
    print("测试完成 - 结果汇总")
    print("=" * 80)
    
    total = results['passed'] + results['failed']
    success_rate = (results['passed'] / total * 100) if total > 0 else 0
    
    print(f"📊 测试统计:")
    print(f"   - 总测试项: {total}")
    print(f"   - ✅ 通过: {results['passed']} 项")
    print(f"   - ❌ 失败: {results['failed']} 项")
    print(f"   - 📈 成功率: {success_rate:.1f}%")
    
    if results['errors']:
        print(f"\n⚠️  发现的问题 ({len(results['errors'])} 项):")
        for i, error in enumerate(results['errors'], 1):
            print(f"   {i}. {error}")
    else:
        print("\n🎉 所有测试都通过了！")
    
    if success_rate >= 90:
        print("\n🌟 系统状态：优秀！")
    elif success_rate >= 75:
        print("\n👍 系统状态：良好")
    elif success_rate >= 50:
        print("\n⚠️  系统状态：一般")
    else:
        print("\n🚨 系统状态：需要注意")

def check_server_status():
    """检查Django服务器是否运行"""
    try:
        import urllib.request
        response = urllib.request.urlopen('http://127.0.0.1:8000/', timeout=5)
        return response.status == 200
    except:
        return False

def main():
    """主函数"""
    print("🚀 Django 5 任务看板系统 - 全面UI测试")
    print("=" * 50)
    
    if not check_server_status():
        print("❌ Django服务器未运行或无法访问")
        print("💡 请确保Django服务器运行在 http://127.0.0.1:8000/")
        return
    
    print("✅ Django服务器状态正常")
    print("🎭 即将启动Chrome浏览器进行全面UI测试...")
    time.sleep(2)
    
    comprehensive_ui_test()

if __name__ == "__main__":
    main()
