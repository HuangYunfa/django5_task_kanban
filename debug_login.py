#!/usr/bin/env python
"""
调试登录问题的简单脚本
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

# 添加项目路径
sys.path.append('d:/Learning/python_dev/django_template/django5_task_kanban/taskkanban')

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')

django.setup()

User = get_user_model()

def debug_login_issue():
    """调试登录问题"""
    print("🔍 调试登录问题...")
    
    client = Client()
    
    # 创建测试用户
    user = User.objects.create_user(
        username='debuguser',
        password='TestPassword123!',
        email='debug@example.com',
        first_name='Debug',
        last_name='User'
    )
    print(f"✅ 测试用户已创建: {user.username}")
    print(f"用户邮箱: {user.email}")
    print(f"用户ID: {user.id}")
    
    # 测试直接认证
    from django.contrib.auth import authenticate
    auth_user = authenticate(username='debuguser', password='TestPassword123!')
    if auth_user:
        print(f"✅ 直接认证成功: {auth_user.username}")
    else:
        print("❌ 直接认证失败")
    
    # 测试邮箱认证
    auth_user_email = authenticate(username='debug@example.com', password='TestPassword123!')
    if auth_user_email:
        print(f"✅ 邮箱认证成功: {auth_user_email.username}")
    else:
        print("❌ 邮箱认证失败")
    
    # 获取登录页面
    login_url = reverse('users:login')
    print(f"🔗 登录URL: {login_url}")
    
    response = client.get(login_url)
    print(f"📄 登录页面状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 登录页面可以正常访问")
        
        # 检查页面内容
        content = response.content.decode()
        if 'csrfmiddlewaretoken' in content:
            print("✅ 页面包含CSRF token")
        else:
            print("❌ 页面缺少CSRF token")
            
        if 'username' in content:
            print("✅ 页面包含用户名字段")
        else:
            print("❌ 页面缺少用户名字段")
            
        if 'password' in content:
            print("✅ 页面包含密码字段")
        else:
            print("❌ 页面缺少密码字段")
    
    # 尝试用用户名登录
    login_data = {
        'username': 'debuguser',
        'password': 'TestPassword123!',
    }
    
    print(f"\n🔑 尝试用用户名登录...")
    print(f"登录数据: {login_data}")
    
    response = client.post(login_url, login_data)
    print(f"登录响应状态码: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ 登录成功 - 已重定向")
        print(f"重定向到: {response.url}")
    elif response.status_code == 200:
        print("❌ 登录失败 - 返回登录页面")
        
        # 检查表单错误
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            if form and hasattr(form, 'errors') and form.errors:
                print(f"表单错误: {form.errors}")
            if form and hasattr(form, 'non_field_errors'):
                non_field_errors = form.non_field_errors()
                if non_field_errors:
                    print(f"非字段错误: {non_field_errors}")
    else:
        print(f"❌ 意外的状态码: {response.status_code}")
    
    # 尝试用邮箱登录
    login_data_email = {
        'username': 'debug@example.com',
        'password': 'TestPassword123!',
    }
    
    print(f"\n📧 尝试用邮箱登录...")
    print(f"登录数据: {login_data_email}")
    
    response = client.post(login_url, login_data_email)
    print(f"登录响应状态码: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ 邮箱登录成功 - 已重定向")
        print(f"重定向到: {response.url}")
    elif response.status_code == 200:
        print("❌ 邮箱登录失败 - 返回登录页面")
        
        # 检查表单错误
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            if form and hasattr(form, 'errors') and form.errors:
                print(f"表单错误: {form.errors}")
            if form and hasattr(form, 'non_field_errors'):
                non_field_errors = form.non_field_errors()
                if non_field_errors:
                    print(f"非字段错误: {non_field_errors}")
    else:
        print(f"❌ 意外的状态码: {response.status_code}")
    
    # 清理
    user.delete()
    print("🧹 测试用户已删除")

if __name__ == '__main__':
    debug_login_issue()
