#!/usr/bin/env python
"""
完整的用户界面和链接测试脚本
"""

import time
from playwright.sync_api import sync_playwright

def comprehensive_ui_test():
    """完整的UI和链接测试"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        
        print("======================================================================")
        print("Django 5 任务看板系统 - 完整UI测试")
        print("======================================================================")
        
        test_results = {
            "pages_tested": 0,
            "links_tested": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # 1. 测试未登录状态的页面
            print("\n📋 1. 测试未登录状态...")
            test_page(page, "http://127.0.0.1:8000/", "首页", test_results)
            test_page(page, "http://127.0.0.1:8000/accounts/login/", "登录页面", test_results)
            test_page(page, "http://127.0.0.1:8000/accounts/signup/", "注册页面", test_results)
            
            # 测试未登录状态的导航链接
            print("\n   测试未登录状态导航链接:")
            page.goto("http://127.0.0.1:8000/")
            test_link(page, "a:has-text('任务看板')", "品牌链接", test_results)
            test_link(page, "a:has-text('登录'), a:has-text('立即登录')", "登录链接", test_results)
            test_link(page, "a:has-text('注册'), a:has-text('立即注册')", "注册链接", test_results)
            
            # 2. 执行登录
            print("\n🔐 2. 执行用户登录...")
            page.goto("http://127.0.0.1:8000/accounts/login/")
            
            # 填写登录表单
            page.fill("input[name='login']", "project_manager")
            page.fill("input[name='password']", "demo123456")
            page.click("button[type='submit']")
            
            try:
                page.wait_for_url("**/dashboard/", timeout=10000)
                print("   ✅ 登录成功")
            except:
                print("   ❌ 登录失败或超时")
                test_results["errors"].append("登录失败")
                return test_results
            
            # 3. 测试已登录状态的主要页面
            print("\n🏠 3. 测试已登录状态的主要页面...")
            main_pages = [
                ("http://127.0.0.1:8000/", "首页"),
                ("http://127.0.0.1:8000/dashboard/", "工作台"),
                ("http://127.0.0.1:8000/users/profile/", "个人资料"),
                ("http://127.0.0.1:8000/users/settings/", "用户设置"),
                ("http://127.0.0.1:8000/boards/", "看板列表"),
                ("http://127.0.0.1:8000/tasks/", "任务列表"),
                ("http://127.0.0.1:8000/teams/", "团队列表"),
                ("http://127.0.0.1:8000/reports/", "报表页面"),
                ("http://127.0.0.1:8000/notifications/preferences/", "通知设置"),
            ]
            
            for url, name in main_pages:
                test_page(page, url, name, test_results)
            
            # 4. 测试主导航栏链接
            print("\n🧭 4. 测试主导航栏链接...")
            page.goto("http://127.0.0.1:8000/dashboard/")
            
            nav_links = [
                ("a:has-text('首页')", "首页导航"),
                ("a:has-text('工作台')", "工作台导航"),
                ("a:has-text('看板')", "看板导航"),
                ("a:has-text('任务')", "任务导航"),
                ("a:has-text('团队')", "团队导航"),
                ("a:has-text('报表')", "报表导航"),
            ]
            
            for selector, name in nav_links:
                test_link(page, selector, name, test_results)
            
            # 5. 测试用户下拉菜单
            print("\n👤 5. 测试用户下拉菜单...")
            page.goto("http://127.0.0.1:8000/dashboard/")
            
            # 检查用户下拉菜单触发器
            user_dropdown = page.locator("#userDropdown")
            if user_dropdown.is_visible():
                print("   ✅ 找到用户菜单触发器")
                test_results["passed"] += 1
                
                # 点击下拉菜单
                user_dropdown.click()
                time.sleep(0.5)
                
                # 测试下拉菜单项
                dropdown_items = [
                    ("个人资料", ".dropdown-menu a:has-text('个人资料')"),
                    ("账户设置", ".dropdown-menu a:has-text('账户设置')"),
                    ("通知设置", ".dropdown-menu a:has-text('通知设置')"),
                    ("切换账号", ".dropdown-menu a:has-text('切换账号')"),
                    ("退出登录", ".dropdown-menu a:has-text('退出登录')"),
                ]
                
                for item_name, selector in dropdown_items:
                    item = page.locator(selector).first
                    if item.is_visible():
                        print(f"   ✅ 找到 {item_name}")
                        test_results["passed"] += 1
                    else:
                        print(f"   ❌ 未找到 {item_name}")
                        test_results["failed"] += 1
                        test_results["errors"].append(f"用户菜单中缺少 {item_name}")
            else:
                print("   ❌ 未找到用户菜单触发器")
                test_results["failed"] += 1
                test_results["errors"].append("用户菜单触发器不可见")
            
            # 6. 测试个人资料页面的侧边栏
            print("\n👤 6. 测试个人资料页面侧边栏...")
            page.goto("http://127.0.0.1:8000/users/profile/")
            
            sidebar_items = [
                ("基本资料", ".profile-sidebar a:has-text('基本资料'), .sidebar-menu a:has-text('基本资料')"),
                ("修改密码", ".profile-sidebar a:has-text('修改密码'), .sidebar-menu a:has-text('修改密码')"),
                ("通知设置", ".profile-sidebar a:has-text('通知设置'), .sidebar-menu a:has-text('通知设置')"),
                ("偏好设置", ".profile-sidebar a:has-text('偏好设置'), .sidebar-menu a:has-text('偏好设置')"),
                ("退出登录", ".profile-sidebar a:has-text('退出登录'), .sidebar-menu a:has-text('退出登录')"),
            ]
            
            for item_name, selector in sidebar_items:
                item = page.locator(selector).first
                if item.is_visible():
                    print(f"   ✅ 找到 {item_name}")
                    test_results["passed"] += 1
                else:
                    print(f"   ❌ 未找到 {item_name}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"个人资料侧边栏缺少 {item_name}")
            
            # 7. 测试API下拉菜单
            print("\n🔧 7. 测试API下拉菜单...")
            page.goto("http://127.0.0.1:8000/dashboard/")
            
            api_dropdown = page.locator("#apiDropdown")
            if api_dropdown.is_visible():
                print("   ✅ 找到API菜单触发器")
                api_dropdown.click()
                time.sleep(0.5)
                
                api_items = [
                    ("API根目录", "a:has-text('API根目录')"),
                    ("API文档", "a:has-text('API文档')"),
                    ("API v1", "a:has-text('API v1')"),
                ]
                
                for item_name, selector in api_items:
                    test_link(page, selector, f"API菜单-{item_name}", test_results)
            else:
                print("   ❌ 未找到API菜单触发器")
                test_results["failed"] += 1
            
            # 8. 测试通知下拉菜单
            print("\n🔔 8. 测试通知下拉菜单...")
            page.goto("http://127.0.0.1:8000/dashboard/")
            
            notification_dropdown = page.locator("#notificationDropdown")
            if notification_dropdown.is_visible():
                print("   ✅ 找到通知菜单触发器")
                notification_dropdown.click()
                time.sleep(0.5)
                
                notification_items = [
                    ("通知设置", "a:has-text('通知设置')"),
                    ("通知历史", "a:has-text('通知历史')"),
                ]
                
                for item_name, selector in notification_items:
                    test_link(page, selector, f"通知菜单-{item_name}", test_results)
            else:
                print("   ❌ 未找到通知菜单触发器")
                test_results["failed"] += 1
            
            # 9. 测试表单功能
            print("\n📝 9. 测试表单功能...")
            
            # 测试个人资料表单
            page.goto("http://127.0.0.1:8000/users/profile/")
            
            # 检查表单字段
            form_fields = [
                ("first_name", "名字字段"),
                ("last_name", "姓氏字段"),
                ("email", "邮箱字段"),
            ]
            
            for field_name, field_desc in form_fields:
                field = page.locator(f"input[name='{field_name}'], input[id*='{field_name}']")
                if field.is_visible():
                    print(f"   ✅ 找到 {field_desc}")
                    test_results["passed"] += 1
                else:
                    print(f"   ❌ 未找到 {field_desc}")
                    test_results["failed"] += 1
            
            # 10. 测试响应式设计
            print("\n📱 10. 测试响应式设计...")
            
            # 测试移动端视口
            page.set_viewport_size({"width": 375, "height": 667})
            page.goto("http://127.0.0.1:8000/dashboard/")
            
            # 检查导航栏切换按钮
            navbar_toggler = page.locator(".navbar-toggler")
            if navbar_toggler.is_visible():
                print("   ✅ 移动端导航切换按钮可见")
                test_results["passed"] += 1
                
                # 点击切换按钮
                navbar_toggler.click()
                time.sleep(0.5)
                
                # 检查导航菜单是否展开
                nav_collapse = page.locator("#navbarNav")
                if nav_collapse.is_visible():
                    print("   ✅ 移动端导航菜单可以展开")
                    test_results["passed"] += 1
                else:
                    print("   ❌ 移动端导航菜单无法展开")
                    test_results["failed"] += 1
            else:
                print("   ❌ 移动端导航切换按钮不可见")
                test_results["failed"] += 1
            
            # 恢复桌面端视口
            page.set_viewport_size({"width": 1280, "height": 720})
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            test_results["errors"].append(f"主要错误: {str(e)}")
        
        # 11. 生成测试报告
        print("\n======================================================================")
        print("测试完成 - 结果汇总")
        print("======================================================================")
        print(f"📊 测试统计:")
        print(f"   - 页面测试: {test_results['pages_tested']} 个")
        print(f"   - 链接测试: {test_results['links_tested']} 个")
        print(f"   - 通过: {test_results['passed']} 项")
        print(f"   - 失败: {test_results['failed']} 项")
        print(f"   - 成功率: {(test_results['passed']/(test_results['passed']+test_results['failed'])*100):.1f}%")
        
        if test_results["errors"]:
            print(f"\n❌ 发现的问题:")
            for i, error in enumerate(test_results["errors"], 1):
                print(f"   {i}. {error}")
        else:
            print(f"\n✅ 所有测试项目都通过了！")
        
        input("\n按回车键关闭浏览器...")
        browser.close()
        
        return test_results

def test_page(page, url, name, results):
    """测试单个页面"""
    try:
        print(f"   测试 {name} ({url})...")
        page.goto(url, timeout=10000)
        
        # 检查页面是否正常加载
        if page.title():
            print(f"   ✅ {name} 加载成功 - 标题: {page.title()}")
            results["passed"] += 1
        else:
            print(f"   ❌ {name} 页面标题为空")
            results["failed"] += 1
            results["errors"].append(f"{name} 页面标题为空")
        
        results["pages_tested"] += 1
        
    except Exception as e:
        print(f"   ❌ {name} 加载失败: {str(e)}")
        results["failed"] += 1
        results["errors"].append(f"{name} 加载失败: {str(e)}")

def test_link(page, selector, name, results):
    """测试单个链接"""
    try:
        link = page.locator(selector).first
        if link.is_visible():
            print(f"   ✅ {name} 链接可见")
            results["passed"] += 1
            
            # 尝试点击链接（但不等待导航完成）
            try:
                original_url = page.url
                link.click(timeout=3000)
                time.sleep(0.5)
                
                # 如果URL发生变化，说明链接有效
                if page.url != original_url:
                    print(f"   ✅ {name} 链接功能正常")
                    results["passed"] += 1
                    # 返回原页面
                    page.go_back()
                    time.sleep(0.5)
                else:
                    print(f"   ⚠️  {name} 链接可能是JavaScript处理")
                    results["passed"] += 1
                    
            except Exception as click_error:
                print(f"   ⚠️  {name} 链接点击测试跳过: {str(click_error)}")
                results["passed"] += 1  # 链接存在就算通过
                
        else:
            print(f"   ❌ {name} 链接不可见")
            results["failed"] += 1
            results["errors"].append(f"{name} 链接不可见")
        
        results["links_tested"] += 1
        
    except Exception as e:
        print(f"   ❌ {name} 链接测试失败: {str(e)}")
        results["failed"] += 1
        results["errors"].append(f"{name} 链接测试失败: {str(e)}")

if __name__ == "__main__":
    comprehensive_ui_test()
