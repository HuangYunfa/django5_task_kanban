#!/usr/bin/env python3
"""
Playwright自动化测试脚本 - 检查具体问题
"""

import asyncio
from playwright.async_api import async_playwright

async def test_ui_issues():
    """测试UI问题"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        print("🔍 开始UI问题检查...")
        
        try:
            # 登录
            print("1. 执行登录...")
            await page.goto("http://127.0.0.1:8000/accounts/login/")
            await page.fill('input[name="login"]', 'project_manager')
            await page.fill('input[name="password"]', 'demo123456')
            await page.click('button[type="submit"]')
            await page.wait_for_url("http://127.0.0.1:8000/dashboard/", timeout=10000)
            print("✅ 登录成功")
            
            # 问题1：检查任务管理页面
            print("\n2. 检查任务管理页面...")
            await page.goto("http://127.0.0.1:8000/tasks/")
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path='task_page_screenshot.png')
            print("✅ 任务页面截图已保存")
            
            # 检查表格样式
            table_header = page.locator('thead.table-light')
            if await table_header.count() > 0:
                print("✅ 找到表格头部")
            else:
                print("❌ 未找到表格头部")
                
            # 检查卡片视图按钮
            card_view_btn = page.locator('button:has-text("卡片视图")')
            if await card_view_btn.count() > 0:
                print("✅ 找到卡片视图按钮")
                await card_view_btn.click()
                await page.wait_for_timeout(1000)
                await page.screenshot(path='task_card_view_screenshot.png')
                print("✅ 卡片视图截图已保存")
            else:
                print("❌ 未找到卡片视图按钮")
              # 问题2：检查API文档页面
            print("\n3. 检查API文档页面...")
            await page.goto("http://127.0.0.1:8000/api/schema/docs/")
            await page.wait_for_load_state('networkidle')
            
            # 检查是否重定向到正确的页面
            current_url = page.url
            if "docs" in current_url and "404" not in await page.title():
                print("✅ API文档重定向正常")
            else:
                print("❌ API文档仍有问题")
                print(f"   当前URL: {current_url}")
                print(f"   页面标题: {await page.title()}")
            
            # 问题3：检查看板管理页面
            print("\n4. 检查看板管理页面...")
            await page.goto("http://127.0.0.1:8000/boards/")
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path='board_page_screenshot.png')
            print("✅ 看板页面截图已保存")
            
            # 检查看板模板标签
            template_badges = page.locator('.board-template-badge')
            badge_count = await template_badges.count()
            print(f"📊 找到 {badge_count} 个看板模板标签")
            
            if badge_count > 0:
                for i in range(badge_count):
                    badge = template_badges.nth(i)
                    badge_text = await badge.inner_text()
                    print(f"   - 模板标签 {i+1}: {badge_text}")
            
            print("\n🎯 检查完成，请查看截图了解具体问题")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
        
        input("按回车键关闭浏览器...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_ui_issues())
