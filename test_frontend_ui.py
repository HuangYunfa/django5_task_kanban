"""
使用Playwright测试前端功能
测试用户体验改进是否生效
"""
import asyncio
from playwright.async_api import async_playwright
import time

async def test_frontend_functionality():
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        print("🚀 开始测试Django任务看板前端功能...")
        
        try:
            # 1. 测试首页访问
            print("\n📋 测试1: 访问首页")
            await page.goto("http://127.0.0.1:8000/")
            await page.wait_for_load_state('networkidle')
            
            title = await page.title()
            print(f"   页面标题: {title}")
            
            # 检查导航栏
            navbar = await page.locator('.navbar').count()
            print(f"   导航栏存在: {'✅' if navbar > 0 else '❌'}")
            
            # 检查登录按钮
            login_btn = await page.locator('a[href*="login"]').count()
            print(f"   登录按钮存在: {'✅' if login_btn > 0 else '❌'}")
            
            # 2. 测试登录功能
            print("\n📋 测试2: 用户登录")
            await page.click('a[href*="login"]')
            await page.wait_for_load_state('networkidle')
            
            current_url = page.url
            print(f"   当前URL: {current_url}")
            
            # 填写登录表单
            await page.fill('input[name="login"]', 'project_manager')
            await page.fill('input[name="password"]', 'demo123456')
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # 检查是否登录成功
            current_url = page.url
            print(f"   登录后URL: {current_url}")
            
            # 3. 测试导航栏用户菜单
            print("\n📋 测试3: 检查导航栏用户菜单")
            
            # 查看导航栏内容
            navbar_html = await page.locator('.navbar').inner_html()
            print(f"   导航栏包含用户名: {'✅' if 'project_manager' in navbar_html else '❌'}")
            
            # 检查用户下拉菜单
            user_dropdown = await page.locator('#userDropdown').count()
            print(f"   用户下拉菜单存在: {'✅' if user_dropdown > 0 else '❌'}")
            
            if user_dropdown > 0:
                # 点击用户下拉菜单
                await page.click('#userDropdown')
                await page.wait_for_timeout(1000)
                
                # 检查下拉菜单项
                dropdown_menu = await page.locator('.dropdown-menu').last()
                menu_items = await dropdown_menu.locator('a.dropdown-item').all()
                
                print(f"   下拉菜单项数量: {len(menu_items)}")
                for item in menu_items:
                    text = await item.inner_text()
                    href = await item.get_attribute('href')
                    print(f"     - {text.strip()}: {href}")
            else:
                print("   ❌ 用户下拉菜单不存在")
            
            # 4. 测试工作台页面
            print("\n📋 测试4: 访问工作台页面")
            await page.goto("http://127.0.0.1:8000/dashboard/")
            await page.wait_for_load_state('networkidle')
            
            page_content = await page.content()
            dashboard_indicators = [
                '工作台' in page_content,
                '快速操作' in page_content,
                '统计' in page_content or '总' in page_content
            ]
            
            print(f"   工作台页面加载: {'✅' if any(dashboard_indicators) else '❌'}")
            
            # 5. 测试个人资料页面
            print("\n📋 测试5: 访问个人资料页面")
            
            # 尝试通过用户菜单访问
            profile_link = await page.locator('a[href*="profile"]').count()
            if profile_link > 0:
                await page.click('a[href*="profile"]')
                await page.wait_for_load_state('networkidle')
                
                current_url = page.url
                print(f"   个人资料URL: {current_url}")
                
                # 检查个人资料页面内容
                page_content = await page.content()
                profile_indicators = [
                    '个人资料' in page_content,
                    '基本资料' in page_content,
                    '修改密码' in page_content
                ]
                
                print(f"   个人资料页面: {'✅' if any(profile_indicators) else '❌'}")
            else:
                print("   ❌ 无法找到个人资料链接")
            
            # 6. 测试退出登录功能
            print("\n📋 测试6: 退出登录功能")
            
            # 查找退出登录链接
            logout_links = await page.locator('a[href*="logout"]').count()
            print(f"   退出登录链接数量: {logout_links}")
            
            if logout_links > 0:
                await page.click('a[href*="logout"]')
                await page.wait_for_load_state('networkidle')
                
                current_url = page.url
                print(f"   退出后URL: {current_url}")
                
                # 检查是否回到未登录状态
                page_content = await page.content()
                login_indicators = [
                    '登录' in page_content,
                    '注册' in page_content,
                    'login' in current_url
                ]
                
                print(f"   退出登录成功: {'✅' if any(login_indicators) else '❌'}")
            else:
                print("   ❌ 无法找到退出登录链接")
            
            print("\n🎉 测试完成!")
            
        except Exception as e:
            print(f"\n❌ 测试过程中出现错误: {e}")
            
        finally:
            await browser.close()

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_frontend_functionality())
