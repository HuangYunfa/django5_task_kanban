#!/usr/bin/env python3
"""
专门测试下拉菜单修复效果的脚本
"""

import time
from playwright.sync_api import sync_playwright

def test_dropdown_fix():
    """测试下拉菜单修复效果"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 70)
        print("测试下拉菜单修复效果")
        print("=" * 70)
        
        try:
            # 登录
            print("🔐 执行登录...")
            page.goto("http://127.0.0.1:8000/accounts/login/")
            page.fill("#id_login", "project_manager")
            page.fill("#id_password", "demo123456")
            page.click("button[type=submit]")
            page.wait_for_load_state()
            print("✅ 登录成功")
            
            # 等待页面完全加载
            time.sleep(2)
            
            # 测试用户下拉菜单
            print("\n👤 测试用户下拉菜单...")
            test_user_dropdown_fix(page)
            
            # 测试API下拉菜单
            print("\n🔧 测试API下拉菜单...")
            test_api_dropdown_fix(page)
            
            # 测试通知下拉菜单
            print("\n🔔 测试通知下拉菜单...")
            test_notification_dropdown_fix(page)
            
            print("\n✅ 所有下拉菜单测试完成!")
            print("请检查下拉菜单是否正常显示完整内容，而不是出现滚动条")
            
            input("按回车键关闭浏览器...")
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
        finally:
            browser.close()

def test_user_dropdown_fix(page):
    """测试用户下拉菜单修复"""
    try:
        # 点击用户下拉菜单
        user_toggle = page.locator("#userDropdown")
        if user_toggle.is_visible():
            print("   ✅ 找到用户下拉菜单")
            user_toggle.click()
            time.sleep(1)
            
            # 检查下拉菜单样式
            menu_styles = page.evaluate("""
                () => {
                    const menu = document.querySelector('#userDropdown + .dropdown-menu');
                    if (!menu) return null;
                    
                    const styles = window.getComputedStyle(menu);
                    return {
                        display: styles.display,
                        opacity: styles.opacity,
                        visibility: styles.visibility,
                        maxHeight: styles.maxHeight,
                        overflow: styles.overflow,
                        height: styles.height,
                        className: menu.className
                    };
                }
            """)
            
            print(f"   📊 用户菜单样式: {menu_styles}")
            
            # 检查菜单项
            menu_items = page.locator("#userDropdown + .dropdown-menu .dropdown-item")
            count = menu_items.count()
            print(f"   📋 找到菜单项数量: {count}")
            
            for i in range(count):
                item = menu_items.nth(i)
                text = item.inner_text().strip()
                is_visible = item.is_visible()
                print(f"   {'✅' if is_visible else '❌'} 菜单项: '{text}' (可见: {is_visible})")
            
            # 点击其他地方关闭菜单
            page.click("body")
            time.sleep(0.5)
        else:
            print("   ❌ 未找到用户下拉菜单")
    except Exception as e:
        print(f"   ❌ 用户下拉菜单测试错误: {e}")

def test_api_dropdown_fix(page):
    """测试API下拉菜单修复"""
    try:
        # 点击API下拉菜单
        api_toggle = page.locator("#apiDropdown")
        if api_toggle.is_visible():
            print("   ✅ 找到API下拉菜单")
            api_toggle.click()
            time.sleep(1)
            
            # 检查下拉菜单样式
            menu_styles = page.evaluate("""
                () => {
                    const menu = document.querySelector('#apiDropdown + .dropdown-menu');
                    if (!menu) return null;
                    
                    const styles = window.getComputedStyle(menu);
                    return {
                        display: styles.display,
                        opacity: styles.opacity,
                        visibility: styles.visibility,
                        maxHeight: styles.maxHeight,
                        overflow: styles.overflow,
                        height: styles.height,
                        className: menu.className
                    };
                }
            """)
            
            print(f"   📊 API菜单样式: {menu_styles}")
            
            # 检查菜单项
            menu_items = page.locator("#apiDropdown + .dropdown-menu .dropdown-item")
            count = menu_items.count()
            print(f"   📋 找到菜单项数量: {count}")
            
            for i in range(count):
                item = menu_items.nth(i)
                text = item.inner_text().strip()
                is_visible = item.is_visible()
                print(f"   {'✅' if is_visible else '❌'} 菜单项: '{text}' (可见: {is_visible})")
            
            # 点击其他地方关闭菜单
            page.click("body")
            time.sleep(0.5)
        else:
            print("   ❌ 未找到API下拉菜单")
    except Exception as e:
        print(f"   ❌ API下拉菜单测试错误: {e}")

def test_notification_dropdown_fix(page):
    """测试通知下拉菜单修复"""
    try:
        # 点击通知下拉菜单
        notification_toggle = page.locator("#notificationDropdown")
        if notification_toggle.is_visible():
            print("   ✅ 找到通知下拉菜单")
            notification_toggle.click()
            time.sleep(1)
            
            # 检查下拉菜单样式
            menu_styles = page.evaluate("""
                () => {
                    const menu = document.querySelector('#notificationDropdown + .dropdown-menu');
                    if (!menu) return null;
                    
                    const styles = window.getComputedStyle(menu);
                    return {
                        display: styles.display,
                        opacity: styles.opacity,
                        visibility: styles.visibility,
                        maxHeight: styles.maxHeight,
                        overflow: styles.overflow,
                        height: styles.height,
                        className: menu.className
                    };
                }
            """)
            
            print(f"   📊 通知菜单样式: {menu_styles}")
            
            # 检查菜单项
            menu_items = page.locator("#notificationDropdown + .dropdown-menu .dropdown-item")
            count = menu_items.count()
            print(f"   📋 找到菜单项数量: {count}")
            
            for i in range(count):
                item = menu_items.nth(i)
                text = item.inner_text().strip()
                is_visible = item.is_visible()
                print(f"   {'✅' if is_visible else '❌'} 菜单项: '{text}' (可见: {is_visible})")
            
            # 点击其他地方关闭菜单
            page.click("body")
            time.sleep(0.5)
        else:
            print("   ❌ 未找到通知下拉菜单")
    except Exception as e:
        print(f"   ❌ 通知下拉菜单测试错误: {e}")

if __name__ == "__main__":
    test_dropdown_fix()
