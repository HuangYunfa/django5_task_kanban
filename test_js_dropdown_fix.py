#!/usr/bin/env python3
"""
直接在页面上执行JavaScript修复下拉菜单的测试
"""

import time
from playwright.sync_api import sync_playwright

def test_dropdown_with_js():
    """直接用JavaScript修复下拉菜单"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 70)
        print("直接用JavaScript修复下拉菜单测试")
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
            
            # 直接用JavaScript修复下拉菜单
            print("\n🛠️ 直接用JavaScript修复下拉菜单...")
            js_fix_result = page.evaluate("""
                () => {
                    // 移除现有的点击事件监听器
                    const newDocument = document.cloneNode(true);
                    
                    // 重新定义下拉菜单点击处理函数
                    function setupDropdowns() {
                        const dropdownToggles = document.querySelectorAll('[data-bs-toggle="dropdown"]');
                        
                        dropdownToggles.forEach(toggle => {
                            // 移除现有的事件监听器
                            toggle.removeEventListener('click', handleClick);
                            
                            // 添加新的事件监听器
                            toggle.addEventListener('click', handleClick);
                        });
                        
                        function handleClick(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            const toggle = e.currentTarget;
                            const menu = toggle.nextElementSibling;
                            
                            if (menu && menu.classList.contains('dropdown-menu')) {
                                // 隐藏所有其他下拉菜单
                                document.querySelectorAll('.dropdown-menu').forEach(m => {
                                    if (m !== menu) {
                                        m.classList.remove('show');
                                        m.style.display = 'none';
                                    }
                                });
                                
                                // 切换当前菜单
                                if (menu.classList.contains('show')) {
                                    menu.classList.remove('show');
                                    menu.style.display = 'none';
                                } else {
                                    menu.classList.add('show');
                                    menu.style.display = 'block';
                                    menu.style.position = 'absolute';
                                    menu.style.inset = '0px auto auto 0px';
                                    menu.style.margin = '0px';
                                    menu.style.transform = 'translate3d(0px, 40px, 0px)';
                                }
                            }
                        }
                        
                        // 点击外部隐藏菜单
                        document.addEventListener('click', function(e) {
                            if (!e.target.closest('.dropdown')) {
                                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                                    menu.classList.remove('show');
                                    menu.style.display = 'none';
                                });
                            }
                        });
                        
                        return dropdownToggles.length;
                    }
                    
                    return setupDropdowns();
                }
            """)
            
            print(f"   📊 修复了 {js_fix_result} 个下拉菜单")
            
            # 测试用户下拉菜单
            print("\n👤 测试用户下拉菜单...")
            page.click("#userDropdown")
            time.sleep(1)
            
            # 检查菜单状态
            user_menu_state = page.evaluate("""
                () => {
                    const menu = document.querySelector('#userDropdown + .dropdown-menu');
                    return {
                        hasShow: menu.classList.contains('show'),
                        display: menu.style.display,
                        computedDisplay: window.getComputedStyle(menu).display
                    };
                }
            """)
            
            print(f"   📊 用户菜单状态: {user_menu_state}")
            
            # 检查菜单项可见性
            menu_items = page.locator("#userDropdown + .dropdown-menu .dropdown-item")
            count = menu_items.count()
            visible_count = 0
            
            for i in range(count):
                item = menu_items.nth(i)
                text = item.inner_text().strip()
                is_visible = item.is_visible()
                if is_visible:
                    visible_count += 1
                print(f"   {'✅' if is_visible else '❌'} 菜单项: '{text}' (可见: {is_visible})")
            
            print(f"   📊 可见菜单项: {visible_count}/{count}")
            
            # 测试API下拉菜单
            print("\n🔧 测试API下拉菜单...")
            page.click("#apiDropdown")
            time.sleep(1)
            
            api_menu_items = page.locator("#apiDropdown + .dropdown-menu .dropdown-item")
            api_count = api_menu_items.count()
            api_visible_count = 0
            
            for i in range(api_count):
                item = api_menu_items.nth(i)
                text = item.inner_text().strip()
                is_visible = item.is_visible()
                if is_visible:
                    api_visible_count += 1
                print(f"   {'✅' if is_visible else '❌'} API菜单项: '{text}' (可见: {is_visible})")
            
            print(f"   📊 API可见菜单项: {api_visible_count}/{api_count}")
            
            print("\n✅ JavaScript下拉菜单修复测试完成!")
            input("按回车键关闭浏览器...")
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    test_dropdown_with_js()
