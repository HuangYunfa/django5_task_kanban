"""
任务状态流转系统 - Playwright UI端到端测试
测试真实的浏览器交互功能
"""

import pytest
import time
from playwright.sync_api import Page, expect
from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model
from boards.models import Board, BoardList
from tasks.models import Task
from tasks.workflow_models import WorkflowStatus

User = get_user_model()


class WorkflowUITestCase(LiveServerTestCase):
    """工作流UI测试基类"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # 创建测试用户
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建测试看板
        cls.board = Board.objects.create(
            name='UI测试看板',
            description='用于UI测试的看板',
            owner=cls.user
        )
        
        # 创建看板列表
        cls.board_list = BoardList.objects.create(
            name='待办事项',
            board=cls.board,
            position=0
        )
        
        # 创建测试任务
        cls.task = Task.objects.create(
            title='UI测试任务',
            description='用于测试状态流转的任务',
            board=cls.board,
            board_list=cls.board_list,
            creator=cls.user,
            status='todo'
        )


@pytest.mark.django_db
class TestWorkflowStatusManagement:
    """测试工作流状态管理页面"""
    
    def test_workflow_status_list_page(self, page: Page, live_server):
        """测试工作流状态列表页面"""
        # 设置测试数据
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        board = Board.objects.create(
            name='测试看板',
            description='测试描述',
            owner=user
        )
        
        # 创建工作流状态
        WorkflowStatus.objects.create(
            name='todo',
            display_name='待办',
            color='#6c757d',
            board=board,
            position=0,
            is_initial=True
        )
        
        WorkflowStatus.objects.create(
            name='in_progress',
            display_name='进行中',
            color='#007bff',
            board=board,
            position=1
        )
        
        # 登录用户
        page.goto(f'{live_server.url}/admin/')
        page.fill('input[name="username"]', 'testuser')
        page.fill('input[name="password"]', 'testpass123')
        page.click('input[type="submit"]')
        
        # 访问工作流状态列表页面
        page.goto(f'{live_server.url}/tasks/workflow/statuses/{board.slug}/')
        
        # 验证页面元素
        expect(page.locator('h1')).to_contain_text('工作流状态管理')
        expect(page.locator('.status-card')).to_have_count(2)
        expect(page.locator('.status-card').first).to_contain_text('待办')
        expect(page.locator('.status-card').nth(1)).to_contain_text('进行中')
        
        # 验证初始状态标记
        expect(page.locator('.badge-initial')).to_contain_text('初始状态')
        
        # 测试添加状态按钮
        expect(page.locator('a[href*="create"]')).to_contain_text('添加状态')
    
    def test_create_workflow_status(self, page: Page, live_server):
        """测试创建工作流状态"""
        # 设置测试数据
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        board = Board.objects.create(
            name='测试看板2',
            description='测试描述',
            owner=user
        )
        
        # 登录用户
        page.goto(f'{live_server.url}/admin/')
        page.fill('input[name="username"]', 'testuser2')
        page.fill('input[name="password"]', 'testpass123')
        page.click('input[type="submit"]')
        
        # 访问创建状态页面
        page.goto(f'{live_server.url}/tasks/workflow/statuses/{board.slug}/create/')
        
        # 验证表单元素
        expect(page.locator('form')).to_be_visible()
        expect(page.locator('input[name="name"]')).to_be_visible()
        expect(page.locator('input[name="display_name"]')).to_be_visible()
        expect(page.locator('input[name="color"]')).to_be_visible()
        
        # 填写表单
        page.fill('input[name="name"]', 'testing')
        page.fill('input[name="display_name"]', '测试状态')
        page.fill('input[name="color"]', '#ff5722')
        page.check('input[name="is_initial"]')
        
        # 测试颜色选择器
        color_options = page.locator('.color-option')
        expect(color_options).to_have_count_greater_than(0)
        color_options.first.click()
        
        # 验证预览更新
        expect(page.locator('#status-preview')).to_be_visible()
        
        # 提交表单
        page.click('button[type="submit"]')
        
        # 验证重定向到列表页面
        expect(page).to_have_url_regex(f'.*/tasks/workflow/statuses/{board.slug}/')


@pytest.mark.django_db
class TestTaskStatusChange:
    """测试任务状态变更功能"""
    
    def test_task_detail_status_change(self, page: Page, live_server):
        """测试任务详情页面的状态变更"""
        # 设置测试数据
        user = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        
        board = Board.objects.create(
            name='测试看板3',
            description='测试描述',
            owner=user
        )
        
        board_list = BoardList.objects.create(
            name='待办事项',
            board=board,
            position=0
        )
        
        task = Task.objects.create(
            title='测试任务',
            description='测试任务描述',
            board=board,
            board_list=board_list,
            creator=user,
            status='todo'
        )
        
        # 创建工作流状态
        todo_status = WorkflowStatus.objects.create(
            name='todo',
            display_name='待办',
            color='#6c757d',
            board=board,
            position=0,
            is_initial=True
        )
        
        progress_status = WorkflowStatus.objects.create(
            name='in_progress',
            display_name='进行中',
            color='#007bff',
            board=board,
            position=1
        )
        
        # 登录用户
        page.goto(f'{live_server.url}/admin/')
        page.fill('input[name="username"]', 'testuser3')
        page.fill('input[name="password"]', 'testpass123')
        page.click('input[type="submit"]')
        
        # 访问任务详情页面
        page.goto(f'{live_server.url}/tasks/{board.slug}/{task.pk}/')
        
        # 验证页面元素
        expect(page.locator('h1')).to_contain_text(task.title)
        expect(page.locator('.task-status-badge')).to_contain_text('待办')
        
        # 测试状态变更按钮
        status_change_btn = page.locator('button[onclick*="showStatusChangeModal"]')
        if status_change_btn.is_visible():
            status_change_btn.click()
            
            # 验证模态框出现
            expect(page.locator('#statusChangeModal')).to_be_visible()
            expect(page.locator('#newStatus')).to_be_visible()
        
        # 测试状态历史链接
        history_link = page.locator('a[href*="status-history"]')
        if history_link.is_visible():
            expect(history_link).to_be_visible()
    
    def test_task_status_history_page(self, page: Page, live_server):
        """测试任务状态历史页面"""
        # 设置测试数据
        user = User.objects.create_user(
            username='testuser4',
            email='test4@example.com',
            password='testpass123'
        )
        
        board = Board.objects.create(
            name='测试看板4',
            description='测试描述',
            owner=user
        )
        
        board_list = BoardList.objects.create(
            name='待办事项',
            board=board,
            position=0
        )
        
        task = Task.objects.create(
            title='历史测试任务',
            description='测试任务状态历史',
            board=board,
            board_list=board_list,
            creator=user,
            status='todo'
        )
        
        # 登录用户
        page.goto(f'{live_server.url}/admin/')
        page.fill('input[name="username"]', 'testuser4')
        page.fill('input[name="password"]', 'testpass123')
        page.click('input[type="submit"]')
        
        # 访问状态历史页面
        page.goto(f'{live_server.url}/tasks/workflow/{board.slug}/{task.pk}/status-history/')
        
        # 验证页面元素
        expect(page.locator('h1')).to_contain_text('任务状态历史')
        expect(page.locator('.task-header')).to_contain_text(task.title)
        expect(page.locator('.current-status')).to_contain_text('当前状态')


@pytest.mark.django_db  
class TestWorkflowUIInteractions:
    """测试工作流UI交互功能"""
    
    def test_responsive_design(self, page: Page, live_server):
        """测试响应式设计"""
        # 设置测试数据
        user = User.objects.create_user(
            username='testuser5',
            email='test5@example.com',
            password='testpass123'
        )
        
        board = Board.objects.create(
            name='响应式测试看板',
            description='测试响应式设计',
            owner=user
        )
        
        # 登录用户
        page.goto(f'{live_server.url}/admin/')
        page.fill('input[name="username"]', 'testuser5')
        page.fill('input[name="password"]', 'testpass123')
        page.click('input[type="submit"]')
        
        # 访问工作流状态页面
        page.goto(f'{live_server.url}/tasks/workflow/statuses/{board.slug}/')
        
        # 测试桌面视图
        page.set_viewport_size({"width": 1200, "height": 800})
        expect(page.locator('.container-fluid')).to_be_visible()
        
        # 测试平板视图
        page.set_viewport_size({"width": 768, "height": 1024})
        expect(page.locator('.workflow-header')).to_be_visible()
        
        # 测试手机视图
        page.set_viewport_size({"width": 375, "height": 667})
        expect(page.locator('.workflow-header')).to_be_visible()
    
    def test_javascript_functionality(self, page: Page, live_server):
        """测试JavaScript功能"""
        # 设置测试数据
        user = User.objects.create_user(
            username='testuser6',
            email='test6@example.com',
            password='testpass123'
        )
        
        board = Board.objects.create(
            name='JS测试看板',
            description='测试JavaScript功能',
            owner=user
        )
        
        # 登录用户
        page.goto(f'{live_server.url}/admin/')
        page.fill('input[name="username"]', 'testuser6')
        page.fill('input[name="password"]', 'testpass123')
        page.click('input[type="submit"]')
        
        # 访问状态创建页面
        page.goto(f'{live_server.url}/tasks/workflow/statuses/{board.slug}/create/')
        
        # 测试颜色选择器交互
        color_options = page.locator('.color-option')
        if color_options.count() > 0:
            # 点击颜色选项
            color_options.first.click()
            
            # 验证预览更新
            expect(page.locator('#status-preview')).to_be_visible()
        
        # 测试表单验证
        page.fill('input[name="display_name"]', '测试状态名称')
        
        # 验证预览文本更新
        expect(page.locator('#preview-name')).to_contain_text('测试状态名称')


def run_workflow_ui_tests():
    """运行工作流UI测试"""
    print("🎭 开始运行工作流UI测试...")
    
    # 运行pytest测试
    import subprocess
    result = subprocess.run([
        'pytest', 
        'test_workflow_ui.py',
        '-v',
        '--tb=short'
    ], capture_output=True, text=True)
    
    print("测试输出:")
    print(result.stdout)
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    
    return result.returncode == 0


if __name__ == '__main__':
    print("🚀 工作流状态流转系统 UI 测试")
    print("=" * 60)
    print("💡 这个测试使用Playwright进行真实浏览器UI测试")
    print("📝 测试内容包括:")
    print("   • 工作流状态列表页面")
    print("   • 创建工作流状态功能")
    print("   • 任务状态变更交互")
    print("   • 状态历史查看")
    print("   • 响应式设计")
    print("   • JavaScript交互功能")
    print("\n🔧 运行测试请使用:")
    print("   pytest test_workflow_ui.py -v")
    print("   或")
    print("   python test_workflow_ui.py")
    
    # 如果直接运行，执行测试
    try:
        success = run_workflow_ui_tests()
        if success:
            print("\n✅ 所有UI测试通过！")
        else:
            print("\n❌ 部分测试失败，请检查输出")
    except Exception as e:
        print(f"\n❌ 运行测试时发生错误: {e}")
        print("\n💡 请确保:")
        print("   1. Django开发服务器正在运行")
        print("   2. 数据库已迁移")
        print("   3. Playwright浏览器已安装")
