#!/usr/bin/env python
"""
更详细的下拉菜单调试脚本
"""

import time
from playwright.sync_api import sync_playwright

def detailed_dropdown_debug():
    """详细调试下拉菜单"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()
        
        print("======================================================================")
        print("详细的下拉菜单调试")
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
            
            # 等待页面完全加载
            page.wait_for_load_state('networkidle')
            
            # 使用JavaScript直接操作下拉菜单
            print("\n🔧 使用JavaScript直接测试下拉菜单...")
              # 获取用户下拉菜单元素
            result = page.evaluate("""
                () => {
                    const userDropdown = document.getElementById('userDropdown');
                    const dropdownMenu = userDropdown.nextElementSibling;
                    
                    console.log('userDropdown:', userDropdown);
                    console.log('dropdownMenu:', dropdownMenu);
                    console.log('dropdownMenu classes before:', dropdownMenu.className);
                    
                    // 手动触发下拉菜单显示
                    userDropdown.click();
                    
                    // 等待一下然后检查状态
                    setTimeout(() => {
                        console.log('dropdownMenu classes after click:', dropdownMenu.className);
                        console.log('dropdownMenu style:', dropdownMenu.style.cssText);
                    }, 500);
                    
                    return {
                        userDropdownExists: !!userDropdown,
                        dropdownMenuExists: !!dropdownMenu,
                        classesBeforeClick: dropdownMenu.className,
                    };
                }
            """)
            
            print(f"   JavaScript结果: {result}")
            
            # 等待下拉菜单动画完成
            time.sleep(1)
              # 再次检查下拉菜单状态
            dropdown_status = page.evaluate("""
                () => {
                    const dropdownMenu = document.querySelector('#userDropdown').nextElementSibling;
                    return {
                        className: dropdownMenu.className,
                        isVisible: window.getComputedStyle(dropdownMenu).display !== 'none',
                        styles: window.getComputedStyle(dropdownMenu).cssText
                    };
                }
            """)
            
            print(f"   下拉菜单状态: {dropdown_status}")
              # 检查是否有show类
            has_show_class = page.evaluate("""
                () => {
                    const dropdownMenu = document.querySelector('#userDropdown').nextElementSibling;
                    return dropdownMenu.classList.contains('show');
                }
            """)
            
            print(f"   下拉菜单有show类: {has_show_class}")
              # 手动添加show类测试
            print("\n🧪 手动添加show类测试...")
            page.evaluate("""
                () => {
                    const dropdownMenu = document.querySelector('#userDropdown').nextElementSibling;
                    dropdownMenu.classList.add('show');
                    console.log('手动添加show类后:', dropdownMenu.className);
                }
            """)
            
            time.sleep(1)
            
            # 检查菜单项是否可见
            menu_items = page.locator("#userDropdown + .dropdown-menu .dropdown-item")
            item_count = menu_items.count()
            print(f"   找到菜单项数量: {item_count}")
            
            for i in range(min(item_count, 5)):  # 只检查前5个
                item = menu_items.nth(i)
                text = item.inner_text()
                is_visible = item.is_visible()
                print(f"   菜单项 {i+1}: '{text}' (可见: {is_visible})")
                
        except Exception as e:
            print(f"❌ 调试过程中出现错误: {e}")
        
        input("按回车键关闭浏览器...")
        browser.close()

if __name__ == "__main__":
    detailed_dropdown_debug()
