#!/usr/bin/env python
"""
邮件通知系统测试脚本
测试通知创建、模板渲染、用户偏好等功能
"""

import os
import sys
import django

# 设置Django环境
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
taskkanban_root = os.path.join(project_root, 'taskkanban')
sys.path.insert(0, taskkanban_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from notifications.models import (
    EmailTemplate, UserNotificationPreference, EmailNotification
)
from notifications.services import EmailService, NotificationTrigger

User = get_user_model()

def test_email_templates():
    """测试邮件模板创建"""
    print("🧪 测试邮件模板创建...")
    
    # 创建任务分配通知模板
    template, created = EmailTemplate.objects.get_or_create(
        template_type='task_assigned',
        defaults={
            'name': '任务分配通知',
            'subject_template': '[{{ site_name }}] 您有新的任务分配: {{ task.title }}',
            'body_template': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>任务分配通知</title>
</head>
<body>
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">您有新的任务分配</h2>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #495057;">{{ task.title }}</h3>
            <p><strong>描述:</strong> {{ task.description|default:"无描述" }}</p>
            <p><strong>分配人:</strong> {{ assigned_by.username }}</p>
            <p><strong>看板:</strong> {{ board.name }}</p>
            <p><strong>截止日期:</strong> {{ task.due_date|date:"Y-m-d H:i"|default:"未设置" }}</p>
        </div>
        
        <div style="margin: 30px 0;">
            <a href="{{ site_url }}/tasks/{{ task.id }}/" 
               style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                查看任务详情
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
        <p style="color: #6c757d; font-size: 12px;">
            如果您不想接收此类通知，可以 <a href="{{ unsubscribe_url }}">点击退订</a>。
        </p>
    </div>
</body>
</html>
            ''',
            'is_html': True,
            'is_active': True,
        }
    )
    
    if created:
        print(f"✅ 创建邮件模板: {template.name}")
    else:
        print(f"✅ 邮件模板已存在: {template.name}")
    
    return template

def test_user_preferences():
    """测试用户通知偏好"""
    print("\n🧪 测试用户通知偏好...")
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': '测试',
            'last_name': '用户',
        }
    )
    
    if created:
        print(f"✅ 创建测试用户: {user.username}")
    else:
        print(f"✅ 测试用户已存在: {user.username}")
    
    # 获取用户通知偏好
    preference = EmailService.get_user_preference(user)
    print(f"✅ 用户通知偏好: email_enabled={preference.email_enabled}, task_assigned={preference.task_assigned}")
    
    return user, preference

def test_notification_creation():
    """测试通知创建"""
    print("\n🧪 测试通知创建...")
    
    # 确保有邮件模板
    template = test_email_templates()
    user, preference = test_user_preferences()
    
    # 模拟任务数据
    class MockTask:
        def __init__(self):
            self.id = 1
            self.title = "测试任务标题"
            self.description = "这是一个测试任务的描述"
            self.due_date = timezone.now() + timezone.timedelta(days=7)
            
        class board:
            name = "测试看板"
    
    class MockUser:
        def __init__(self, username):
            self.username = username
    
    mock_task = MockTask()
    mock_assigned_by = MockUser("admin")
    
    # 创建通知
    notification = EmailService.create_notification(
        recipient=user,
        template_type='task_assigned',
        context={
            'task': mock_task,
            'assigned_by': mock_assigned_by,
            'board': mock_task.board,
        },
        related_task_id=mock_task.id,
    )
    
    if notification:
        print(f"✅ 成功创建通知: {notification.id}")
        print(f"   - 收件人: {notification.recipient.username}")
        print(f"   - 主题: {notification.subject}")
        print(f"   - 状态: {notification.get_status_display()}")
        return notification
    else:
        print("❌ 通知创建失败")
        return None

def test_email_sending():
    """测试邮件发送 (使用console backend)"""
    print("\n🧪 测试邮件发送...")
    
    notification = test_notification_creation()
    if not notification:
        print("❌ 无法测试邮件发送，通知创建失败")
        return False
    
    # 发送邮件
    success = EmailService.send_notification(notification)
    
    if success:
        print(f"✅ 邮件发送成功")
        print(f"   - 通知ID: {notification.id}")
        print(f"   - 发送状态: {notification.get_status_display()}")
        print(f"   - 发送时间: {notification.sent_at}")
        return True
    else:
        print(f"❌ 邮件发送失败")
        print(f"   - 错误信息: {notification.error_message}")
        return False

def test_unsubscribe_token():
    """测试退订令牌"""
    print("\n🧪 测试退订令牌...")
    
    user = User.objects.get(username='test_user')
    
    # 生成退订链接
    unsubscribe_url = EmailService.generate_unsubscribe_url(user, 'task_assigned')
    print(f"✅ 生成退订链接: {unsubscribe_url}")
    
    return True

def test_notification_stats():
    """测试通知统计"""
    print("\n📊 通知系统统计...")
    
    # 统计各种数据
    total_templates = EmailTemplate.objects.count()
    active_templates = EmailTemplate.objects.filter(is_active=True).count()
    total_notifications = EmailNotification.objects.count()
    pending_notifications = EmailNotification.objects.filter(status='pending').count()
    sent_notifications = EmailNotification.objects.filter(status='sent').count()
    failed_notifications = EmailNotification.objects.filter(status='failed').count()
    
    print(f"📧 邮件模板: {active_templates}/{total_templates} 个已激活")
    print(f"📨 通知记录: {total_notifications} 个总数")
    print(f"   - 待发送: {pending_notifications} 个")
    print(f"   - 已发送: {sent_notifications} 个")
    print(f"   - 发送失败: {failed_notifications} 个")
    
    # 用户偏好统计
    total_users = User.objects.count()
    users_with_notifications = UserNotificationPreference.objects.filter(email_enabled=True).count()
    print(f"👥 用户统计: {users_with_notifications}/{total_users} 个启用了邮件通知")

def main():
    """主测试函数"""
    print("🚀 开始邮件通知系统测试...")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_email_templates()
        test_user_preferences()
        test_notification_creation()
        test_email_sending()
        test_unsubscribe_token()
        test_notification_stats()
        
        print("\n" + "=" * 50)
        print("✅ 邮件通知系统测试完成！")
        print("\n💡 注意事项:")
        print("   - 当前使用console邮件后端，邮件将在控制台显示")
        print("   - 生产环境需要配置真实的SMTP邮件服务")
        print("   - 建议配置Celery异步任务队列处理邮件发送")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
