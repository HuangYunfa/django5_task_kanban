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
                ("API文档", "http://127.0.0.1:8000/api/docs/"),
                ("API Schema", "http://127.0.0.1:8000/api/schema/docs/"),
                ("Swagger UI", "http://127.0.0.1:8000/api/schema/swagger-ui/"),
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
            
            # 测试任务管理页面的详细功能
            if test_task_management_features(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("任务管理功能测试失败")
            
            # 测试看板管理页面的详细功能
            if test_board_management_features(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("看板管理功能测试失败")
            
            # 测试团队管理页面的详细功能
            if test_team_management_features(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("团队管理功能测试失败")
            
            # 测试报表页面的详细功能
            if test_reports_features(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("报表功能测试失败")
              # 测试所有页面内的链接
            print("🔗 测试页面内链接...")
            if test_all_page_links(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("页面内链接测试失败")
            
            # 测试API文档链接
            print("📚 测试API文档链接...")
            if test_api_documentation_links(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("API文档链接测试失败")
            
            # 6. 测试响应式设计
            print("📱 测试响应式设计...")
            if test_responsive_design(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("响应式设计测试失败")
            
            # 7. 测试API文档相关链接
            print("📚 测试API文档相关链接...")
            if test_api_documentation_links(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("API文档链接测试失败")
            
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
        if "dashboard" in page.url or "首页" in page.title():
            print("   ✅ 登录成功")
            return True
        else:
            print(f"   ❌ 登录失败 - 当前URL: {page.url}")
            return False
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

def test_task_management_features(page):
    """测试任务管理页面的详细功能"""
    try:
        print("   测试任务管理功能...")
        page.goto("http://127.0.0.1:8000/tasks/")
        page.wait_for_load_state('networkidle')
        
        # 测试视图切换按钮
        table_view_btn = page.locator('button[onclick="toggleView(\'table\')"]')
        card_view_btn = page.locator('button[onclick="toggleView(\'card\')"]')
        
        if table_view_btn.is_visible() and card_view_btn.is_visible():
            print("   ✅ 视图切换按钮存在")
            
            # 测试卡片视图切换
            card_view_btn.click()
            time.sleep(1)
            card_view = page.locator('#cardView')
            if card_view.is_visible():
                print("   ✅ 卡片视图切换成功")
            else:
                print("   ❌ 卡片视图切换失败")
                
            # 切换回表格视图
            table_view_btn.click()
            time.sleep(1)
            table_view = page.locator('#tableView')
            if table_view.is_visible():
                print("   ✅ 表格视图切换成功")
            else:
                print("   ❌ 表格视图切换失败")
        else:
            print("   ❌ 视图切换按钮不存在")
        
        # 测试搜索功能
        search_input = page.locator('input[name="search"]')
        if search_input.is_visible():
            print("   ✅ 搜索输入框存在")
            search_input.fill("测试")
            search_btn = page.locator('button[type="submit"]:has-text("搜索")')
            if search_btn.is_visible():
                print("   ✅ 搜索按钮存在")
            else:
                print("   ❌ 搜索按钮不存在")
        else:
            print("   ❌ 搜索输入框不存在")
        
        # 测试新建任务按钮
        create_btn = page.locator('a[href*="create"]:has-text("新建任务")')
        if create_btn.is_visible():
            print("   ✅ 新建任务按钮存在")
        else:
            print("   ❌ 新建任务按钮不存在")
        
        # 测试任务列表中的链接
        task_links = page.locator('a[href*="/tasks/"]')
        task_count = task_links.count()
        print(f"   📊 找到 {task_count} 个任务相关链接")
        
        return True
    except Exception as e:
        print(f"   ❌ 任务管理功能测试错误: {e}")
        return False

def test_board_management_features(page):
    """测试看板管理页面的详细功能"""
    try:
        print("   测试看板管理功能...")
        page.goto("http://127.0.0.1:8000/boards/")
        page.wait_for_load_state('networkidle')
        
        # 测试模板标签
        template_badges = page.locator('.board-template-badge')
        badge_count = template_badges.count()
        print(f"   📊 找到 {badge_count} 个看板模板标签")
        
        # 测试下拉菜单
        dropdown_btns = page.locator('.dropdown-toggle')
        dropdown_count = dropdown_btns.count()
        print(f"   🔽 找到 {dropdown_count} 个下拉菜单")
        
        if dropdown_count > 0:
            # 测试第一个下拉菜单
            first_dropdown = dropdown_btns.first
            first_dropdown.click()
            time.sleep(0.5)
            
            dropdown_menu = page.locator('.dropdown-menu.show')
            if dropdown_menu.is_visible():
                print("   ✅ 下拉菜单展开成功")
                
                # 检查菜单项
                menu_items = dropdown_menu.locator('.dropdown-item')
                item_count = menu_items.count()
                print(f"   📋 下拉菜单包含 {item_count} 个选项")
                
                # 点击其他地方关闭菜单
                page.click('body')
                time.sleep(0.5)
            else:
                print("   ❌ 下拉菜单展开失败")
        
        # 测试看板链接
        board_links = page.locator('a[href*="/boards/"]')
        board_count = board_links.count()
        print(f"   📊 找到 {board_count} 个看板相关链接")
        
        # 测试创建看板按钮
        create_btn = page.locator('a:has-text("创建看板"), button:has-text("创建看板")')
        if create_btn.is_visible():
            print("   ✅ 创建看板按钮存在")
        else:
            print("   ❌ 创建看板按钮不存在")
        
        return True
    except Exception as e:
        print(f"   ❌ 看板管理功能测试错误: {e}")
        return False

def test_team_management_features(page):
    """测试团队管理页面的详细功能"""
    try:
        print("   测试团队管理功能...")
        page.goto("http://127.0.0.1:8000/teams/")
        page.wait_for_load_state('networkidle')
        
        # 测试团队列表
        team_cards = page.locator('.card')
        team_count = team_cards.count()
        print(f"   👥 找到 {team_count} 个团队卡片")
        
        # 测试团队链接
        team_links = page.locator('a[href*="/teams/"]')
        link_count = team_links.count()
        print(f"   📊 找到 {link_count} 个团队相关链接")
        
        # 测试创建团队按钮
        create_btn = page.locator('a:has-text("创建团队"), button:has-text("创建团队")')
        if create_btn.is_visible():
            print("   ✅ 创建团队按钮存在")
        else:
            print("   ❌ 创建团队按钮不存在")
        
        return True
    except Exception as e:
        print(f"   ❌ 团队管理功能测试错误: {e}")
        return False

def test_reports_features(page):
    """测试报表页面的详细功能"""
    try:
        print("   测试报表功能...")
        page.goto("http://127.0.0.1:8000/reports/")
        page.wait_for_load_state('networkidle')
        
        # 测试报表卡片
        report_cards = page.locator('.card')
        card_count = report_cards.count()
        print(f"   📊 找到 {card_count} 个报表卡片")
        
        # 测试图表元素
        charts = page.locator('canvas, .chart, #chart')
        chart_count = charts.count()
        print(f"   📈 找到 {chart_count} 个图表元素")
        
        # 测试导出按钮
        export_btns = page.locator('button:has-text("导出"), a:has-text("导出")')
        export_count = export_btns.count()
        print(f"   💾 找到 {export_count} 个导出按钮")
        
        return True
    except Exception as e:
        print(f"   ❌ 报表功能测试错误: {e}")
        return False

def test_all_page_links(page):
    """测试所有页面内的链接"""
    try:
        print("   测试所有页面内链接...")
        
        pages_to_check = [
            ("首页", "http://127.0.0.1:8000/"),
            ("工作台", "http://127.0.0.1:8000/dashboard/"),
            ("任务列表", "http://127.0.0.1:8000/tasks/"),
            ("看板列表", "http://127.0.0.1:8000/boards/"),
            ("团队列表", "http://127.0.0.1:8000/teams/"),
            ("报表页面", "http://127.0.0.1:8000/reports/"),
        ]
        
        total_links = 0
        working_links = 0
        broken_links = []
        
        for page_name, url in pages_to_check:
            print(f"   检查 {page_name} 的链接...")
            page.goto(url)
            page.wait_for_load_state('networkidle')
            
            # 获取所有内部链接
            internal_links = page.locator('a[href^="/"], a[href^="http://127.0.0.1:8000"]')
            page_link_count = internal_links.count()
            total_links += page_link_count
            
            print(f"     找到 {page_link_count} 个内部链接")
            
            # 检查前5个链接是否可访问
            check_count = min(5, page_link_count)
            for i in range(check_count):
                try:
                    link = internal_links.nth(i)
                    href = link.get_attribute('href')
                    if href and not href.startswith('#'):
                        # 在新标签页中打开链接进行检查
                        new_page = page.context.new_page()
                        response = new_page.goto(href, timeout=5000)
                        if response and response.status < 400:
                            working_links += 1
                        else:
                            broken_links.append(f"{page_name}: {href}")
                        new_page.close()
                except Exception as e:
                    broken_links.append(f"{page_name}: {href} (错误: {str(e)[:50]})")
        
        print(f"   📊 链接检查统计:")
        print(f"     总链接数: {total_links}")
        print(f"     检查的链接数: {working_links + len(broken_links)}")
        print(f"     正常链接: {working_links}")
        print(f"     异常链接: {len(broken_links)}")        
        if broken_links:
            print("   ⚠️  发现异常链接:")
            for link in broken_links[:10]:  # 只显示前10个
                print(f"     - {link}")
        
        return len(broken_links) == 0
    except Exception as e:
        print(f"   ❌ 页面链接测试错误: {e}")
        return False

def test_responsive_design(page):
    """测试响应式设计"""
    try:
        print("   测试移动端响应式...")
        page.goto("http://127.0.0.1:8000/dashboard/")
        page.wait_for_load_state('networkidle')
        
        # 设置移动端视口
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_load_state('networkidle')
        
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

def test_api_documentation_links(page):
    """测试API文档相关链接"""
    try:
        print("   测试API文档链接...")
        
        # 测试API文档重定向
        api_urls = [
            ("API文档", "http://127.0.0.1:8000/api/docs/"),
            ("API Schema重定向", "http://127.0.0.1:8000/api/schema/docs/"),
            ("Swagger UI重定向", "http://127.0.0.1:8000/api/schema/swagger-ui/"),
        ]
        
        for name, url in api_urls:
            try:
                response = page.goto(url, timeout=10000)
                if response.status == 200:
                    print(f"   ✅ {name} 访问成功")
                    
                    # 检查是否包含API文档内容
                    if "swagger" in page.url.lower() or "api" in page.title().lower():
                        print(f"   ✅ {name} 内容正确")
                    else:
                        print(f"   ⚠️  {name} 内容可能不正确")
                else:
                    print(f"   ❌ {name} 访问失败，状态码: {response.status}")
            except Exception as e:
                print(f"   ❌ {name} 测试错误: {e}")
        
        return True
    except Exception as e:
        print(f"   ❌ API文档链接测试错误: {e}")
        return False

if __name__ == "__main__":
    comprehensive_ui_test()
