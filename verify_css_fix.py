#!/usr/bin/env python3
"""
验证CSS样式泄漏修复效果的测试脚本
检查指定页面是否还有CSS代码泄漏到页面内容中
"""

import asyncio
from playwright.async_api import async_playwright

class CSSLeakageVerifier:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        
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
            await self.page.goto(f"{self.base_url}/accounts/login/")
            await self.page.fill('input[name="login"]', 'project_manager')
            await self.page.fill('input[name="password"]', 'demo123456')
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_url(f"{self.base_url}/dashboard/", timeout=10000)
            print("✅ 登录成功")
            return True
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return False    async def check_css_leakage(self, url, page_name):
        """检查页面是否有CSS样式泄漏"""
        print(f"\n🔍 检查{page_name} ({url})")
        
        try:
            await self.page.goto(f"{self.base_url}{url}", timeout=15000)
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # 获取页面内容
            page_content = await self.page.content()
            
            # 检查是否有CSS相关的泄漏内容
            css_indicators = [
                'background:',
                'border-radius:',
                'box-shadow:',
                'transform:',
                'transition:',
                'padding:',
                'margin:',
                '.stat-card',
                '.search-section',
                '.create-board-btn',
                '.board-stats',
                '.status-todo',
                '.assignee-avatar'
            ]
            
            leaked_css = []
            for indicator in css_indicators:
                # 检查CSS是否出现在HTML内容中（排除<style>标签内的内容）
                import re
                # 移除所有<style>...</style>标签内的内容
                content_without_styles = re.sub(r'<style[^>]*>.*?</style>', '', page_content, flags=re.DOTALL)
                # 移除所有CSS文件引用
                content_without_styles = re.sub(r'<link[^>]*stylesheet[^>]*>', '', content_without_styles)
                # 移除所有<head>标签内容，因为CSS通常在head中
                content_without_styles = re.sub(r'<head[^>]*>.*?</head>', '', content_without_styles, flags=re.DOTALL)
                
                if indicator in content_without_styles:
                    # 找到具体位置上下文
                    lines = content_without_styles.split('\n')
                    for i, line in enumerate(lines):
                        if indicator in line:
                            # 提供上下文行
                            start = max(0, i-2)
                            end = min(len(lines), i+3)
                            context = '\n'.join(lines[start:end])
                            leaked_css.append(f"{indicator} (行{i+1}): {line.strip()}")
                            print(f"    上下文:\n{context}")
                            break
            
            if leaked_css:
                print(f"  ❌ 发现CSS样式泄漏:")
                for leak in leaked_css:
                    print(f"    - {leak}")
                return False
            else:
                print(f"  ✅ 无CSS样式泄漏")
                return True
                
        except Exception as e:
            print(f"  ❌ 检查{page_name}页面失败: {e}")
            return False
    
    async def run_verification(self):
        """运行验证"""
        print("🎨 开始CSS样式泄漏修复验证...")
        print("="*60)
        
        await self.setup_browser()
        
        # 登录系统
        if not await self.login():
            print("❌ 登录失败，无法继续测试")
            await self.teardown()
            return
        
        # 检查各个页面
        test_pages = [
            ('/reports/', '报表分析'),
            ('/tasks/', '任务管理'),
            ('/boards/', '看板管理'),
            ('/', '首页'),
            ('/dashboard/', '工作台'),
            ('/teams/', '团队协作')
        ]
        
        passed_count = 0
        total_count = len(test_pages)
        
        for url, name in test_pages:
            if await self.check_css_leakage(url, name):
                passed_count += 1
        
        # 生成总结报告
        print("\n" + "="*60)
        print("📊 CSS样式泄漏修复验证报告")
        print("="*60)
        
        success_rate = (passed_count / total_count * 100) if total_count > 0 else 0
        
        print(f"总检查页面: {total_count}")
        print(f"修复成功页面: {passed_count}")
        print(f"修复成功率: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 优秀！所有页面的CSS样式泄漏问题都已修复")
        elif success_rate >= 80:
            print(f"\n⚠️  良好！大部分页面已修复，修复率为 {success_rate:.1f}%")
        else:
            print(f"\n❌ 需要继续改进！仍有页面存在CSS样式泄漏，修复率仅为 {success_rate:.1f}%")
        
        await self.teardown()

async def main():
    verifier = CSSLeakageVerifier()
    await verifier.run_verification()

if __name__ == "__main__":
    asyncio.run(main())
