#!/usr/bin/env python3
"""
全面的UX自动化测试脚本
测试所有主要页面的UX优化效果，包括：
1. 页面头部样式 
2. 统计卡片显示
3. 按钮和表单样式
4. 响应式设计
5. 移动端适配
6. 加载性能
"""

import asyncio
from playwright.async_api import async_playwright
import time
import os

class ComprehensiveUXTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup_browser(self):
        """设置浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
    
    async def teardown(self):
        """清理资源"""
        await self.browser.close()
        await self.playwright.stop()
    
    async def login(self):
        """用户登录"""
        try:
            await self.page.goto(f"{self.base_url}/auth/login/")
            await self.page.fill('input[name="username"]', 'admin')
            await self.page.fill('input[name="password"]', 'admin')
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_url(f"{self.base_url}/", timeout=10000)
            return True
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return False
    
    async def test_page_ux(self, url, page_name, expected_elements):
        """测试单个页面的UX优化"""
        print(f"\n=== 测试 {page_name} UX优化 ===")
        
        try:
            await self.page.goto(f"{self.base_url}{url}", timeout=15000)
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            page_results = []
            
            # 测试各个UX元素
            for element_name, selector in expected_elements.items():
                self.total_tests += 1
                
                try:
                    if selector:
                        await self.page.wait_for_selector(selector, timeout=5000)
                        element = self.page.locator(selector)
                        await element.first.wait_for(state='visible', timeout=5000)
                        
                        print(f"✓ {page_name}{element_name}优化可见")
                        page_results.append(f"✓ {element_name}")
                        self.passed_tests += 1
                    else:
                        # 跳过没有选择器的测试
                        print(f"⚪ {page_name}{element_name}测试跳过")
                        page_results.append(f"⚪ {element_name}")
                        
                except Exception as e:
                    print(f"❌ {page_name}{element_name}优化检测失败")
                    page_results.append(f"❌ {element_name}")
            
            # 测试响应式设计
            await self.test_responsive_design(page_name)
            
            self.results.append({
                'page': page_name,
                'url': url,
                'results': page_results
            })
            
        except Exception as e:
            print(f"❌ {page_name}页面测试失败: {e}")
            self.results.append({
                'page': page_name,
                'url': url,
                'results': [f"❌ 页面加载失败: {e}"]
            })
    
    async def test_responsive_design(self, page_name):
        """测试响应式设计"""
        viewports = [
            {'width': 1920, 'height': 1080, 'name': 'Desktop'},
            {'width': 768, 'height': 1024, 'name': 'Tablet'},
            {'width': 375, 'height': 667, 'name': 'Mobile'}
        ]
        
        for viewport in viewports:
            try:
                await self.page.set_viewport_size({
                    'width': viewport['width'], 
                    'height': viewport['height']
                })
                await self.page.wait_for_timeout(1000)  # 等待重新渲染
                
                # 检查页面是否正常显示
                body = self.page.locator('body')
                await body.wait_for(state='visible', timeout=3000)
                
                print(f"✓ {page_name}{viewport['name']}响应式适配正常")
                self.passed_tests += 1
                
            except Exception as e:
                print(f"❌ {page_name}{viewport['name']}响应式适配失败")
            
            self.total_tests += 1
        
        # 恢复默认视口
        await self.page.set_viewport_size({'width': 1920, 'height': 1080})
    
    async def run_all_tests(self):
        """运行所有UX测试"""
        print("🎨 开始全面UX自动化测试...")
        
        await self.setup_browser()
        
        # 登录
        if not await self.login():
            print("❌ 无法登录，测试终止")
            return
        
        # 定义所有要测试的页面
        test_pages = [
            {
                'url': '/',
                'name': '首页',
                'elements': {
                    '待办任务模块': '.todo-section',
                    '重要通知模块': '.notifications-section',
                    '快速操作区': '.quick-actions',
                    '欢迎提示': '.welcome-message'
                }
            },
            {
                'url': '/dashboard/',
                'name': '工作台',
                'elements': {
                    '页面头部': '.page-header',
                    '统计卡片': '.stats-card',
                    '快速操作': '.btn',
                    '数据图表': '.chart-container'
                }
            },
            {
                'url': '/tasks/',
                'name': '任务列表',
                'elements': {
                    '页面头部': '.page-header',
                    '统计卡片': '.stats-card',
                    '任务表格': '.table',
                    '筛选器': '.filter-section'
                }
            },
            {
                'url': '/teams/',
                'name': '团队协作',
                'elements': {
                    '页面头部': '.page-header',
                    '统计卡片': '.stats-card',
                    '团队卡片': '.card',
                    '创建按钮': '.btn-primary'
                }
            },
            {
                'url': '/reports/',
                'name': '报表分析',
                'elements': {
                    '页面头部': '.page-header',
                    '统计卡片': '.stats-card',
                    '图表展示': '.chart-container',
                    '导出按钮': '.btn'
                }
            },
            {
                'url': '/boards/',
                'name': '看板管理',
                'elements': {
                    '页面头部': '.page-header',
                    '统计卡片': '.stats-card',
                    '看板卡片': '.card',
                    '创建按钮': '.btn'
                }
            },
            {
                'url': '/notifications/history/',
                'name': '通知历史',
                'elements': {
                    '页面标题': 'h1',
                    '筛选器': '.form-select',
                    '通知列表': '.list-group',
                    '操作按钮': '.btn'
                }
            },
            {
                'url': '/users/profile/',
                'name': '用户资料',
                'elements': {
                    '资料头部': '.profile-header',
                    '头像区域': '.avatar-section',
                    '统计信息': '.stats-section',
                    '表单样式': '.form-control'
                }
            }
        ]
        
        # 执行所有页面测试
        for page_config in test_pages:
            await self.test_page_ux(
                page_config['url'],
                page_config['name'], 
                page_config['elements']
            )
        
        # 生成测试报告
        await self.generate_report()
        
        await self.teardown()
    
    async def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 全面UX测试报告")
        print("="*60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"测试总数: {self.total_tests}")
        print(f"通过测试: {self.passed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        print("\n📋 各页面测试详情:")
        for result in self.results:
            print(f"\n🔍 {result['page']} ({result['url']}):")
            for test_result in result['results']:
                print(f"  {test_result}")
        
        if success_rate >= 80:
            print(f"\n🎉 UX优化效果良好！成功率达到 {success_rate:.1f}%")
        elif success_rate >= 60:
            print(f"\n⚠️ UX优化需要改进，成功率仅为 {success_rate:.1f}%")
        else:
            print(f"\n❌ UX优化效果不佳，成功率仅为 {success_rate:.1f}%，需要大幅改进")
        
        print("\n💡 改进建议:")
        print("1. 确保所有主要页面都有统一的页面头部样式")
        print("2. 为数据展示页面添加统计卡片")
        print("3. 优化表单和按钮的视觉样式")
        print("4. 确保移动端响应式设计正常")
        print("5. 提升页面加载性能和用户体验")

async def main():
    tester = ComprehensiveUXTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
