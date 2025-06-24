import pytest
import asyncio
from asgiref.sync_to_async import sync_to_async
from playwright.async_api import Page, expect
from django.urls import reverse
from django.contrib.auth import get_user_model
from taskkanban.boards.models import Board, BoardList
from taskkanban.teams.models import Team
from taskkanban.tasks.models import Task
from datetime import datetime, timedelta
from typing import List

pytestmark = pytest.mark.asyncio

User = get_user_model()

# 封装数据库操作
@sync_to_async
def create_test_user() -> User:
    return User.objects.create_user(
        username='test_reports_user',
        email='test_reports@example.com',
        password='test_reports_pass'
    )

@sync_to_async
def create_test_team(user: User) -> Team:
    return Team.objects.create(
        name='测试团队',
        owner=user,
        description='用于报表测试的团队'
    )

@sync_to_async
def create_test_board(user: User, team: Team) -> Board:
    return Board.objects.create(
        name='测试看板',
        owner=user,
        team=team,
        template='kanban',
        visibility='team'
    )

@sync_to_async
def create_board_lists(board: Board) -> List[BoardList]:
    return [
        BoardList.objects.create(name='待处理', board=board, position=0),
        BoardList.objects.create(name='进行中', board=board, position=1),
        BoardList.objects.create(name='已完成', board=board, position=2, is_done_list=True)
    ]

@pytest.fixture(scope='function')
async def test_data(django_db_setup, django_db_blocker):
    """创建测试数据"""
    async with django_db_blocker.unblock():
        user = await create_test_user()
        team = await create_test_team(user)
        board = await create_test_board(user, team)
        lists = await create_board_lists(board)
          # 创建测试任务
        @sync_to_async
        def create_test_tasks():
            tasks = []
            for i in range(5):
                task = Task.objects.create(
                    title=f'测试任务 {i+1}',
                    description=f'测试任务描述 {i+1}',
                    list=lists[i % 3],
                    creator=user,
                    assignee=user,
                    due_date=datetime.now() + timedelta(days=i)
                )
                tasks.append(task)
            return tasks
        
        tasks = await create_test_tasks()
        
        return {
            'user': user,
            'team': team,
            'board': board,
            'lists': lists,
            'tasks': tasks
        }

