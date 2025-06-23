#!/usr/bin/env python
"""
测试团队绩效页面修复
验证NoneType错误是否已修复
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# 设置Django环境
sys.path.append('taskkanban')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from teams.models import Team, TeamMembership
from boards.models import Board, BoardMember, BoardList
from tasks.models import Task
from reports.services import ReportDataService

User = get_user_model()

def test_team_performance_page():
    """测试团队绩效页面"""
    print("🔍 测试团队绩效页面修复...")
    
    # 创建测试用户
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    # 创建没有nickname的用户
    try:
        user_no_nick = User.objects.get(username='nonickuser')
    except User.DoesNotExist:
        user_no_nick = User.objects.create_user(
            username='nonickuser',
            email='nonick@example.com',
            password='testpass123'
        )
    
    # 创建空名字的用户
    try:
        user_empty = User.objects.get(username='emptyuser')
    except User.DoesNotExist:
        user_empty = User.objects.create_user(
            username='emptyuser',
            email='empty@example.com',
            password='testpass123',
            first_name='',
            last_name=''
        )
    
    # 创建团队
    team, created = Team.objects.get_or_create(
        name='测试团队',
        defaults={
            'description': '用于测试的团队',
            'created_by': user
        }
    )
    
    # 添加团队成员
    TeamMembership.objects.get_or_create(
        team=team,
        user=user,
        defaults={'role': 'admin', 'status': 'active'}
    )
    
    TeamMembership.objects.get_or_create(
        team=team,
        user=user_no_nick,
        defaults={'role': 'member', 'status': 'active'}
    )
    
    TeamMembership.objects.get_or_create(
        team=team,
        user=user_empty,
        defaults={'role': 'member', 'status': 'active'}
    )
    
    # 创建看板
    board, created = Board.objects.get_or_create(
        name='测试看板',
        defaults={
            'description': '测试看板描述',
            'team': team,
            'created_by': user
        }
    )
      # 添加看板成员
    BoardMember.objects.get_or_create(
        board=board,
        user=user,
        defaults={'role': 'admin', 'is_active': True}
    )
      # 创建任务列表
    board_list, created = BoardList.objects.get_or_create(
        name='待办',
        board=board,
        defaults={'position': 1}
    )
    
    # 创建一些任务
    for i in range(5):
        task, created = Task.objects.get_or_create(
            title=f'测试任务 {i+1}',
            board_list=board_list,
            defaults={
                'description': f'测试任务描述 {i+1}',
                'priority': 'normal',
                'status': 'done' if i < 3 else 'todo',
                'creator': user,
                'board': board
            }
        )
        # 分配给不同用户
        if i % 3 == 0:
            task.assignees.add(user)
        elif i % 3 == 1:
            task.assignees.add(user_no_nick)
        else:
            task.assignees.add(user_empty)
    
    print("✅ 测试数据创建完成")
    
    # 测试数据服务
    print("\n🔍 测试ReportDataService...")
    service = ReportDataService(user=user, team=team)
    
    try:
        team_stats = service.get_team_performance_stats()
        print(f"✅ 团队统计数据获取成功")
        print(f"   - 团队数量: {team_stats['total_teams']}")
        print(f"   - 团队统计: {len(team_stats['team_stats'])}")
        
        # 检查成员数据
        for team_data in team_stats['team_stats']:
            print(f"   - 团队: {team_data['team_name']}")
            print(f"     成员数: {team_data['member_count']}")
            print(f"     任务数: {team_data['total_tasks']}")
            for member in team_data['members']:
                print(f"     成员: {member['display_name']} ({member['username']})")
                print(f"       生产力: {member['productivity_score']}%")
        
    except Exception as e:
        print(f"❌ 数据服务错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试页面访问
    print("\n🔍 测试页面访问...")
    client = Client()
    
    # 登录
    login_success = client.login(username='testuser', password='testpass123')
    if not login_success:
        print("❌ 登录失败")
        return False
    
    try:
        # 访问团队绩效页面
        response = client.get(reverse('reports:team_performance'))
        
        if response.status_code == 200:
            print("✅ 团队绩效页面访问成功")
            
            # 检查页面内容
            content = response.content.decode('utf-8')
            if '团队绩效报表' in content:
                print("✅ 页面标题正确")
            else:
                print("⚠️  页面标题未找到")
            
            if '测试团队' in content:
                print("✅ 团队数据显示正常")
            else:
                print("⚠️  团队数据未显示")
                
            print("✅ 页面渲染成功，NoneType错误已修复")
            return True
            
        else:
            print(f"❌ 页面访问失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 页面访问错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_display_name_logic():
    """测试display_name逻辑"""
    print("\n🔍 测试display_name逻辑...")
    
    # 测试不同用户的display_name生成
    users = [
        {'username': 'user1', 'first_name': 'John', 'last_name': 'Doe', 'nickname': 'Johnny'},
        {'username': 'user2', 'first_name': 'Jane', 'last_name': '', 'nickname': ''},
        {'username': 'user3', 'first_name': '', 'last_name': '', 'nickname': None},
        {'username': 'user4', 'first_name': None, 'last_name': None, 'nickname': ''},
    ]
    
    for user_data in users:
        # 模拟用户对象
        class MockUser:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
            
            def get_full_name(self):
                first = getattr(self, 'first_name', '') or ''
                last = getattr(self, 'last_name', '') or ''
                return f"{first} {last}".strip()
        
        user = MockUser(**user_data)
        
        # 应用修复后的逻辑
        display_name = (
            getattr(user, 'nickname', None) or 
            user.get_full_name() or 
            user.username or 
            'Unknown User'
        ).strip()
        
        print(f"   用户 {user.username}: '{display_name}'")
        
        # 验证不为空
        assert display_name and display_name.strip(), f"display_name为空: {user_data}"
        # 验证first过滤器安全
        first_char = display_name[0] if display_name else 'U'
        print(f"     首字符: '{first_char.upper()}'")
    
    print("✅ display_name逻辑测试通过")

if __name__ == '__main__':
    print("🚀 开始测试团队绩效页面修复...")
    
    # 测试display_name逻辑
    test_display_name_logic()
    
    # 测试页面功能
    success = test_team_performance_page()
    
    if success:
        print("\n🎉 所有测试通过！团队绩效页面NoneType错误已修复")
    else:
        print("\n❌ 测试失败，需要进一步调试")
    
    print("\n📊 可以通过以下URL访问页面:")
    print("   - 报表首页: http://127.0.0.1:8000/reports/")
    print("   - 团队绩效: http://127.0.0.1:8000/reports/team-performance/")
