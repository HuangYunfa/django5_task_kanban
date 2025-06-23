#!/usr/bin/env python
"""
工作流状态流转系统 - 简化UI测试脚本
使用Playwright测试真实浏览器交互
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright
import time


async def test_workflow_ui_basic():
    """基础UI测试 - 无需Django LiveServer"""
    print("🎭 启动Playwright浏览器测试...")
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 设置为False可以看到浏览器
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 访问Django应用首页
            print("📝 测试1: 访问Django应用首页...")
            await page.goto('http://127.0.0.1:8000/')
            
            # 等待页面加载
            await page.wait_for_load_state('networkidle')
            
            # 检查页面标题
            title = await page.title()
            print(f"   ✅ 页面标题: {title}")
            
            # 截图保存
            await page.screenshot(path='screenshots/homepage.png')
            
            # 测试导航到管理后台
            print("📝 测试2: 访问管理后台...")
            await page.goto('http://127.0.0.1:8000/admin/')
            await page.wait_for_load_state('networkidle')
            
            # 检查登录表单
            login_form = page.locator('form')
            if await login_form.is_visible():
                print("   ✅ 找到登录表单")
                await page.screenshot(path='screenshots/admin_login.png')
            
            # 测试用户登录 (如果有测试用户)
            print("📝 测试3: 尝试用户登录...")
            username_field = page.locator('input[name="username"]')
            password_field = page.locator('input[name="password"]')
            
            if await username_field.is_visible():
                # 使用之前创建的超级用户
                await username_field.fill('huangyunfa')
                await password_field.fill('huangyunfa123')  # 假设密码
                
                submit_btn = page.locator('input[type="submit"]')
                await submit_btn.click()
                
                await page.wait_for_load_state('networkidle')
                
                # 检查是否登录成功
                if 'admin' in await page.url():
                    print("   ✅ 用户登录成功")
                    await page.screenshot(path='screenshots/admin_dashboard.png')
                    
                    # 测试访问工作流管理页面
                    print("📝 测试4: 访问工作流状态管理...")
                    
                    # 尝试访问第一个看板的工作流页面
                    await page.goto('http://127.0.0.1:8000/tasks/workflow/statuses/ui/')
                    await page.wait_for_load_state('networkidle')
                    
                    current_url = await page.url()
                    print(f"   📍 当前URL: {current_url}")
                    
                    # 检查工作流页面元素
                    workflow_header = page.locator('h1')
                    if await workflow_header.is_visible():
                        header_text = await workflow_header.text_content()
                        print(f"   ✅ 找到工作流页面标题: {header_text}")
                        await page.screenshot(path='screenshots/workflow_page.png')
                    
                    # 检查状态卡片
                    status_cards = page.locator('.status-card')
                    card_count = await status_cards.count()
                    print(f"   📊 找到 {card_count} 个状态卡片")
                    
                    if card_count > 0:
                        # 获取第一个状态卡片的信息
                        first_card = status_cards.first
                        card_text = await first_card.text_content()
                        print(f"   📋 第一个状态: {card_text[:50]}...")
                    
                    # 测试创建状态页面
                    print("📝 测试5: 访问创建状态页面...")
                    create_btn = page.locator('a[href*="create"]')
                    if await create_btn.is_visible():
                        await create_btn.click()
                        await page.wait_for_load_state('networkidle')
                        
                        # 检查表单元素
                        form = page.locator('form')
                        if await form.is_visible():
                            print("   ✅ 找到创建状态表单")
                            await page.screenshot(path='screenshots/create_status_form.png')
                            
                            # 测试表单交互
                            name_input = page.locator('input[name="name"]')
                            display_name_input = page.locator('input[name="display_name"]')
                            
                            if await name_input.is_visible():
                                await name_input.fill('test_status')
                                await display_name_input.fill('测试状态')
                                print("   ✅ 表单填写测试完成")
                                
                                # 测试颜色选择器
                                color_options = page.locator('.color-option')
                                if await color_options.count() > 0:
                                    await color_options.first.click()
                                    print("   ✅ 颜色选择器交互测试完成")
                
                else:
                    print("   ❌ 登录可能失败")
            
            print("\n🎉 UI测试完成！")
            print("📸 截图已保存到 screenshots/ 目录")
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            await page.screenshot(path='screenshots/error.png')
        
        finally:
            await browser.close()


async def test_workflow_responsiveness():
    """测试响应式设计"""
    print("\n📱 测试响应式设计...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto('http://127.0.0.1:8000/tasks/workflow/statuses/ui/')
            
            # 测试不同屏幕尺寸
            screen_sizes = [
                (1920, 1080, 'desktop'),
                (1024, 768, 'tablet'),
                (375, 667, 'mobile')
            ]
            
            for width, height, device in screen_sizes:
                print(f"   📏 测试 {device} 视图 ({width}x{height})")
                await page.set_viewport_size({"width": width, "height": height})
                await page.wait_for_timeout(1000)  # 等待布局调整
                
                await page.screenshot(path=f'screenshots/responsive_{device}.png')
                print(f"   ✅ {device} 视图截图完成")
        
        except Exception as e:
            print(f"❌ 响应式测试错误: {e}")
        
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
    print("🚀 工作流状态流转系统 - Playwright UI测试")
    print("=" * 60)
    print("💡 这是一个真实浏览器UI测试，将会:")
    print("   • 启动Chrome浏览器 (可见模式)")
    print("   • 测试Django应用的各个页面")
    print("   • 测试工作流状态管理功能")
    print("   • 测试表单交互和响应式设计")
    print("   • 保存测试截图")
    print()
    
    # 检查Django服务器是否运行
    print("🔍 检查Django开发服务器...")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:8000/') as response:
                if response.status == 200:
                    print("   ✅ Django服务器正在运行")
                else:
                    print(f"   ⚠️  Django服务器响应状态: {response.status}")
    except Exception:
        print("   ❌ 无法连接Django服务器，请确保运行: python manage.py runserver")
        return
    
    setup_screenshots_dir()
    
    # 运行基础UI测试
    await test_workflow_ui_basic()
    
    # 运行响应式测试
    await test_workflow_responsiveness()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print("   ✅ UI基础功能测试完成")
    print("   ✅ 响应式设计测试完成")
    print("   📸 测试截图已保存")
    print("\n💡 查看测试截图:")
    print("   screenshots/homepage.png          - 首页")
    print("   screenshots/admin_login.png       - 管理登录")
    print("   screenshots/workflow_page.png     - 工作流页面")
    print("   screenshots/create_status_form.png - 创建状态表单")
    print("   screenshots/responsive_*.png      - 响应式视图")


if __name__ == '__main__':
    print("🎭 启动Playwright UI测试...")
    
    # 检查依赖
    try:
        from playwright.async_api import async_playwright
        print("✅ Playwright已安装")
    except ImportError:
        print("❌ 请先安装Playwright: pip install playwright")
        print("   然后安装浏览器: playwright install")
        sys.exit(1)
    
    try:
        import aiohttp
    except ImportError:
        print("⚠️  建议安装aiohttp以进行连接测试: pip install aiohttp")
    
    # 运行异步测试
    asyncio.run(main())
