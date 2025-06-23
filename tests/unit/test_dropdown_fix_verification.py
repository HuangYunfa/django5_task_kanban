#!/usr/bin/env python3
"""
深入测试API和通知下拉菜单显示问题
测试修复方案的有效性
"""

import time
import sys
import os
from playwright.sync_api import sync_playwright, expect

def test_dropdown_fix_verification():
    """验证下拉菜单修复方案的有效性"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 70)
        print("下拉菜单修复验证测试")
        print("=" * 70)
        
        try:
            # 1. 登录
            login(page)
            
            # 2. 系统性检查下拉菜单
            check_all_dropdowns(page)
            
            # 3. 移动端测试
            test_mobile_view(page)
            
            # 4. 生成最终报告
            generate_final_report()
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
        
        input("按回车键关闭浏览器...")
        browser.close()

def login(page):
    """执行登录"""
    try:
        print("\n🔐 执行登录...")
        page.goto("http://127.0.0.1:8000/accounts/login/")
        page.fill("input[name='login']", "project_manager")
        page.fill("input[name='password']", "demo123456")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard/")
        print("✅ 登录成功")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        sys.exit(1)

def check_all_dropdowns(page):
    """系统性检查所有下拉菜单"""
    print("\n🔍 系统性检查所有下拉菜单...")
    
    # 检查用户下拉菜单
    print("\n   👤 检查用户下拉菜单...")
    check_dropdown(page, 'user')
    
    # 检查API下拉菜单
    print("\n   🔌 检查API下拉菜单...")
    check_dropdown(page, 'api')
    
    # 检查通知下拉菜单
    print("\n   🔔 检查通知下拉菜单...")
    check_dropdown(page, 'notification')

def check_dropdown(page, dropdown_type):
    """检查特定类型的下拉菜单"""
    dropdown_id = f"{dropdown_type}Dropdown"
    
    try:
        # 1. 检查下拉菜单触发器
        trigger = page.locator(f"#{dropdown_id}")
        if not trigger.is_visible():
            print(f"   ❌ {dropdown_type}下拉菜单触发器不可见")
            return
        
        print(f"   ✅ {dropdown_type}下拉菜单触发器可见")
        
        # 2. 点击触发器
        trigger.click()
        time.sleep(0.5)
        
        # 3. 检查下拉菜单是否显示
        menu_visible = page.evaluate(f"""
            () => {{
                const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                if (!menu) return {{ exists: false }};
                
                const style = window.getComputedStyle(menu);
                return {{
                    exists: true,
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity,
                    position: style.position,
                    zIndex: style.zIndex,
                    hasShowClass: menu.classList.contains('show')
                }};
            }}
        """)
        
        print(f"   📊 菜单状态: {menu_visible}")
        
        # 4. 检查菜单项
        menu_items = page.evaluate(f"""
            () => {{
                const menu = document.querySelector('#{dropdown_id} + .dropdown-menu');
                if (!menu) return {{ exists: false }};
                
                const items = Array.from(menu.querySelectorAll('.dropdown-item, .dropdown-header, .dropdown-divider, .dropdown-item-text'));
                return {{
                    exists: true,
                    itemCount: items.length,
                    items: items.map(item => {{
                        const style = window.getComputedStyle(item);
                        return {{
                            text: item.innerText.trim(),
                            type: item.tagName.toLowerCase(),
                            classes: item.className,
                            isVisible: style.display !== 'none' && style.visibility !== 'hidden',
                            display: style.display,
                            visibility: style.visibility
                        }};
                    }})
                }};
            }}
        """)
        
        print(f"   📋 菜单项: {menu_items}")
        
        # 5. 尝试截图下拉菜单
        try:
            page.screenshot(path=f"{dropdown_type}_dropdown.png", full_page=False)
            print(f"   📸 已保存{dropdown_type}下拉菜单截图")
        except Exception as e:
            print(f"   ❌ 无法保存截图: {e}")
        
        # 6. 关闭下拉菜单
        trigger.click()
        time.sleep(0.5)
        
    except Exception as e:
        print(f"   ❌ 检查{dropdown_type}下拉菜单时出错: {e}")

def test_mobile_view(page):
    """测试移动视图下的下拉菜单"""
    print("\n📱 测试移动端视图下的下拉菜单...")
    
    try:
        # 设置移动视图大小
        page.set_viewport_size({"width": 375, "height": 667})
        print("   ✅ 已设置移动端视图大小 (375x667)")
        
        # 点击汉堡菜单
        page.click(".navbar-toggler")
        time.sleep(0.5)
        
        # 依次测试各下拉菜单
        check_dropdown(page, 'user')
        check_dropdown(page, 'api')
        check_dropdown(page, 'notification')
        
        # 恢复桌面视图
        page.set_viewport_size({"width": 1280, "height": 800})
        print("   ✅ 已恢复桌面视图大小 (1280x800)")
        
    except Exception as e:
        print(f"   ❌ 测试移动端视图时出错: {e}")

def generate_final_report():
    """生成最终测试报告"""
    print("\n📝 生成最终修复验证报告...")
    
    print("""
修复验证报告:
-----------
1. 用户下拉菜单: [测试结果将在运行时显示]
2. API下拉菜单: [测试结果将在运行时显示]
3. 通知下拉菜单: [测试结果将在运行时显示]
4. 移动端表现: [测试结果将在运行时显示]

修复方案有效性评估:
----------------
* dropdown-fix.js是否正确解决了所有菜单的显示问题?
* 所有菜单项是否都正确显示且可点击?
* 在移动端和桌面端是否都能正常工作?
* 修复是否与Bootstrap 5的原生功能兼容?

后续建议:
--------
1. 确保所有新页面都引入了修复脚本
2. 考虑升级Bootstrap版本或使用官方推荐的方法
3. 完善自动化测试，确保UI功能稳定
""")

if __name__ == "__main__":
    test_dropdown_fix_verification()
