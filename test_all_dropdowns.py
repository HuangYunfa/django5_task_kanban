#!/usr/bin/env python3
"""
全面的下拉菜单调试和修复脚本
测试所有下拉菜单的可见性和功能
"""

import sys
import os

# 设置Django环境
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'taskkanban'))
sys.path.insert(0, os.getcwd())

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from playwright.sync_api import sync_playwright
import time

def test_all_dropdowns():
    print("=" * 70)
    print("全面下拉菜单测试和修复")
    print("=" * 70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 登录
            print("🔐 执行登录...")
            page.goto("http://127.0.0.1:8000/accounts/login/")
            page.fill("#id_login", "admin")
            page.fill("#id_password", "admin123")
            page.click("button[type=submit]")
            page.wait_for_load_state()
            print("✅ 登录成功")
            
            # 1. 测试用户下拉菜单
            print("\n👤 测试用户下拉菜单...")
            test_user_dropdown(page)
            
            # 2. 测试API下拉菜单
            print("\n🔧 测试API下拉菜单...")
            test_api_dropdown(page)
            
            # 3. 测试通知下拉菜单
            print("\n🔔 测试通知下拉菜单...")
            test_notification_dropdown(page)
            
            # 4. 使用JavaScript强制显示所有下拉菜单项
            print("\n🛠️ 强制显示所有下拉菜单项...")
            force_show_dropdown_items(page)
            
            input("按回车键关闭浏览器...")
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
        finally:
            browser.close()

def test_user_dropdown(page):
    """测试用户下拉菜单"""
    try:
        # 点击用户下拉菜单
        user_toggle = page.locator("#userDropdown")
        if user_toggle.is_visible():
            print("   ✅ 找到用户菜单触发器")
            user_toggle.click()
            time.sleep(0.5)
            
            # 检查菜单项
            menu_items = page.locator("#userDropdownMenu .dropdown-item")
            count = menu_items.count()
            print(f"   📋 用户菜单项数量: {count}")
            
            for i in range(count):
                item = menu_items.nth(i)
                text = item.inner_text().strip()
                is_visible = item.is_visible()
                print(f"   {'✅' if is_visible else '❌'} 用户菜单项 {i+1}: '{text}' (可见: {is_visible})")
        else:
            print("   ❌ 未找到用户菜单触发器")
    except Exception as e:
        print(f"   ❌ 用户下拉菜单测试错误: {e}")

def test_api_dropdown(page):
    """测试API下拉菜单"""
    try:
        # 点击API下拉菜单
        api_toggle = page.locator("#apiDropdown")
        if api_toggle.is_visible():
            print("   ✅ 找到API菜单触发器")
            api_toggle.click()
            time.sleep(0.5)
            
            # 检查菜单项
            menu_items = page.locator("#apiDropdownMenu .dropdown-item")
            count = menu_items.count()
            print(f"   📋 API菜单项数量: {count}")
            
            for i in range(count):
                item = menu_items.nth(i)
                text = item.inner_text().strip()
                is_visible = item.is_visible()
                print(f"   {'✅' if is_visible else '❌'} API菜单项 {i+1}: '{text}' (可见: {is_visible})")
        else:
            print("   ❌ 未找到API菜单触发器")
    except Exception as e:
        print(f"   ❌ API下拉菜单测试错误: {e}")

def test_notification_dropdown(page):
    """测试通知下拉菜单"""
    try:
        # 点击通知下拉菜单
        notification_toggle = page.locator("#notificationDropdown")
        if notification_toggle.is_visible():
            print("   ✅ 找到通知菜单触发器")
            notification_toggle.click()
            time.sleep(0.5)
            
            # 检查菜单项
            menu_items = page.locator("#notificationDropdownMenu .dropdown-item")
            count = menu_items.count()
            print(f"   📋 通知菜单项数量: {count}")
            
            for i in range(count):
                item = menu_items.nth(i)
                text = item.inner_text().strip()
                is_visible = item.is_visible()
                print(f"   {'✅' if is_visible else '❌'} 通知菜单项 {i+1}: '{text}' (可见: {is_visible})")
        else:
            print("   ❌ 未找到通知菜单触发器")
    except Exception as e:
        print(f"   ❌ 通知下拉菜单测试错误: {e}")

def force_show_dropdown_items(page):
    """强制显示所有下拉菜单项"""
    try:
        # JavaScript代码来强制显示所有下拉菜单项
        js_code = """
        // 强制显示所有下拉菜单
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.classList.add('show');
            menu.style.display = 'block';
            menu.style.visibility = 'visible';
            menu.style.opacity = '1';
            menu.style.position = 'absolute';
            menu.style.transform = 'none';
        });
        
        // 强制显示所有下拉菜单项
        document.querySelectorAll('.dropdown-item').forEach(item => {
            item.style.display = 'block';
            item.style.visibility = 'visible';
            item.style.opacity = '1';
        });
        
        // 返回统计信息
        return {
            totalMenus: document.querySelectorAll('.dropdown-menu').length,
            totalItems: document.querySelectorAll('.dropdown-item').length,
            userMenuItems: document.querySelectorAll('#userDropdownMenu .dropdown-item').length,
            apiMenuItems: document.querySelectorAll('#apiDropdownMenu .dropdown-item').length,
            notificationMenuItems: document.querySelectorAll('#notificationDropdownMenu .dropdown-item').length
        };
        """
        
        result = page.evaluate(js_code)
        print(f"   📊 总下拉菜单数: {result['totalMenus']}")
        print(f"   📊 总菜单项数: {result['totalItems']}")
        print(f"   📊 用户菜单项数: {result['userMenuItems']}")
        print(f"   📊 API菜单项数: {result['apiMenuItems']}")
        print(f"   📊 通知菜单项数: {result['notificationMenuItems']}")
        
        time.sleep(2)  # 等待显示效果
        
        # 再次检查每个菜单的项目
        print("\n   🔍 强制显示后的菜单项检查:")
        
        # 用户菜单
        user_items = page.locator("#userDropdownMenu .dropdown-item")
        for i in range(user_items.count()):
            item = user_items.nth(i)
            text = item.inner_text().strip()
            is_visible = item.is_visible()
            print(f"   用户菜单: '{text}' - 可见: {is_visible}")
        
        # API菜单
        api_items = page.locator("#apiDropdownMenu .dropdown-item")
        for i in range(api_items.count()):
            item = api_items.nth(i)
            text = item.inner_text().strip()
            is_visible = item.is_visible()
            print(f"   API菜单: '{text}' - 可见: {is_visible}")
        
        # 通知菜单
        notification_items = page.locator("#notificationDropdownMenu .dropdown-item")
        for i in range(notification_items.count()):
            item = notification_items.nth(i)
            text = item.inner_text().strip()
            is_visible = item.is_visible()
            print(f"   通知菜单: '{text}' - 可见: {is_visible}")
            
    except Exception as e:
        print(f"   ❌ 强制显示下拉菜单项时出错: {e}")

if __name__ == "__main__":
    test_all_dropdowns()
