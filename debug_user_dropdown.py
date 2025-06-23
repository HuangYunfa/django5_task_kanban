#!/usr/bin/env python
"""
专门调试用户下拉菜单的脚本
"""

import time
from playwright.sync_api import sync_playwright

def debug_user_dropdown():
    """调试用户下拉菜单"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()
        
        print("======================================================================")
        print("用户下拉菜单调试")
        print("======================================================================")
        
        try:
            # 访问登录页面
            page.goto("http://127.0.0.1:8000/accounts/login/")
            
            # 登录
            page.fill("input[name='login']", "project_manager")
            page.fill("input[name='password']", "demo123456")
            page.click("button[type='submit']")
            page.wait_for_url("**/dashboard/")
            
            print("✅ 登录成功")
            
            # 检查用户下拉菜单触发器
            print("\n🔍 检查用户下拉菜单触发器...")
            user_dropdown_selectors = [
                "#userDropdown",
                "a[id='userDropdown']",
                ".nav-link.dropdown-toggle",
                "a:has-text('project_manager')"
            ]
            
            for selector in user_dropdown_selectors:
                elements = page.locator(selector)
                count = elements.count()
                print(f"   选择器 '{selector}': 找到 {count} 个元素")
                
                if count > 0:
                    first_element = elements.first
                    is_visible = first_element.is_visible()
                    print(f"   第一个元素可见性: {is_visible}")
                    
                    if is_visible:
                        # 获取元素的HTML内容
                        html_content = first_element.inner_html()
                        print(f"   元素内容: {html_content[:100]}...")
            
            # 尝试点击用户下拉菜单
            print("\n🖱️ 尝试点击用户下拉菜单...")
            user_dropdown = page.locator("#userDropdown").first
            if user_dropdown.is_visible():
                print("   点击用户下拉菜单触发器...")
                user_dropdown.click()
                time.sleep(2)  # 等待下拉菜单展开
                
                # 检查下拉菜单是否展开
                dropdown_menu = page.locator(".dropdown-menu")
                menu_count = dropdown_menu.count()
                print(f"   找到 {menu_count} 个下拉菜单")
                
                if menu_count > 0:
                    menu_visible = dropdown_menu.first.is_visible()
                    print(f"   下拉菜单可见性: {menu_visible}")
                    
                    if menu_visible:
                        # 获取所有菜单项
                        menu_items = page.locator(".dropdown-menu .dropdown-item")
                        item_count = menu_items.count()
                        print(f"   找到 {item_count} 个菜单项")
                        
                        for i in range(item_count):
                            item = menu_items.nth(i)
                            text = item.inner_text()
                            is_visible = item.is_visible()
                            print(f"   菜单项 {i+1}: '{text}' (可见: {is_visible})")
                    else:
                        print("   ❌ 下拉菜单不可见")
                        # 检查CSS类
                        menu_class = dropdown_menu.first.get_attribute("class")
                        print(f"   下拉菜单CSS类: {menu_class}")
                else:
                    print("   ❌ 未找到下拉菜单")
            else:
                print("   ❌ 用户下拉菜单触发器不可见")
            
            # 检查Bootstrap是否正确加载
            print("\n🔧 检查Bootstrap加载状态...")
            bootstrap_js = page.evaluate("typeof bootstrap !== 'undefined'")
            print(f"   Bootstrap JS 加载: {bootstrap_js}")
            
            # 检查jQuery是否加载（如果使用）
            jquery_loaded = page.evaluate("typeof $ !== 'undefined'")
            print(f"   jQuery 加载: {jquery_loaded}")
            
            # 检查页面错误
            print("\n🐛 检查页面错误...")
            page.on("console", lambda msg: print(f"   控制台: {msg.text}"))
            page.on("pageerror", lambda error: print(f"   页面错误: {error}"))
            
        except Exception as e:
            print(f"❌ 调试过程中出现错误: {e}")
        
        input("按回车键关闭浏览器...")
        browser.close()

if __name__ == "__main__":
    debug_user_dropdown()
