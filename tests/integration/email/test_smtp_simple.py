#!/usr/bin/env python
"""
简单的SMTP邮件测试
"""
import os
import sys
import django
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent / 'taskkanban'
sys.path.insert(0, str(project_root))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

def test_smtp_send():
    """测试SMTP邮件发送"""
    print("=== SMTP邮件发送测试 ===")
    print(f"SMTP配置:")
    print(f"  后端: {settings.EMAIL_BACKEND}")
    print(f"  服务器: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"  TLS: {settings.EMAIL_USE_TLS}")
    print(f"  用户: {settings.EMAIL_HOST_USER}")
    print(f"  发件人: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    try:
        # 发送测试邮件
        subject = "任务看板系统 - SMTP测试邮件"
        message = """
您好！

这是一封来自Django任务看板系统的测试邮件。

如果您收到这封邮件，说明SMTP邮件配置正常工作。

测试时间: {datetime}
系统状态: 正常运行

祝好，
任务看板团队
""".format(datetime=django.utils.timezone.now())
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['yunfa.huang@lvyuetravel.com'],
            fail_silently=False
        )
        
        if result == 1:
            print("✅ 邮件发送成功！")
            print(f"收件人: yunfa.huang@lvyuetravel.com")
            print("请检查邮箱是否收到邮件")
            return True
        else:
            print("❌ 邮件发送失败 - 未知错误")
            return False
            
    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")
        
        # 分析错误类型
        if "certificate verify failed" in str(e).lower():
            print("\n🔧 SSL证书问题解决方案:")
            print("1. 尝试使用不同的端口 (25, 465, 587)")
            print("2. 检查 EMAIL_USE_TLS 和 EMAIL_USE_SSL 设置")
            print("3. 联系邮件服务提供商确认SMTP配置")
        elif "authentication" in str(e).lower():
            print("\n🔧 认证问题解决方案:")
            print("1. 检查用户名和密码是否正确")
            print("2. 确认是否需要应用专用密码")
            print("3. 检查账户是否启用了SMTP服务")
        elif "connection" in str(e).lower():
            print("\n🔧 连接问题解决方案:")
            print("1. 检查网络连接")
            print("2. 确认SMTP服务器地址和端口")
            print("3. 检查防火墙设置")
        
        return False

def test_web_email_send():
    """测试Web界面的邮件发送"""
    print("\n=== Web界面邮件发送测试 ===")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        # 确保超级用户存在
        user = User.objects.filter(username='huangyunfa').first()
        if not user:
            print("创建测试用户...")
            user = User.objects.create_user(
                username='huangyunfa',
                email='yunfa.huang@lvyuetravel.com',
                password='testpass123',
                is_superuser=True,
                is_staff=True,
                email_verified=False
            )
        else:
            user.email_verified = False
            user.save()
        
        print(f"测试用户: {user.username} ({user.email})")
        
        # 创建客户端并登录
        client = Client()
        user.set_password('testpass123')
        user.save()
        
        login_success = client.login(username=user.username, password='testpass123')
        print(f"登录状态: {'成功' if login_success else '失败'}")
        
        if login_success:
            # 测试重新发送验证邮件
            resend_url = reverse('users:resend_verification')
            response = client.post(resend_url)
            
            print(f"重发邮件响应: {response.status_code}")
            if response.status_code == 302:
                print(f"重定向到: {response.url}")
                print("✅ Web界面邮件发送功能正常")
                return True
            else:
                print("❌ Web界面邮件发送可能有问题")
                return False
        else:
            print("❌ 无法登录，跳过Web测试")
            return False
            
    except Exception as e:
        print(f"❌ Web界面测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("开始SMTP邮件配置测试...")
    print("=" * 50)
    
    # 1. 测试SMTP发送
    smtp_ok = test_smtp_send()
    
    # 2. 测试Web界面
    if smtp_ok:
        web_ok = test_web_email_send()
    else:
        print("\nSMTP测试失败，跳过Web界面测试")
        web_ok = False
    
    print("\n" + "=" * 50)
    print("测试完成！")
    
    if smtp_ok and web_ok:
        print("\n🎉 邮件功能完全正常！")
        print("✅ SMTP发送正常")
        print("✅ Web界面功能正常")
        print("\n📧 请检查 yunfa.huang@lvyuetravel.com 邮箱")
        print("📋 下一步可以测试:")
        print("1. 访问 http://127.0.0.1:8000/users/profile/")
        print("2. 点击'重新发送验证邮件'按钮")
        print("3. 检查邮箱并点击验证链接")
    elif smtp_ok:
        print("\n⚠️  SMTP正常，但Web界面可能有问题")
    else:
        print("\n❌ SMTP配置需要调整")
        print("请检查邮件服务器配置")

if __name__ == '__main__':
    import django.utils.timezone
    main()
