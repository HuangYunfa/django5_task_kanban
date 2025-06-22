#!/usr/bin/env python3
"""
简化的批量操作测试脚本
"""
import os
import sys
import json
import django

# 添加项目路径
project_root = os.path.join(os.path.dirname(__file__), 'taskkanban')
sys.path.insert(0, project_root)

# 配置Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from boards.models import Board, BoardList
from tasks.models import Task

User = get_user_model()

def test_batch_operations():
    """测试批量操作API"""
    print("开始批量操作测试...")
      # 创建测试用户（如果不存在）
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
      # 创建测试看板
    board = Board.objects.create(
        name='测试看板',
        description='测试用看板',
        owner=user
    )
      # 创建测试列表
    list1 = BoardList.objects.create(
        name='待办事项',
        board=board,
        position=0
    )
    
    # 创建测试任务
    task1 = Task.objects.create(
        title='测试任务1',
        description='测试描述1',
        board=board,
        board_list=list1,
        creator=user,
        status='todo',
        priority='normal'
    )
    
    task2 = Task.objects.create(
        title='测试任务2',
        description='测试描述2',
        board=board,
        board_list=list1,
        creator=user,
        status='todo',
        priority='normal'
    )
    
    # 创建客户端并登录
    client = Client()
    client.login(username='testuser', password='testpass123')
    
    print("✅ 测试数据创建成功")
    
    # 测试批量状态变更
    print("🔍 测试批量状态变更...")
    data = {
        'action': 'change_status',
        'task_ids': [task1.id, task2.id],
        'new_status': 'in_progress'
    }
    
    response = client.post('/tasks/batch-operation/', 
        json.dumps(data), 
        content_type='application/json'
    )
    
    if response.status_code == 200:
        result = json.loads(response.content)
        if result['success']:
            print("✅ 批量状态变更测试通过")
            
            # 验证任务状态是否更新
            task1.refresh_from_db()
            task2.refresh_from_db()
            if task1.status == 'in_progress' and task2.status == 'in_progress':
                print("✅ 任务状态更新验证通过")
            else:
                print("❌ 任务状态更新验证失败")
        else:
            print(f"❌ 批量状态变更失败: {result.get('error', '未知错误')}")
    else:
        print(f"❌ 批量状态变更请求失败: HTTP {response.status_code}")
        try:
            error_data = json.loads(response.content)
            print(f"   错误信息: {error_data}")
        except:
            print(f"   响应内容: {response.content}")
    
    # 测试批量优先级变更
    print("🔍 测试批量优先级变更...")
    data = {
        'action': 'change_priority',
        'task_ids': [task1.id, task2.id],
        'new_priority': 'high'
    }
    
    response = client.post('/tasks/batch-operation/', 
        json.dumps(data), 
        content_type='application/json'
    )
    
    if response.status_code == 200:
        result = json.loads(response.content)
        if result['success']:
            print("✅ 批量优先级变更测试通过")
        else:
            print(f"❌ 批量优先级变更失败: {result.get('error', '未知错误')}")
    else:
        print(f"❌ 批量优先级变更请求失败: HTTP {response.status_code}")
    
    # 测试批量删除
    print("🔍 测试批量删除...")
    data = {
        'action': 'delete',
        'task_ids': [task1.id, task2.id]
    }
    
    response = client.post('/tasks/batch-operation/', 
        json.dumps(data), 
        content_type='application/json'
    )
    
    if response.status_code == 200:
        result = json.loads(response.content)
        if result['success']:
            print("✅ 批量删除测试通过")
            
            # 验证任务是否被软删除
            task1.refresh_from_db()
            task2.refresh_from_db()
            if task1.is_archived and task2.is_archived:
                print("✅ 任务软删除验证通过")
            else:
                print("❌ 任务软删除验证失败")
        else:
            print(f"❌ 批量删除失败: {result.get('error', '未知错误')}")
    else:
        print(f"❌ 批量删除请求失败: HTTP {response.status_code}")
    
    # 测试无效操作
    print("🔍 测试无效操作...")
    data = {
        'action': 'invalid_action',
        'task_ids': [task1.id]
    }
    
    response = client.post('/tasks/batch-operation/', 
        json.dumps(data), 
        content_type='application/json'
    )
    
    if response.status_code == 400:
        result = json.loads(response.content)
        if not result['success'] and 'Unknown operation' in result['error']:
            print("✅ 无效操作错误处理测试通过")
        else:
            print(f"❌ 无效操作错误信息不正确: {result}")
    else:
        print(f"❌ 无效操作应该返回400，实际返回: HTTP {response.status_code}")
    
    print("🎉 批量操作测试完成！")

if __name__ == "__main__":
    test_batch_operations()
