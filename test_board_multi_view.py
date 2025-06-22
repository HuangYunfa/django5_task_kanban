#!/usr/bin/env python
"""
测试看板多视图功能的脚本
验证后端API和前端集成是否正常工作
"""
import sys
import os
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'taskkanban'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from boards.models import Board, BoardList
from tasks.models import Task
from django.contrib.auth.models import User

User = get_user_model()

def test_board_multi_view_api():
    """测试看板多视图API"""
    print("🧪 开始测试看板多视图API...")
    
    client = Client()
      # 创建测试用户
    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    username = f'testuser_{random_suffix}'
    
    user = User.objects.create_user(
        username=username,
        email=f'test_{random_suffix}@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    
    # 登录用户
    client.login(username=username, password='testpass123')
      # 创建测试看板
    board_slug = f'multi-view-test-board-{random_suffix}'
    board = Board.objects.create(
        name='多视图测试看板',
        slug=board_slug,
        description='用于测试多视图功能的看板',
        owner=user,
        background_color='#4a90e2'
    )
    
    # 创建测试列表
    todo_list = BoardList.objects.create(
        board=board,
        name='待办',
        position=0
    )
    
    in_progress_list = BoardList.objects.create(
        board=board,
        name='进行中',
        position=1
    )
    
    done_list = BoardList.objects.create(
        board=board,
        name='已完成',
        position=2
    )
      # 创建测试任务
    tasks_data = [
        {
            'title': '设计用户界面',
            'description': '设计应用的用户界面原型',
            'board_list': todo_list,
            'status': 'todo',
            'priority': 2,
        },
        {
            'title': '实现后端API',
            'description': '开发RESTful API接口',
            'board_list': in_progress_list,
            'status': 'in_progress',
            'priority': 3,
        },
        {
            'title': '编写测试用例',
            'description': '为核心功能编写单元测试',
            'board_list': done_list,
            'status': 'done',
            'priority': 1,
        }
    ]
    
    for task_data in tasks_data:
        Task.objects.create(
            board=board,
            creator=user,
            **task_data
        )
    
    print(f"✅ 创建测试数据完成:")
    print(f"   - 看板: {board.name}")
    print(f"   - 列表: {board.lists.count()} 个")
    print(f"   - 任务: {Task.objects.filter(board=board).count()} 个")
    
    # 测试看板数据API
    print("\n🔍 测试看板数据API...")
    api_url = reverse('boards:board_data_api', kwargs={'slug': board.slug})
    response = client.get(api_url)
    
    print(f"   API URL: {api_url}")
    print(f"   响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API调用成功")
        print(f"   看板信息: {data['board']['name']}")
        print(f"   列表数量: {len(data['lists'])}")
        print(f"   任务数量: {len(data['tasks'])}")
        print(f"   统计信息: {data['stats']}")
        
        # 验证数据结构
        required_keys = ['board', 'lists', 'tasks', 'stats', 'members']
        for key in required_keys:
            if key not in data:
                print(f"   ❌ 缺少必需字段: {key}")
                return False
        
        # 验证任务数据结构
        if data['tasks']:
            task = data['tasks'][0]
            task_keys = ['id', 'title', 'status', 'priority', 'list_id', 'created_at']
            for key in task_keys:
                if key not in task:
                    print(f"   ❌ 任务数据缺少字段: {key}")
                    return False
        
        print(f"   ✅ 数据结构验证通过")
        
        # 测试不同状态的任务统计
        expected_stats = {
            'total_tasks': 3,
            'todo_tasks': 1,
            'in_progress_tasks': 1,
            'completed_tasks': 1
        }
        
        for key, expected_value in expected_stats.items():
            if data['stats'][key] != expected_value:
                print(f"   ❌ 统计数据错误: {key} = {data['stats'][key]}, 期望 {expected_value}")
                return False
        
        print(f"   ✅ 统计数据验证通过")
        
    else:
        print(f"   ❌ API调用失败: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"   错误内容: {response.content.decode()}")
        return False
    
    # 测试看板详情页面
    print("\n🔍 测试看板详情页面...")
    detail_url = reverse('boards:detail', kwargs={'slug': board.slug})
    response = client.get(detail_url)
    
    print(f"   详情页URL: {detail_url}")
    print(f"   响应状态: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # 检查关键元素是否存在
        checks = [
            ('board-container', '看板容器'),
            ('BoardViewManager', '多视图管理器'),
            ('board-multi-view.js', '多视图脚本'),
        ]
        
        for check_item, description in checks:
            if check_item in content:
                print(f"   ✅ {description}已加载")
            else:
                print(f"   ❌ {description}未找到")
                return False
        
        print(f"   ✅ 看板详情页面验证通过")
        
    else:
        print(f"   ❌ 看板详情页面加载失败: {response.status_code}")
        return False
    
    # 清理测试数据
    print("\n🧹 清理测试数据...")
    Task.objects.filter(board=board).delete()
    board.delete()
    user.delete()
    print("   ✅ 测试数据清理完成")
    
    print("\n🎉 看板多视图功能测试完成！所有测试均通过。")
    return True

def main():
    """主函数"""
    print("🚀 看板多视图功能集成测试")
    print("=" * 50)
    
    try:
        success = test_board_multi_view_api()
        
        if success:
            print("\n✅ 所有测试通过！看板多视图功能集成成功。")
            print("\n📋 功能说明:")
            print("   • 支持卡片视图(默认看板视图)")
            print("   • 支持列表视图(表格形式)")
            print("   • 支持日历视图(基于到期日期)")
            print("   • 支持甘特图视图(项目进度)")
            print("   • 视图切换状态自动保存")
            print("   • 数据实时同步")
            
            print("\n🔧 使用说明:")
            print("   1. 访问任意看板详情页")
            print("   2. 使用顶部的视图切换按钮")
            print("   3. 系统会自动记住您的视图偏好")
            
        else:
            print("\n❌ 测试失败！请检查错误信息并修复。")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 测试运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
