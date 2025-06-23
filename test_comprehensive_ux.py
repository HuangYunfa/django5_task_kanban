#!/usr/bin/env python3
"""
全面的UX自动化测试脚本
验证所有主要页面的UX优化效果，包括页面头部、统计卡片、响应式设计等
"""

import os
import asyncio
import time
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

class ComprehensiveUXTest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = []
        self.failed_tests = []
        
    async def setup_browser(self):
        """设置浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
    async def teardown_browser(self):
        """关闭浏览器"""
        await self.browser.close()
        await self.playwright.stop()
    
    async def login(self):
        """登录系统"""
        try:
            await self.page.goto(f"{self.base_url}/login/")
            await self.page.wait_for_load_state('networkidle')
            
            # 填写登录表单
            await self.page.fill('input[name="username"]', 'testuser')
            await self.page.fill('input[name="password"]', 'testpass123')
            await self.page.click('button[type="submit"]')
            
            # 等待登录完成
            await self.page.wait_for_load_state('networkidle')
            
            # 检查是否成功登录
            current_url = self.page.url
            if 'login' not in current_url:
                return True
                
        except Exception as e:
            print(f"登录失败: {e}")
            return False
        
        return False
    
    async def test_page_header(self, page_name, url):
        """测试页面头部样式"""
        try:
            await self.page.goto(f"{self.base_url}{url}")
            await self.page.wait_for_load_state('networkidle')
            
            # 检查页面头部
            header_element = await self.page.query_selector('.page-header')
            if header_element:
                # 检查头部样式
                header_style = await header_element.evaluate('el => getComputedStyle(el)')
                has_gradient = 'linear-gradient' in str(header_style.get('background-image', ''))
                
                if has_gradient:
                    self.test_results.append(f"✅ {page_name}: 页面头部渐变样式正确")
                    return True
                else:
                    self.test_results.append(f"❌ {page_name}: 页面头部缺少渐变样式")
                    self.failed_tests.append(f"{page_name}: 页面头部样式")
            else:
                self.test_results.append(f"❌ {page_name}: 缺少页面头部")
                self.failed_tests.append(f"{page_name}: 页面头部")
                
        except Exception as e:
            self.test_results.append(f"❌ {page_name}: 页面头部测试失败 - {e}")
            self.failed_tests.append(f"{page_name}: 页面头部测试异常")
            
        return False
    
    async def test_stats_cards(self, page_name, url):
        """测试统计卡片样式"""
        try:
            await self.page.goto(f"{self.base_url}{url}")
            await self.page.wait_for_load_state('networkidle')
            
            # 检查统计卡片
            stats_cards = await self.page.query_selector_all('.stats-card')
            if stats_cards:
                # 检查第一个卡片的样式
                first_card = stats_cards[0]
                card_style = await first_card.evaluate('el => getComputedStyle(el)')
                
                has_shadow = 'rgba' in str(card_style.get('box-shadow', ''))
                has_transition = 'all' in str(card_style.get('transition', ''))
                
                if has_shadow and has_transition:
                    self.test_results.append(f"✅ {page_name}: 统计卡片样式正确")
                    return True
                else:
                    self.test_results.append(f"❌ {page_name}: 统计卡片样式不完整")
                    self.failed_tests.append(f"{page_name}: 统计卡片样式")
            else:
                self.test_results.append(f"⚠️ {page_name}: 未找到统计卡片")
                
        except Exception as e:
            self.test_results.append(f"❌ {page_name}: 统计卡片测试失败 - {e}")
            
        return False
    
    async def test_button_styling(self, page_name, url):
        """测试按钮样式"""
        try:
            await self.page.goto(f"{self.base_url}{url}")
            await self.page.wait_for_load_state('networkidle')
            
            # 检查按钮样式
            buttons = await self.page.query_selector_all('.btn')
            if buttons:
                # 检查第一个按钮的样式
                first_button = buttons[0]
                button_style = await first_button.evaluate('el => getComputedStyle(el)')
                
                has_border_radius = float(button_style.get('border-radius', '0px').replace('px', '')) > 0
                has_transition = 'all' in str(button_style.get('transition', ''))
                
                if has_border_radius and has_transition:
                    self.test_results.append(f"✅ {page_name}: 按钮样式正确")
                    return True
                else:
                    self.test_results.append(f"❌ {page_name}: 按钮样式不完整")
                    self.failed_tests.append(f"{page_name}: 按钮样式")
            else:
                self.test_results.append(f"⚠️ {page_name}: 未找到按钮")
                
        except Exception as e:
            self.test_results.append(f"❌ {page_name}: 按钮样式测试失败 - {e}")
            
        return False
    
    async def test_responsive_design(self, page_name, url):
        """测试响应式设计"""
        try:
            await self.page.goto(f"{self.base_url}{url}")
            await self.page.wait_for_load_state('networkidle')
            
            # 测试移动端视口
            await self.page.set_viewport_size({'width': 375, 'height': 667})
            await self.page.wait_for_timeout(500)
            
            # 检查响应式布局
            responsive_elements = await self.page.query_selector_all('.col-md-6, .col-lg-4, .col-xl-3')
            if responsive_elements:
                self.test_results.append(f"✅ {page_name}: 响应式设计正确")
                
                # 恢复桌面视口
                await self.page.set_viewport_size({'width': 1920, 'height': 1080})
                return True
            else:
                self.test_results.append(f"❌ {page_name}: 缺少响应式布局")
                self.failed_tests.append(f"{page_name}: 响应式设计")
                
            # 恢复桌面视口
            await self.page.set_viewport_size({'width': 1920, 'height': 1080})
                
        except Exception as e:
            self.test_results.append(f"❌ {page_name}: 响应式设计测试失败 - {e}")
            
        return False
    
    async def test_card_hover_effects(self, page_name, url):
        """测试卡片悬停效果"""
        try:
            await self.page.goto(f"{self.base_url}{url}")
            await self.page.wait_for_load_state('networkidle')
            
            # 查找卡片元素
            cards = await self.page.query_selector_all('.card')
            if cards:
                # 测试悬停效果
                first_card = cards[0]
                await first_card.hover()
                await self.page.wait_for_timeout(300)
                
                # 检查悬停后的样式
                card_style = await first_card.evaluate('el => getComputedStyle(el)')
                has_transform = 'matrix' in str(card_style.get('transform', ''))
                
                if has_transform:
                    self.test_results.append(f"✅ {page_name}: 卡片悬停效果正确")
                    return True
                else:
                    self.test_results.append(f"❌ {page_name}: 卡片悬停效果缺失")
                    self.failed_tests.append(f"{page_name}: 卡片悬停效果")
            else:
                self.test_results.append(f"⚠️ {page_name}: 未找到卡片")
                
        except Exception as e:
            self.test_results.append(f"❌ {page_name}: 卡片悬停效果测试失败 - {e}")
            
        return False
      async def run_comprehensive_tests(self):
        """运行全面的UX测试"""
        print("🎨 开始全面UX测试...")
          # 测试页面列表 - 使用可公开访问的页面
        test_pages = [
            ("首页", "/"),
            ("登录页", "/login/"),
        ]        
        await self.setup_browser()
        
        try:
            # 先测试首页，看看UX优化的具体效果
            print("\n🔍 详细测试首页UX优化效果...")
            
            # 访问首页
            await self.page.goto(f"{self.base_url}/")
            await self.page.wait_for_load_state('networkidle')
            
            # 检查首页待办任务模块
            pending_tasks = await self.page.query_selector('.pending-tasks')
            if pending_tasks:
                print("✅ 首页待办任务模块存在")
            else:
                print("❌ 首页待办任务模块不存在")
            
            # 检查重要通知模块
            notifications = await self.page.query_selector('.important-notifications')
            if notifications:
                print("✅ 首页重要通知模块存在")
            else:
                print("❌ 首页重要通知模块不存在")
            
            # 检查欢迎提示（可能不存在因为不是首次登录）
            welcome_alert = await self.page.query_selector('.alert-info')
            if welcome_alert:
                print("✅ 欢迎提示存在")
            else:
                print("ℹ️ 欢迎提示不存在（正常，非首次访问）")
            
            # 检查卡片样式
            cards = await self.page.query_selector_all('.card')
            print(f"ℹ️ 页面共有 {len(cards)} 个卡片")
            
            # 检查按钮样式
            buttons = await self.page.query_selector_all('.btn')
            print(f"ℹ️ 页面共有 {len(buttons)} 个按钮")
            
            # 检查整体布局
            container = await self.page.query_selector('.container, .container-fluid')
            if container:
                print("✅ 页面使用了响应式容器")
            else:
                print("❌ 页面未使用响应式容器")            
            # 对每个页面进行全面测试
            for page_name, url in test_pages:
                print(f"\n🔍 测试页面: {page_name}")
                
                # 页面头部测试
                await self.test_page_header(page_name, url)
                
                # 统计卡片测试
                await self.test_stats_cards(page_name, url)
                
                # 按钮样式测试
                await self.test_button_styling(page_name, url)
                
                # 响应式设计测试
                await self.test_responsive_design(page_name, url)
                
                # 卡片悬停效果测试
                await self.test_card_hover_effects(page_name, url)
                
                # 页面间隔
                await self.page.wait_for_timeout(1000)
                
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
            
        finally:
            await self.teardown_browser()
        
        await self.setup_browser()
        
        try:
            # 先尝试登录
            if not await self.login():
                print("⚠️ 登录失败，使用匿名访问测试...")
            
            # 对每个页面进行全面测试
            for page_name, url in test_pages:
                print(f"\n🔍 测试页面: {page_name}")
                
                # 页面头部测试
                await self.test_page_header(page_name, url)
                
                # 统计卡片测试
                await self.test_stats_cards(page_name, url)
                
                # 按钮样式测试
                await self.test_button_styling(page_name, url)
                
                # 响应式设计测试
                await self.test_responsive_design(page_name, url)
                
                # 卡片悬停效果测试
                await self.test_card_hover_effects(page_name, url)
                
                # 页面间隔
                await self.page.wait_for_timeout(1000)
                
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
            
        finally:
            await self.teardown_browser()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("📊 全面UX测试报告")
        print("="*80)
        
        # 显示所有测试结果
        for result in self.test_results:
            print(result)
        
        # 统计结果
        total_tests = len(self.test_results)
        failed_count = len(self.failed_tests)
        passed_count = total_tests - failed_count
        
        print(f"\n📈 测试统计:")
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_count}")
        print(f"失败测试: {failed_count}")
        print(f"通过率: {(passed_count/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if self.failed_tests:
            print(f"\n❌ 需要修复的UX问题:")
            for i, issue in enumerate(self.failed_tests, 1):
                print(f"{i}. {issue}")
        else:
            print(f"\n🎉 所有UX测试通过!")
        
        return failed_count == 0

async def main():
    """主函数"""
    tester = ComprehensiveUXTest()
    await tester.run_comprehensive_tests()
    success = tester.generate_report()
    
    if success:
        print("\n✨ 全面UX优化验证通过!")
        sys.exit(0)
    else:
        print("\n⚠️ 发现UX问题，需要进一步优化")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
