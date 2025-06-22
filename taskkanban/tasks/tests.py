"""
Tasks应用测试
任务管理相关测试
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Task, TaskComment, TaskAttachment
from boards.models import Board, BoardList, BoardLabel
from teams.models import Team, TeamMembership

User = get_user_model()


class TaskModelTest(TestCase):
    """任务模型测试"""
    
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
            template='kanban'
        )
        
        self.board_list = BoardList.objects.create(
            name='待办',
            board=self.board,
            position=1
        )
    
    def test_task_creation(self):
        """测试任务创建"""
        task = Task.objects.create(
            title='测试任务',
            description='测试任务描述',
            board=self.board,
            board_list=self.board_list,
            creator=self.user,
            priority='normal',
            status='todo'
        )
        
        self.assertEqual(task.title, '测试任务')
        self.assertEqual(task.board, self.board)
        self.assertEqual(task.board_list, self.board_list)
        self.assertEqual(task.creator, self.user)
        self.assertEqual(task.status, 'todo')
    
    def test_task_str_representation(self):
        """测试任务字符串表示"""
        task = Task.objects.create(
            title='测试任务',
            board=self.board,
            board_list=self.board_list,
            creator=self.user
        )
        
        self.assertEqual(str(task), '测试任务')


class TaskViewTest(TestCase):
    """任务视图测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.board = Board.objects.create(
            name='测试看板',
            owner=self.user,
            template='kanban'
        )
        
        self.board_list = BoardList.objects.create(
            name='待办',
            board=self.board,
            position=1
        )
        
        self.task = Task.objects.create(
            title='测试任务',
            board=self.board,
            board_list=self.board_list,
            creator=self.user
        )
    
    def test_task_list_view_authenticated(self):
        """测试已认证用户访问任务列表"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('tasks:list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试任务')
    
    def test_task_detail_view(self):
        """测试任务详情页面"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('tasks:detail', kwargs={'pk': self.task.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
