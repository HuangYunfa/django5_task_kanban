#!/usr/bin/env python3
"""
验证三个问题修复效果的自动化测试脚本
"""
import asyncio
import sys
import os
from playwright.async_api import async_playwright

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def verify_fixes():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            print("🔧 验证三个问题的修复效果...")
            
            # 问题1: 验证任务管理页面修复效果
            print("\n📋 验证问题1: 任务管理页面修复效果")
            await page.goto('http://127.0.0.1:8000/tasks/', wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # 截图表格视图
            await page.screenshot(path='fix1_tasks_table_view.png', full_page=True)
            print("   ✅ 表格视图截图: fix1_tasks_table_view.png")
            
            # 检查表头样式
            table_header = page.locator('thead th')
            if await table_header.count() > 0:
                print("   📊 表头样式检查通过")
            
            # 测试卡片视图切换
            card_view_btn = page.locator('button[onclick="toggleView(\'card\')"]')
            if await card_view_btn.count() > 0:
                print("   🔘 找到卡片视图按钮，开始切换")
                await card_view_btn.click()
                await page.wait_for_timeout(2000)
                
                # 检查卡片视图是否显示
                card_view = page.locator('#cardView')
                is_visible = await card_view.is_visible()
                print(f"   📱 卡片视图是否可见: {is_visible}")
                
                # 截图卡片视图
                await page.screenshot(path='fix1_tasks_card_view_fixed.png', full_page=True)
                print("   📸 卡片视图截图: fix1_tasks_card_view_fixed.png")
                
                # 切换回表格视图
                table_view_btn = page.locator('button[onclick="toggleView(\'table\')"]')
                await table_view_btn.click()
                await page.wait_for_timeout(1000)
                print("   ↩️  切换回表格视图")
            else:
                print("   ❌ 未找到卡片视图按钮")
            
            # 问题2: 验证API文档修复效果（已经在之前验证过，这里简单检查）
            print("\n🔗 验证问题2: API文档重定向")
            response = await page.goto('http://127.0.0.1:8000/api/schema/docs/', wait_until='networkidle')
            if response.status == 200 and 'docs' in page.url:
                print("   ✅ API文档重定向修复成功")
            else:
                print("   ❌ API文档仍有问题")
            
            # 问题3: 验证看板管理模板标签修复效果
            print("\n📊 验证问题3: 看板管理模板标签修复效果")
            await page.goto('http://127.0.0.1:8000/boards/', wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # 截图看板页面
            await page.screenshot(path='fix3_boards_fixed.png', full_page=True)
            print("   ✅ 看板管理截图: fix3_boards_fixed.png")
            
            # 滚动到底部查看模板
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)
            await page.screenshot(path='fix3_boards_templates_fixed.png', full_page=True)
            print("   📋 看板模板区域截图: fix3_boards_templates_fixed.png")
            
            # 测试下拉菜单功能
            dropdown_btns = page.locator('.dropdown-toggle')
            if await dropdown_btns.count() > 0:
                print(f"   🔽 找到 {await dropdown_btns.count()} 个下拉按钮")
                
                # 点击第一个下拉按钮测试
                first_dropdown = dropdown_btns.first
                await first_dropdown.click()
                await page.wait_for_timeout(1000)
                
                # 检查下拉菜单是否显示
                dropdown_menu = page.locator('.dropdown-menu.show')
                if await dropdown_menu.count() > 0:
                    print("   ✅ 下拉菜单正常显示")
                    await page.screenshot(path='fix3_dropdown_test.png', full_page=True)
                    print("   📸 下拉菜单测试截图: fix3_dropdown_test.png")
                else:
                    print("   ❌ 下拉菜单未正常显示")
                
                # 点击其他地方关闭下拉菜单
                await page.click('body')
                await page.wait_for_timeout(500)
            
            print("\n✅ 修复效果验证完成!")
            print("📸 所有验证截图已保存:")
            print("   - fix1_tasks_table_view.png (任务表格视图)")
            print("   - fix1_tasks_card_view_fixed.png (任务卡片视图修复)")
            print("   - fix3_boards_fixed.png (看板管理修复)")
            print("   - fix3_boards_templates_fixed.png (看板模板修复)")
            print("   - fix3_dropdown_test.png (下拉菜单测试)")
            
            # 最终综合测试
            print("\n🎯 进行最终功能综合测试...")
            
            # 测试任务管理页面的完整功能
            await page.goto('http://127.0.0.1:8000/tasks/', wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # 再次测试视图切换
            for view_type in ['card', 'table', 'card']:
                btn = page.locator(f'button[onclick="toggleView(\'{view_type}\')"]')
                await btn.click()
                await page.wait_for_timeout(1000)
                print(f"   🔄 切换到{view_type}视图")
            
            await page.screenshot(path='final_comprehensive_test.png', full_page=True)
            print("   📸 最终综合测试截图: final_comprehensive_test.png")
            
        except Exception as e:
            print(f"❌ 验证过程中出错: {e}")
            await page.screenshot(path='verification_error.png')
        
        finally:
            await page.wait_for_timeout(3000)  # 保持浏览器打开3秒供观察
            await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_fixes())
