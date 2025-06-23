#!/usr/bin/env python3
"""
全面的UX自动化测试脚本 - 使用正确的登录凭据
测试所有主要页面的UX优化效果
"""

import asyncio
from playwright.async_api import async_playwright

class FinalUXTester:
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
        """用户登录 - 使用提供的正确凭据"""
        try:
            await self.page.goto(f"{self.base_url}/accounts/login/")
            await self.page.fill('input[name="login"]', 'project_manager')
            await self.page.fill('input[name="password"]', 'demo123456')
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_url(f"{self.base_url}/dashboard/", timeout=10000)
            print("✅ 使用project_manager账户登录成功")
            return True
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return False
    
    async def test_page_elements(self, url, page_name, elements):
        """测试页面元素"""
        print(f"\n🔍 测试{page_name} ({url})")
        
        try:
            await self.page.goto(f"{self.base_url}{url}", timeout=15000)
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            page_results = []
            
            for element_name, selector in elements.items():
                self.total_tests += 1
                
                try:
                    if selector:
                        element = self.page.locator(selector)
                        await element.first.wait_for(state='visible', timeout=5000)
                        print(f"  ✓ {element_name}显示正常")
                        page_results.append(f"✓ {element_name}")
                        self.passed_tests += 1
                    else:
                        print(f"  ⚪ {element_name}跳过测试")
                        page_results.append(f"⚪ {element_name}")
                        
                except Exception:
                    print(f"  ❌ {element_name}未找到或不可见")
                    page_results.append(f"❌ {element_name}")
            
            self.results.append({
                'page': page_name,
                'url': url,
                'results': page_results
            })
            
        except Exception as e:
            print(f"  ❌ {page_name}页面访问失败: {e}")
            self.results.append({
                'page': page_name,
                'url': url,
                'results': [f"❌ 页面访问失败"]
            })
    
    async def run_comprehensive_test(self):
        """运行全面UX测试"""
        print("🎨 开始全面UX自动化测试...")
        print("="*60)
        
        await self.setup_browser()
        
        # 登录系统
        if not await self.login():
            print("❌ 登录失败，无法继续测试")
            await self.teardown()
            return
        
        # 定义所有要测试的页面
        test_pages = [
            {
                'url': '/',
                'name': '首页',
                'elements': {
                    '我的待办任务': '.todo-tasks, .my-todos, .pending-tasks',
                    '重要通知': '.notifications, .important-notifications',
                    '快速操作区': '.quick-actions, .action-buttons',
                    '统计概览': '.stats-overview, .dashboard-stats'
                }
            },
            {
                'url': '/dashboard/',
                'name': '工作台',
                'elements': {
                    '页面头部': '.page-header',
                    '统计卡片': '.stats-card',
                    '操作按钮': '.btn-primary, .btn',
                    '图表区域': '.chart-container, canvas'
                }
            },
            {
                'url': '/tasks/',
                'name': '任务管理',
                'elements': {
                    '页面头部': '.page-header',
                    '统计卡片': '.stats-card',
                    '任务列表': '.table, .task-list',
                    '新建按钮': '.btn-primary'
                }
            },
            {
                'url': '/teams/',
                'name': '团队协作',
                'elements': {
                    '页面头部': '.page-header',
                    '统计卡片': '.stats-card',
                    '团队卡片': '.card, .team-card',
                    '创建按钮': '.btn-primary'
                }
            },
            {
                'url': '/reports/',
                'name': '报表分析',
                'elements': {
                    '页面头部': '.page-header',
                    '统计卡片': '.stats-card',
                    '图表展示': '.chart-container, canvas',
                    '导出功能': '.btn, .export-btn'
                }
            },
            {
                'url': '/boards/',
                'name': '看板管理',
                'elements': {
                    '页面头部': '.page-header',
                    '统计卡片': '.stats-card',
                    '看板列表': '.card, .board-card',
                    '创建看板': '.btn-primary'
                }
            }
        ]
        
        # 测试所有页面
        for page_config in test_pages:
            await self.test_page_elements(
                page_config['url'],
                page_config['name'],
                page_config['elements']
            )
        
        # 生成最终报告
        await self.generate_final_report()
        await self.teardown()
    
    async def generate_final_report(self):
        """生成最终测试报告"""
        print("\n" + "="*60)
        print("📊 最终UX测试报告")
        print("="*60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"总测试项: {self.total_tests}")
        print(f"通过测试: {self.passed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        print("\n📋 详细结果:")
        for result in self.results:
            print(f"\n{result['page']} ({result['url']}):")
            for test_result in result['results']:
                print(f"  {test_result}")
        
        print(f"\n🎯 UX优化总结:")
        if success_rate >= 80:
            print(f"🎉 优秀！UX优化效果很好，成功率达到 {success_rate:.1f}%")
        elif success_rate >= 60:
            print(f"⚠️  良好！UX优化有待改进，成功率为 {success_rate:.1f}%")
        else:
            print(f"❌ 需要改进！UX优化效果不理想，成功率仅为 {success_rate:.1f}%")
        
        print("\n💡 改进建议:")
        print("1. 确保所有主页面都有统一的页面头部(.page-header)")
        print("2. 为数据展示页面添加统计卡片(.stats-card)")  
        print("3. 保持按钮和表单样式的一致性")
        print("4. 优化响应式设计和移动端适配")
        print("5. 提升整体用户体验和视觉层次")

async def main():
    tester = FinalUXTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
