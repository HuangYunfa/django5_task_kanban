#!/usr/bin/env python
"""
快速邮件配置工具 - 根据用户原有代码配置
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

from core.models import EmailConfiguration

def create_correct_email_config():
    """根据用户原有代码创建正确的邮件配置"""
    
    print("=== 根据您的原有代码创建正确的邮件配置 ===")
    print("分析您的代码:")
    print("  smtp = smtplib.SMTP(host, 80)    # 端口80")
    print("  smtp.starttls()                  # 使用TLS")
    print("  smtp.login(user, password)")
    print("")
    
    # 删除错误的配置
    try:
        old_config = EmailConfiguration.objects.get(name='default')
        print(f"删除错误的配置: {old_config}")
        old_config.delete()
    except EmailConfiguration.DoesNotExist:
        pass
    
    # 创建正确的配置
    config_data = {
        'name': 'default',
        'backend': 'django.core.mail.backends.smtp.EmailBackend',
        'host': 'smtp.163.com',
        'port': 80,
        'use_tls': True,   # 对应 smtp.starttls()
        'use_ssl': False,  # 没有使用SSL
        'username': 'hugo__huang@163.com',
        'password': 'demo123456',
        'default_from_email': 'hugo__huang@163.com',
        'is_active': True,
        'is_default': True,
        'timeout': 30,
        'description': '根据原有代码配置 - smtp.163.com:80 + TLS'
    }
    
    config = EmailConfiguration.objects.create(**config_data)
    print(f"✅ 邮件配置创建成功: {config}")
    
    # 测试连接
    print("\n🔧 测试邮件配置连接...")
    success, message = config.test_connection()
    
    if success:
        print(f"✅ 连接测试成功: {message}")
    else:
        print(f"❌ 连接测试失败: {message}")
    
    return config

def test_send_email(config):
    """测试发送邮件"""
    print(f"\n📧 测试发送邮件...")
    
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        # 临时设置邮件配置
        original_backend = getattr(settings, 'EMAIL_BACKEND', None)
        settings.EMAIL_BACKEND = 'core.email_backends.DatabaseConfigEmailBackend'
        
        result = send_mail(
            subject='测试邮件 - Django邮件配置',
            message='这是一封测试邮件，验证数据库邮件配置功能。\n\n发送时间: ' + str(django.utils.timezone.now()),
            from_email=None,  # 使用默认发件人
            recipient_list=['hugo__huang@163.com'],
            fail_silently=False,
        )
        
        if result:
            print(f"✅ 邮件发送成功！")
        else:
            print(f"❌ 邮件发送失败")
            
        # 恢复原始后端
        if original_backend:
            settings.EMAIL_BACKEND = original_backend
            
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def show_config_summary():
    """显示配置摘要"""
    print(f"\n{'='*50}")
    print("📋 邮件配置摘要")
    print(f"{'='*50}")
    
    configs = EmailConfiguration.objects.filter(is_active=True)
    
    for config in configs:
        print(f"\n配置名称: {config.name}")
        print(f"SMTP服务器: {config.host}")
        print(f"端口: {config.port}")
        print(f"用户名: {config.username}")
        print(f"密码: {'*' * len(config.password)}")
        print(f"使用TLS: {config.use_tls}")
        print(f"使用SSL: {config.use_ssl}")
        print(f"默认发件人: {config.default_from_email}")
        print(f"状态: {'✅ 默认' if config.is_default else '⚪ 备用'}")

def main():
    """主函数"""
    print("Django邮件配置快速修复工具")
    print("=" * 40)
    
    # 创建正确的配置
    config = create_correct_email_config()
    
    # 测试发送邮件
    test_send_email(config)
    
    # 显示配置摘要
    show_config_summary()
    
    print(f"\n💡 使用建议:")
    print(f"   1. 配置已根据您的原有代码创建")
    print(f"   2. 可通过Django管理界面进一步调整: http://127.0.0.1:8000/admin/core/emailconfiguration/")
    print(f"   3. 现有的邮件发送代码无需修改，会自动使用数据库配置")

if __name__ == '__main__':
    main()
