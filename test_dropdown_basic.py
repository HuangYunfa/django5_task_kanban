#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的下拉菜单测试
专注于测试基本的开关功能
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_dropdown_basic():
    """测试下拉菜单基本功能"""
    
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
            print("🔧 测试下拉菜单基本功能")
            print("=" * 40)
            
            # 访问首页
            await page.goto('http://localhost:8000/')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)  # 等待脚本加载完成
            
            print("\n🖱️ 测试用户下拉菜单...")
            
            # 获取菜单元素
            user_menu = await page.query_selector('#userDropdown + .dropdown-menu')
            
            if not user_menu:
                print("❌ 未找到用户下拉菜单")
                return
            
            # 测试5次点击
            for i in range(1, 6):
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
    print("🚀 启动简化下拉菜单测试...")
    asyncio.run(test_dropdown_basic())
