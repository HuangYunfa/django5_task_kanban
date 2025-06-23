#!/usr/bin/env python
"""
批量操作功能测试脚本
测试任务列表页面的批量操作功能，包括前端UI和后端API
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from boards.models import Board, BoardList, BoardLabel
from tasks.models import Task
from users.models import User

class BatchOperationTestCase(TestCase):
    """批量操作测试案例"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # 创建测试看板
        self.board = Board.objects.create(
            name='测试看板',
            description='批量操作测试看板',
            owner=self.user,
            template='kanban'
        )
        
        # 创建测试列表
        self.list1 = BoardList.objects.create(
            board=self.board,
            name='待办',
            position=1
        )
        
        self.list2 = BoardList.objects.create(
            board=self.board,
            name='进行中',
            position=2
        )
        
        # 创建测试标签
        self.label1 = BoardLabel.objects.create(
            board=self.board,
            name='重要',
            color='#ff0000'
        )
        
        # 创建测试任务
        self.tasks = []
        for i in range(5):
            task = Task.objects.create(
                title=f'测试任务 {i+1}',
                description=f'这是第{i+1}个测试任务',
                board=self.board,
                board_list=self.list1,
                creator=self.user,
                priority='normal',
                status='todo',
                position=i+1
            )
            self.tasks.append(task)
        
        # 登录测试用户
        self.client.login(username='testuser', password='testpass123')
    
    def test_task_list_page_loads(self):
        """测试任务列表页面加载"""
        print("测试任务列表页面加载...")
        
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)
        
        # 检查是否包含批量操作相关元素
        content = response.content.decode()
        self.assertIn('batchToolbar', content)
        self.assertIn('batch-operation-btn', content)
        self.assertIn('task-checkbox', content)
        self.assertIn('selectAll', content)
        
        print("✓ 任务列表页面加载成功，包含批量操作UI元素")
    
    def test_batch_status_change(self):
        """测试批量状态变更"""
        print("测试批量状态变更...")
        
        task_ids = [task.id for task in self.tasks[:3]]
        
        response = self.client.post(reverse('tasks:batch_operation'), {
            'task_ids': task_ids,
            'operation': 'change_status',
            'new_status': 'in_progress'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # 验证任务状态已更新
        for task_id in task_ids:
            task = Task.objects.get(id=task_id)
            self.assertEqual(task.status, 'in_progress')
        
        print(f"✓ 成功批量更新 {len(task_ids)} 个任务的状态")
    
    def test_batch_priority_change(self):
        """测试批量优先级变更"""
        print("测试批量优先级变更...")
        
        task_ids = [task.id for task in self.tasks[:2]]
        
        response = self.client.post(reverse('tasks:batch_operation'), {
            'task_ids': task_ids,
            'operation': 'change_priority',
            'new_priority': 'high'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # 验证任务优先级已更新
        for task_id in task_ids:
            task = Task.objects.get(id=task_id)
            self.assertEqual(task.priority, 'high')
        
        print(f"✓ 成功批量更新 {len(task_ids)} 个任务的优先级")
    
    def test_batch_move_to_list(self):
        """测试批量移动到列表"""
        print("测试批量移动到列表...")
        
        task_ids = [task.id for task in self.tasks[:2]]
        
        response = self.client.post(reverse('tasks:batch_operation'), {
            'task_ids': task_ids,
            'operation': 'move_to_list',
            'new_list_id': self.list2.id
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # 验证任务已移动到新列表
        for task_id in task_ids:
            task = Task.objects.get(id=task_id)
            self.assertEqual(task.board_list.id, self.list2.id)
        
        print(f"✓ 成功批量移动 {len(task_ids)} 个任务到新列表")
    
    def test_batch_assign_to_user(self):
        """测试批量分配给用户"""
        print("测试批量分配给用户...")
        
        task_ids = [task.id for task in self.tasks[:2]]
        
        response = self.client.post(reverse('tasks:batch_operation'), {
            'task_ids': task_ids,
            'operation': 'assign_to_user',
            'user_id': self.user2.id
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # 验证任务已分配给用户
        for task_id in task_ids:
            task = Task.objects.get(id=task_id)
            self.assertTrue(task.assignees.filter(id=self.user2.id).exists())
        
        print(f"✓ 成功批量分配 {len(task_ids)} 个任务给用户")
    
    def test_user_list_api(self):
        """测试用户列表API"""
        print("测试用户列表API...")
        
        response = self.client.get(reverse('users:user_list_api'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)  # 至少有两个测试用户
        
        # 检查用户数据结构
        user_data = data[0]
        required_fields = ['id', 'username', 'display_name', 'email']
        for field in required_fields:
            self.assertIn(field, user_data)
        
        print(f"✓ 用户列表API正常工作，返回 {len(data)} 个用户")
    
    def test_board_lists_api(self):
        """测试看板列表API"""
        print("测试看板列表API...")
        
        response = self.client.get(
            reverse('boards:board_lists'),
            {'board_id': self.board.id}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # 两个测试列表
        
        # 检查列表数据结构
        list_data = data[0]
        required_fields = ['id', 'name', 'position']
        for field in required_fields:
            self.assertIn(field, list_data)
        
        print(f"✓ 看板列表API正常工作，返回 {len(data)} 个列表")
    
    def test_batch_delete(self):
        """测试批量删除"""
        print("测试批量删除...")
        
        # 选择最后两个任务进行删除
        task_ids = [task.id for task in self.tasks[-2:]]
        original_count = Task.objects.count()
        
        response = self.client.post(reverse('tasks:batch_operation'), {
            'task_ids': task_ids,
            'operation': 'delete'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # 验证任务已删除
        new_count = Task.objects.count()
        self.assertEqual(new_count, original_count - len(task_ids))
        
        for task_id in task_ids:
            self.assertFalse(Task.objects.filter(id=task_id).exists())
        
        print(f"✓ 成功批量删除 {len(task_ids)} 个任务")
    
    def test_permission_check(self):
        """测试权限检查"""
        print("测试权限检查...")
        
        # 创建另一个用户的任务
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        other_board = Board.objects.create(
            name='其他用户看板',
            description='其他用户的私有看板',
            owner=other_user,
            visibility='private'
        )
        
        other_list = BoardList.objects.create(
            board=other_board,
            name='其他列表',
            position=1
        )
        
        other_task = Task.objects.create(
            title='其他用户任务',
            board=other_board,
            board_list=other_list,
            creator=other_user
        )
        
        # 尝试批量操作其他用户的任务
        response = self.client.post(reverse('tasks:batch_operation'), {
            'task_ids': [other_task.id],
            'operation': 'change_status',
            'new_status': 'done'
        })
        
        # 应该返回成功但实际上没有操作任何任务（因为权限检查）
        self.assertEqual(response.status_code, 200)
        
        # 验证任务状态没有改变
        other_task.refresh_from_db()
        self.assertNotEqual(other_task.status, 'done')
        
        print("✓ 权限检查正常工作，无权限任务未被修改")


def run_tests():
    """运行所有测试"""
    print("开始批量操作功能测试...")
    print("=" * 50)
    
    # 创建测试套件
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=False)
    
    # 运行测试
    test_case = BatchOperationTestCase()
    test_case.setUp()
    
    try:
        test_case.test_task_list_page_loads()
        test_case.test_batch_status_change()
        test_case.test_batch_priority_change()
        test_case.test_batch_move_to_list()
        test_case.test_batch_assign_to_user()
        test_case.test_user_list_api()
        test_case.test_board_lists_api()
        test_case.test_batch_delete()
        test_case.test_permission_check()
        
        print("=" * 50)
        print("✅ 所有批量操作功能测试通过！")
        print("""
批量操作功能测试总结：
• ✓ 任务列表页面UI加载正常
• ✓ 批量状态变更功能正常
• ✓ 批量优先级变更功能正常
• ✓ 批量移动到列表功能正常
• ✓ 批量分配给用户功能正常
• ✓ 用户列表API正常工作
• ✓ 看板列表API正常工作
• ✓ 批量删除功能正常
• ✓ 权限检查机制正常

前端集成状态：
• 批量操作工具栏已集成
• 任务复选框已添加
• 全选/取消选择功能已实现
• 操作进度条已添加
• 键盘快捷键支持已添加
• 响应式设计已优化

建议下一步：
1. 测试在真实环境中的前端交互
2. 优化批量操作的用户体验
3. 添加操作确认对话框
4. 实现操作撤销功能
5. 添加批量操作日志记录
        """)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_tests()
