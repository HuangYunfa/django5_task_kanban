#!/usr/bin/env python
"""
团队协作模块Web界面测试脚本
测试团队页面的基本功能和导航
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'taskkanban'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from teams.models import Team, TeamMembership

User = get_user_model()


def test_teams_web_interface():
    """测试团队Web界面"""
    print("=== 团队Web界面测试 ===")
    
    # 创建测试用户
    try:
        user = User.objects.create_user(
            username='webtest',
            email='webtest@example.com',
            password='testpass123'
        )
        print("✓ 创建测试用户成功")
    except Exception as e:
        print(f"✗ 创建测试用户失败: {e}")
        return False
    
    # 创建测试客户端
    client = Client()
    
    # 测试未登录访问（应该重定向到登录页）
    try:
        response = client.get(reverse('teams:list'))
        assert response.status_code == 302  # 重定向到登录
        print("✓ 未登录访问正确重定向")
    except Exception as e:
        print(f"✗ 未登录访问测试失败: {e}")
        return False
    
    # 登录用户
    try:
        login_success = client.login(username='webtest@example.com', password='testpass123')
        assert login_success
        print("✓ 用户登录成功")
    except Exception as e:
        print(f"✗ 用户登录失败: {e}")
        return False
    
    # 测试团队列表页面
    try:
        response = client.get(reverse('teams:list'))
        assert response.status_code == 200
        assert 'teams/list.html' in [t.name for t in response.templates]
        assert 'teams' in response.context
        print("✓ 团队列表页面正常")
    except Exception as e:
        print(f"✗ 团队列表页面测试失败: {e}")
        return False
    
    # 测试团队创建页面
    try:
        response = client.get(reverse('teams:create'))
        assert response.status_code == 200
        assert 'teams/create.html' in [t.name for t in response.templates]
        print("✓ 团队创建页面正常")
    except Exception as e:
        print(f"✗ 团队创建页面测试失败: {e}")
        return False
    
    # 测试创建团队功能
    try:
        team_data = {
            'name': 'Web测试团队',
            'description': '这是通过Web界面创建的测试团队',
            'is_public': True,
            'allow_join_request': True
        }
        response = client.post(reverse('teams:create'), data=team_data)
        assert response.status_code == 302  # 重定向到团队列表
        
        # 验证团队是否创建成功
        team = Team.objects.get(name='Web测试团队')
        assert team.created_by == user
        assert team.is_public == True
        
        # 验证成员关系是否创建
        membership = TeamMembership.objects.get(team=team, user=user)
        assert membership.role == 'owner'
        assert membership.status == 'active'
        
        print("✓ 团队创建功能正常")
    except Exception as e:
        print(f"✗ 团队创建功能测试失败: {e}")
        return False
    
    # 测试团队详情页面
    try:
        response = client.get(reverse('teams:detail', kwargs={'pk': team.pk}))
        assert response.status_code == 200
        assert 'teams/detail.html' in [t.name for t in response.templates]
        assert response.context['team'] == team
        assert response.context['is_admin'] == True
        print("✓ 团队详情页面正常")
    except Exception as e:
        print(f"✗ 团队详情页面测试失败: {e}")
        return False
    
    # 测试团队编辑页面
    try:
        response = client.get(reverse('teams:edit', kwargs={'pk': team.pk}))
        assert response.status_code == 200
        assert 'teams/edit.html' in [t.name for t in response.templates]
        print("✓ 团队编辑页面正常")
    except Exception as e:
        print(f"✗ 团队编辑页面测试失败: {e}")
        return False
    
    # 测试成员管理页面
    try:
        response = client.get(reverse('teams:members', kwargs={'pk': team.pk}))
        assert response.status_code == 200
        assert 'teams/members.html' in [t.name for t in response.templates]
        print("✓ 成员管理页面正常")
    except Exception as e:
        print(f"✗ 成员管理页面测试失败: {e}")
        return False
    
    # 测试我的邀请页面
    try:
        response = client.get(reverse('teams:my_invitations'))
        assert response.status_code == 200
        assert 'teams/my_invitations.html' in [t.name for t in response.templates]
        print("✓ 我的邀请页面正常")
    except Exception as e:
        print(f"✗ 我的邀请页面测试失败: {e}")
        return False
    
    return True


def test_team_search_functionality():
    """测试团队搜索功能"""
    print("\n=== 团队搜索功能测试 ===")
    
    client = Client()
    user = User.objects.get(username='webtest')
    client.login(username='webtest@example.com', password='testpass123')
    
    try:
        # 测试按名称搜索
        response = client.get(reverse('teams:list'), {'search': 'Web测试'})
        assert response.status_code == 200
        teams = response.context['teams']
        assert len(teams) == 1
        assert teams[0].name == 'Web测试团队'
        print("✓ 按名称搜索功能正常")
        
        # 测试按可见性筛选
        response = client.get(reverse('teams:list'), {'is_public': 'true'})
        assert response.status_code == 200
        teams = response.context['teams']
        assert all(team.is_public for team in teams)
        print("✓ 按可见性筛选功能正常")
        
        # 测试按角色筛选
        response = client.get(reverse('teams:list'), {'role': 'owner'})
        assert response.status_code == 200
        print("✓ 按角色筛选功能正常")
        
        return True
    except Exception as e:
        print(f"✗ 团队搜索功能测试失败: {e}")
        return False


def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    try:
        # 清理团队相关数据
        TeamMembership.objects.all().delete()
        Team.objects.all().delete()
        
        # 清理测试用户
        User.objects.filter(username='webtest').delete()
        
        print("✓ 测试数据清理完成")
    except Exception as e:
        print(f"✗ 清理数据失败: {e}")


def main():
    """主测试函数"""
    print("Django 5 任务看板 - 团队协作模块Web界面测试")
    print("=" * 55)
    
    try:
        success = True
        success &= test_teams_web_interface()
        success &= test_team_search_functionality()
        
        print("\n" + "=" * 55)
        if success:
            print("🎉 所有Web界面测试通过！")
            print("📋 测试覆盖的功能：")
            print("   - 团队列表页面")
            print("   - 团队创建页面")
            print("   - 团队详情页面")
            print("   - 团队编辑页面")
            print("   - 成员管理页面")
            print("   - 我的邀请页面")
            print("   - 团队搜索功能")
            print("   - 权限控制")
        else:
            print("❌ 部分测试失败，请检查上述错误信息")
        
        return success
        
    except Exception as e:
        print(f"测试执行过程中发生错误: {e}")
        return False
    
    finally:
        cleanup_test_data()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
