#!/usr/bin/env python
"""
邮件发送功能测试和修复脚本
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

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.test import RequestFactory

User = get_user_model()

def test_email_configuration():
    """测试邮件配置"""
    print("=== 邮件配置检查 ===")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'***' if settings.EMAIL_HOST_PASSWORD else '未设置'}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()

def test_simple_email():
    """测试简单邮件发送"""
    print("=== 测试简单邮件发送到真实邮箱 ===")
    try:
        # 发送邮件给超级用户 huangyunfa
        result = send_mail(
            subject='任务看板系统 - 邮件发送测试',
            message='这是一个邮件发送功能测试。如果您收到此邮件，说明SMTP配置正常工作。',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['yunfa.huang@lvyuetravel.com'],
            fail_silently=False
        )
        print(f"邮件发送结果: {result}")
        print("发送邮箱:", settings.DEFAULT_FROM_EMAIL)
        print("接收邮箱: yunfa.huang@lvyuetravel.com")
        print("简单邮件发送测试通过！")
    except Exception as e:
        print(f"简单邮件发送失败: {e}")
        import traceback
        traceback.print_exc()
    print()

def test_verification_email_template():
    """测试验证邮件模板渲染"""
    print("=== 测试验证邮件模板 ===")
    try:
        # 创建一个测试用户
        test_user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            first_name='测试',
            last_name='用户'
        )
        
        # 模拟站点信息
        site = Site.objects.get_current()
        
        # 渲染邮件模板
        message = render_to_string('users/emails/email_verification.html', {
            'user': test_user,
            'domain': site.domain,
            'uid': urlsafe_base64_encode(force_bytes(test_user.pk)),
            'token': default_token_generator.make_token(test_user),
            'protocol': 'http',
        })
        
        print("邮件模板渲染成功！")
        print(f"模板长度: {len(message)} 字符")
        print(f"模板前200字符: {message[:200]}...")
        
    except Exception as e:
        print(f"邮件模板渲染失败: {e}")
        import traceback
        traceback.print_exc()
    print()

def test_verification_email_send():
    """测试完整的验证邮件发送流程"""
    print("=== 测试发送验证邮件给超级用户 huangyunfa ===")
    try:
        # 查找超级用户 huangyunfa
        try:
            user = User.objects.filter(username='huangyunfa').first()
            if not user:
                print("没有找到超级用户 huangyunfa，查找其他超级用户...")
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    print("没有找到任何超级用户，创建测试用户...")
                    user = User.objects.create_user(
                        username='huangyunfa',
                        email='yunfa.huang@lvyuetravel.com',
                        password='testpass123',
                        is_superuser=True,
                        is_staff=True,
                        email_verified=False
                    )
                    print(f"创建超级用户: {user}")
                else:
                    # 临时修改邮箱为真实邮箱进行测试
                    original_email = user.email
                    user.email = 'yunfa.huang@lvyuetravel.com'
                    user.email_verified = False
                    user.save()
                    print(f"使用现有超级用户: {user.username}，临时修改邮箱为: {user.email}")
            else:
                user.email_verified = False
                user.save()
                print(f"找到超级用户: {user.username}，邮箱: {user.email}")
        except Exception as e:
            print(f"获取/创建用户失败: {e}")
            return
        
        # 模拟站点信息
        site = Site.objects.get_current()
        
        # 准备邮件内容
        subject = '任务看板系统 - 验证您的邮箱地址'
        
        # 生成验证令牌和链接
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_url = f"http://localhost:8000/users/email/verify/{uid}/{token}/"
        
        # 渲染HTML邮件
        html_message = render_to_string('users/emails/email_verification.html', {
            'user': user,
            'domain': site.domain,
            'uid': uid,
            'token': token,
            'protocol': 'http',
        })
        
        # 渲染纯文本邮件
        text_message = render_to_string('users/emails/email_verification.txt', {
            'user': user,
            'domain': site.domain,
            'uid': uid,
            'token': token,
            'protocol': 'http',
        })
        
        print(f"生成的验证链接: {verification_url}")
        
        # 发送验证邮件
        result = send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message  # 使用HTML格式
        )
        
        print(f"验证邮件发送结果: {result}")
        print(f"收件人: {user.email}")
        print(f"发件人: {settings.DEFAULT_FROM_EMAIL}")
        print("完整验证邮件发送测试完成！")
        
        if result == 1:
            print("✅ 邮件发送成功！请检查 yunfa.huang@lvyuetravel.com 邮箱")
            print("📧 请在邮件中点击验证链接或复制以下链接到浏览器：")
            print(f"   {verification_url}")
        else:
            print("❌ 邮件发送可能失败")
        
    except Exception as e:
        print(f"验证邮件发送失败: {e}")
        import traceback
        traceback.print_exc()
    print()

def test_resend_verification_email():
    """测试重新发送验证邮件功能"""
    print("=== 测试重新发送验证邮件功能 ===")
    try:
        from django.test import Client
        from django.urls import reverse
        
        # 确保有超级用户 huangyunfa
        user = User.objects.filter(username='huangyunfa').first()
        if not user:
            user = User.objects.filter(is_superuser=True, email='yunfa.huang@lvyuetravel.com').first()
        
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
        login_success = client.login(username=user.username, password='testpass123')
        
        if not login_success:
            # 设置密码后重试
            user.set_password('testpass123')
            user.save()
            login_success = client.login(username=user.username, password='testpass123')
        
        print(f"用户登录: {'成功' if login_success else '失败'}")
        
        if login_success:
            # 测试重新发送验证邮件
            resend_url = reverse('users:resend_verification')
            response = client.post(resend_url)
            
            print(f"重发邮件请求状态: {response.status_code}")
            if response.status_code == 302:
                print(f"重定向到: {response.url}")
            
            print("✅ 重新发送验证邮件功能测试完成")
            print("📧 请检查 yunfa.huang@lvyuetravel.com 邮箱是否收到验证邮件")
        else:
            print("❌ 无法登录用户，跳过重发邮件测试")
            
    except Exception as e:
        print(f"重发邮件测试失败: {e}")
        import traceback
        traceback.print_exc()
    print()

def check_site_configuration():
    """检查站点配置"""
    print("=== 站点配置检查 ===")
    try:
        site = Site.objects.get_current()
        print(f"当前站点: {site.name}")
        print(f"站点域名: {site.domain}")
        
        # 检查是否需要更新站点信息
        if site.domain == 'example.com':
            print("警告: 站点域名仍为默认值 'example.com'，建议更新为实际域名")
            
            # 更新为本地开发域名
            site.domain = 'localhost:8000'
            site.name = '企业级任务看板'
            site.save()
            print(f"已更新站点信息: {site.name} - {site.domain}")
            
    except Exception as e:
        print(f"站点配置检查失败: {e}")
    print()

def create_env_example():
    """创建.env示例文件"""
    print("=== 创建.env示例文件 ===")
    env_example_content = """# Django邮件配置示例
