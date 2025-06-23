#!/usr/bin/env python
"""
模板渲染和导航问题调试脚本
"""
import os
import sys
import django
from django.conf import settings

# 添加项目目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'taskkanban'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')

# 初始化Django
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from django.template.loader import render_to_string
from django.template import Context, Template
from django.http import HttpRequest

User = get_user_model()

def test_url_patterns():
    """测试URL模式"""
    print("=== URL模式测试 ===")
    
    urls_to_test = [
        'common:index',
        'common:dashboard', 
        'users:profile',
        'users:settings',
        'account_login',
        'account_logout',
        'boards:list',
        'tasks:list',
        'teams:list',
        'reports:index'
    ]
    
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✓ {url_name}: {url}")
        except Exception as e:
            print(f"✗ {url_name}: {e}")

def test_template_rendering():
    """测试模板渲染"""
    print("\n=== 模板渲染测试 ===")
      # 创建测试用户
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        try:
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
        except Exception as e:
            # 如果用户已存在但用户名不同，尝试获取任何现有用户
            user = User.objects.first()
            if not user:
                print(f"无法创建或获取测试用户: {e}")
                return
    
    # 创建请求工厂
    factory = RequestFactory()
    request = factory.get('/')
    request.user = user
    
    # 测试base.html渲染
    try:
        context = {
            'user': user,
            'request': request
        }
        
        # 简化的base模板测试
        simple_template = Template("""
        {% load static %}
        <nav class="navbar">
            {% if user.is_authenticated %}
                <ul class="navbar-nav">
                    <li><a href="{% url 'common:index' %}">首页</a></li>
                    <li><a href="{% url 'common:dashboard' %}">工作台</a></li>
                </ul>
                <ul class="navbar-nav">
                    <li class="dropdown">
                        <a href="#" id="userDropdown">{{ user.username }}</a>
                        <ul class="dropdown-menu">
                            <li><a href="{% url 'users:profile' %}">个人资料</a></li>
                            <li><a href="{% url 'account_logout' %}">退出登录</a></li>
                        </ul>
                    </li>
                </ul>
            {% endif %}
        </nav>
        """)
        
        rendered = simple_template.render(Context(context))
        print("✓ 基础导航模板渲染成功")
        print("渲染结果片段:")
        print(rendered[:500] + "..." if len(rendered) > 500 else rendered)
        
    except Exception as e:
        print(f"✗ 模板渲染失败: {e}")

def test_client_requests():
    """测试客户端请求"""
    print("\n=== 客户端请求测试 ===")
    
    client = Client()
    
    # 测试未登录访问
    print("1. 测试未登录访问首页:")
    try:
        response = client.get('/')
        print(f"   状态码: {response.status_code}")
        print(f"   模板: {[t.name for t in response.templates] if hasattr(response, 'templates') else 'N/A'}")
    except Exception as e:
        print(f"   错误: {e}")
      # 登录测试用户
    print("\n2. 登录测试用户:")
    try:
        user = User.objects.first()  # 获取任何现有用户
        if user:
            client.force_login(user)
            print(f"   ✓ 登录成功: {user.username}")
        else:
            print("   ✗ 没有可用的测试用户")
            return
    except Exception as e:
        print(f"   ✗ 登录失败: {e}")
        return
    
    # 测试已登录访问各页面
    pages_to_test = [
        ('/', '首页'),
        ('/dashboard/', '工作台'),
        ('/users/profile/', '个人资料'),
    ]
    
    print("\n3. 测试已登录用户访问:")
    for url, name in pages_to_test:
        try:
            response = client.get(url)
            print(f"   {name} ({url}): {response.status_code}")
            if response.status_code != 200:
                print(f"      重定向到: {response.get('Location', 'N/A')}")
        except Exception as e:
            print(f"   {name} ({url}): 错误 - {e}")

def test_allauth_urls():
    """测试django-allauth URL配置"""
    print("\n=== Allauth URL测试 ===")
    
    allauth_urls = [
        'account_login',
        'account_logout', 
        'account_signup'
    ]
    
    for url_name in allauth_urls:
        try:
            url = reverse(url_name)
            print(f"✓ {url_name}: {url}")
        except Exception as e:
            print(f"✗ {url_name}: {e}")

def main():
    """主函数"""
    print("开始Django导航和模板渲染调试...")
    
    test_url_patterns()
    test_allauth_urls()
    test_template_rendering()
    test_client_requests()
    
    print("\n调试完成！")

if __name__ == '__main__':
    main()
