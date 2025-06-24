"""
测试报表分析模块的UI功能
使用Playwright自动化测试报表页面
"""
import pytest
import time
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import LiveServerTestCase
from playwright.sync_api import sync_playwright

from teams.models import Team, TeamMembership
from boards.models import Board, BoardMember, BoardList
from tasks.models import Task
from reports.models import Report

User = get_user_model()


class ReportsUITest(LiveServerTestCase):
    """报表UI测试类"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # 创建测试团队和看板
        self.team = Team.objects.create(
            name='测试团队',
            description='用于测试的团队',
            created_by=self.user
        )
        
        TeamMembership.objects.create(
            team=self.team,
            user=self.user,
            role='admin',
            status='active'
        )
        
        self.board = Board.objects.create(
            name='测试看板',
            description='用于测试的看板',
            team=self.team,
            owner=self.user
        )
        
        BoardMember.objects.create(
            board=self.board,
            user=self.user,
            is_active=True
        )
        
        # 创建看板列表
        self.board_list = BoardList.objects.create(
            board=self.board,
            name='待办列表',
            position=0
        )
        
        # 创建测试任务
        statuses = ['todo', 'in_progress', 'done']
        priorities = ['low', 'medium', 'high']
        
        for i in range(15):
            task = Task.objects.create(
                title=f'测试任务 {i+1}',
                description=f'用于测试的任务描述 {i+1}',
                board=self.board,
                board_list=self.board_list,
                status=statuses[i % 3],
                priority=priorities[i % 3],
                creator=self.user
            )
            task.assignees.add(self.user)
    
    def test_reports_page_rendering(self):
        """测试报表页面渲染"""
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # 登录
                login_url = self.live_server_url + '/accounts/login/'
                page.goto(login_url)
                
                # 填写登录表单
                page.fill('input[name="login"]', 'testuser')
                page.fill('input[name="password"]', 'testpassword')
                page.click('button[type="submit"]')
                
                # 等待重定向完成
                page.wait_for_load_state('networkidle')
                
                # 访问报表页面
                reports_url = self.live_server_url + reverse('reports:index')
                page.goto(reports_url)
                
                # 验证页面标题
                assert '数据报表' in page.title()
                
                # 验证页面内容
                assert page.is_visible('text=数据报表')
                assert page.is_visible('text=任务完成趋势')
                assert page.is_visible('text=任务状态分布')
                assert page.is_visible('text=用户工作负载')
                
                # 验证图表是否渲染
                assert page.is_visible('canvas#taskCompletionChart')
                assert page.is_visible('canvas#statusDistributionChart')
                assert page.is_visible('canvas#userWorkloadChart')
                
                # 等待图表加载完成
                page.wait_for_timeout(1000)
                
                # 测试筛选功能
                page.select_option('select[name="time_range"]', '7days')
                page.click('button:has-text("应用筛选")')
                
                # 等待页面刷新
                page.wait_for_load_state('networkidle')
                
                # 验证筛选后图表仍然存在
                assert page.is_visible('canvas#taskCompletionChart')
                
                # 测试导出功能
                with page.expect_download() as download_info:
                    page.evaluate('exportReport()')
                
                download = download_info.value
                assert download.suggested_filename.endswith('.xlsx')
                
                # 截图保存到标准位置
                screenshot_path = "tests/screenshots/reports_page_rendering.png"
                page.screenshot(path=screenshot_path)
                
            finally:
                browser.close()
    
    def test_chart_interactions(self):
        """测试图表交互功能"""
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # 登录
                login_url = self.live_server_url + '/accounts/login/'
                page.goto(login_url)
                
                page.fill('input[name="login"]', 'testuser')
                page.fill('input[name="password"]', 'testpassword')
                page.click('button[type="submit"]')
                
                # 访问报表页面
                reports_url = self.live_server_url + reverse('reports:index')
                page.goto(reports_url)
                
                # 等待图表加载
                page.wait_for_selector('canvas#taskCompletionChart', state='visible')
                page.wait_for_timeout(1000)
                
                # 测试图表悬停交互
                # 获取图表元素的位置和大小
                chart_box = page.query_selector('canvas#taskCompletionChart').bounding_box()
                
                # 模拟在图表上移动鼠标
                page.mouse.move(
                    chart_box['x'] + chart_box['width'] / 2,
                    chart_box['y'] + chart_box['height'] / 2
                )
                
                # 等待一下看是否有提示框出现
                page.wait_for_timeout(500)
                
                # 测试饼图交互
                pie_chart_box = page.query_selector('canvas#statusDistributionChart').bounding_box()
                
                # 点击饼图的一个扇区
                page.mouse.click(
                    pie_chart_box['x'] + pie_chart_box['width'] / 4,
                    pie_chart_box['y'] + pie_chart_box['height'] / 2
                )
                
                # 等待交互响应
                page.wait_for_timeout(500)
                
                # 截图保存到标准位置
                screenshot_path = "tests/screenshots/chart_interactions.png"
                page.screenshot(path=screenshot_path)
                
            finally:
                browser.close()
                
    def test_filters_and_exports(self):
        """测试筛选和导出功能"""
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # 登录
                login_url = self.live_server_url + '/accounts/login/'
                page.goto(login_url)
                
                # 填写登录表单
                page.fill('input[name="login"]', 'testuser')
                page.fill('input[name="password"]', 'testpassword')
                page.click('button[type="submit"]')
                
                # 等待重定向完成
                page.wait_for_load_state('networkidle')
                
                # 访问报表页面
                reports_url = self.live_server_url + reverse('reports:index')
                page.goto(reports_url)
                
                # 等待页面加载完成
                page.wait_for_selector('select[name="time_range"]', state='visible')
                  # 测试不同的筛选选项
                filter_options = ['7days', '30days', '3months', '6months', '1year']
                
                for option in filter_options:
                    # 选择筛选选项
                    page.select_option('#timeRangeSelect', option)
                    page.click('button[type="submit"].btn-primary')
                    
                    # 等待页面刷新和图表加载
                    page.wait_for_selector('.chart-container', state='visible')
                    page.wait_for_load_state('networkidle')
                    
                    # 验证图表仍然存在
                    assert page.is_visible('canvas#taskCompletionChart')
                    assert page.is_visible('canvas#statusDistributionChart')
                    assert page.is_visible('canvas#userWorkloadChart')
                    
                    # 短暂等待确保图表已更新
                    page.wait_for_timeout(1000)
                
                # 测试导出功能
                with page.expect_download() as download_info:
                    page.evaluate('exportReport()')
                
                download = download_info.value
                assert download.suggested_filename.endswith('.xlsx')
                
                # 截图保存到标准位置
                screenshot_path = "tests/screenshots/filters_and_exports.png"
                page.screenshot(path=screenshot_path)
                
            finally:
                browser.close()