@pytest.mark.django_db
class TestReportsAnalysis:
    """报表分析页面测试类"""
    
    async def test_reports_page_access(self, page: Page, live_server, test_data):
        """测试报表页面访问"""
        # 登录
        await page.goto(f"{live_server.url}/accounts/login/")
        await page.fill('input[name="username"]', 'test_reports_user')
        await page.fill('input[name="password"]', 'test_reports_pass')
        await page.click('button[type="submit"]')
        
        # 访问报表页面
        reports_url = f"{live_server.url}/reports/"
        await page.goto(reports_url)
        
        # 验证页面标题
        expect(page.locator('h1')).to_contain_text('报表分析')
        
        # 验证页面上是否有图表容器
        expect(page.locator('#task-status-chart')).to_be_visible()
        expect(page.locator('#task-priority-chart')).to_be_visible()
        expect(page.locator('#task-timeline-chart')).to_be_visible()
    
    async def test_report_filters(self, page: Page, live_server, test_data):
        """测试报表筛选功能"""
        # 登录
        await page.goto(f"{live_server.url}/accounts/login/")
        await page.fill('input[name="username"]', 'test_reports_user')
        await page.fill('input[name="password"]', 'test_reports_pass')
        await page.click('button[type="submit"]')
        
        # 访问报表页面
        await page.goto(f"{live_server.url}/reports/")
        
        # 测试看板筛选
        board_select = page.locator('select[name="board"]')
        await board_select.select_option(value=str(test_data['board'].id))
        await page.click('button:text("应用筛选")')
        
        # 验证图表更新
        expect(page.locator('#task-status-chart')).to_be_visible()
        # 等待图表重新渲染
        await page.wait_for_timeout(1000)
        
        # 测试日期范围筛选
        await page.fill('input[name="date_from"]', datetime.now().strftime('%Y-%m-%d'))
        await page.fill('input[name="date_to"]', (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'))
        await page.click('button:text("应用筛选")')
        await page.wait_for_timeout(1000)
    
    async def test_report_exports(self, page: Page, live_server, test_data):
        """测试报表导出功能"""
        # 登录
        await page.goto(f"{live_server.url}/accounts/login/")
        await page.fill('input[name="username"]', 'test_reports_user')
        await page.fill('input[name="password"]', 'test_reports_pass')
        await page.click('button[type="submit"]')
        
        # 访问报表页面
        await page.goto(f"{live_server.url}/reports/")
        
        # 测试Excel导出
        with page.expect_download() as download_info:
            await page.click('button:text("导出Excel")')
        download = await download_info.value
        
        # 验证下载的文件名
        assert 'task_report' in download.suggested_filename
        assert download.suggested_filename.endswith('.xlsx')
        
        # 测试CSV导出
        with page.expect_download() as download_info:
            await page.click('button:text("导出CSV")')
        download = await download_info.value
        assert download.suggested_filename.endswith('.csv')
    
    async def test_chart_interactions(self, page: Page, live_server, test_data):
        """测试图表交互功能"""
        # 登录
        await page.goto(f"{live_server.url}/accounts/login/")
        await page.fill('input[name="username"]', 'test_reports_user')
        await page.fill('input[name="password"]', 'test_reports_pass')
        await page.click('button[type="submit"]')
        
        # 访问报表页面
        await page.goto(f"{live_server.url}/reports/")
        
        # 验证图表切换按钮
        view_buttons = [
            ('button:text("状态分布")', '#task-status-chart'),
            ('button:text("优先级分布")', '#task-priority-chart'),
            ('button:text("时间线")', '#task-timeline-chart'),
        ]
        
        for button_selector, chart_selector in view_buttons:
            await page.click(button_selector)
            await page.wait_for_timeout(500)  # 等待图表切换动画
            expect(page.locator(chart_selector)).to_be_visible()
        
        # 测试图表图例点击
        status_chart = page.locator('#task-status-chart')
        await status_chart.hover()  # 确保图表完全加载
        
        # 点击图例项并验证图表更新
        legend_items = page.locator('.echarts-legend-item')
        for i in range(await legend_items.count()):
            await legend_items.nth(i).click()
            await page.wait_for_timeout(300)  # 等待图表更新
    
    async def test_data_refresh(self, page: Page, live_server, test_data):
        """测试数据刷新功能"""
        # 登录
        await page.goto(f"{live_server.url}/accounts/login/")
        await page.fill('input[name="username"]', 'test_reports_user')
        await page.fill('input[name="password"]', 'test_reports_pass')
        await page.click('button[type="submit"]')
        
        # 访问报表页面
        await page.goto(f"{live_server.url}/reports/")
        
        # 点击刷新按钮
        await page.click('button:text("刷新数据")')
        await page.wait_for_timeout(1000)  # 等待数据刷新
        
        # 验证加载指示器显示后隐藏
        expect(page.locator('.loading-indicator')).not_to_be_visible()
        
        # 验证图表已更新
        charts = ['#task-status-chart', '#task-priority-chart', '#task-timeline-chart']
        for chart_id in charts:
            expect(page.locator(chart_id)).to_be_visible()
    
    async def test_responsive_layout(self, page: Page, live_server, test_data):
        """测试响应式布局"""
        # 登录
        await page.goto(f"{live_server.url}/accounts/login/")
        await page.fill('input[name="username"]', 'test_reports_user')
        await page.fill('input[name="password"]', 'test_reports_pass')
        await page.click('button[type="submit"]')
        
        # 访问报表页面并测试不同屏幕尺寸
        await page.goto(f"{live_server.url}/reports/")
        
        # 桌面布局
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        expect(page.locator('.reports-grid')).to_have_css('grid-template-columns', 'repeat(auto-fit, minmax(300px, 1fr))')
        
        # 平板布局
        await page.set_viewport_size({'width': 768, 'height': 1024})
        await page.wait_for_timeout(500)
        expect(page.locator('.reports-grid')).to_be_visible()
        
        # 手机布局
        await page.set_viewport_size({'width': 375, 'height': 812})
        await page.wait_for_timeout(500)
        expect(page.locator('.reports-grid')).to_be_visible()
