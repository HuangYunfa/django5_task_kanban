#!/usr/bin/env python
"""
测试真实SMTP邮件配置
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

def test_smtp_configuration():
    """测试SMTP配置"""
    print("=== 当前SMTP配置检查 ===")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'***设置***' if settings.EMAIL_HOST_PASSWORD else '未设置'}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()

def test_simple_email_send():
    """测试简单邮件发送"""
    print("=== 测试简单邮件发送 ===")
    
    # 使用真实邮箱地址进行测试
    test_email = input("请输入您的测试邮箱地址（用于接收测试邮件）: ").strip()
    if not test_email:
        print("未输入邮箱地址，跳过简单邮件测试")
        return False
    
    try:
        subject = '任务看板系统 - 邮件配置测试'
        message = '''
这是一封来自任务看板系统的测试邮件。

如果您收到此邮件，说明邮件配置已经成功！

测试时间: {datetime}
发送方式: 真实SMTP服务器
'''.format(datetime=django.utils.timezone.now())
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False
        )
        
        if result:
            print(f"✅ 简单邮件发送成功！")
            print(f"   收件人: {test_email}")
            print(f"   发件人: {settings.DEFAULT_FROM_EMAIL}")
            print(f"   请检查您的邮箱是否收到测试邮件")
            return True
        else:
            print("❌ 邮件发送失败 - 返回值为0")
            return False
            
    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")
        if "Authentication" in str(e):
            print("   错误类型: SMTP认证失败")
            print("   建议检查: 用户名和密码是否正确")
        elif "Connection" in str(e):
            print("   错误类型: 连接失败")
            print("   建议检查: SMTP服务器地址和端口是否正确")
        elif "timed out" in str(e).lower():
            print("   错误类型: 连接超时")
            print("   建议检查: 网络连接和防火墙设置")
        return False

def test_verification_email_send():
    """测试验证邮件发送"""
    print("\n=== 测试验证邮件发送 ===")
    
    # 获取或创建测试用户
    test_email = input("请输入接收验证邮件的邮箱地址: ").strip()
    if not test_email:
        print("未输入邮箱地址，跳过验证邮件测试")
        return False
    
    try:
        # 创建或获取测试用户
        user, created = User.objects.get_or_create(
            email=test_email,
            defaults={
                'username': f'testuser_{test_email.split("@")[0]}',
                'email_verified': False
            }
        )
        
        if not created:
            user.email_verified = False
            user.save()
        
        print(f"测试用户: {user.username} ({user.email})")
        
        # 创建请求对象
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_HOST'] = 'localhost:8000'
        
        # 准备邮件内容
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        
        subject = '验证您的邮箱地址 - 任务看板系统'
        
        email_context = {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'protocol': 'http',
        }
        
        # 渲染邮件模板
        html_message = render_to_string('users/emails/email_verification.html', email_context)
        text_message = render_to_string('users/emails/email_verification.txt', email_context)
        
        # 发送验证邮件
        result = send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message
        )
        
        if result:
            print("✅ 验证邮件发送成功！")
            print(f"   收件人: {user.email}")
            print(f"   验证链接: http://localhost:8000/users/email/verify/{email_context['uid']}/{email_context['token']}/")
            print("   请检查邮箱并点击验证链接完成验证")
            return True
        else:
            print("❌ 验证邮件发送失败")
            return False
            
    except Exception as e:
        print(f"❌ 验证邮件发送失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_smtp_connection():
    """测试SMTP连接"""
    print("\n=== 测试SMTP连接 ===")
    
    try:
        from django.core.mail import get_connection
        
        connection = get_connection(
            backend=settings.EMAIL_BACKEND,
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
        )
        
        # 尝试打开连接
        is_open = connection.open()
        
        if is_open:
            print("✅ SMTP连接成功建立")
            connection.close()
            return True
        else:
            print("❌ SMTP连接失败")
            return False
            
    except Exception as e:
        print(f"❌ SMTP连接测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("开始测试真实SMTP邮件配置...")
    print("=" * 60)
    
    # 1. 检查配置
    test_smtp_configuration()
    
    # 2. 测试SMTP连接
    connection_ok = test_smtp_connection()
    
    if not connection_ok:
        print("❌ SMTP连接失败，无法继续邮件发送测试")
        return
    
    # 3. 测试简单邮件发送
    simple_ok = test_simple_email_send()
    
    if simple_ok:
        # 4. 测试验证邮件发送
        verification_ok = test_verification_email_send()
    
    print("\n" + "=" * 60)
    print("邮件配置测试完成！")
    
    if connection_ok and simple_ok:
        print("\n🎉 邮件配置测试成功！")
        print("✅ SMTP连接正常")
        print("✅ 邮件发送功能正常")
        print("✅ 可以接收真实邮件")
        
        print("\n📧 接下来您可以：")
        print("1. 在网站上注册新用户，会自动发送验证邮件")
        print("2. 在用户资料页面点击'重新发送验证邮件'")
        print("3. 接收邮件并点击验证链接完成验证")
    else:
        print("\n❌ 邮件配置仍有问题")
        print("请检查SMTP服务器配置和网络连接")

if __name__ == '__main__':
    import django.utils.timezone
    main()
