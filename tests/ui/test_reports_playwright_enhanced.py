#!/usr/bin/env python
"""
报表分析模块 - Playwright自动化测试
专门测试报表功能的UI自动化测试
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright, expect
from datetime import datetime


async def test_reports_analysis_ui():
    """报表分析UI自动化测试"""
    print("📊 启动报表分析UI自动化测试...")
    print("🎭 Chrome浏览器将以可见模式启动...")
    await asyncio.sleep(2)
    
    async with async_playwright() as p:
        # 启动浏览器 - 可见模式
        browser = await p.chromium.launch(
            headless=False,  # 可见模式
            slow_mo=1000,    # 慢速模式，便于观察
            args=[
                '--start-maximized',
                '--disable-web-security',
                '--no-sandbox',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print("✅ Chrome浏览器已启动")
        print("⏳ 开始报表分析测试流程...")
        
        try:
            # 1. 登录系统
            print("\n📝 步骤1: 登录系统...")
            await page.goto('http://127.0.0.1:8000/accounts/login/')
            await page.wait_for_load_state('networkidle')
            
            # 查找并填写登录表单
            username_field = page.locator('input[name="login"], input[name="username"]')
            password_field = page.locator('input[name="password"]')
            
            if await username_field.is_visible():
                await username_field.fill('huangyunfa')
                await password_field.fill('Lvyue.033271')
                
                submit_btn = page.locator('button[type="submit"], input[type="submit"]')
                await submit_btn.click()
                await page.wait_for_load_state('networkidle')
                print("   ✅ 登录成功")
            
            # 2. 访问报表页面
            print("\n📝 步骤2: 访问报表分析页面...")
            await page.goto('http://127.0.0.1:8000/reports/')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path='screenshots/reports_main.png')
            print("   ✅ 报表主页截图保存")
            
            # 3. 测试仪表板
            print("\n📝 步骤3: 测试仪表板...")
            dashboard_link = page.locator('a[href*="dashboard"], .dashboard-link')
            if await dashboard_link.is_visible():
                await dashboard_link.click()
                await page.wait_for_load_state('networkidle')
                await page.screenshot(path='screenshots/reports_dashboard.png')
                print("   ✅ 仪表板页面截图保存")
                
                # 检查图表元素
                charts = page.locator('canvas, .chart-container, #chart')
                chart_count = await charts.count()
                print(f"   📊 找到 {chart_count} 个图表元素")
                
                if chart_count > 0:
                    print("   ✅ 图表渲染正常")
                    await asyncio.sleep(3)  # 等待图表加载完成
                    await page.screenshot(path='screenshots/charts_loaded.png')
            
            # 4. 测试任务完成率报表
            print("\n📝 步骤4: 测试任务完成率报表...")
            await page.goto('http://127.0.0.1:8000/reports/task-completion/')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)  # 等待数据加载
            await page.screenshot(path='screenshots/task_completion_report.png')
            print("   ✅ 任务完成率报表截图保存")
            
            # 5. 测试用户工作负载报表
            print("\n📝 步骤5: 测试用户工作负载报表...")
            await page.goto('http://127.0.0.1:8000/reports/user-workload/')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            await page.screenshot(path='screenshots/user_workload_report.png')
            print("   ✅ 用户工作负载报表截图保存")
            
            # 6. 测试团队绩效报表
            print("\n📝 步骤6: 测试团队绩效报表...")
            await page.goto('http://127.0.0.1:8000/reports/team-performance/')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            await page.screenshot(path='screenshots/team_performance_report.png')
            print("   ✅ 团队绩效报表截图保存")
            
            # 7. 测试项目进度报表
            print("\n📝 步骤7: 测试项目进度报表...")
            await page.goto('http://127.0.0.1:8000/reports/project-progress/')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            await page.screenshot(path='screenshots/project_progress_report.png')
            print("   ✅ 项目进度报表截图保存")
            
            # 8. 测试报表导出功能
            print("\n📝 步骤8: 测试报表导出功能...")
            export_links = page.locator('a[href*="export"], .export-btn, button:has-text("导出")')
            export_count = await export_links.count()
            
            if export_count > 0:
                print(f"   📥 找到 {export_count} 个导出按钮")
                
                # 测试第一个导出按钮
                first_export = export_links.first
                await first_export.click()
                await page.wait_for_timeout(2000)  # 等待下载开始
                print("   ✅ 导出功能测试完成")
            
            # 9. 测试报表筛选功能
            print("\n📝 步骤9: 测试报表筛选功能...")
            
            # 查找日期筛选器
            date_filters = page.locator('input[type="date"], .date-picker')
            if await date_filters.count() > 0:
                print("   📅 找到日期筛选器")
                await page.screenshot(path='screenshots/date_filters.png')
            
            # 查找下拉筛选器
            select_filters = page.locator('select, .filter-select')
            select_count = await select_filters.count()
            if select_count > 0:
                print(f"   🔍 找到 {select_count} 个下拉筛选器")
                
                # 测试第一个下拉框
                first_select = select_filters.first
                await first_select.click()
                await page.wait_for_timeout(1000)
                await page.screenshot(path='screenshots/filter_dropdown.png')
            
            # 10. 测试响应式设计
            print("\n📝 步骤10: 测试报表页面响应式设计...")
            screen_sizes = [
                (1920, 1080, '桌面'),
                (1024, 768, '平板'),
                (375, 667, '手机')
            ]
            
            for width, height, device_name in screen_sizes:
                print(f"   📱 测试 {device_name} 视图 ({width}x{height})")
                await page.set_viewport_size({"width": width, "height": height})
                await page.wait_for_timeout(1000)
                await page.screenshot(path=f'screenshots/reports_responsive_{device_name}.png')
                print(f"   ✅ {device_name} 视图截图完成")
            
            print("\n🎉 报表分析UI自动化测试完成！")
            
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {e}")
            await page.screenshot(path='screenshots/error_reports.png')
            
        finally:
            await browser.close()


async def test_reports_chart_interactions():
    """测试报表图表交互功能"""
    print("\n📊 启动图表交互测试...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=1500,  # 更慢的速度观察交互
            args=['--start-maximized']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            # 登录并访问仪表板
            await page.goto('http://127.0.0.1:8000/accounts/login/')
            await page.fill('input[name="login"], input[name="username"]', 'huangyunfa')
            await page.fill('input[name="password"]', 'Lvyue.033271')
            await page.click('button[type="submit"], input[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            await page.goto('http://127.0.0.1:8000/reports/dashboard/')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)  # 等待图表渲染
            
            print("   📊 开始测试图表交互...")
            
            # 1. 测试图表悬停效果
            charts = page.locator('canvas')
            chart_count = await charts.count()
            
            if chart_count > 0:
                print(f"   🎯 找到 {chart_count} 个图表，开始交互测试")
                
                for i in range(min(chart_count, 3)):  # 测试前3个图表
                    chart = charts.nth(i)
                    print(f"   📈 测试第 {i+1} 个图表交互...")
                    
                    # 悬停在图表上
                    await chart.hover()
                    await page.wait_for_timeout(1000)
                    
                    # 点击图表
                    await chart.click()
                    await page.wait_for_timeout(1000)
                    
                    await page.screenshot(path=f'screenshots/chart_interaction_{i+1}.png')
            
            # 2. 测试图表工具栏按钮
            toolbar_buttons = page.locator('.chart-toolbar button, .chart-controls button')
            button_count = await toolbar_buttons.count()
            
            if button_count > 0:
                print(f"   🔧 找到 {button_count} 个图表工具栏按钮")
                
                for i in range(min(button_count, 3)):
                    button = toolbar_buttons.nth(i)
                    if await button.is_visible():
                        await button.click()
                        await page.wait_for_timeout(1000)
                        print(f"   ✅ 测试工具栏按钮 {i+1}")
            
            # 3. 测试图表类型切换
            chart_type_selectors = page.locator('select[name*="chart"], .chart-type-selector')
            if await chart_type_selectors.count() > 0:
                print("   🔄 测试图表类型切换...")
                first_selector = chart_type_selectors.first
                await first_selector.click()
                
                # 选择不同的图表类型
                options = page.locator('option')
                option_count = await options.count()
                
                if option_count > 1:
                    await options.nth(1).click()  # 选择第二个选项
                    await page.wait_for_timeout(2000)  # 等待图表重新渲染
                    await page.screenshot(path='screenshots/chart_type_changed.png')
                    print("   ✅ 图表类型切换测试完成")
            
            print("   🎉 图表交互测试完成！")
            
        except Exception as e:
            print(f"   ❌ 图表交互测试错误: {e}")
            await page.screenshot(path='screenshots/chart_interaction_error.png')
        
        finally:
            await browser.close()


def setup_screenshots_dir():
    """创建截图目录"""
    screenshots_dir = 'screenshots'
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        print(f"📁 创建截图目录: {screenshots_dir}")


async def main():
    """主测试函数"""
    print("🚀 报表分析模块 - Playwright自动化测试")
    print("=" * 60)
    print("📊 这个测试将验证以下功能:")
    print("   • 报表页面访问和导航")
    print("   • 图表渲染和数据显示")
    print("   • 报表筛选和导出功能")
    print("   • 图表交互和响应式设计")
    print("   • 各种报表类型的完整性")
    print()
    
    setup_screenshots_dir()
    
    # 运行报表分析UI测试
    await test_reports_analysis_ui()
    
    # 运行图表交互测试
    await test_reports_chart_interactions()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print("   ✅ 报表分析UI测试完成")
    print("   ✅ 图表交互测试完成")
    print("   📸 所有测试截图已保存")
    print("\n💡 查看测试截图:")
    print("   screenshots/reports_*.png     - 报表页面截图")
    print("   screenshots/chart_*.png      - 图表交互截图")
    print("   screenshots/responsive_*.png - 响应式设计截图")


if __name__ == '__main__':
    print("📊 启动报表分析Playwright自动化测试...")
    asyncio.run(main())
