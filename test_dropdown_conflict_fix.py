#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下拉菜单冲突修复验证测试
验证main.js与dropdown-fix.js冲突解决后的效果
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_dropdown_conflict_resolution():
    """测试下拉菜单冲突解决效果"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(
            viewport={'width': 1200, 'height': 800}
        )
        
        # 监听控制台消息
        page = await context.new_page()
        console_messages = []
        
        def handle_console(msg):
            console_messages.append(f"[{msg.type}] {msg.text}")
            print(f"Console: [{msg.type}] {msg.text}")
        
        page.on("console", handle_console)
        
        try:
            print("🔧 测试下拉菜单冲突修复效果")
            print("=" * 60)
            
            # 访问首页
            await page.goto('http://localhost:8000/')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            print("\n📊 检查脚本加载状态...")
            
            # 检查脚本初始化标志
            dropdown_fix_initialized = await page.evaluate("""
                window.dropdownFixInitialized || false
            """)
            print(f"下拉菜单修复脚本已初始化: {dropdown_fix_initialized}")
            
            # 检查下拉菜单元素
            user_dropdown = await page.query_selector('#userDropdown')
            print(f"用户下拉菜单元素存在: {user_dropdown is not None}")
            
            user_menu = await page.query_selector('#userDropdown + .dropdown-menu')
            print(f"用户下拉菜单存在: {user_menu is not None}")
            
            if user_menu:
                menu_display = await user_menu.get_attribute('style')
                menu_classes = await user_menu.get_attribute('class')
                print(f"菜单初始状态 - 样式: {menu_display}")
                print(f"菜单初始状态 - 类: {menu_classes}")
            
            print("\n🖱️ 执行连续点击测试...")
            
            # 连续点击测试
            for i in range(1, 11):
                print(f"\n--- 第 {i} 次点击 ---")
                
                # 点击前状态
                if user_menu:
                    pre_click_display = await user_menu.evaluate("el => el.style.display")
                    pre_click_classes = await user_menu.get_attribute('class')
                    has_show_class = 'show' in (pre_click_classes or '')
                    print(f"点击前: display={pre_click_display}, has_show={has_show_class}")
                
                # 点击下拉菜单
                await page.click('#userDropdown')
                await asyncio.sleep(300)  # 等待动画和事件处理
                
                # 点击后状态
                if user_menu:
                    post_click_display = await user_menu.evaluate("el => el.style.display")
                    post_click_classes = await user_menu.get_attribute('class')
                    has_show_class = 'show' in (post_click_classes or '')
                    print(f"点击后: display={post_click_display}, has_show={has_show_class}")
                    
                    # 判断菜单状态
                    is_visible = post_click_display == 'block' and has_show_class
                    expected_visible = (i % 2 == 1)  # 奇数次应该可见，偶数次应该隐藏
                    
                    if is_visible == expected_visible:
                        print(f"✅ 第{i}次点击状态正确: {'显示' if is_visible else '隐藏'}")
                    else:
                        print(f"❌ 第{i}次点击状态错误: 实际{'显示' if is_visible else '隐藏'}, 期望{'显示' if expected_visible else '隐藏'}")
                
                await asyncio.sleep(200)
            
            print("\n🔍 测试其他下拉菜单...")
            
            # 测试API下拉菜单
            api_dropdown = await page.query_selector('#apiDropdown')
            if api_dropdown:
                print("\n测试API下拉菜单...")
                await page.click('#apiDropdown')
                await asyncio.sleep(500)
                
                api_menu = await page.query_selector('#apiDropdown + .dropdown-menu')
                if api_menu:
                    api_display = await api_menu.evaluate("el => el.style.display")
                    api_classes = await api_menu.get_attribute('class')
                    print(f"API菜单状态: display={api_display}, classes={api_classes}")
            
            # 测试通知下拉菜单
            notification_dropdown = await page.query_selector('#notificationDropdown')
            if notification_dropdown:
                print("\n测试通知下拉菜单...")
                await page.click('#notificationDropdown')
                await asyncio.sleep(500)
                
                notification_menu = await page.query_selector('#notificationDropdown + .dropdown-menu')
                if notification_menu:
                    notification_display = await notification_menu.evaluate("el => el.style.display")
                    notification_classes = await notification_menu.get_attribute('class')
                    print(f"通知菜单状态: display={notification_display}, classes={notification_classes}")
            
            print("\n📋 控制台消息汇总:")
            for msg in console_messages[-20:]:  # 显示最后20条消息
                print(f"  {msg}")
            
            print("\n🎯 测试结论:")
            print("1. 检查脚本是否只初始化一次")
            print("2. 检查事件冲突是否解决")
            print("3. 检查菜单状态是否正确切换")
            print("4. 检查控制台是否有错误信息")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    print("🚀 启动下拉菜单冲突修复验证测试...")
    asyncio.run(test_dropdown_conflict_resolution())
