#!/usr/bin/env python3
"""
简化的拖拽排序测试脚本
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

def test_task_sorting():
    """测试任务拖拽排序API"""
    print("开始任务拖拽排序测试...")
    
    # 获取测试用户
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    # 创建或获取测试看板
    board, _ = Board.objects.get_or_create(
        name='排序测试看板',
        defaults={
            'description': '测试拖拽排序用看板',
            'owner': user
        }
    )
    
    # 创建测试列表
    list1, _ = BoardList.objects.get_or_create(
        name='排序测试列表',
        board=board,
        defaults={'position': 0}
    )
    
    # 创建测试任务
    task1, _ = Task.objects.get_or_create(
        title='排序测试任务1',
        board=board,
        board_list=list1,
        creator=user,
        defaults={
            'description': '测试描述1',
            'status': 'todo',
            'priority': 'normal',
            'position': 0
        }
    )
    
    task2, _ = Task.objects.get_or_create(
        title='排序测试任务2',
        board=board,
        board_list=list1,
        creator=user,
        defaults={
            'description': '测试描述2',
            'status': 'todo',
            'priority': 'normal',
            'position': 1
        }
    )
    
    # 创建客户端并登录
    client = Client()
    client.login(username='testuser', password='testpass123')
    
    print("✅ 排序测试数据创建成功")
    
    # 测试任务拖拽排序
    print("🔍 测试任务拖拽排序...")
    data = {
        'task_id': task1.id,
        'new_list_id': list1.id,
        'new_position': 1
    }
    
    response = client.post('/tasks/sort/', 
        json.dumps(data), 
        content_type='application/json'
    )
    
    if response.status_code == 200:
        result = json.loads(response.content)
        if result['success']:
            print("✅ 任务拖拽排序API测试通过")
            
            # 验证任务位置是否更新
            task1.refresh_from_db()
            if task1.position == 1:
                print("✅ 任务位置更新验证通过")
            else:
                print(f"❌ 任务位置更新验证失败: 期望1，实际{task1.position}")
        else:
            print(f"❌ 任务拖拽排序失败: {result.get('error', '未知错误')}")
    else:
        print(f"❌ 任务拖拽排序请求失败: HTTP {response.status_code}")
        try:
            error_data = json.loads(response.content)
            print(f"   错误信息: {error_data}")
        except:
            print(f"   响应内容: {response.content}")
    
    print("🎉 任务拖拽排序测试完成！")

if __name__ == "__main__":
    test_task_sorting()
