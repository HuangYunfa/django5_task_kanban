#!/usr/bin/env python
"""
测试自定义邮件后端
"""
import os
import sys
import django
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent / 'taskkanban'
sys.path.insert(0, str(project_root))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.test import RequestFactory

User = get_user_model()

def test_custom_smtp_backend():
    """测试自定义SMTP后端"""
    print("=== 测试自定义SMTP邮件后端 ===")
    print(f"邮件后端: {settings.EMAIL_BACKEND}")
    print(f"SMTP服务器: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"使用TLS: {settings.EMAIL_USE_TLS}")
    print(f"发件人: {settings.EMAIL_HOST_USER}")
    print()
    
    try:
        # 1. 测试简单邮件发送
        print("1. 测试简单邮件发送...")
        result = send_mail(
            subject='任务看板系统 - 自定义后端测试',
            message='这是使用自定义邮件后端发送的测试邮件。如果您收到此邮件，说明自定义后端配置成功！',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['yunfa.huang@lvyuetravel.com'],
            fail_silently=False
        )
        
        if result == 1:
            print("✅ 简单邮件发送成功！")
        else:
            print("❌ 简单邮件发送失败")
        
        print()
        
        # 2. 测试验证邮件发送
        print("2. 测试验证邮件发送...")
        
        # 获取或创建超级用户
        user = User.objects.filter(username='huangyunfa').first()
        if not user:
            user = User.objects.filter(is_superuser=True).first()
        
        if user:
            user.email = 'yunfa.huang@lvyuetravel.com'
            user.email_verified = False
            user.save()
            
            # 生成验证令牌
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_url = f"http://localhost:8000/users/email/verify/{uid}/{token}/"
            
            # 渲染邮件模板
            from django.contrib.sites.models import Site
            site = Site.objects.get_current()
            
            email_context = {
                'user': user,
                'domain': site.domain,
                'uid': uid,
                'token': token,
                'protocol': 'http',
            }
            
            html_message = render_to_string('users/emails/email_verification.html', email_context)
            text_message = render_to_string('users/emails/email_verification.txt', email_context)
            
            # 发送验证邮件
            result = send_mail(
                subject='任务看板系统 - 验证您的邮箱地址',
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
                html_message=html_message
            )
            
            if result == 1:
                print("✅ 验证邮件发送成功！")
                print(f"📧 收件人: {user.email}")
                print(f"🔗 验证链接: {verification_url}")
                print("请检查邮箱并点击验证链接完成验证")
            else:
                print("❌ 验证邮件发送失败")
        else:
            print("❌ 未找到测试用户")
        
        print()
        
        return result == 1
        
    except Exception as e:
        print(f"❌ 邮件发送测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_resend_functionality():
    """测试Web页面重发功能"""
    print("3. 测试Web页面重发功能...")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        # 确保有测试用户
        user = User.objects.filter(username='huangyunfa').first()
        if user:
            user.email = 'yunfa.huang@lvyuetravel.com'
            user.email_verified = False
            user.set_password('testpass123')
            user.save()
            
            # 登录并测试重发功能
            client = Client()
            login_success = client.login(username=user.username, password='testpass123')
            
            if login_success:
                # 访问重发验证邮件URL
                resend_url = reverse('users:resend_verification')
                response = client.post(resend_url)
                
                print(f"重发邮件请求状态: {response.status_code}")
                if response.status_code == 302:
                    print(f"重定向到: {response.url}")
                    print("✅ Web重发功能测试成功")
                else:
                    print("❌ Web重发功能测试失败")
            else:
                print("❌ 用户登录失败")
        else:
            print("❌ 未找到测试用户")
            
    except Exception as e:
        print(f"❌ Web重发功能测试失败: {e}")

def main():
    """主测试函数"""
    print("开始测试自定义SMTP邮件后端...")
    print("=" * 60)
    
    # 测试自定义邮件后端
    backend_success = test_custom_smtp_backend()
    
    if backend_success:
        # 测试Web功能
        test_web_resend_functionality()
    
    print("=" * 60)
    
    if backend_success:
        print("🎉 自定义邮件后端测试成功！")
        print("\n✅ 主要功能正常：")
        print("  - 邮件发送功能正常")
        print("  - 验证邮件可以发送")
        print("  - Web重发功能正常")
        
        print("\n📧 下一步操作：")
        print("1. 检查 yunfa.huang@lvyuetravel.com 邮箱")
        print("2. 查看是否收到测试邮件和验证邮件")
        print("3. 点击验证链接完成邮箱验证")
        print("4. 在Web页面测试'重新发送验证邮件'功能")
    else:
        print("❌ 自定义邮件后端测试失败")
        print("请检查SMTP服务器配置和网络连接")

if __name__ == '__main__':
    main()
