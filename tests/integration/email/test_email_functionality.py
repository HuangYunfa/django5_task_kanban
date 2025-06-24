#!/usr/bin/env python
"""
测试修复后的邮件验证功能
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from users.views import resend_verification_email

User = get_user_model()

@pytest.mark.django_db
def test_resend_verification_email():
    """测试重新发送验证邮件功能"""
    print("=== 测试重新发送验证邮件功能 ===")
    # 创建测试用户
    try:
        user = User.objects.filter(email='test@example.com').first()
        if not user:
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                email_verified=False  # 确保邮箱未验证
            )
            print(f"创建测试用户: {user}")
        else:
            user.email_verified = False
            user.save()
            print(f"使用现有用户: {user}")
        
        # 创建请求工厂
        factory = RequestFactory()
        request = factory.post('/users/email/resend/')
        
        # 设置用户
        request.user = user
        
        # 设置sessions和messages
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()
        
        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)
        
        # 调用视图函数
        response = resend_verification_email(request)
        
        print(f"响应状态码: {response.status_code}")
        print(f"重定向URL: {response.url}")
        
        # 检查消息
        messages = list(request._messages)
        for message in messages:
            print(f"消息: {message}")
        
        print("邮件重发测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_email_verification_token():
    """测试邮箱验证令牌生成"""
    print("=== 测试邮箱验证令牌生成 ===")
    
    try:
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        user = User.objects.filter(email='test@example.com').first()
        if user:
            # 生成令牌
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            print(f"用户ID: {user.pk}")
            print(f"编码后的UID: {uid}")
            print(f"生成的Token: {token}")
            
            # 验证令牌
            is_valid = default_token_generator.check_token(user, token)
            print(f"令牌验证结果: {is_valid}")
            
            # 生成验证链接
            verification_url = f"http://localhost:8000/users/email/verify/{uid}/{token}/"
            print(f"验证链接: {verification_url}")
        else:
            print("未找到测试用户")
            
    except Exception as e:
        print(f"令牌测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_user_email_status():
    """检查用户邮箱验证状态"""
    print("=== 检查用户邮箱验证状态 ===")
    
    try:
        users = User.objects.all()[:5]  # 获取前5个用户
        for user in users:
            print(f"用户: {user.username}")
            print(f"  邮箱: {user.email}")
            print(f"  邮箱已验证: {user.email_verified}")
            print(f"  注册时间: {user.date_joined}")
            print(f"  最后登录: {user.last_login}")
            print("---")
            
    except Exception as e:
        print(f"状态检查失败: {e}")
    
    print()

def main():
    """主函数"""
    print("开始测试修复后的邮件验证功能...")
    print("=" * 50)
    
    # 1. 检查用户邮箱验证状态
    test_user_email_status()
    
    # 2. 测试令牌生成
    test_email_verification_token()
    
    # 3. 测试重新发送验证邮件
    test_resend_verification_email()
    
    print("=" * 50)
    print("邮件验证功能测试完成！")
    
    print("\n=== 使用说明 ===")
    print("1. 当前使用console邮件后端，邮件内容会在Django运行的终端显示")
    print("2. 点击'重新发送验证邮件'按钮后，检查终端输出的邮件内容")
    print("3. 复制邮件中的验证链接到浏览器中访问即可完成验证")
    print("4. 要实际发送邮件，请配置真实的SMTP服务器")

if __name__ == '__main__':
    main()
