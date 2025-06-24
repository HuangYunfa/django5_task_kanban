#!/usr/bin/env python
"""
测试和修复邮箱验证链接问题
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

from django.test import Client
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

User = get_user_model()

def test_email_verification_link():
    """测试邮箱验证链接"""
    print("=== 测试邮箱验证链接 ===")
    
    # 您提供的验证链接
    test_link = "http://localhost:8000/users/email/verify/MQ/crwvt9-2fa6bbc292b31f6d25f2987ece788940/"
    
    # 解析链接参数
    uidb64 = "MQ"
    token = "crwvt9-2fa6bbc292b31f6d25f2987ece788940"
    
    print(f"测试链接: {test_link}")
    print(f"UID Base64: {uidb64}")
    print(f"Token: {token}")
    
    try:
        # 解码用户ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(f"解码后的用户ID: {uid}")
        
        # 查找用户
        user = User.objects.get(pk=uid)
        print(f"找到用户: {user.username} ({user.email})")
        print(f"当前验证状态: {user.email_verified}")
        
        # 验证token
        is_valid_token = default_token_generator.check_token(user, token)
        print(f"Token验证结果: {is_valid_token}")
        
        if is_valid_token:
            print("✅ Token有效，链接应该可以工作")
        else:
            print("❌ Token无效或已过期")
            # 生成新的验证链接
            new_token = default_token_generator.make_token(user)
            new_link = f"http://localhost:8000/users/email/verify/{uidb64}/{new_token}/"
            print(f"新的验证链接: {new_link}")
        
    except Exception as e:
        print(f"解析链接失败: {e}")
        return False
    
    # 测试实际访问
    print("\n--- 测试实际访问 ---")
    client = Client()
    
    try:
        # 访问验证链接
        verify_url = f"/users/email/verify/{uidb64}/{token}/"
        response = client.get(verify_url)
        
        print(f"访问 {verify_url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 302:
            print(f"重定向到: {response.url}")
            
            # 检查是否重定向到登录页
            if '/login/' in response.url:
                print("❌ 重定向到登录页，存在问题")
                return False
            else:
                print("✅ 重定向到其他页面，可能正常")
                
                # 检查用户验证状态是否更新
                user.refresh_from_db()
                print(f"验证后用户状态: {user.email_verified}")
                return user.email_verified
        elif response.status_code == 200:
            print("✅ 页面正常显示")
            return True
        else:
            print(f"❌ 异常状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"访问测试失败: {e}")
        return False

def check_dashboard_access():
    """检查dashboard访问权限"""
    print("\n=== 检查Dashboard访问权限 ===")
    
    client = Client()
    try:
        # 尝试访问dashboard
        response = client.get('/dashboard/')
        print(f"Dashboard访问状态码: {response.status_code}")
        
        if response.status_code == 302 and '/login/' in response.url:
            print("❌ Dashboard需要登录，这可能是问题所在")
            return False
        else:
            print("✅ Dashboard可以访问或重定向正常")
            return True
            
    except Exception as e:
        print(f"Dashboard访问测试失败: {e}")
        return False

def fix_email_verification_redirect():
    """修复邮箱验证重定向问题"""
    print("\n=== 修复邮箱验证重定向 ===")
    
    # 检查是否存在common应用的dashboard
    try:
        from django.urls import reverse
        dashboard_url = reverse('common:dashboard')
        print(f"Dashboard URL: {dashboard_url}")
    except Exception as e:
        print(f"Dashboard URL解析失败: {e}")
        print("建议修改邮箱验证视图的重定向目标")
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始测试和修复邮箱验证链接问题...")
    print("=" * 60)
    
    # 1. 测试验证链接
    link_ok = test_email_verification_link()
    
    # 2. 检查dashboard访问
    dashboard_ok = check_dashboard_access()
    
    # 3. 修复建议
    print("\n" + "=" * 60)
    print("测试完成！")
    
    if link_ok:
        print("✅ 邮箱验证链接功能正常")
    else:
        print("❌ 邮箱验证链接存在问题")
        
        print("\n🔧 修复建议:")
        print("1. 检查common应用的dashboard视图是否需要登录")
        print("2. 考虑修改验证成功后的重定向目标")
        print("3. 确保验证视图本身不需要登录")
    
    if not dashboard_ok:
        print("\n⚠️  Dashboard需要登录，建议修改验证成功后的重定向")
        print("可以重定向到:")
        print("- 用户资料页面")
        print("- 登录页面并显示成功消息")
        print("- 专门的验证成功页面")

if __name__ == '__main__':
    main()
