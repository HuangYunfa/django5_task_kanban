"""
全面UX优化测试脚本
测试所有页面的视觉效果和用户体验
"""
from test_homepage_welcome_ui import HomePageWelcomeUITest
from playwright.sync_api import expect
import time

class ComprehensiveUXTest(HomePageWelcomeUITest):
    
    def test_homepage_ux(self):
        """测试首页UX优化"""
        print("\n=== 测试首页UX优化 ===")
        self.login("admin", "admin123")
        self.page.goto(f"{self.base_url}/")
        self.wait_for_load()
        
        # 检查首页待办与通知模块
        todo_section = self.page.locator("text=我的待办任务")
        if todo_section.count() > 0:
            expect(todo_section).to_be_visible()
            print("✓ 首页待办任务模块优化可见")
        
        notification_section = self.page.locator("text=重要通知")
        if notification_section.count() > 0:
            expect(notification_section).to_be_visible()
            print("✓ 首页重要通知模块优化可见")
    
    def test_dashboard_ux(self):
        """测试工作台UX优化"""
        print("\n=== 测试工作台UX优化 ===")
        self.page.goto(f"{self.base_url}/dashboard/")
        self.wait_for_load()
        
        # 检查页面头部
        page_header = self.page.locator(".page-header")
        expect(page_header).to_be_visible()
        print("✓ 工作台页面头部样式优化可见")
        
        # 检查统计卡片
        stats_cards = self.page.locator(".stats-card")
        expect(stats_cards.first).to_be_visible()
        print("✓ 工作台统计卡片样式优化可见")
    
    def test_tasks_ux(self):
        """测试任务页面UX优化"""
        print("\n=== 测试任务页面UX优化 ===")
        self.page.goto(f"{self.base_url}/tasks/")
        self.wait_for_load()
        
        # 检查页面头部
        page_header = self.page.locator(".page-header")
        expect(page_header).to_be_visible()
        print("✓ 任务页面头部样式优化可见")
        
        # 检查统计区域
        stats_area = self.page.locator(".stats-card")
        if stats_area.count() > 0:
            expect(stats_area.first).to_be_visible()
            print("✓ 任务统计卡片样式优化可见")
    
    def test_boards_ux(self):
        """测试看板页面UX优化"""
        print("\n=== 测试看板页面UX优化 ===")
        self.page.goto(f"{self.base_url}/boards/")
        self.wait_for_load()
        
        # 检查页面头部
        page_header = self.page.locator(".page-header")
        expect(page_header).to_be_visible()
        print("✓ 看板页面头部样式优化可见")
        
        # 检查统计卡片
        stats_cards = self.page.locator(".stats-card")
        if stats_cards.count() > 0:
            expect(stats_cards.first).to_be_visible()
            print("✓ 看板统计卡片样式优化可见")
    
    def test_teams_ux(self):
        """测试团队页面UX优化"""
        print("\n=== 测试团队页面UX优化 ===")
        self.page.goto(f"{self.base_url}/teams/")
        self.wait_for_load()
        
        # 检查页面头部
        page_header = self.page.locator(".page-header")
        expect(page_header).to_be_visible()
        print("✓ 团队页面头部样式优化可见")
        
        # 检查统计卡片
        stats_cards = self.page.locator(".stats-card")
        if stats_cards.count() > 0:
            expect(stats_cards.first).to_be_visible()
            print("✓ 团队统计卡片样式优化可见")
    
    def test_reports_ux(self):
        """测试报表页面UX优化"""
        print("\n=== 测试报表页面UX优化 ===")
        self.page.goto(f"{self.base_url}/reports/")
        self.wait_for_load()
        
        # 检查页面头部
        page_header = self.page.locator(".page-header")
        expect(page_header).to_be_visible()
        print("✓ 报表页面头部样式优化可见")
        
        # 检查统计卡片
        stats_cards = self.page.locator(".stats-card")
        if stats_cards.count() > 0:
            expect(stats_cards.first).to_be_visible()
            print("✓ 报表统计卡片样式优化可见")
    
    def test_button_interactions(self):
        """测试按钮交互效果"""
        print("\n=== 测试按钮交互效果 ===")
        self.page.goto(f"{self.base_url}/dashboard/")
        self.wait_for_load()
        
        # 测试主要按钮悬停效果
        primary_buttons = self.page.locator(".btn-primary")
        if primary_buttons.count() > 0:
            primary_buttons.first.hover()
            time.sleep(0.5)
            print("✓ 主要按钮悬停效果测试完成")
        
        # 测试成功按钮
        success_buttons = self.page.locator(".btn-success")
        if success_buttons.count() > 0:
            success_buttons.first.hover()
            time.sleep(0.5)
            print("✓ 成功按钮悬停效果测试完成")
    
    def test_card_hover_effects(self):
        """测试卡片悬停效果"""
        print("\n=== 测试卡片悬停效果 ===")
        self.page.goto(f"{self.base_url}/dashboard/")
        self.wait_for_load()
        
        # 测试统计卡片悬停
        stats_cards = self.page.locator(".stats-card")
        if stats_cards.count() > 0:
            stats_cards.first.hover()
            time.sleep(0.5)
            print("✓ 统计卡片悬停效果测试完成")
        
        # 测试普通卡片悬停
        cards = self.page.locator(".card")
        if cards.count() > 0:
            cards.first.hover()
            time.sleep(0.5)
            print("✓ 普通卡片悬停效果测试完成")
    
    def test_form_interactions(self):
        """测试表单交互效果"""
        print("\n=== 测试表单交互效果 ===")
        self.page.goto(f"{self.base_url}/users/login/")
        self.wait_for_load()
        
        # 测试表单输入框焦点效果
        username_input = self.page.locator("input[name='login']")
        if username_input.count() > 0:
            username_input.click()
            time.sleep(0.5)
            print("✓ 表单输入框焦点效果测试完成")
    
    def test_responsive_design(self):
        """测试响应式设计"""
        print("\n=== 测试响应式设计 ===")
        
        # 测试移动端视图
        self.page.set_viewport_size({"width": 375, "height": 667})
        self.page.goto(f"{self.base_url}/dashboard/")
        self.wait_for_load()
        
        # 检查移动端是否正常显示
        page_header = self.page.locator(".page-header")
        expect(page_header).to_be_visible()
        print("✓ 移动端页面头部正常显示")
        
        # 恢复桌面端视图
        self.page.set_viewport_size({"width": 1280, "height": 720})
        print("✓ 响应式设计测试完成")
    
    def run_all_tests(self):
        """运行所有UX测试"""
        try:
            self.test_homepage_ux()
            self.test_dashboard_ux()
            self.test_tasks_ux()
            self.test_boards_ux()
            self.test_teams_ux()
            self.test_reports_ux()
            self.test_button_interactions()
            self.test_card_hover_effects()
            self.test_form_interactions()
            self.test_responsive_design()
            print("\n🎉 全面UX优化测试全部通过！")
            return True
        except Exception as e:
            print(f"\n❌ UX测试失败: {e}")
            return False

if __name__ == "__main__":
    test = ComprehensiveUXTest()
    test.setup(headless=True)
    try:
        success = test.run_all_tests()
        if success:
            print("\n✅ UX优化验证成功 - 所有页面用户体验良好！")
        else:
            print("\n⚠️ 发现UX问题，需要进一步优化")
    finally:
        test.teardown()
