#!/usr/bin/env python
"""
用户管理功能综合测试脚本
用于验证用户注册、登录、密码重置等核心功能
"""
import os
import sys
import django
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

# 添加项目路径
sys.path.append('d:/Learning/python_dev/django_template/django5_task_kanban/taskkanban')

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')

# 设置测试环境
os.environ['DJANGO_SETTINGS_MODULE'] = 'taskkanban.settings'
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'

django.setup()

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_user_management_workflow():
    """测试完整的用户管理工作流程"""
    print("🚀 开始用户管理功能综合测试...")
    
    client = Client()
    
    # 生成随机用户数据避免冲突
    import random
    import string
    random_suffix = ''.join(random.choices(string.digits, k=6))
    
    # 测试1: 用户注册
    print("\n📝 测试用户注册功能...")
    register_data = {
        'username': f'testuser{random_suffix}',
        'first_name': '测试',
        'last_name': '用户',
        'email': f'testuser{random_suffix}@example.com',
        'nickname': '测试昵称',
        'password1': 'SecurePassword123!',
        'password2': 'SecurePassword123!',
    }
    
    register_url = reverse('users:register')
    response = client.post(register_url, register_data)
    
    if response.status_code == 302:
        print("✅ 用户注册成功 - 已重定向到登录页面")
          # 验证用户已创建
        try:
            user = User.objects.get(username=register_data['username'])
            print(f"✅ 用户已创建: {user.username}, {user.first_name} {user.last_name}, {user.email}")
        except User.DoesNotExist:
            print("❌ 用户创建失败 - 数据库中找不到用户")
            return False
    else:
        print(f"❌ 用户注册失败 - 状态码: {response.status_code}")
        if hasattr(response, 'context') and response.context.get('form'):
            form = response.context['form']
            if form.errors:
                print(f"表单错误: {form.errors}")
        return False
    
    # 测试2: 用户登录
    print("\n🔑 测试用户登录功能...")
    login_data = {
        'username': register_data['username'],
        'password': 'SecurePassword123!',
    }
    
    login_url = reverse('users:login')
    response = client.post(login_url, login_data)
    
    if response.status_code == 302:
        print("✅ 用户登录成功 - 已重定向")
        
        # 验证用户已登录
        if '_auth_user_id' in client.session:
            print("✅ 用户会话已建立")
        else:
            print("❌ 用户会话建立失败")
            return False
    else:
        print(f"❌ 用户登录失败 - 状态码: {response.status_code}")
        return False
      # 测试3: 访问用户资料页面
    print("\n👤 测试用户资料页面访问...")
    profile_url = reverse('users:profile')
    response = client.get(profile_url)
    
    if response.status_code == 200:
        print("✅ 用户资料页面访问成功")
        if register_data['username'] in response.content.decode():
            print("✅ 页面包含用户信息")
        else:
            print("⚠️ 页面不包含用户信息")
    else:
        print(f"❌ 用户资料页面访问失败 - 状态码: {response.status_code}")
        return False    # 测试4: 更新用户资料
    print("\n📝 测试用户资料更新...")
    update_data = {
        'first_name': '更新的名',
        'last_name': '更新的姓',
        'email': f'updated_{register_data["username"]}@example.com',
        'nickname': '更新的昵称',
        'language': 'zh-hans',
        'timezone': 'Asia/Shanghai',
    }
    
    response = client.post(profile_url, update_data)
    
    if response.status_code == 302:
        print("✅ 用户资料更新成功 - 已重定向")
        
        # 验证更新是否生效
        user.refresh_from_db()
        if user.first_name == '更新的名' and user.last_name == '更新的姓':
            print("✅ 用户资料更新已保存到数据库")
        else:
            print(f"❌ 用户资料更新未保存 - 实际值: {user.first_name} {user.last_name}")
            return False
    else:
        print(f"❌ 用户资料更新失败 - 状态码: {response.status_code}")
        return False
      # 测试5: 密码重置请求
    print("\n🔄 测试密码重置功能...")
    reset_data = {
        'email': update_data['email'],
    }
    
    reset_url = reverse('users:password_reset')
    response = client.post(reset_url, reset_data)
    
    if response.status_code == 302:
        print("✅ 密码重置请求成功 - 已重定向")
        
        # 验证邮件是否发送
        if len(mail.outbox) > 0:
            print(f"✅ 密码重置邮件已发送 - 邮件数量: {len(mail.outbox)}")
            last_email = mail.outbox[-1]
            print(f"邮件主题: {last_email.subject}")
            print(f"收件人: {last_email.to}")
        else:
            print("❌ 密码重置邮件未发送")
            return False
    else:
        print(f"❌ 密码重置请求失败 - 状态码: {response.status_code}")
        return False
    
    # 测试6: 用户登出
    print("\n🚪 测试用户登出功能...")
    logout_url = reverse('users:logout')
    response = client.post(logout_url)
    
    if response.status_code == 302:
        print("✅ 用户登出成功 - 已重定向")
        
        # 验证会话是否清除
        if '_auth_user_id' not in client.session:
            print("✅ 用户会话已清除")
        else:
            print("❌ 用户会话清除失败")
            return False
    else:
        print(f"❌ 用户登出失败 - 状态码: {response.status_code}")
        return False
    
    # 清理测试数据
    print("\n🧹 清理测试数据...")
    try:
        user.delete()
        print("✅ 测试用户已删除")
    except:
        print("⚠️ 测试用户删除失败")
    
    print("\n🎉 用户管理功能综合测试完成！")
    return True


def test_user_authentication_templates():
    """测试用户认证相关模板"""
    print("\n🎨 测试用户认证模板...")
    
    client = Client()
    
    # 测试各个页面是否能正常访问
    test_pages = [
        ('users:register', '注册页面'),
        ('users:login', '登录页面'),
        ('users:password_reset', '密码重置页面'),
    ]
    
    for url_name, page_name in test_pages:
        try:
            url = reverse(url_name)
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {page_name}访问成功")
            else:
                print(f"❌ {page_name}访问失败 - 状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {page_name}测试出错: {e}")
            return False
    
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("Django 5 企业级任务看板 - 用户管理功能测试")
    print("=" * 60)
    
    # 运行模板测试
    if test_user_authentication_templates():
        print("✅ 用户认证模板测试通过")
    else:
        print("❌ 用户认证模板测试失败")
        sys.exit(1)
    
    # 运行功能测试
    if test_user_management_workflow():
        print("\n🎉 所有测试通过！用户管理功能运行正常。")
        print("\n📋 功能清单:")
        print("  ✅ 用户注册")
        print("  ✅ 用户登录")
        print("  ✅ 用户登出")
        print("  ✅ 用户资料管理")
        print("  ✅ 密码重置")
        print("  ✅ 邮件发送")
        print("  ✅ 认证模板")
        
        print("\n🎯 TODO工作任务状态更新:")
        print("  ✅ 第6-7周：用户管理模块开发")
        print("    ✅ 用户认证与授权系统实现")
        print("    ✅ 用户资料管理")
        print("    ✅ 密码重置功能")
        print("    ✅ 邮箱验证（基础版）")
        print("    ✅ 用户表单、视图、URL和模板")
        print("    ✅ 用户管理测试")
        
        print("\n🚀 下一步建议:")
        print("  📋 完善用户角色与权限管理")
        print("  🔐 集成OAuth2.0（Google/GitHub）")
        print("  👥 开发团队协作功能")
        print("  📊 开始看板管理模块开发")
        
    else:
        print("\n❌ 部分测试失败，请检查相关功能。")
        sys.exit(1)
