#!/usr/bin/env python3
"""
简单的下拉菜单测试
"""

import time
from playwright.sync_api import sync_playwright

def simple_dropdown_test():
    """简单的下拉菜单测试"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 50)
        print("简单下拉菜单测试")
        print("=" * 50)
        
        try:
            # 登录
            page.goto("http://127.0.0.1:8000/accounts/login/")
            page.fill("#id_login", "project_manager")
            page.fill("#id_password", "demo123456")
            page.click("button[type=submit]")
            page.wait_for_load_state()
            print("✅ 登录成功")
            
            time.sleep(3)  # 等待页面完全加载
            
            # 测试用户下拉菜单
            print("\n👤 点击用户下拉菜单...")
            page.click("#userDropdown")
            time.sleep(2)
            
            # 检查菜单是否可见
            user_menu = page.locator("#userDropdown + .dropdown-menu")
            if user_menu.is_visible():
                print("✅ 用户下拉菜单现在可见")
                
                # 检查菜单项
                items = page.locator("#userDropdown + .dropdown-menu .dropdown-item")
                count = items.count()
                print(f"📋 菜单项数量: {count}")
                
                for i in range(count):
                    item = items.nth(i)
                    text = item.inner_text().strip()
                    is_visible = item.is_visible()
                    print(f"   {'✅' if is_visible else '❌'} {text}")
            else:
                print("❌ 用户下拉菜单仍然不可见")
            
            print("\n🔧 点击API下拉菜单...")
            page.click("#apiDropdown")
            time.sleep(2)
            
            # 检查API菜单是否可见
            api_menu = page.locator("#apiDropdown + .dropdown-menu")
            if api_menu.is_visible():
                print("✅ API下拉菜单现在可见")
                
                # 检查菜单项
                items = page.locator("#apiDropdown + .dropdown-menu .dropdown-item")
                count = items.count()
                print(f"📋 API菜单项数量: {count}")
                
                for i in range(count):
                    item = items.nth(i)
                    text = item.inner_text().strip()
                    is_visible = item.is_visible()
                    print(f"   {'✅' if is_visible else '❌'} {text}")
            else:
                print("❌ API下拉菜单仍然不可见")
            
            print("\n✅ 测试完成! 请检查下拉菜单显示是否正常")
            input("按回车键关闭浏览器...")
            
        except Exception as e:
            print(f"❌ 测试错误: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    simple_dropdown_test()
