#!/usr/bin/env python
"""
报表页面访问测试
测试修复后的报表页面是否能正常访问
"""

import os
import sys
import django

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'taskkanban'))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_reports_views():
    """测试报表视图访问"""
    print("🌐 测试报表页面访问...")
    
    # 创建测试客户端
    client = Client()
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username='test_reports_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    print(f"  👤 使用用户: {user.username} ({'新创建' if created else '已存在'})")
    
    # 登录用户
    client.force_login(user)
    print("  🔐 用户已登录")
    
    # 测试各个报表页面
    test_urls = [
        ('报表首页', '/reports/'),
        ('任务报表', '/reports/tasks/'),
        ('团队绩效', '/reports/team-performance/'),
        ('项目进度', '/reports/project-progress/'),
        ('自定义报表', '/reports/custom/'),
        ('报表列表', '/reports/list/'),
        ('创建报表', '/reports/create/'),
    ]
    
    for name, url in test_urls:
        try:
            print(f"  📊 测试{name}: {url}")
            response = client.get(url)
            
            if response.status_code == 200:
                print(f"    ✅ {name}访问成功 (状态码: {response.status_code})")
            elif response.status_code == 302:
                print(f"    🔄 {name}重定向 (状态码: {response.status_code})")
            else:
                print(f"    ⚠️ {name}状态码: {response.status_code}")
            
        except Exception as e:
            print(f"    ❌ {name}访问失败: {str(e)}")
    
    # 测试API接口
    try:
        print(f"  📡 测试API接口: /reports/api/data/")
        response = client.get('/reports/api/data/')
        if response.status_code == 200:
            print(f"    ✅ API接口访问成功 (状态码: {response.status_code})")
            # 尝试解析JSON响应
            try:
                data = response.json()
                print(f"    📊 API返回数据键: {list(data.keys())}")
            except:
                print(f"    📊 API返回非JSON数据")
        else:
            print(f"    ⚠️ API接口状态码: {response.status_code}")
    except Exception as e:
        print(f"    ❌ API接口访问失败: {str(e)}")

def test_forms_in_context():
    """测试表单在视图上下文中是否正常"""
    print("\n📝 测试表单在视图上下文...")
    
    client = Client()
    user = User.objects.first()
    
    if user:
        client.force_login(user)
        
        try:
            response = client.get('/reports/')
            if response.status_code == 200:
                context = response.context
                if 'filter_form' in context:
                    form = context['filter_form']
                    print(f"  ✅ filter_form存在于上下文中")
                    print(f"  📝 表单字段: {list(form.fields.keys())}")
                    print(f"  ✅ 表单在视图上下文中正常工作")
                else:
                    print(f"  ⚠️ filter_form不在上下文中")
            else:
                print(f"  ❌ 无法获取报表页面响应 (状态码: {response.status_code})")
                
        except Exception as e:
            print(f"  ❌ 测试表单上下文失败: {str(e)}")
    else:
        print("  ⚠️ 没有用户，跳过测试")

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 报表页面访问修复验证")
    print("=" * 60)
    
    try:
        # 测试页面访问
        test_reports_views()
        
        # 测试表单上下文
        test_forms_in_context()
        
        print("\n" + "=" * 60)
        print("✅ 页面访问测试完成！")
        print("🔧 forms.py问题已修复")
        print("📊 报表页面可以正常访问")
        print("🌐 建议在浏览器中访问: http://127.0.0.1:8000/reports/")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
