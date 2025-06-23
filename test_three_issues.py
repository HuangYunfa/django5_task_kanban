#!/usr/bin/env python3
"""
测试三个主要问题的自动化脚本
1. 任务管理页面样式问题
2. API文档404问题  
3. 看板管理模板样式混乱问题
"""
import asyncio
import sys
import os
from playwright.async_api import async_playwright

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_three_main_issues():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            print("🔍 开始测试三个主要问题...")
            
            # 先尝试访问首页确认服务器运行
            await page.goto('http://127.0.0.1:8000/', wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # 问题1: 任务管理页面样式问题
            print("\n📋 问题1: 检查任务管理页面 (/tasks/)")
            await page.goto('http://127.0.0.1:8000/tasks/', wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # 截图任务管理页面
            await page.screenshot(path='issue1_tasks_current.png', full_page=True)
            print("   ✅ 任务管理页面截图已保存: issue1_tasks_current.png")
            
            # 检查表头样式
            table_header = page.locator('thead')
            if await table_header.count() > 0:
                header_style = await table_header.first.get_attribute('class')
                print(f"   📊 当前表头样式class: {header_style}")
            
            # 检查是否有卡片视图切换按钮
            card_view_btn = page.locator('button:has-text("卡片视图"), button[data-view="card"]')
            if await card_view_btn.count() > 0:
                print("   🔘 找到卡片视图切换按钮")
                await card_view_btn.first.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path='issue1_tasks_card_view.png', full_page=True)
                print("   📱 卡片视图截图已保存: issue1_tasks_card_view.png")
            else:
                print("   ❌ 未找到卡片视图切换按钮")
            
            # 问题2: API文档404问题
            print("\n🔗 问题2: 检查API文档页面 (/api/schema/docs/)")
            response = await page.goto('http://127.0.0.1:8000/api/schema/docs/', wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            print(f"   📄 响应状态码: {response.status}")
            current_url = page.url
            print(f"   🌐 当前URL: {current_url}")
            
            if response.status == 404:
                print("   ❌ 仍然返回404错误")
            elif 'swagger' in current_url.lower() or 'docs' in current_url.lower():
                print("   ✅ 成功重定向到API文档")
                await page.screenshot(path='issue2_api_docs.png', full_page=True)
                print("   📸 API文档截图已保存: issue2_api_docs.png")
            else:
                print("   ⚠️  重定向到了其他页面")
            
            # 问题3: 看板管理模板样式混乱
            print("\n📊 问题3: 检查看板管理页面 (/boards/)")
            await page.goto('http://127.0.0.1:8000/boards/', wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # 截图看板管理页面
            await page.screenshot(path='issue3_boards_current.png', full_page=True)
            print("   ✅ 看板管理页面截图已保存: issue3_boards_current.png")
            
            # 滚动到页面底部查看模板
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)
            await page.screenshot(path='issue3_boards_templates.png', full_page=True)
            print("   📋 看板模板区域截图已保存: issue3_boards_templates.png")
            
            # 检查模板标签的样式和位置
            template_labels = page.locator('.template-label, .badge')
            if await template_labels.count() > 0:
                print(f"   🏷️  找到 {await template_labels.count()} 个模板标签")
                for i in range(min(3, await template_labels.count())):
                    label = template_labels.nth(i)
                    text = await label.text_content()
                    style = await label.get_attribute('style')
                    class_attr = await label.get_attribute('class')
                    print(f"   标签{i+1}: '{text}' - class: {class_attr} - style: {style}")
            else:
                print("   ❌ 未找到模板标签")
            
            print("\n✅ 三个问题检查完成!")
            print("📸 所有截图已保存，请查看以下文件:")
            print("   - issue1_tasks_current.png (任务管理当前状态)")
            print("   - issue1_tasks_card_view.png (任务卡片视图)")
            print("   - issue2_api_docs.png (API文档页面)")
            print("   - issue3_boards_current.png (看板管理当前状态)")
            print("   - issue3_boards_templates.png (看板模板区域)")
            
        except Exception as e:
            print(f"❌ 测试过程中出错: {e}")
            await page.screenshot(path='error_screenshot.png')
        
        finally:
            await page.wait_for_timeout(3000)  # 保持浏览器打开3秒供观察
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_three_main_issues())
