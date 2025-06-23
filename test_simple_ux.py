#!/usr/bin/env python3
"""
简化的UX测试脚本
验证首页和主要页面的UX优化效果
"""

import asyncio
from playwright.async_api import async_playwright

class SimpleUXTest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        
    async def test_homepage_ux(self):
        """测试首页UX优化"""
        print("🎨 开始测试首页UX优化...")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 访问首页
            await page.goto(self.base_url)
            await page.wait_for_load_state('networkidle')
            
            print("📋 首页UX检查结果:")
            
            # 检查待办任务模块
            pending_tasks = await page.query_selector('.pending-tasks')
            if pending_tasks:
                print("✅ 待办任务模块存在")
            else:
                print("❌ 待办任务模块不存在")
            
            # 检查重要通知模块
            notifications = await page.query_selector('.important-notifications')
            if notifications:
                print("✅ 重要通知模块存在")
            else:
                print("❌ 重要通知模块不存在")
            
            # 检查卡片数量
            cards = await page.query_selector_all('.card')
            print(f"ℹ️ 发现 {len(cards)} 个卡片组件")
            
            # 检查按钮数量
            buttons = await page.query_selector_all('.btn')
            print(f"ℹ️ 发现 {len(buttons)} 个按钮组件")
            
            # 检查响应式容器
            container = await page.query_selector('.container, .container-fluid')
            if container:
                print("✅ 使用了响应式容器")
            else:
                print("❌ 未使用响应式容器")
            
            # 检查导航栏
            navbar = await page.query_selector('.navbar')
            if navbar:
                print("✅ 导航栏存在")
            else:
                print("❌ 导航栏不存在")
            
            # 检查页脚
            footer = await page.query_selector('.footer')
            if footer:
                print("✅ 页脚存在")
            else:
                print("❌ 页脚不存在")
            
            # 测试卡片悬停效果
            if cards:
                print("🖱️ 测试卡片悬停效果...")
                await cards[0].hover()
                await page.wait_for_timeout(500)
                print("✅ 卡片悬停效果测试完成")
            
            # 测试响应式设计
            print("📱 测试响应式设计...")
            await page.set_viewport_size({'width': 375, 'height': 667})
            await page.wait_for_timeout(1000)
            print("✅ 移动端视口测试完成")
            
            # 恢复桌面视口
            await page.set_viewport_size({'width': 1920, 'height': 1080})
            
            print("\n🎯 首页UX测试完成!")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            
        finally:
            await browser.close()
            await playwright.stop()

    async def test_style_application(self):
        """测试样式是否正确应用"""
        print("\n🎨 测试CSS样式应用...")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto(self.base_url)
            await page.wait_for_load_state('networkidle')
            
            # 检查全局CSS变量
            body_style = await page.evaluate('''
                () => {
                    const styles = getComputedStyle(document.body);
                    return {
                        fontFamily: styles.fontFamily,
                        background: styles.background,
                        minHeight: styles.minHeight
                    };
                }
            ''')
            
            print("📋 全局样式检查:")
            print(f"ℹ️ 字体: {body_style.get('fontFamily', 'N/A')}")
            print(f"ℹ️ 背景: {body_style.get('background', 'N/A')}")
            print(f"ℹ️ 最小高度: {body_style.get('minHeight', 'N/A')}")
            
            # 检查卡片样式
            card_elements = await page.query_selector_all('.card')
            if card_elements:
                card_style = await card_elements[0].evaluate('el => getComputedStyle(el)')
                print(f"ℹ️ 卡片圆角: {card_style.get('border-radius', 'N/A')}")
                print(f"ℹ️ 卡片阴影: {card_style.get('box-shadow', 'N/A')}")
            
            # 检查按钮样式
            button_elements = await page.query_selector_all('.btn')
            if button_elements:
                button_style = await button_elements[0].evaluate('el => getComputedStyle(el)')
                print(f"ℹ️ 按钮圆角: {button_style.get('border-radius', 'N/A')}")
                print(f"ℹ️ 按钮过渡: {button_style.get('transition', 'N/A')}")
            
            print("✅ CSS样式检查完成!")
            
        except Exception as e:
            print(f"❌ 样式测试失败: {e}")
            
        finally:
            await browser.close()
            await playwright.stop()

async def main():
    """主函数"""
    test = SimpleUXTest()
    
    # 测试首页UX
    await test.test_homepage_ux()
    
    # 测试样式应用
    await test.test_style_application()
    
    print("\n🎉 所有UX测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
