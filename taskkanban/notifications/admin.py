from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html
from .models import (
    EmailTemplate, UserNotificationPreference, EmailNotification,
    NotificationQueue, UnsubscribeToken
)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """邮件模板管理"""
    list_display = ['name', 'template_type', 'is_active', 'is_html', 'created_at']
    list_filter = ['template_type', 'is_active', 'is_html', 'created_at']
    search_fields = ['name', 'template_type', 'subject_template']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        (_('基本信息'), {
            'fields': ['name', 'template_type', 'is_active']
        }),
        (_('邮件内容'), {
            'fields': ['subject_template', 'body_template', 'is_html']
        }),
        (_('系统信息'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    """用户通知偏好管理"""
    list_display = [
        'user', 'email_enabled', 'email_verified', 
        'task_assigned', 'team_invitation', 'created_at'
    ]
    list_filter = [
        'email_enabled', 'email_verified', 'task_assigned', 
        'team_invitation', 'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        (_('用户信息'), {
            'fields': ['user', 'email_enabled', 'email_verified']
        }),
        (_('任务通知'), {
            'fields': [
                'task_assigned', 'task_status_changed', 
                'task_due_reminder', 'task_comment_mention'
            ]
        }),
        (_('团队通知'), {
            'fields': ['team_invitation', 'board_member_added']
        }),
        (_('摘要通知'), {
            'fields': ['daily_summary', 'weekly_summary', 'team_activity_summary']
        }),
        (_('系统信息'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    """邮件通知管理"""
    list_display = [
        'recipient', 'template_type', 'subject', 'status', 
        'send_at', 'sent_at', 'created_at'
    ]
    list_filter = [
        'status', 'template_type', 'is_html', 'send_at', 
        'sent_at', 'created_at'
    ]
    search_fields = [
        'recipient__username', 'recipient__email', 'subject', 
        'recipient_email'
    ]
    readonly_fields = [
        'id', 'sent_at', 'read_at', 'clicked_at', 'unsubscribed_at',
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = [
        (_('收件人信息'), {
            'fields': ['recipient', 'recipient_email']
        }),
        (_('邮件内容'), {
            'fields': ['template_type', 'subject', 'body', 'is_html']
        }),
        (_('发送状态'), {
            'fields': ['status', 'send_at', 'sent_at', 'error_message']
        }),
        (_('关联对象'), {
            'fields': ['related_task_id', 'related_board_id', 'related_team_id'],
            'classes': ['collapse']
        }),
        (_('追踪信息'), {
            'fields': ['read_at', 'clicked_at', 'unsubscribed_at'],
            'classes': ['collapse']
        }),
        (_('系统信息'), {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    actions = ['resend_failed_notifications', 'mark_as_sent']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient')
    
    def resend_failed_notifications(self, request, queryset):
        """重新发送失败的通知"""
        failed_notifications = queryset.filter(status='failed')
        count = 0
        
        for notification in failed_notifications:
            notification.status = 'pending'
            notification.error_message = ''
            notification.save(update_fields=['status', 'error_message'])
            count += 1
        
        self.message_user(request, f'已重置 {count} 个失败通知的状态，等待重新发送。')
    
    resend_failed_notifications.short_description = _('重新发送失败通知')
    
    def mark_as_sent(self, request, queryset):
        """标记为已发送"""
        from django.utils import timezone
        count = queryset.filter(status='pending').update(
            status='sent',
            sent_at=timezone.now()
        )
        self.message_user(request, f'已标记 {count} 个通知为已发送。')
    
    mark_as_sent.short_description = _('标记为已发送')


@admin.register(NotificationQueue)
class NotificationQueueAdmin(admin.ModelAdmin):
    """通知队列管理"""
    list_display = [
        'name', 'queue_type', 'template_type', 'status',
        'total_count', 'success_count', 'failed_count',
        'scheduled_at', 'created_at'
    ]
    list_filter = [
        'queue_type', 'template_type', 'status', 'scheduled_at', 'created_at'
    ]
    search_fields = ['name', 'description', 'template_type']
    readonly_fields = [
        'id', 'started_at', 'completed_at', 'total_count',
        'success_count', 'failed_count', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = [
        (_('基本信息'), {
            'fields': ['name', 'description', 'queue_type', 'template_type']
        }),
        (_('执行状态'), {
            'fields': ['status', 'scheduled_at', 'started_at', 'completed_at', 'error_message']
        }),
        (_('统计信息'), {
            'fields': ['total_count', 'success_count', 'failed_count']
        }),
        (_('系统信息'), {
            'fields': ['id', 'created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(UnsubscribeToken)
class UnsubscribeTokenAdmin(admin.ModelAdmin):
    """退订令牌管理"""
    list_display = [
        'user', 'template_type', 'is_used', 'expires_at', 'created_at'
    ]
    list_filter = [
        'template_type', 'is_used', 'expires_at', 'created_at'
    ]
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = [
        'id', 'token', 'is_used', 'used_at', 'created_at'
    ]
    
    fieldsets = [
        (_('令牌信息'), {
            'fields': ['id', 'token', 'user', 'template_type']
        }),
        (_('状态信息'), {
            'fields': ['is_used', 'used_at', 'expires_at']
        }),
        (_('系统信息'), {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