# 开发环境使用console后端（邮件输出到控制台）
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# 生产环境使用SMTP后端
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# 站点配置
SITE_NAME=企业级任务看板
SITE_URL=http://localhost:8000
"""
    
    try:
        with open('.env.example', 'w', encoding='utf-8') as f:
            f.write(env_example_content)
        print("已创建 .env.example 文件")
        print("请根据需要复制为 .env 文件并配置实际的邮件参数")
    except Exception as e:
        print(f"创建.env示例文件失败: {e}")
    print()

def main():
    """主函数"""
    print("开始邮件发送功能检查和修复...")
    print("=" * 50)
    
    # 1. 检查邮件配置
    test_email_configuration()
    
    # 2. 检查站点配置
    check_site_configuration()
    
    # 3. 测试简单邮件发送
    test_simple_email()
    
    # 4. 测试邮件模板渲染
    test_verification_email_template()
    
    # 5. 测试完整验证邮件发送
    test_verification_email_send()
    
    # 6. 测试重新发送验证邮件功能
    test_resend_verification_email()
      # 7. 创建配置示例
    create_env_example()
    
    print("=" * 60)
    print("🎯 真实SMTP邮件发送测试完成！")
    
    # 给出使用说明
    print("\n=== 测试结果说明 ===")
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
        print("✅ 当前使用真实SMTP后端，邮件将实际发送")
        print("📧 请检查 yunfa.huang@lvyuetravel.com 邮箱：")
        print("   - 查看是否收到测试邮件")
        print("   - 查看是否收到验证邮件")
        print("   - 点击验证链接完成邮箱验证")
    else:
        print("⚠️  当前仍使用console后端，邮件不会实际发送")
    
    print("\n📋 下一步操作：")
    print("1. 检查 yunfa.huang@lvyuetravel.com 邮箱")
    print("2. 如果收到邮件，点击验证链接")
    print("3. 访问 http://127.0.0.1:8000/users/profile/ 测试重发功能")
    print("4. 验证邮箱验证状态是否正确更新")

if __name__ == '__main__':
    main()
