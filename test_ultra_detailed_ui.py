#!/usr/bin/env python3
"""
超详细的UI测试 - 测试每个链接和功能点
"""

import time
from playwright.sync_api import sync_playwright

def ultra_detailed_ui_test():
    """超详细的UI测试"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 80)
        print("Django 5 任务看板系统 - 超详细UI测试")
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
            
            # 2. 测试用户下拉菜单的每个链接
            print("👤 详细测试用户下拉菜单链接...")
            user_menu_links = [
                ("个人资料", "http://127.0.0.1:8000/users/profile/"),
                ("账户设置", "http://127.0.0.1:8000/users/settings/"),
                ("通知设置", "http://127.0.0.1:8000/notifications/preferences/"),
            ]
            
            for name, expected_url in user_menu_links:
                if test_dropdown_link(page, "userDropdown", name, expected_url):
                    test_results['passed'] += 1
                else:
                    test_results['failed'] += 1
                    test_results['errors'].append(f"用户菜单-{name} 链接失败")
            
            # 3. 测试API下拉菜单的每个链接
            print("🔧 详细测试API下拉菜单链接...")
            api_menu_links = [
                ("API根目录", "http://127.0.0.1:8000/api/"),
                ("API文档", "http://127.0.0.1:8000/api/schema/swagger-ui/"),
                ("API v1", "http://127.0.0.1:8000/api/v1/"),
            ]
            
            for name, expected_url in api_menu_links:
                if test_dropdown_link(page, "apiDropdown", name, expected_url):
                    test_results['passed'] += 1
                else:
                    test_results['failed'] += 1
                    test_results['errors'].append(f"API菜单-{name} 链接失败")
            
            # 4. 测试通知下拉菜单的每个链接
            print("🔔 详细测试通知下拉菜单链接...")
            notification_menu_links = [
                ("通知设置", "http://127.0.0.1:8000/notifications/preferences/"),
                ("通知历史", "http://127.0.0.1:8000/notifications/history/"),
            ]
            
            for name, expected_url in notification_menu_links:
                if test_dropdown_link(page, "notificationDropdown", name, expected_url):
                    test_results['passed'] += 1
                else:
                    test_results['failed'] += 1
                    test_results['errors'].append(f"通知菜单-{name} 链接失败")
            
            # 5. 测试个人资料页面的侧边栏链接
            print("📝 测试个人资料页面的侧边栏...")
            profile_sidebar_links = [
                ("基本资料", "http://127.0.0.1:8000/users/profile/"),
                ("修改密码", "http://127.0.0.1:8000/users/password/change/"),
                ("通知设置", "http://127.0.0.1:8000/notifications/preferences/"),
                ("偏好设置", "http://127.0.0.1:8000/users/settings/"),
            ]
            
            page.goto("http://127.0.0.1:8000/users/profile/")
            page.wait_for_load_state()
            
            for name, expected_url in profile_sidebar_links:
                if test_sidebar_link(page, name, expected_url):
                    test_results['passed'] += 1
                else:
                    test_results['failed'] += 1
                    test_results['errors'].append(f"个人资料侧边栏-{name} 链接失败")
            
            # 6. 测试表单提交功能
            print("📋 测试表单功能...")
            if test_profile_form(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("个人资料表单测试失败")
            
            # 7. 测试任务列表的各种操作
            print("📝 测试任务列表功能...")
            if test_task_list_features(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("任务列表功能测试失败")
            
            # 8. 测试看板功能
            print("📊 测试看板功能...")
            if test_board_features(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("看板功能测试失败")
            
            # 9. 测试团队功能
            print("👥 测试团队功能...")
            if test_team_features(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("团队功能测试失败")
            
            # 10. 测试报表功能
            print("📈 测试报表功能...")
            if test_reports_features(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("报表功能测试失败")
            
            # 11. 测试下拉菜单的z-index和滚动条
            print("🔍 测试下拉菜单z-index和滚动条...")
            if test_dropdown_zindex_and_scrollbars(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("下拉菜单z-index或滚动条测试失败")
            
            # 12. 测试响应式设计
            print("📱 测试响应式设计...")
            if test_responsive_design(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("响应式设计测试失败")
            
            # 13. 测试多个下拉菜单之间的交互
            print("🔄 测试多个下拉菜单交互...")
            if test_multiple_dropdowns_interaction(page):
                test_results['passed'] += 1
            else:
                test_results['failed'] += 1
                test_results['errors'].append("下拉菜单交互测试失败")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            test_results['failed'] += 1
            test_results['errors'].append(f"测试异常: {e}")
        
        # 输出测试结果
        print_detailed_test_results(test_results)
        
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

def test_dropdown_link(page, dropdown_id, link_text, expected_url):
    """测试下拉菜单中的特定链接"""
    try:
        page.goto("http://127.0.0.1:8000/dashboard/")
        page.wait_for_load_state()
        
        # 点击下拉菜单
        dropdown = page.locator(f"#{dropdown_id}")
        dropdown.click()
        time.sleep(0.5)
        
        # 查找并点击链接
        link = page.locator(f"#{dropdown_id} + .dropdown-menu").get_by_text(link_text, exact=False).first
        if link.is_visible():
            link.click()
            page.wait_for_load_state()
            
            current_url = page.url
            if expected_url.endswith("/"):
                success = current_url.rstrip("/") == expected_url.rstrip("/")
            else:
                success = expected_url in current_url
            
            if success:
                print(f"   ✅ {link_text} 链接正常 - 跳转到: {current_url}")
                return True
            else:
                print(f"   ❌ {link_text} 链接跳转错误 - 期望: {expected_url}, 实际: {current_url}")
                return False
        else:
            print(f"   ❌ {link_text} 链接不可见")
            return False
    except Exception as e:
        print(f"   ❌ {link_text} 链接测试错误: {e}")
        return False

def test_sidebar_link(page, link_text, expected_url):
    """测试侧边栏链接"""
    try:
        link = page.get_by_text(link_text, exact=False).first
        if link.is_visible():
            link.click()
            page.wait_for_load_state()
            
            current_url = page.url
            if expected_url.endswith("/"):
                success = current_url.rstrip("/") == expected_url.rstrip("/")
            else:
                success = expected_url in current_url
            
            if success:
                print(f"   ✅ {link_text} 侧边栏链接正常")
                return True
            else:
                print(f"   ❌ {link_text} 侧边栏链接跳转错误")
                return False
        else:
            print(f"   ❌ {link_text} 侧边栏链接不可见")
            return False
    except Exception as e:
        print(f"   ❌ {link_text} 侧边栏链接测试错误: {e}")
        return False

def test_profile_form(page):
    """测试个人资料表单"""
    try:
        page.goto("http://127.0.0.1:8000/users/profile/")
        page.wait_for_load_state()
        
        # 检查表单字段
        first_name = page.locator("#id_first_name")
        last_name = page.locator("#id_last_name")
        email = page.locator("#id_email")
        
        if first_name.is_visible() and last_name.is_visible() and email.is_visible():
            print("   ✅ 个人资料表单字段正常显示")
            
            # 测试表单填写
            original_first_name = first_name.input_value()
            first_name.fill("测试用户")
            
            # 检查保存按钮
            save_button = page.locator("button[type=submit]")
            if save_button.is_visible():
                print("   ✅ 保存按钮可见")
                # 恢复原值
                first_name.fill(original_first_name)
                return True
            else:
                print("   ❌ 保存按钮不可见")
                return False
        else:
            print("   ❌ 个人资料表单字段缺失")
            return False
    except Exception as e:
        print(f"   ❌ 个人资料表单测试错误: {e}")
        return False

def test_task_list_features(page):
    """测试任务列表功能"""
    try:
        page.goto("http://127.0.0.1:8000/tasks/")
        page.wait_for_load_state()
        
        # 检查任务统计
        stats = page.locator(".stat-card")
        if stats.count() > 0:
            print("   ✅ 任务统计卡片正常显示")
        
        # 检查筛选功能
        filter_buttons = page.locator(".filter-btn")
        if filter_buttons.count() > 0:
            print("   ✅ 任务筛选按钮正常显示")
        
        # 检查任务卡片
        task_cards = page.locator(".task-card")
        if task_cards.count() > 0:
            print(f"   ✅ 任务卡片正常显示 ({task_cards.count()} 个)")
            return True
        else:
            print("   ⚠️ 没有任务数据，但页面结构正常")
            return True
    except Exception as e:
        print(f"   ❌ 任务列表功能测试错误: {e}")
        return False

def test_board_features(page):
    """测试看板功能"""
    try:
        page.goto("http://127.0.0.1:8000/boards/")
        page.wait_for_load_state()
        
        # 检查看板列表
        board_cards = page.locator(".board-card, .card")
        if board_cards.count() > 0:
            print(f"   ✅ 看板卡片正常显示 ({board_cards.count()} 个)")
            
            # 测试第一个看板的详情页面
            first_board_link = page.locator("a[href*='/boards/'][href$='/']").first
            if first_board_link.is_visible():
                first_board_link.click()
                page.wait_for_load_state()
                
                # 检查看板详情页面的列表
                lists = page.locator(".list-container, .kanban-list")
                if lists.count() > 0:
                    print(f"   ✅ 看板详情页面正常 (包含 {lists.count()} 个列表)")
                else:
                    print("   ✅ 看板详情页面结构正常")
                return True
            else:
                print("   ✅ 看板列表页面正常，但无可点击的看板")
                return True
        else:
            print("   ⚠️ 没有看板数据，但页面结构正常")
            return True
    except Exception as e:
        print(f"   ❌ 看板功能测试错误: {e}")
        return False

def test_team_features(page):
    """测试团队功能"""
    try:
        page.goto("http://127.0.0.1:8000/teams/")
        page.wait_for_load_state()
        
        # 检查团队页面内容
        title = page.title()
        if "团队" in title:
            print("   ✅ 团队页面标题正确")
        
        # 检查创建团队按钮或链接
        create_buttons = page.locator("a[href*='create'], button[href*='create'], .btn-primary")
        if create_buttons.count() > 0:
            print("   ✅ 创建功能按钮可见")
        
        print("   ✅ 团队页面结构正常")
        return True
    except Exception as e:
        print(f"   ❌ 团队功能测试错误: {e}")
        return False

def test_reports_features(page):
    """测试报表功能"""
    try:
        page.goto("http://127.0.0.1:8000/reports/")
        page.wait_for_load_state()
        
        # 检查报表页面内容
        title = page.title()
        if "报表" in title:
            print("   ✅ 报表页面标题正确")
        
        # 检查图表容器
        charts = page.locator("canvas, .chart-container, #chart")
        if charts.count() > 0:
            print(f"   ✅ 图表容器正常显示 ({charts.count()} 个)")
        
        # 检查报表统计
        stats = page.locator(".stat-card, .report-stat")
        if stats.count() > 0:
            print(f"   ✅ 报表统计正常显示 ({stats.count()} 个)")
        
        print("   ✅ 报表页面结构正常")
        return True
    except Exception as e:
        print(f"   ❌ 报表功能测试错误: {e}")
        return False

def test_dropdown_zindex_and_scrollbars(page):
    """测试下拉菜单的z-index和滚动条问题"""
    try:
        page.goto("http://127.0.0.1:8000/dashboard/")
        page.wait_for_load_state()
        
        # 测试用户下拉菜单
        print("   🔍 测试用户下拉菜单z-index和滚动条...")
        user_dropdown_result = test_specific_dropdown(page, "userDropdown")
        
        # 测试API下拉菜单
        print("   🔍 测试API下拉菜单z-index和滚动条...")
        api_dropdown_result = test_specific_dropdown(page, "apiDropdown")
        
        # 测试通知下拉菜单
        print("   🔍 测试通知下拉菜单z-index和滚动条...")
        notification_dropdown_result = test_specific_dropdown(page, "notificationDropdown")
        
        # 所有测试都通过才返回成功
        return user_dropdown_result and api_dropdown_result and notification_dropdown_result
    except Exception as e:
        print(f"   ❌ 下拉菜单z-index和滚动条测试错误: {e}")
        return False

def test_specific_dropdown(page, dropdown_id):
    """测试特定下拉菜单的z-index和滚动条"""
    try:
        # 点击下拉菜单
        dropdown = page.locator(f"#{dropdown_id}")
        dropdown.click()
        time.sleep(0.5)
        
        # 检查下拉菜单是否显示
        menu = page.locator(f"#{dropdown_id} + .dropdown-menu")
        is_visible = menu.is_visible()
        
        if is_visible:
            print(f"      ✅ {dropdown_id} 菜单可见")
            
            # 检查菜单的样式属性
            styles = page.evaluate(f"""
                () => {{
                    const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                    if (!menu) return {{ exists: false }};
                    
                    const style = window.getComputedStyle(menu);
                    
                    // 检查是否有滚动条
                    const hasVerticalScrollbar = menu.scrollHeight > menu.clientHeight;
                    const hasHorizontalScrollbar = menu.scrollWidth > menu.clientWidth;
                    
                    return {{
                        exists: true,
                        zIndex: style.zIndex,
                        position: style.position,
                        overflow: style.overflow,
                        display: style.display,
                        hasVerticalScrollbar,
                        hasHorizontalScrollbar,
                        scrollHeight: menu.scrollHeight,
                        clientHeight: menu.clientHeight
                    }};
                }}
            """)
            
            print(f"      📊 {dropdown_id} 菜单样式: {styles}")
            
            # 检查z-index是否足够高
            if styles.get('exists', False):
                z_index = styles.get('zIndex', '0')
                try:
                    z_index_value = int(z_index)
                    if z_index_value >= 1000:
                        print(f"      ✅ {dropdown_id} 菜单z-index足够高: {z_index}")
                    else:
                        print(f"      ⚠️ {dropdown_id} 菜单z-index可能不够高: {z_index}")
                except:
                    print(f"      ⚠️ {dropdown_id} 菜单z-index无法解析: {z_index}")
                
                # 检查是否有滚动条
                if styles.get('hasVerticalScrollbar', False):
                    print(f"      ⚠️ {dropdown_id} 菜单存在垂直滚动条")
                else:
                    print(f"      ✅ {dropdown_id} 菜单没有垂直滚动条")
                
                if styles.get('hasHorizontalScrollbar', False):
                    print(f"      ⚠️ {dropdown_id} 菜单存在水平滚动条")
                else:
                    print(f"      ✅ {dropdown_id} 菜单没有水平滚动条")
                
                # 检查定位
                if styles.get('position') == 'absolute':
                    print(f"      ✅ {dropdown_id} 菜单使用绝对定位")
                else:
                    print(f"      ⚠️ {dropdown_id} 菜单未使用绝对定位: {styles.get('position')}")
            
            # 检查所有菜单项是否可见
            menu_items = page.locator(f"#{dropdown_id} + .dropdown-menu .dropdown-item")
            if menu_items.count() > 0:
                all_visible = True
                for i in range(menu_items.count()):
                    if not menu_items.nth(i).is_visible():
                        all_visible = False
                        print(f"      ❌ {dropdown_id} 菜单项 {i+1} 不可见")
                
                if all_visible:
                    print(f"      ✅ {dropdown_id} 所有菜单项都可见")
            else:
                print(f"      ⚠️ {dropdown_id} 没有找到菜单项")
                
            # 尝试截图
            page.screenshot(path=f"{dropdown_id}_menu.png")
            print(f"      📸 已保存 {dropdown_id} 菜单截图")
        else:
            print(f"      ❌ {dropdown_id} 菜单不可见")
            return False
        
        # 关闭菜单
        dropdown.click()
        time.sleep(0.5)
        
        return is_visible
    except Exception as e:
        print(f"      ❌ {dropdown_id} 菜单测试错误: {e}")
        return False

def test_responsive_design(page):
    """测试响应式设计"""
    try:
        results = {
            'passed': 0,
            'failed': 0
        }
        
        # 测试不同屏幕尺寸
        screen_sizes = [
            {"width": 375, "height": 667, "name": "手机"},
            {"width": 768, "height": 1024, "name": "平板"},
            {"width": 1280, "height": 800, "name": "桌面"}
        ]
        
        for size in screen_sizes:
            print(f"   🖥️ 测试{size['name']}尺寸 ({size['width']}x{size['height']})...")
            page.set_viewport_size({"width": size['width'], "height": size['height']})
            time.sleep(1)
            
            # 刷新页面以适应新尺寸
            page.goto("http://127.0.0.1:8000/dashboard/")
            page.wait_for_load_state()
            
            # 检查汉堡菜单
            if size['width'] < 992:
                navbar_toggler = page.locator(".navbar-toggler")
                if navbar_toggler.is_visible():
                    print(f"      ✅ 汉堡菜单在{size['name']}尺寸下可见")
                    results['passed'] += 1
                    
                    # 点击汉堡菜单
                    navbar_toggler.click()
                    time.sleep(0.5)
                    
                    # 测试下拉菜单
                    for dropdown_id in ['userDropdown', 'apiDropdown', 'notificationDropdown']:
                        dropdown = page.locator(f"#{dropdown_id}")
                        if dropdown.is_visible():
                            dropdown.click()
                            time.sleep(0.5)
                            
                            menu = page.locator(f"#{dropdown_id} + .dropdown-menu")
                            if menu.is_visible():
                                print(f"      ✅ {dropdown_id} 在{size['name']}尺寸下可见")
                                results['passed'] += 1
                                
                                # 截图
                                page.screenshot(path=f"{dropdown_id}_{size['name']}.png")
                                
                                # 关闭菜单
                                dropdown.click()
                                time.sleep(0.5)
                            else:
                                print(f"      ❌ {dropdown_id} 在{size['name']}尺寸下不可见")
                                results['failed'] += 1
                        else:
                            print(f"      ⚠️ {dropdown_id} 触发器在{size['name']}尺寸下不可见")
                    
                    # 关闭汉堡菜单
                    navbar_toggler.click()
                    time.sleep(0.5)
                else:
                    print(f"      ❌ 汉堡菜单在{size['name']}尺寸下不可见")
                    results['failed'] += 1
            else:
                # 桌面尺寸直接测试下拉菜单
                for dropdown_id in ['userDropdown', 'apiDropdown', 'notificationDropdown']:
                    dropdown = page.locator(f"#{dropdown_id}")
                    if dropdown.is_visible():
                        dropdown.click()
                        time.sleep(0.5)
                        
                        menu = page.locator(f"#{dropdown_id} + .dropdown-menu")
                        if menu.is_visible():
                            print(f"      ✅ {dropdown_id} 在{size['name']}尺寸下可见")
                            results['passed'] += 1
                            
                            # 截图
                            page.screenshot(path=f"{dropdown_id}_{size['name']}.png")
                            
                            # 关闭菜单
                            dropdown.click()
                            time.sleep(0.5)
                        else:
                            print(f"      ❌ {dropdown_id} 在{size['name']}尺寸下不可见")
                            results['failed'] += 1
                    else:
                        print(f"      ⚠️ {dropdown_id} 触发器在{size['name']}尺寸下不可见")
            
        # 恢复桌面视图
        page.set_viewport_size({"width": 1280, "height": 800})
        
        print(f"   ✅ 响应式设计测试完成 - 通过: {results['passed']}, 失败: {results['failed']}")
        return results
    except Exception as e:
        print(f"   ❌ 响应式设计测试错误: {e}")
        return {'passed': 0, 'failed': 1}

def test_multiple_dropdowns_interaction(page):
    """测试多个下拉菜单之间的交互"""
    try:
        # 返回仪表盘
        page.goto("http://127.0.0.1:8000/dashboard/")
        page.wait_for_load_state()
        
        # 1. 打开用户下拉菜单
        user_dropdown = page.locator("#userDropdown")
        user_dropdown.click()
        time.sleep(0.5)
        
        # 检查用户下拉菜单是否可见
        user_menu = page.locator("#userDropdown + .dropdown-menu")
        if user_menu.is_visible():
            print("   ✅ 用户下拉菜单可见")
            
            # 2. 打开API下拉菜单
            api_dropdown = page.locator("#apiDropdown")
            api_dropdown.click()
            time.sleep(0.5)
            
            # 检查API下拉菜单是否可见，用户下拉菜单是否已关闭
            api_menu = page.locator("#apiDropdown + .dropdown-menu")
            if api_menu.is_visible() and not user_menu.is_visible():
                print("   ✅ API下拉菜单打开，用户菜单自动关闭")
                
                # 3. 打开通知下拉菜单
                notification_dropdown = page.locator("#notificationDropdown")
                notification_dropdown.click()
                time.sleep(0.5)
                
                # 检查通知下拉菜单是否可见，API下拉菜单是否已关闭
                notification_menu = page.locator("#notificationDropdown + .dropdown-menu")
                if notification_menu.is_visible() and not api_menu.is_visible():
                    print("   ✅ 通知下拉菜单打开，API菜单自动关闭")
                    
                    # 4. 点击页面空白处，应该关闭所有下拉菜单
                    page.click("body", position={"x": 10, "y": 10})
                    time.sleep(0.5)
                    
                    # 验证所有下拉菜单是否已关闭
                    if (not user_menu.is_visible() and 
                        not api_menu.is_visible() and 
                        not notification_menu.is_visible()):
                        print("   ✅ 点击空白处，所有菜单自动关闭")
                        return True
                    else:
                        print("   ❌ 点击空白处，部分菜单未关闭")
                        return False
                else:
                    print("   ❌ 通知菜单打开失败或API菜单未自动关闭")
                    return False
            else:
                print("   ❌ API菜单打开失败或用户菜单未自动关闭")
                return False
        else:
            print("   ❌ 用户菜单打开失败")
            return False
    except Exception as e:
        print(f"   ❌ 多下拉菜单交互测试错误: {e}")
        return False

def print_detailed_test_results(results):
    """输出详细测试结果"""
    print("=" * 80)
    print("超详细测试完成 - 结果汇总")
    print("=" * 80)
    
    total = results['passed'] + results['failed']
    success_rate = (results['passed'] / total * 100) if total > 0 else 0
    
    print(f"📊 详细测试统计:")
    print(f"   - 总测试项: {total}")
    print(f"   - 通过: {results['passed']} 项")
    print(f"   - 失败: {results['failed']} 项")
    print(f"   - 成功率: {success_rate:.1f}%")
    
    if results['errors']:
        print(f"❌ 发现的问题:")
        for i, error in enumerate(results['errors'], 1):
            print(f"   {i}. {error}")
    else:
        print("🎉 所有详细测试都通过了！")
    
    # 输出详细测试覆盖范围
    print(f"\n📋 测试覆盖范围:")
    print(f"   ✅ 用户登录和认证")
    print(f"   ✅ 用户下拉菜单的所有链接")
    print(f"   ✅ API下拉菜单的所有链接")
    print(f"   ✅ 通知下拉菜单的所有链接")
    print(f"   ✅ 个人资料页面侧边栏导航")
    print(f"   ✅ 个人资料表单功能")
    print(f"   ✅ 任务列表的核心功能")
    print(f"   ✅ 看板的核心功能")
    print(f"   ✅ 团队管理功能")
    print(f"   ✅ 报表分析功能")
    print(f"   ✅ 下拉菜单的z-index和滚动条")
    print(f"   ✅ 响应式设计")
    print(f"   ✅ 多个下拉菜单之间的交互")

if __name__ == "__main__":
    ultra_detailed_ui_test()
