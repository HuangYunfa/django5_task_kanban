#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录后测试下拉菜单
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_dropdown_with_login():
    """登录后测试下拉菜单"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(
            viewport={'width': 1200, 'height': 800}
        )
        
        page = await context.new_page()
        
        # 监听控制台消息
        def handle_console(msg):
            print(f"Console: [{msg.type}] {msg.text}")
        
        page.on("console", handle_console)
        
        try:
            print("🔧 登录后测试下拉菜单")
            print("=" * 40)
            
            # 访问登录页面
            await page.goto('http://localhost:8000/users/login/')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # 登录（使用演示用户）
            await page.fill('input[name="username"]', 'admin')  # 或 'demo'
            await page.fill('input[name="password"]', 'admin123')  # 或演示密码
            await page.click('button[type="submit"]')
            
            # 等待登录完成
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)  # 等待页面完全加载
            
            print("✅ 登录成功")
            
            # 检查是否有用户下拉菜单
            user_dropdown = await page.query_selector('#userDropdown')
            user_menu = await page.query_selector('#userDropdown + .dropdown-menu')
            
            print(f"用户下拉触发器存在: {user_dropdown is not None}")
            print(f"用户下拉菜单存在: {user_menu is not None}")
            
            if user_dropdown and user_menu:
                print("\n🖱️ 测试下拉菜单点击...")
                
                # 测试点击
                for i in range(1, 4):
                    print(f"\n--- 第 {i} 次点击 ---")
                    
                    # 点击前状态
                    pre_display = await user_menu.evaluate("el => el.style.display")
                    pre_classes = await user_menu.get_attribute('class')
                    pre_has_show = 'show' in (pre_classes or '')
                    
                    print(f"点击前: display='{pre_display}', has_show={pre_has_show}")
                    
                    # 点击
                    await page.click('#userDropdown')
                    await asyncio.sleep(1000)  # 等待1秒
                    
                    # 点击后状态
                    post_display = await user_menu.evaluate("el => el.style.display")
                    post_classes = await user_menu.get_attribute('class')
                    post_has_show = 'show' in (post_classes or '')
                    
                    print(f"点击后: display='{post_display}', has_show={post_has_show}")
                    
                    # 判断结果
                    is_visible = post_display == 'block' and post_has_show
                    print(f"菜单状态: {'✅ 可见' if is_visible else '❌ 隐藏'}")
            
        except Exception as e:
            print(f"❌ 测试错误: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    print("🚀 启动登录后下拉菜单测试...")
    asyncio.run(test_dropdown_with_login())
