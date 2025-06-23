#!/usr/bin/env python
"""
团队协作模块基础功能测试脚本
测试团队管理的基础CRUD功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.join(os.path.dirname(__file__), 'taskkanban'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from teams.models import Team, TeamMembership, TeamInvitation
from teams.forms import TeamForm, TeamInvitationForm

User = get_user_model()


def test_team_basic_operations():
    """测试团队基础操作"""
    print("=== 团队基础操作测试 ===")
    
    # 创建测试用户
    try:
        user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123'
        )
        print("✓ 创建测试用户成功")
    except Exception as e:
        print(f"✗ 创建测试用户失败: {e}")
        return False
    
    # 测试团队创建
    try:
        team_data = {
            'name': '测试团队',
            'description': '这是一个测试团队',
            'is_public': True,
            'allow_join_request': True
        }
        form = TeamForm(data=team_data, user=user1)
        if form.is_valid():
            team = form.save()
            print(f"✓ 团队创建成功: {team.name}")
            
            # 验证创建者是否自动成为所有者
            membership = TeamMembership.objects.get(team=team, user=user1)
            assert membership.role == 'owner'
            assert membership.status == 'active'
            print("✓ 创建者自动成为所有者")
        else:
            print(f"✗ 团队表单验证失败: {form.errors}")
            return False
    except Exception as e:
        print(f"✗ 团队创建失败: {e}")
        return False
    
    # 测试团队邀请
    try:
        invitation_data = {
            'user_identifier': 'test2@example.com',  # 使用邮箱邀请
            'role': 'member',
            'message': '欢迎加入我们的团队！'
        }
        form = TeamInvitationForm(data=invitation_data, team=team, inviter=user1)
        if form.is_valid():
            invitation = form.save()
            print(f"✓ 邀请发送成功: {invitation.invitee.email}")
            
            # 验证邀请状态
            assert invitation.status == 'pending'
            assert invitation.team == team
            assert invitation.inviter == user1
            assert invitation.invitee == user2
            print("✓ 邀请信息验证成功")
            
            # 测试接受邀请的流程
            print("\n=== 团队成员关系测试 ===")
            
            # 创建成员关系（模拟接受邀请的过程）
            membership = TeamMembership.objects.create(
                team=team,
                user=user2,
                role=invitation.role,
                status='active',
                invited_by=invitation.inviter
            )
            
            # 更新邀请状态
            invitation.status = 'accepted'
            invitation.save()
            
            print("✓ 成员加入团队成功")
            
            # 验证成员关系
            assert membership.is_active
            assert not membership.is_admin  # member角色不是管理员
            print("✓ 成员关系验证成功")
            
            # 验证团队统计更新
            team.refresh_from_db()
            assert team.member_count == 2
            print("✓ 团队统计更新正确")
            
        else:
            print(f"✗ 邀请表单验证失败: {form.errors}")
            return False
    except Exception as e:
        print(f"✗ 邀请发送失败: {e}")
        return False
    
    # 测试团队成员统计
    try:
        assert team.member_count == 2  # 现在有两个成员
        assert team.admin_count == 1   # 只有创建者是管理员
        print("✓ 团队统计信息正确")
        
        # 测试团队方法
        print(f"  - 成员数量: {team.member_count}")
        print(f"  - 管理员数量: {team.admin_count}")
        print(f"  - 团队头像URL: {team.get_avatar_url()}")
    except Exception as e:
        print(f"✗ 团队统计测试失败: {e}")
        return False
    
    return True


def test_team_membership_operations():
    """这个函数现在已经合并到test_team_basic_operations中"""
    return True


def test_team_models():
    """测试团队模型的方法和属性"""
    print("\n=== 团队模型测试 ===")
    
    try:
        team = Team.objects.first()
        memberships = TeamMembership.objects.filter(team=team)
        invitations = TeamInvitation.objects.filter(team=team)
        
        # 测试模型字符串表示
        print(f"✓ 团队字符串表示: {str(team)}")
        
        for membership in memberships:
            print(f"✓ 成员关系字符串表示: {str(membership)}")
            print(f"  - 是否管理员: {membership.is_admin}")
            print(f"  - 是否活跃: {membership.is_active}")
        
        for invitation in invitations:
            print(f"✓ 邀请字符串表示: {str(invitation)}")
            print(f"  - 是否过期: {invitation.is_expired}")
            print(f"  - 是否待处理: {invitation.is_pending}")
        
        return True
    except Exception as e:
        print(f"✗ 团队模型测试失败: {e}")
        return False


def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    try:
        # 清理邀请
        TeamInvitation.objects.all().delete()
        print("✓ 清理邀请数据")
        
        # 清理成员关系
        TeamMembership.objects.all().delete()
        print("✓ 清理成员关系数据")
        
        # 清理团队
        Team.objects.all().delete()
        print("✓ 清理团队数据")
        
        # 清理用户
        User.objects.filter(username__startswith='testuser').delete()
        print("✓ 清理用户数据")
        
    except Exception as e:
        print(f"✗ 清理数据失败: {e}")


def main():
    """主测试函数"""
    print("Django 5 任务看板 - 团队协作模块基础功能测试")
    print("=" * 50)
    
    try:
        # 执行测试
        success = True
        success &= test_team_basic_operations()
        success &= test_team_membership_operations() 
        success &= test_team_models()
        
        # 显示测试结果
        print("\n" + "=" * 50)
        if success:
            print("🎉 所有测试通过！团队协作模块基础功能正常")
        else:
            print("❌ 部分测试失败，请检查上述错误信息")
        
        return success
        
    except Exception as e:
        print(f"测试执行过程中发生错误: {e}")
        return False
    
    finally:
        # 清理测试数据
        cleanup_test_data()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
