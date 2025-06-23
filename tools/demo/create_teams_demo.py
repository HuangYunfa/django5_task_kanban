#!/usr/bin/env python
"""
团队协作模块功能展示脚本
创建示例数据用于Web界面测试
"""
import os
import sys
import django
from datetime import timedelta

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'taskkanban'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from teams.models import Team, TeamMembership, TeamInvitation

User = get_user_model()


def create_demo_data():
    """创建演示数据"""
    print("=== 创建团队协作模块演示数据 ===")
    
    # 创建演示用户
    users_data = [
        {
            'username': 'alice_manager',
            'email': 'alice@company.com',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'nickname': 'Alice (项目经理)',
            'password': 'demo123456'
        },
        {
            'username': 'bob_developer',
            'email': 'bob@company.com', 
            'first_name': 'Bob',
            'last_name': 'Smith',
            'nickname': 'Bob (开发者)',
            'password': 'demo123456'
        },
        {
            'username': 'carol_designer',
            'email': 'carol@company.com',
            'first_name': 'Carol',
            'last_name': 'Brown',
            'nickname': 'Carol (设计师)',
            'password': 'demo123456'
        },
        {
            'username': 'david_tester',
            'email': 'david@company.com',
            'first_name': 'David',
            'last_name': 'Wilson',
            'nickname': 'David (测试员)',
            'password': 'demo123456'
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'nickname': user_data['nickname'],
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✓ 创建用户: {user.nickname}")
        else:
            print(f"  - 用户已存在: {user.nickname}")
        created_users.append(user)
    
    alice, bob, carol, david = created_users
    
    # 创建团队
    teams_data = [
        {
            'name': 'Web开发团队',
            'description': '负责公司官网和内部系统的开发维护',
            'is_public': True,
            'allow_join_request': True,
            'owner': alice,
            'members': [
                {'user': bob, 'role': 'admin'},
                {'user': carol, 'role': 'member'},
            ]
        },
        {
            'name': '移动应用团队',
            'description': '专注于iOS和Android应用开发',
            'is_public': False,
            'allow_join_request': False, 
            'owner': alice,
            'members': [
                {'user': david, 'role': 'member'},
            ]
        },
        {
            'name': '设计团队',
            'description': '负责UI/UX设计和品牌视觉',
            'is_public': True,
            'allow_join_request': True,
            'owner': carol,
            'members': [
                {'user': alice, 'role': 'member'},
            ]
        }
    ]
    
    for team_data in teams_data:
        team, created = Team.objects.get_or_create(
            name=team_data['name'],
            defaults={
                'description': team_data['description'],
                'is_public': team_data['is_public'],
                'allow_join_request': team_data['allow_join_request'],
                'created_by': team_data['owner']
            }
        )
        
        if created:
            print(f"✓ 创建团队: {team.name}")
            
            # 创建所有者成员关系
            TeamMembership.objects.create(
                team=team,
                user=team_data['owner'],
                role='owner',
                status='active',
                joined_at=team.created_at
            )
            
            # 创建其他成员关系
            for member_data in team_data['members']:
                TeamMembership.objects.create(
                    team=team,
                    user=member_data['user'],
                    role=member_data['role'],
                    status='active',
                    invited_by=team_data['owner'],
                    joined_at=timezone.now()
                )
                print(f"  - 添加成员: {member_data['user'].nickname} ({member_data['role']})")
        else:
            print(f"  - 团队已存在: {team.name}")
    
    # 创建一些待处理的邀请
    print("\n=== 创建演示邀请 ===")
    
    web_team = Team.objects.get(name='Web开发团队')
    
    # David邀请加入Web开发团队
    invitation, created = TeamInvitation.objects.get_or_create(
        team=web_team,
        inviter=alice,
        invitee=david,
        defaults={
            'role': 'member',
            'status': 'pending',
            'message': '我们需要你的测试技能来改进我们的Web产品质量，欢迎加入！',
            'expires_at': timezone.now() + timedelta(days=7)
        }
    )
    
    if created:
        print(f"✓ 创建邀请: {invitation.inviter.nickname} 邀请 {invitation.invitee.nickname} 加入 {invitation.team.name}")
    else:
        print(f"  - 邀请已存在")
    
    # 统计信息
    print("\n=== 数据统计 ===")
    print(f"✓ 用户总数: {User.objects.count()}")
    print(f"✓ 团队总数: {Team.objects.count()}")
    print(f"✓ 成员关系总数: {TeamMembership.objects.count()}")
    print(f"✓ 邀请总数: {TeamInvitation.objects.count()}")
    
    # 显示访问信息
    print("\n=== Web界面访问信息 ===")
    print("请在浏览器中访问以下地址测试团队功能：")
    print("1. 团队列表: http://127.0.0.1:8000/teams/")
    print("2. 创建团队: http://127.0.0.1:8000/teams/create/")
    print("3. 我的邀请: http://127.0.0.1:8000/teams/my-invitations/")
    print("\n演示用户登录信息：")
    for user in created_users:
        print(f"  - 用户名: {user.username}, 密码: demo123456")
    
    return True


def cleanup_demo_data():
    """清理演示数据"""
    print("=== 清理演示数据 ===")
    
    # 清理邀请
    TeamInvitation.objects.all().delete()
    print("✓ 清理邀请数据")
    
    # 清理成员关系  
    TeamMembership.objects.all().delete()
    print("✓ 清理成员关系数据")
    
    # 清理团队
    Team.objects.all().delete()
    print("✓ 清理团队数据")
    
    # 清理演示用户
    User.objects.filter(username__in=[
        'alice_manager', 'bob_developer', 'carol_designer', 'david_tester'
    ]).delete()
    print("✓ 清理用户数据")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'cleanup':
        cleanup_demo_data()
    else:
        create_demo_data()
