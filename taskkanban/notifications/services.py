"""
邮件通知服务
提供邮件发送、模板渲染、队列管理等功能
"""

import logging
from datetime import timedelta
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from celery import shared_task

from .models import (
    EmailTemplate, EmailNotification, UserNotificationPreference,
    NotificationQueue, UnsubscribeToken
)

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务类"""
    
    @staticmethod
    def get_user_preference(user):
        """获取用户通知偏好，如果不存在则创建默认设置"""
        preference, created = UserNotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'email_enabled': True,
                'email_verified': bool(user.email),
            }
        )
        return preference
    
    @staticmethod
    def should_send_notification(user, template_type: str) -> bool:
        """检查是否应该发送通知"""
        preference = EmailService.get_user_preference(user)
        
        # 检查用户是否启用邮件通知
        if not preference.email_enabled:
            return False
        
        # 检查邮箱是否已验证
        if not preference.email_verified:
            return False
        
        # 检查特定类型的通知偏好
        frequency = getattr(preference, template_type, 'immediate')
        return frequency != 'never'
    
    @staticmethod
    def create_notification(
        recipient: User,
        template_type: str,
        context: Dict[str, Any],
        send_at: Optional[timezone.datetime] = None,
        related_task_id: Optional[int] = None,
        related_board_id: Optional[int] = None,
        related_team_id: Optional[int] = None
    ) -> Optional[EmailNotification]:
        """创建邮件通知"""
        
        # 检查是否应该发送
        if not EmailService.should_send_notification(recipient, template_type):
            logger.info(f"Skipping notification for {recipient.username}: {template_type}")
            return None
        
        # 获取邮件模板
        try:
            template = EmailTemplate.objects.get(template_type=template_type, is_active=True)
        except EmailTemplate.DoesNotExist:
            logger.error(f"Email template not found: {template_type}")
            return None
        
        # 渲染邮件内容
        try:
            # 添加通用上下文
            context.update({
                'user': recipient,
                'site_name': getattr(settings, 'SITE_NAME', '任务看板'),
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
                'unsubscribe_url': EmailService.generate_unsubscribe_url(recipient, template_type),
            })
            
            # 渲染主题和正文
            subject = Template(template.subject_template).render(Context(context))
            body = Template(template.body_template).render(Context(context))
            
        except Exception as e:
            logger.error(f"Error rendering email template {template_type}: {e}")
            return None
        
        # 创建通知记录
        notification = EmailNotification.objects.create(
            recipient=recipient,
            recipient_email=recipient.email,
            template_type=template_type,
            subject=subject,
            body=body,
            is_html=template.is_html,
            send_at=send_at or timezone.now(),
            related_task_id=related_task_id,
            related_board_id=related_board_id,
            related_team_id=related_team_id,
        )
        
        logger.info(f"Created email notification {notification.id} for {recipient.username}")
        return notification
    
    @staticmethod
    def send_notification(notification: EmailNotification) -> bool:
        """发送单个邮件通知"""
        try:
            # 更新状态为发送中
            notification.status = 'sending'
            notification.save(update_fields=['status'])
            
            # 发送邮件
            if notification.is_html:
                # HTML邮件
                msg = EmailMultiAlternatives(
                    subject=notification.subject,
                    body=notification.body,  # 纯文本版本
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[notification.recipient_email],
                )
                msg.attach_alternative(notification.body, "text/html")
                msg.send()
            else:
                # 纯文本邮件
                send_mail(
                    subject=notification.subject,
                    message=notification.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notification.recipient_email],
                    fail_silently=False,
                )
            
            # 更新状态为已发送
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save(update_fields=['status', 'sent_at'])
            
            logger.info(f"Successfully sent email notification {notification.id}")
            return True
            
        except Exception as e:
            # 更新状态为发送失败
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save(update_fields=['status', 'error_message'])
            
            logger.error(f"Failed to send email notification {notification.id}: {e}")
            return False
    
    @staticmethod
    def generate_unsubscribe_url(user: User, template_type: str = '') -> str:
        """生成退订链接"""
        # 创建退订令牌
        token = UnsubscribeToken.objects.create(
            user=user,
            template_type=template_type,
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return f"{base_url}/notifications/unsubscribe/{token.token}/"
    
    @staticmethod
    def process_unsubscribe(token: str) -> bool:
        """处理退订请求"""
        try:
            unsubscribe_token = UnsubscribeToken.objects.get(token=token)
            
            if not unsubscribe_token.is_valid():
                return False
            
            # 使用令牌
            unsubscribe_token.use_token()
            
            # 更新用户偏好
            preference = EmailService.get_user_preference(unsubscribe_token.user)
            
            if unsubscribe_token.template_type:
                # 特定类型退订
                setattr(preference, unsubscribe_token.template_type, 'never')
            else:
                # 全部退订
                preference.email_enabled = False
            
            preference.save()
            
            logger.info(f"User {unsubscribe_token.user.username} unsubscribed from {unsubscribe_token.template_type or 'all'}")
            return True
            
        except UnsubscribeToken.DoesNotExist:
            logger.warning(f"Invalid unsubscribe token: {token}")
            return False
        except Exception as e:
            logger.error(f"Error processing unsubscribe: {e}")
            return False


class NotificationTrigger:
    """通知触发器 - 在业务事件发生时触发相应的邮件通知"""
    
    @staticmethod
    def task_assigned(task, assigned_users: List[User], assigned_by: User):
        """任务分配通知"""
        for user in assigned_users:
            if user != assigned_by:  # 不给自己发通知
                EmailService.create_notification(
                    recipient=user,
                    template_type='task_assigned',
                    context={
                        'task': task,
                        'assigned_by': assigned_by,
                        'board': task.board,
                    },
                    related_task_id=task.id,
                    related_board_id=task.board.id,
                )
    
    @staticmethod
    def task_status_changed(task, old_status: str, new_status: str, changed_by: User):
        """任务状态变更通知"""
        # 通知任务的所有相关用户
        recipients = set()
        recipients.add(task.creator)
        recipients.update(task.assignees.all())
        recipients.discard(changed_by)  # 不给操作者自己发通知
        
        for user in recipients:
            EmailService.create_notification(
                recipient=user,
                template_type='task_status_changed',
                context={
                    'task': task,
                    'old_status': old_status,
                    'new_status': new_status,
                    'changed_by': changed_by,
                    'board': task.board,
                },
                related_task_id=task.id,
                related_board_id=task.board.id,
            )
    
    @staticmethod
    def task_due_reminder(task):
        """任务截止提醒"""
        # 通知任务的所有分配用户
        for user in task.assignees.all():
            EmailService.create_notification(
                recipient=user,
                template_type='task_due_reminder',
                context={
                    'task': task,
                    'board': task.board,
                    'due_date': task.due_date,
                },
                related_task_id=task.id,
                related_board_id=task.board.id,
            )
    
    @staticmethod
    def team_invitation(team, invited_user: User, invited_by: User):
        """团队邀请通知"""
        EmailService.create_notification(
            recipient=invited_user,
            template_type='team_invitation',
            context={
                'team': team,
                'invited_by': invited_by,
                'accept_url': f"/teams/{team.id}/join/",
            },
            related_team_id=team.id,
        )
    
    @staticmethod
    def board_member_added(board, new_member: User, added_by: User):
        """看板成员添加通知"""
        if new_member != added_by:
            EmailService.create_notification(
                recipient=new_member,
                template_type='board_member_added',
                context={
                    'board': board,
                    'added_by': added_by,
                    'board_url': f"/boards/{board.slug}/",
                },
                related_board_id=board.id,
            )


# Celery 异步任务

@shared_task
def send_email_notification_task(notification_id: str):
    """异步发送邮件通知"""
    try:
        notification = EmailNotification.objects.get(id=notification_id)
        return EmailService.send_notification(notification)
    except EmailNotification.DoesNotExist:
        logger.error(f"Email notification {notification_id} not found")
        return False


@shared_task
def send_pending_notifications():
    """发送所有待发送的邮件通知"""
    notifications = EmailNotification.objects.filter(
        status='pending',
        send_at__lte=timezone.now()
    )
    
    sent_count = 0
    failed_count = 0
    
    for notification in notifications:
        if EmailService.send_notification(notification):
            sent_count += 1
        else:
            failed_count += 1
    
    logger.info(f"Sent {sent_count} notifications, {failed_count} failed")
    return {'sent': sent_count, 'failed': failed_count}


@shared_task
def send_daily_summary():
    """发送每日工作摘要"""
    # 获取需要每日摘要的用户
    users = User.objects.filter(
        notification_preference__daily_summary='daily',
        notification_preference__email_enabled=True,
        notification_preference__email_verified=True,
    )
    
    for user in users:
        # 获取用户今天的任务活动
        today = timezone.now().date()
        
        # 这里可以根据需要收集用户的任务数据
        context = {
            'date': today,
            'user': user,
            # 添加更多摘要数据...
        }
        
        EmailService.create_notification(
            recipient=user,
            template_type='daily_summary',
            context=context,
        )


@shared_task
def send_due_date_reminders():
    """发送任务截止日期提醒"""
    from tasks.models import Task
    
    # 获取明天截止的任务
    tomorrow = timezone.now().date() + timedelta(days=1)
    due_tasks = Task.objects.filter(
        due_date__date=tomorrow,
        status__in=['todo', 'in_progress']
    ).select_related('board').prefetch_related('assignees')
    
    for task in due_tasks:
        NotificationTrigger.task_due_reminder(task)


@shared_task
def cleanup_old_notifications():
    """清理旧的通知记录"""
    # 删除30天前的已发送通知
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted_count, _ = EmailNotification.objects.filter(
        status='sent',
        sent_at__lt=cutoff_date
    ).delete()
    
    logger.info(f"Cleaned up {deleted_count} old notifications")
    return deleted_count
