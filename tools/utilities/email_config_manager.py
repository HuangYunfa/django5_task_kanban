#!/usr/bin/env python
"""
邮件配置管理工具
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
from core.models import EmailConfiguration

User = get_user_model()

def create_default_email_config():
    """创建默认邮件配置"""
    print("=== 创建默认邮件配置 ===")
    
    # 检查是否已存在配置
    existing_config = EmailConfiguration.objects.filter(name='default').first()
    if existing_config:
        print(f"默认邮件配置已存在: {existing_config}")
        return existing_config
    
    # 从环境变量或用户输入获取配置
    print("请输入邮件配置信息:")
    
    name = input("配置名称 [default]: ").strip() or 'default'
    host = input("SMTP服务器 [smtp.lvyuetravel.com]: ").strip() or 'smtp.lvyuetravel.com'
    port = input("SMTP端口 [80]: ").strip() or '80'
    username = input("邮箱用户名 [LYtech@lvyuetravel.com]: ").strip() or 'LYtech@lvyuetravel.com'
    password = input("邮箱密码: ").strip()
    
    if not password:
        print("❌ 邮箱密码不能为空")
        return None
    
    use_tls = input("使用TLS? [y/N]: ").strip().lower() in ['y', 'yes', '1', 'true']
    use_ssl = input("使用SSL? [y/N]: ").strip().lower() in ['y', 'yes', '1', 'true']
    
    try:
        config = EmailConfiguration.objects.create(
            name=name,
            host=host,
            port=int(port),
            username=username,
            password=password,
            default_from_email=username,
            use_tls=use_tls,
            use_ssl=use_ssl,
            is_default=True,
            is_active=True,
            description=f"默认邮件配置 - {host}"
        )
        
        print(f"✅ 邮件配置创建成功: {config}")
        
        # 测试连接
        print("\n🔧 测试邮件配置...")
        success, message = config.test_connection()
        if success:
            print(f"✅ 连接测试成功: {message}")
        else:
            print(f"⚠️  连接测试失败: {message}")
            print("配置已保存，请检查网络连接和配置信息")
        
        return config
        
    except Exception as e:
        print(f"❌ 创建邮件配置失败: {e}")
        return None

def create_console_email_config():
    """创建控制台邮件配置（用于测试）"""
    print("=== 创建控制台邮件配置 ===")
    
    try:
        config = EmailConfiguration.objects.create(
            name='console',
            backend='django.core.mail.backends.console.EmailBackend',
            host='localhost',
            port=25,
            username='test@localhost',
            password='dummy',
            default_from_email='test@localhost',
            use_tls=False,
            use_ssl=False,
            is_default=False,
            is_active=True,
            description="控制台邮件后端 - 用于开发测试"
        )
        
        print(f"✅ 控制台邮件配置创建成功: {config}")
        return config
        
    except Exception as e:
        print(f"❌ 创建控制台邮件配置失败: {e}")
        return None

def list_email_configs():
    """列出所有邮件配置"""
    print("=== 邮件配置列表 ===")
    
    configs = EmailConfiguration.objects.all()
    if not configs:
        print("没有找到邮件配置")
        return
    
    for config in configs:
        status = "✅ 激活" if config.is_active else "❌ 禁用"
        default = " [默认]" if config.is_default else ""
        print(f"{config.name}: {config.host}:{config.port} - {status}{default}")
        print(f"   用户: {config.username}")
        print(f"   后端: {config.backend}")
        print(f"   描述: {config.description}")
        print()

def test_email_config(config_name=None):
    """测试邮件配置"""
    if config_name:
        config = EmailConfiguration.get_config_by_name(config_name)
        if not config:
            print(f"❌ 找不到配置: {config_name}")
            return
    else:
        config = EmailConfiguration.get_default_config()
        if not config:
            print("❌ 没有默认邮件配置")
            return
    
    print(f"=== 测试邮件配置: {config.name} ===")
    success, message = config.test_connection()
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def send_test_email():
    """发送测试邮件"""
    print("=== 发送测试邮件 ===")
    
    try:
        from django.core.mail import send_mail
        
        subject = "Django邮件配置测试"
        message = f"""
这是一封测试邮件，用于验证Django邮件配置是否正常工作。

发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

如果您收到这封邮件，说明邮件配置已正确设置。
        """.strip()
        
        to_email = input("收件人邮箱: ").strip()
        if not to_email:
            print("❌ 收件人邮箱不能为空")
            return
        
        send_mail(
            subject,
            message,
            None,  # 使用默认发件人
            [to_email],
            fail_silently=False,
        )
        
        print(f"✅ 测试邮件已发送到: {to_email}")
        
    except Exception as e:
        print(f"❌ 发送测试邮件失败: {e}")

def main():
    """主菜单"""
    print("Django邮件配置管理工具")
    print("=" * 40)
    
    while True:
        print("\n请选择操作:")
        print("1. 创建默认邮件配置")
        print("2. 创建控制台邮件配置")
        print("3. 列出所有邮件配置")
        print("4. 测试邮件配置")
        print("5. 发送测试邮件")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == "1":
            create_default_email_config()
        elif choice == "2":
            create_console_email_config()
        elif choice == "3":
            list_email_configs()
        elif choice == "4":
            config_name = input("配置名称 (留空使用默认): ").strip() or None
            test_email_config(config_name)
        elif choice == "5":
            send_test_email()
        elif choice == "0":
            print("退出程序")
            break
        else:
            print("❌ 无效选项")

if __name__ == '__main__':
    from datetime import datetime
    main()
