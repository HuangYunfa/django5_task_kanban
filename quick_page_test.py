#!/usr/bin/env python3
"""
快速页面访问测试脚本 - 验证所有主要页面是否正常
"""

import asyncio
from playwright.async_api import async_playwright

class QuickPageTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.results = []
        
    async def setup_browser(self):
        """设置浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
    
    async def teardown(self):
        """清理资源"""
        await self.browser.close()
        await self.playwright.stop()
    
    async def login(self):
        """用户登录"""
        try:
            await self.page.goto(f"{self.base_url}/accounts/login/")
            await self.page.fill('input[name="login"]', 'project_manager')
            await self.page.fill('input[name="password"]', 'demo123456')
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_url(f"{self.base_url}/dashboard/", timeout=10000)
            print("✅ 登录成功")
            return True
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return False
    
    async def test_page(self, url, name):
        """测试单个页面"""
        try:
            print(f"测试 {name}: {url}")
            await self.page.goto(f"{self.base_url}{url}", timeout=15000)
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # 检查页面标题
            title = await self.page.title()
            
            # 检查是否有错误
            if any(error in title.lower() for error in ['error', '404', '500', 'not found']):
                print(f"  ❌ {name} - 页面错误: {title}")
                return False
                
            # 检查页面内容是否有错误信息
            content = await self.page.content()
            if 'NoReverseMatch' in content or 'TemplateDoesNotExist' in content:
                print(f"  ❌ {name} - 模板或URL错误")
                return False
                
            print(f"  ✅ {name} - 正常 ({title})")
            return True
            
        except Exception as e:
            print(f"  ❌ {name} - 访问失败: {e}")
            return False
    
    async def run_test(self):
        """运行测试"""
        print("🔍 开始快速页面访问测试...")
        print("="*60)
        
        await self.setup_browser()
        
        # 登录
        if not await self.login():
            await self.teardown()
            return
        
        # 测试页面列表
        test_pages = [
            ('/', '首页'),
            ('/dashboard/', '工作台'),
            ('/boards/', '看板列表'),
            ('/tasks/', '任务列表'),
            ('/teams/', '团队列表'),
            ('/reports/', '报表页面'),
            ('/users/profile/', '个人资料'),
            ('/users/settings/', '用户设置'),
            ('/api/', 'API根页面'),
            ('/api/docs/', 'API文档'),
            ('/notifications/preferences/', '通知设置'),
        ]
        
        passed = 0
        total = len(test_pages)
        
        print("\n📋 测试结果:")
        for url, name in test_pages:
            if await self.test_page(url, name):
                passed += 1
        
        # 输出总结
        print("\n" + "="*60)
        print("📊 测试总结")
        print("="*60)
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"总页面数: {total}")
        print(f"正常页面: {passed}")
        print(f"问题页面: {total - passed}")
        print(f"成功率: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 所有页面都正常访问！")
        elif success_rate >= 80:
            print(f"\n✅ 大部分页面正常，成功率 {success_rate:.1f}%")
        else:
            print(f"\n⚠️ 需要修复更多页面，成功率仅 {success_rate:.1f}%")
        
        await self.teardown()

async def main():
    tester = QuickPageTester()
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())
