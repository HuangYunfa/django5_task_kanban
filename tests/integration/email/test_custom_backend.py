#!/usr/bin/env python
"""
测试自定义SMTP邮件后端
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
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site

User = get_user_model()

def test_custom_smtp():
    """测试自定义SMTP后端"""
    print("=== 测试自定义SMTP邮件后端 ===")
    print(f"邮件后端: {settings.EMAIL_BACKEND}")
    print(f"SMTP服务器: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"用户: {settings.EMAIL_HOST_USER}")
    print(f"TLS: {settings.EMAIL_USE_TLS}")
    print()
    
    try:
        # 测试简单邮件
        print("1. 测试简单邮件发送...")
        result = send_mail(
            subject='任务看板系统 - 自定义SMTP测试',
            message='这是使用自定义SMTP后端发送的测试邮件。\n\n如果您收到此邮件，说明配置成功！',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['yunfa.huang@lvyuetravel.com'],
            fail_silently=False
        )
        
        if result == 1:
            print("✅ 简单邮件发送成功！")
        else:
            print("❌ 简单邮件发送失败")
            return False
        
        # 测试HTML邮件
        print("\n2. 测试HTML验证邮件发送...")
        
        # 获取或创建测试用户
        user = User.objects.filter(username='huangyunfa').first()
        if not user:
            user = User.objects.create_user(
                username='huangyunfa',
                email='yunfa.huang@lvyuetravel.com',
                password='testpass123',
                email_verified=False
            )
        else:
            user.email_verified = False
            user.save()
        
        # 生成验证链接
        site = Site.objects.get_current()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        email_context = {
            'user': user,
            'domain': site.domain,
            'uid': uid,
            'token': token,
            'protocol': 'http',
        }
        
        # 渲染邮件模板
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
            print("✅ HTML验证邮件发送成功！")
            print(f"验证链接: http://localhost:8000/users/email/verify/{uid}/{token}/")
            return True
        else:
            print("❌ HTML验证邮件发送失败")
            return False
            
    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_web_integration():
    """测试Web集成"""
    print("\n=== 测试Web集成 ===")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        # 确保用户存在
        user = User.objects.filter(username='huangyunfa').first()
        if user:
            user.email_verified = False
            user.set_password('testpass123')
            user.save()
            
            # 创建客户端并登录
            client = Client()
            login_success = client.login(username=user.username, password='testpass123')
            
            if login_success:
                print("✅ 用户登录成功")
                
                # 测试重新发送验证邮件
                resend_url = reverse('users:resend_verification')
                response = client.post(resend_url)
                
                print(f"重发邮件响应: {response.status_code}")
                if response.status_code == 302:
                    print("✅ Web界面邮件发送功能正常")
                    return True
                else:
                    print("❌ Web界面响应异常")
                    return False
            else:
                print("❌ 用户登录失败")
                return False
        else:
            print("❌ 找不到测试用户")
            return False
            
    except Exception as e:
        print(f"❌ Web集成测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("开始测试自定义SMTP邮件后端...")
    print("=" * 60)
    
    # 1. 测试自定义SMTP后端
    smtp_ok = test_custom_smtp()
    
    # 2. 测试Web集成
    if smtp_ok:
        web_ok = test_web_integration()
    else:
        web_ok = False
    
    print("\n" + "=" * 60)
    print("测试完成！")
    
    if smtp_ok and web_ok:
        print("\n🎉 自定义SMTP邮件后端测试成功！")
        print("✅ 基础邮件发送功能正常")
        print("✅ HTML邮件发送正常")
        print("✅ Web界面集成正常")
        print("\n📧 请检查 yunfa.huang@lvyuetravel.com 邮箱")
        print("📋 验证步骤:")
        print("1. 查看是否收到测试邮件")
        print("2. 查看是否收到验证邮件")
        print("3. 点击验证链接完成验证")
        print("4. 访问 http://127.0.0.1:8000/users/profile/ 测试重发功能")
    elif smtp_ok:
        print("\n⚠️  SMTP功能正常，但Web集成可能有问题")
    else:
        print("\n❌ 自定义SMTP后端测试失败")
        print("请检查SMTP配置参数")

if __name__ == '__main__':
    main()
