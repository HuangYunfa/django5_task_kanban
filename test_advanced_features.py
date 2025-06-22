#!/usr/bin/env python
"""
高级功能测试脚本
测试批量操作、拖拽排序等新功能
"""

import os
import sys
import django
import json
import requests
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
sys.path.append('taskkanban')
django.setup()

from boards.models import Board, BoardList, BoardMember
from tasks.models import Task
from teams.models import Team

User = get_user_model()

class AdvancedFeaturesTest(TestCase):
    """高级功能测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建测试用户
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
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
            description='用于测试的看板',
            owner=self.user1,
            visibility='private'
        )
        
        # 创建看板列表
        self.list1 = BoardList.objects.create(
            board=self.board,
            name='待办',
            position=0
        )
        self.list2 = BoardList.objects.create(
            board=self.board,
            name='进行中',
            position=1
        )
        self.list3 = BoardList.objects.create(
            board=self.board,
            name='已完成',
            position=2
        )
          # 创建测试任务
        self.task1 = Task.objects.create(
            title='任务1',
            description='第一个测试任务',
            board=self.board,
            board_list=self.list1,
            creator=self.user1,
            position=0,
            priority='normal'
        )
        self.task2 = Task.objects.create(
            title='任务2',
            description='第二个测试任务',
            board=self.board,
            board_list=self.list1,
            creator=self.user1,
            position=1,
            priority='high'
        )
        self.task3 = Task.objects.create(
            title='任务3',
            description='第三个测试任务',
            board=self.board,
            board_list=self.list2,
            creator=self.user1,
            position=0,
            priority='low'
        )
        
        # 设置客户端
        self.client = Client()
        self.client.login(username='testuser1', password='testpass123')
    
    def test_batch_operations_access(self):
        """测试批量操作API访问权限"""
        # 测试未登录用户
        client = Client()
        response = client.post('/tasks/batch-operation/', {
            'action': 'change_status',
            'task_ids': [self.task1.id, self.task2.id],
            'new_status': 'in_progress'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 302)  # 重定向到登录页面
        
        # 测试已登录用户
        response = self.client.post('/tasks/batch-operation/', 
            json.dumps({
                'action': 'change_status',
                'task_ids': [self.task1.id, self.task2.id],
                'new_status': 'in_progress'
            }), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_batch_status_change(self):
        """测试批量状态变更"""
        data = {
            'action': 'change_status',
            'task_ids': [self.task1.id, self.task2.id],
            'new_status': 'in_progress'
        }
        
        response = self.client.post('/tasks/batch-operation/', 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 验证任务状态已更新
        self.task1.refresh_from_db()
        self.task2.refresh_from_db()
        self.assertEqual(self.task1.status, 'in_progress')
        self.assertEqual(self.task2.status, 'in_progress')
    
    def test_batch_priority_change(self):
        """测试批量优先级变更"""
        data = {
            'action': 'change_priority',
            'task_ids': [self.task1.id, self.task3.id],
            'new_priority': 'urgent'
        }
        
        response = self.client.post('/tasks/batch-operation/', 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 验证任务优先级已更新
        self.task1.refresh_from_db()
        self.task3.refresh_from_db()
        self.assertEqual(self.task1.priority, 'urgent')
        self.assertEqual(self.task3.priority, 'urgent')
    
    def test_batch_move_tasks(self):
        """测试批量移动任务到另一个列表"""
        data = {
            'action': 'move_to_list',
            'task_ids': [self.task1.id, self.task2.id],
            'new_list_id': self.list2.id
        }
        
        response = self.client.post('/tasks/batch-operation/', 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
          # 验证任务已移动到新列表
        self.task1.refresh_from_db()
        self.task2.refresh_from_db()
        self.assertEqual(self.task1.board_list, self.list2)
        self.assertEqual(self.task2.board_list, self.list2)
    
    def test_batch_assign_tasks(self):
        """测试批量分配任务"""
        # 添加用户2为看板成员
        BoardMember.objects.create(
            board=self.board,
            user=self.user2,
            role='member',
            is_active=True
        )
        
        data = {
            'action': 'assign',
            'task_ids': [self.task1.id, self.task2.id],
            'assignee_id': self.user2.id
        }
        
        response = self.client.post('/tasks/batch-operation/', 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 验证任务已分配给用户2
        self.task1.refresh_from_db()
        self.task2.refresh_from_db()
        self.assertIn(self.user2, self.task1.assignees.all())
        self.assertIn(self.user2, self.task2.assignees.all())
    
    def test_batch_delete_tasks(self):
        """测试批量删除任务"""
        task_ids = [self.task1.id, self.task2.id]
        
        data = {
            'action': 'delete',
            'task_ids': task_ids
        }
        
        response = self.client.post('/tasks/batch-operation/', 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # 验证任务已被删除（软删除）
        self.task1.refresh_from_db()
        self.task2.refresh_from_db()
        self.assertTrue(self.task1.is_archived)
        self.assertTrue(self.task2.is_archived)
    
    def test_task_sorting_api(self):
        """测试任务拖拽排序API"""
        data = {
            'task_id': self.task1.id,
            'new_list_id': self.list2.id,
            'new_position': 1
        }
        
        response = self.client.post('/tasks/sort/', 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
          # 验证任务已移动到新列表并更新位置
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.board_list, self.list2)
        self.assertEqual(self.task1.position, 1)
    
    def test_task_sorting_position_update(self):
        """测试拖拽排序时其他任务位置的更新"""
        # 将task1移动到list2的位置0
        data = {
            'task_id': self.task1.id,
            'new_list_id': self.list2.id,
            'new_position': 0
        }
        
        response = self.client.post('/tasks/sort/', 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
          # 验证原来在list2位置0的task3位置被更新
        self.task3.refresh_from_db()
        self.assertEqual(self.task3.position, 1)
        # 验证task1现在在位置0
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.position, 0)
        self.assertEqual(self.task1.board_list, self.list2)
    
    def test_unauthorized_batch_operation(self):
        """测试无权限用户的批量操作"""
        # 登录用户2（无权限）
        client = Client()
        client.login(username='testuser2', password='testpass123')
        
        data = {
            'action': 'change_status',
            'task_ids': [self.task1.id, self.task2.id],
            'new_status': 'in_progress'
        }
        
        response = client.post('/tasks/batch-operation/', 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)  # 应该返回403 Forbidden
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('permission', response_data['error'].lower())  # 检查权限相关错误信息
    
    def test_invalid_batch_operation_data(self):
        """测试无效的批量操作数据"""
        # 测试无效的action        data = {
            'action': 'invalid_action',
            'task_ids': [self.task1.id],
        }
        
        response = self.client.post('/tasks/batch-operation/', 
            json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)  # 应该返回400 Bad Request
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Unknown operation', response_data['error'])
    
    def test_task_search_form_with_board_filter(self):
        """测试带看板筛选的任务搜索表单"""
        # 访问任务列表页面，应该加载搜索表单
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'search_form')
        
        # 测试带看板筛选的搜索
        response = self.client.get('/tasks/', {
            'board': self.board.id,
            'status': 'pending'
        })
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    import unittest
    
    print("开始测试高级功能...")
    print("=" * 50)
    
    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(AdvancedFeaturesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("✅ 所有高级功能测试通过！")
    else:
        print("❌ 部分测试失败")
        print(f"失败: {len(result.failures)}, 错误: {len(result.errors)}")
