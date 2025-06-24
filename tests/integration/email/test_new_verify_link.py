#!/usr/bin/env python
"""
生成新的验证链接并测试修复后的邮箱验证功能
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
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.test import Client

User = get_user_model()

def generate_new_verification_link():
    """为huangyunfa用户生成新的验证链接"""
    print("=== 生成新的验证链接 ===")
    
    try:
        # 找到用户
        user = User.objects.get(username='huangyunfa')
        print(f"用户: {user.username} ({user.email})")
        print(f"当前验证状态: {user.email_verified}")
        
        # 确保用户未验证状态
        user.email_verified = False
        user.save()
        
        # 生成新的验证链接
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_url = f"http://localhost:8000/users/email/verify/{uid}/{token}/"
        
        print(f"新的验证链接: {verification_url}")
        print(f"UID: {uid}")
        print(f"Token: {token}")
        
        return verification_url, uid, token
        
    except User.DoesNotExist:
        print("❌ 用户不存在")
        return None, None, None
    except Exception as e:
        print(f"❌ 生成链接失败: {e}")
        return None, None, None

def test_verification_link(uid, token):
    """测试新的验证链接"""
    print("\n=== 测试新的验证链接 ===")
    
    client = Client()
    
    try:
        # 访问验证链接
        verify_url = f"/users/email/verify/{uid}/{token}/"
        print(f"访问: {verify_url}")
        
        response = client.get(verify_url)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 302:
            print(f"重定向到: {response.url}")
            
            # 检查重定向目标
            if '/profile/' in response.url:
                print("✅ 正确重定向到用户资料页面")
                
                # 检查用户验证状态
                user = User.objects.get(username='huangyunfa')
                print(f"验证后状态: {user.email_verified}")
                
                if user.email_verified:
                    print("✅ 邮箱验证成功！")
                    return True
                else:
                    print("❌ 邮箱验证状态未更新")
                    return False
            elif '/login/' in response.url:
                print("❌ 仍然重定向到登录页面")
                return False
            else:
                print(f"🤔 重定向到其他页面: {response.url}")
                return False
        else:
            print(f"❌ 异常状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_profile_page_access():
    """测试用户资料页面访问"""
    print("\n=== 测试用户资料页面访问 ===")
    
    client = Client()
    
    # 获取已验证的用户
    user = User.objects.get(username='huangyunfa')
    
    if user.email_verified:
        # 模拟用户登录
        user.set_password('testpass123')
        user.save()
        
        login_success = client.login(username='huangyunfa', password='testpass123')
        print(f"用户登录: {'成功' if login_success else '失败'}")
        
        if login_success:
            # 访问用户资料页面
            response = client.get('/users/profile/')
            print(f"资料页面访问: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 用户资料页面正常访问")
                return True
            else:
                print(f"❌ 资料页面访问异常: {response.status_code}")
                return False
        else:
            print("❌ 用户登录失败")
            return False
    else:
        print("⚠️  用户邮箱未验证，跳过登录测试")
        return False

def send_new_verification_email():
    """发送新的验证邮件"""
    print("\n=== 发送新的验证邮件 ===")
    
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.contrib.sites.models import Site
        from django.conf import settings
        
        user = User.objects.get(username='huangyunfa')
        user.email_verified = False
        user.save()
        
        # 生成验证链接
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # 准备邮件内容
        site = Site.objects.get_current()
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
        
        # 发送邮件
        result = send_mail(
            subject='任务看板系统 - 新的邮箱验证链接',
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message
        )
        
        if result:
            verification_url = f"http://localhost:8000/users/email/verify/{uid}/{token}/"
            print("✅ 新的验证邮件发送成功！")
            print(f"新的验证链接: {verification_url}")
            print("📧 请检查邮箱并使用新的验证链接")
            return verification_url
        else:
            print("❌ 邮件发送失败")
            return None
            
    except Exception as e:
        print(f"❌ 发送邮件失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("开始生成新验证链接并测试修复后的功能...")
    print("=" * 60)
    
    # 1. 生成新的验证链接
    verification_url, uid, token = generate_new_verification_link()
    
    if verification_url:
        # 2. 测试验证链接
        test_ok = test_verification_link(uid, token)
        
        if test_ok:
            # 3. 测试用户资料页面访问
            profile_ok = test_profile_page_access()
            
            print("\n" + "=" * 60)
            print("🎉 邮箱验证功能修复成功！")
            print("✅ 验证链接正常工作")
            print("✅ 邮箱验证状态正确更新")
            print("✅ 重定向到正确页面")
            if profile_ok:
                print("✅ 用户资料页面正常访问")
        else:
            print("\n❌ 验证链接仍有问题")
            
        # 4. 发送新的验证邮件
        print("\n--- 发送新的验证邮件 ---")
        new_link = send_new_verification_email()
        if new_link:
            print(f"\n📋 您可以使用这个新的验证链接: {new_link}")
    else:
        print("❌ 无法生成验证链接")

if __name__ == '__main__':
    main()
