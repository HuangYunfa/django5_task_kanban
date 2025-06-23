#!/usr/bin/env python
"""
调试用户资料更新问题的脚本
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

def debug_profile_update():
    """调试用户资料更新问题"""
    print("🔍 调试用户资料更新问题...")
    
    client = Client()
    
    # 创建测试用户
    user = User.objects.create_user(
        username='profileuser',
        password='TestPassword123!',
        email='profile@example.com',
        first_name='Profile',
        last_name='User'
    )
    print(f"✅ 测试用户已创建: {user.username}")
    
    # 登录用户
    login_success = client.login(username='profileuser', password='TestPassword123!')
    if login_success:
        print("✅ 用户登录成功")
    else:
        print("❌ 用户登录失败")
        return
    
    # 获取用户资料页面
    profile_url = reverse('users:profile')
    print(f"🔗 用户资料URL: {profile_url}")
    
    response = client.get(profile_url)
    print(f"📄 资料页面状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 用户资料页面可以正常访问")
        
        # 检查表单
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            if form:
                print(f"✅ 表单存在: {type(form)}")
                print(f"表单字段: {list(form.fields.keys())}")
            else:
                print("❌ 表单不存在")
        else:
            print("❌ 响应没有context")
    
    # 尝试更新用户资料
    update_data = {
        'first_name': '更新的名',
        'last_name': '更新的姓',
        'email': 'updated_profile@example.com',
        'nickname': '更新的昵称',
    }
    
    print(f"\n📝 尝试更新用户资料...")
    print(f"更新数据: {update_data}")
    
    response = client.post(profile_url, update_data)
    print(f"更新响应状态码: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ 用户资料更新成功 - 已重定向")
        print(f"重定向到: {response.url}")
        
        # 验证更新是否生效
        user.refresh_from_db()
        print(f"更新后的用户信息: {user.first_name} {user.last_name} - {user.email}")
        
    elif response.status_code == 200:
        print("❌ 用户资料更新失败 - 返回表单页面")
        
        # 检查表单错误
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            if form and hasattr(form, 'errors') and form.errors:
                print(f"表单错误: {form.errors}")
            if form and hasattr(form, 'non_field_errors'):
                non_field_errors = form.non_field_errors()
                if non_field_errors:
                    print(f"非字段错误: {non_field_errors}")
            
            # 检查CSRF错误
            if 'csrfmiddlewaretoken' not in response.content.decode():
                print("⚠️ 页面可能缺少CSRF token")
        else:
            print("❌ 响应没有context，无法获取错误信息")
    else:
        print(f"❌ 意外的状态码: {response.status_code}")
    
    # 清理
    user.delete()
    print("🧹 测试用户已删除")

if __name__ == '__main__':
    debug_profile_update()
