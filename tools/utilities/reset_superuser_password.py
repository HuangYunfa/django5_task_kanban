#!/usr/bin/env python
"""
重置超级用户密码脚本
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
from django.contrib.auth.hashers import make_password

User = get_user_model()

def reset_superuser_password():
    """重置超级用户密码"""
    print("=== 重置超级用户密码 ===")
    
    try:
        # 查找超级用户
        user = User.objects.get(username='huangyunfa', email='yunfa.huang@lvyuetravel.com')
        print(f"找到用户: {user.username} ({user.email})")
        print(f"超级用户: {user.is_superuser}")
        print(f"员工用户: {user.is_staff}")
        print(f"账户激活: {user.is_active}")
        
        # 设置新密码
        print("\n请输入新密码:")
        new_password = input("新密码: ").strip()
        
        if not new_password:
            print("❌ 密码不能为空")
            return False
        
        if len(new_password) < 6:
            print("❌ 密码长度至少6位")
            return False
        
        # 确认密码
        confirm_password = input("确认密码: ").strip()
        
        if new_password != confirm_password:
            print("❌ 两次输入的密码不一致")
            return False
        
        # 更新密码
        user.set_password(new_password)
        user.save()
        
        print(f"\n✅ 超级用户 {user.username} 密码重置成功！")
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        print(f"新密码: {new_password}")
        
        print("\n🔐 登录信息:")
        print("访问: http://127.0.0.1:8000/users/login/")
        print("或者: http://127.0.0.1:8000/admin/")
        
        return True
        
    except User.DoesNotExist:
        print("❌ 用户不存在")
        print("请检查用户名和邮箱是否正确")
        return False
    except Exception as e:
        print(f"❌ 重置密码失败: {e}")
        return False

def quick_reset_password():
    """快速重置密码（使用预设密码）"""
    print("=== 快速重置密码 ===")
    
    try:
        user = User.objects.get(username='huangyunfa', email='yunfa.huang@lvyuetravel.com')
        
        # 使用预设的临时密码
        temp_password = "huangyunfa123"
        user.set_password(temp_password)
        user.save()
        
        print(f"✅ 快速重置成功！")
        print(f"用户名: {user.username}")
        print(f"临时密码: {temp_password}")
        print("\n⚠️  请登录后立即修改密码！")
        
        print("\n🔐 登录方式:")
        print("1. 前台登录: http://127.0.0.1:8000/users/login/")
        print("2. 后台登录: http://127.0.0.1:8000/admin/")
        print("3. 登录后访问: http://127.0.0.1:8000/users/password/change/")
        
        return True
        
    except Exception as e:
        print(f"❌ 快速重置失败: {e}")
        return False

def check_user_info():
    """检查用户信息"""
    print("=== 检查用户信息 ===")
    
    try:
        user = User.objects.get(username='huangyunfa')
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        print(f"姓名: {user.get_full_name() or '未设置'}")
        print(f"昵称: {user.nickname or '未设置'}")
        print(f"超级用户: {user.is_superuser}")
        print(f"员工用户: {user.is_staff}")
        print(f"账户激活: {user.is_active}")
        print(f"邮箱验证: {user.email_verified}")
        print(f"注册时间: {user.date_joined}")
        print(f"最后登录: {user.last_login or '从未登录'}")
        return True
        
    except User.DoesNotExist:
        print("❌ 用户不存在")
        return False
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return False

def main():
    """主菜单"""
    print("Django超级用户密码重置工具")
    print("=" * 40)
    
    # 首先检查用户信息
    if not check_user_info():
        return
    
    print("\n请选择操作:")
    print("1. 交互式重置密码")
    print("2. 快速重置密码（使用临时密码）")
    print("3. 仅查看用户信息")
    print("0. 退出")
    
    choice = input("\n请输入选项 (0-3): ").strip()
    
    if choice == "1":
        reset_superuser_password()
    elif choice == "2":
        quick_reset_password()
    elif choice == "3":
        check_user_info()
    elif choice == "0":
        print("退出程序")
    else:
        print("❌ 无效选项")

if __name__ == '__main__':
    main()
