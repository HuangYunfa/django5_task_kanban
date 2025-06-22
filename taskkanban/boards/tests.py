"""
看板应用测试
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Board, BoardList, BoardMember
from .forms import BoardCreateForm, BoardUpdateForm, BoardSearchForm
from teams.models import Team, TeamMembership
from tasks.models import Task

User = get_user_model()


class BoardModelTest(TestCase):
    """看板模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_board_creation(self):
        """测试看板创建"""
        board = Board.objects.create(
            name='测试看板',
            description='这是一个测试看板',
            owner=self.user,
            template='kanban'
        )
        
        self.assertEqual(board.name, '测试看板')
        self.assertEqual(board.owner, self.user)
        self.assertEqual(board.template, 'kanban')
        self.assertEqual(board.visibility, 'private')  # 默认值
        self.assertIsNotNone(board.slug)
        
    def test_board_str_representation(self):
        """测试看板字符串表示"""
        board = Board.objects.create(
            name='测试看板',
            owner=self.user
        )
        self.assertEqual(str(board), '测试看板')


class BoardViewTest(TestCase):
    """看板视图测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.board = Board.objects.create(
            name='测试看板',
            description='测试描述',
            owner=self.user,
            slug='test-board'
        )
        
    def test_board_list_view_authenticated(self):
        """测试已认证用户访问看板列表"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('boards:list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试看板')
        
    def test_board_create_view_post_valid(self):
        """测试看板创建POST请求 - 有效数据"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': '新看板',
            'description': '新看板描述',
            'template': 'kanban',
            'visibility': 'private',
            'background_color': '#4a90e2'
        }
        response = self.client.post(reverse('boards:create'), data)
        
        # 检查看板是否真的被创建
        new_board = Board.objects.get(name='新看板')
        self.assertEqual(new_board.owner, self.user)
        self.assertEqual(new_board.template, 'kanban')
        
        # 检查slug是否正确生成
        self.assertIsNotNone(new_board.slug)
        self.assertTrue(len(new_board.slug) > 0)
        
        # 检查是否创建成功并重定向
        self.assertEqual(response.status_code, 302)


class BoardAPITest(TestCase):
    """看板API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.board = Board.objects.create(
            name='测试看板',
            description='测试描述',
            owner=self.user,
            template='kanban',
            visibility='private'
        )
        
    def test_list_create_api_success(self):
        """测试列表创建API - 成功"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'name': '新列表',
            'position': 1
        }
        
        response = self.client.post(
            reverse('boards:list_create_api', kwargs={'slug': self.board.slug}),
            data
        )
        
        # 调试响应
        if response.status_code != 200:
            print("Response content:", response.content)
            print("Response status:", response.status_code)
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['list']['name'], '新列表')
        
        # 验证列表确实被创建
        self.assertTrue(BoardList.objects.filter(name='新列表', board=self.board).exists())
    
    def test_list_create_api_permission_denied(self):
        """测试列表创建API - 权限拒绝"""
        self.client.login(username='otheruser', password='testpass123')
        
        data = {'name': '新列表'}
        
        response = self.client.post(
            reverse('boards:list_create_api', kwargs={'slug': self.board.slug}),
            data
        )
        
        self.assertEqual(response.status_code, 403)
        
    def test_member_invite_api_success(self):
        """测试成员邀请API - 成功"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'email': 'other@example.com',
            'role': 'member'
        }
        
        response = self.client.post(
            reverse('boards:member_invite_api', kwargs={'slug': self.board.slug}),
            data
        )
        
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['member']['user']['email'], 'other@example.com')


class BoardDetailViewTest(TestCase):
    """看板详情视图测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.board = Board.objects.create(
            name='测试看板',
            description='测试描述',
            owner=self.user,
            template='kanban',
            visibility='private'
        )
        
        # 创建测试列表
        self.board_list = BoardList.objects.create(
            name='待办',
            board=self.board,
            position=1
        )
        
    def test_board_detail_view_context(self):
        """测试看板详情视图上下文"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('boards:detail', kwargs={'slug': self.board.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.board.name)
        self.assertContains(response, self.board.description)
        
        # 检查上下文
        self.assertEqual(response.context['board'], self.board)
        self.assertTrue('board_lists' in response.context)
        self.assertTrue('total_tasks' in response.context)
        self.assertTrue('completed_tasks' in response.context)
        
    def test_board_detail_with_tasks(self):
        """测试带任务的看板详情"""
        # 创建一些任务
        task1 = Task.objects.create(
            title='任务1',
            board=self.board,
            board_list=self.board_list,
            creator=self.user,
            status='todo'
        )
        
        task2 = Task.objects.create(
            title='任务2',
            board=self.board,
            board_list=self.board_list,
            creator=self.user,
            status='done'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('boards:detail', kwargs={'slug': self.board.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, task1.title)
        self.assertContains(response, task2.title)
        
        # 检查统计信息
        self.assertEqual(response.context['total_tasks'], 2)
        self.assertEqual(response.context['completed_tasks'], 1)


class BoardIntegrationTest(TestCase):
    """看板集成测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
          # 创建团队
        self.team = Team.objects.create(
            name='测试团队',
            description='测试团队描述',
            created_by=self.user
        )
        
        TeamMembership.objects.create(
            team=self.team,
            user=self.user,
            role='owner'
        )
        
    def test_complete_board_workflow(self):
        """测试完整的看板工作流程"""
        self.client.login(username='testuser', password='testpass123')
        
        # 1. 创建看板
        board_data = {
            'name': '项目看板',
            'description': '项目描述',
            'template': 'kanban',
            'visibility': 'team',
            'team': self.team.id,
            'background_color': '#4a90e2'
        }
        
        response = self.client.post(reverse('boards:create'), board_data)
        self.assertEqual(response.status_code, 302)  # 重定向到看板详情
        
        board = Board.objects.get(name='项目看板')
        self.assertEqual(board.owner, self.user)
        self.assertEqual(board.team, self.team)
        
        # 2. 创建列表
        list_data = {
            'name': '待办事项',
            'position': 1
        }
        
        response = self.client.post(
            reverse('boards:list_create_api', kwargs={'slug': board.slug}),
            list_data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(BoardList.objects.filter(name='待办事项', board=board).exists())
        
        # 3. 访问看板详情页面
        response = self.client.get(reverse('boards:detail', kwargs={'slug': board.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '项目看板')
        self.assertContains(response, '待办事项')
