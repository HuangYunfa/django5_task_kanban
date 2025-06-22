from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from notifications.models import EmailTemplate, UserNotificationPreference, EmailNotification
from notifications.services import EmailService

User = get_user_model()

class Command(BaseCommand):
    help = '测试邮件通知系统功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-templates',
            action='store_true',
            help='创建基础邮件模板',
        )
        parser.add_argument(
            '--test-user',
            type=str,
            help='测试用户用户名',
            default='admin',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 开始邮件通知系统测试...'))
        
        if options['create_templates']:
            self.create_basic_templates()
        
        self.test_user_preferences(options['test_user'])
        self.test_notification_creation(options['test_user'])
        self.show_stats()
        
        self.stdout.write(self.style.SUCCESS('✅ 邮件通知系统测试完成！'))

    def create_basic_templates(self):
        """创建基础邮件模板"""
        self.stdout.write('📧 创建基础邮件模板...')
        
        templates = [
            {
                'template_type': 'task_assigned',
                'name': '任务分配通知',
                'subject_template': '[{{ site_name }}] 您有新的任务分配: {{ task.title }}',
                'body_template': '''
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>任务分配通知</title></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2c3e50;">您有新的任务分配</h2>
    <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #495057;">{{ task.title }}</h3>
        <p><strong>描述:</strong> {{ task.description|default:"无描述" }}</p>
        <p><strong>分配人:</strong> {{ assigned_by.username }}</p>
        <p><strong>看板:</strong> {{ board.name }}</p>
    </div>
    <div style="margin: 30px 0;">
        <a href="{{ site_url }}/tasks/{{ task.id }}/" 
           style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
            查看任务详情
        </a>
    </div>
    <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
    <p style="color: #6c757d; font-size: 12px;">
        如果您不想接收此类通知，可以 <a href="{{ unsubscribe_url }}">点击退订</a>。
    </p>
</body>
</html>
                ''',
                'is_html': True,
            },
            {
                'template_type': 'team_invitation',
                'name': '团队邀请通知',
                'subject_template': '[{{ site_name }}] 您被邀请加入团队: {{ team.name }}',
                'body_template': '''
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>团队邀请</title></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2c3e50;">团队邀请</h2>
    <p>您好！{{ invited_by.username }} 邀请您加入团队 <strong>{{ team.name }}</strong>。</p>
    <div style="margin: 30px 0;">
        <a href="{{ accept_url }}" 
           style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
            接受邀请
        </a>
    </div>
    <p style="color: #6c757d; font-size: 12px;">
        如果您不想接收此类通知，可以 <a href="{{ unsubscribe_url }}">点击退订</a>。
    </p>
</body>
</html>
                ''',
                'is_html': True,
            }
        ]
        
        for template_data in templates:
            template, created = EmailTemplate.objects.get_or_create(
                template_type=template_data['template_type'],
                defaults=template_data
            )
            
            if created:
                self.stdout.write(f'  ✅ 创建模板: {template.name}')
            else:
                self.stdout.write(f'  ℹ️  模板已存在: {template.name}')

    def test_user_preferences(self, username):
        """测试用户通知偏好"""
        self.stdout.write(f'👤 测试用户通知偏好: {username}')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'用户 {username} 不存在'))
            return
        
        preference = EmailService.get_user_preference(user)
        self.stdout.write(f'  ✅ 邮件启用: {preference.email_enabled}')
        self.stdout.write(f'  ✅ 邮箱验证: {preference.email_verified}')
        self.stdout.write(f'  ✅ 任务分配通知: {preference.task_assigned}')

    def test_notification_creation(self, username):
        """测试通知创建"""
        self.stdout.write(f'📨 测试通知创建: {username}')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'用户 {username} 不存在'))
            return
        
        # 模拟任务数据
        class MockTask:
            def __init__(self):
                self.id = 999
                self.title = "测试邮件通知任务"
                self.description = "这是一个用于测试邮件通知功能的模拟任务"
        
        class MockBoard:
            name = "测试看板"
        
        class MockUser:
            def __init__(self, username):
                self.username = username
        
        mock_task = MockTask()
        mock_task.board = MockBoard()
        mock_assigned_by = MockUser("系统管理员")
        
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
            self.stdout.write(f'  ✅ 通知创建成功: {notification.id}')
            self.stdout.write(f'  📧 邮件主题: {notification.subject}')
            
            # 尝试发送邮件
            if EmailService.send_notification(notification):
                self.stdout.write(f'  ✅ 邮件发送成功 (状态: {notification.get_status_display()})')
            else:
                self.stdout.write(f'  ❌ 邮件发送失败: {notification.error_message}')
        else:
            self.stdout.write('  ❌ 通知创建失败 (可能是用户关闭了通知或没有模板)')

    def show_stats(self):
        """显示通知系统统计"""
        self.stdout.write('📊 通知系统统计:')
        
        total_templates = EmailTemplate.objects.count()
        active_templates = EmailTemplate.objects.filter(is_active=True).count()
        total_notifications = EmailNotification.objects.count()
        pending_notifications = EmailNotification.objects.filter(status='pending').count()
        sent_notifications = EmailNotification.objects.filter(status='sent').count()
        
        self.stdout.write(f'  📧 邮件模板: {active_templates}/{total_templates} 个已激活')
        self.stdout.write(f'  📨 通知记录: {total_notifications} 个总数')
        self.stdout.write(f'     - 待发送: {pending_notifications} 个')
        self.stdout.write(f'     - 已发送: {sent_notifications} 个')
        
        users_count = User.objects.count()
        users_with_email = User.objects.exclude(email='').count()
        
        self.stdout.write(f'  👥 用户统计: {users_with_email}/{users_count} 个用户有邮箱')
