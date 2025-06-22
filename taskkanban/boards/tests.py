"""
看板应用测试
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Board, BoardList, BoardMember
from .forms import BoardCreateForm, BoardUpdateForm, BoardSearchForm
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
