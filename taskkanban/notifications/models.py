from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

User = get_user_model()


class EmailTemplate(models.Model):
    """
    邮件模板模型
    """
    TEMPLATE_TYPES = [
        ('task_assigned', _('任务分配通知')),
        ('task_status_changed', _('任务状态变更')),
        ('task_due_reminder', _('任务截止提醒')),
        ('task_comment_mention', _('任务评论@提及')),
        ('team_invitation', _('团队邀请')),
        ('board_member_added', _('看板成员添加')),
        ('daily_summary', _('每日工作摘要')),
        ('weekly_summary', _('每周工作摘要')),
        ('team_activity_summary', _('团队活动摘要')),
    ]

    name = models.CharField(_('模板名称'), max_length=100)
    template_type = models.CharField(_('模板类型'), max_length=30, choices=TEMPLATE_TYPES, unique=True)
    subject_template = models.CharField(_('邮件主题模板'), max_length=200, help_text=_('支持Django模板语法'))
    body_template = models.TextField(_('邮件正文模板'), help_text=_('支持Django模板语法，支持HTML'))
    is_html = models.BooleanField(_('HTML格式'), default=True)
    is_active = models.BooleanField(_('启用'), default=True)
    
    # 系统字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('邮件模板')
        verbose_name_plural = _('邮件模板')
        db_table = 'notifications_email_template'
    
    def __str__(self):
        return f'{self.name} ({self.get_template_type_display()})'


class UserNotificationPreference(models.Model):
    """
    用户通知偏好设置
    """
    FREQUENCY_CHOICES = [
        ('immediate', _('立即通知')),
        ('daily', _('每日摘要')),
        ('weekly', _('每周摘要')),
        ('never', _('不接收')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preference',
        verbose_name=_('用户')
    )
    
    # 任务相关通知
    task_assigned = models.CharField(_('任务分配'), max_length=10, choices=FREQUENCY_CHOICES, default='immediate')
    task_status_changed = models.CharField(_('任务状态变更'), max_length=10, choices=FREQUENCY_CHOICES, default='immediate')
    task_due_reminder = models.CharField(_('任务截止提醒'), max_length=10, choices=FREQUENCY_CHOICES, default='immediate')
    task_comment_mention = models.CharField(_('任务评论@提及'), max_length=10, choices=FREQUENCY_CHOICES, default='immediate')
    
    # 团队协作通知
    team_invitation = models.CharField(_('团队邀请'), max_length=10, choices=FREQUENCY_CHOICES, default='immediate')
    board_member_added = models.CharField(_('看板成员添加'), max_length=10, choices=FREQUENCY_CHOICES, default='immediate')
    
    # 摘要通知
    daily_summary = models.CharField(_('每日工作摘要'), max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    weekly_summary = models.CharField(_('每周工作摘要'), max_length=10, choices=FREQUENCY_CHOICES, default='weekly')
    team_activity_summary = models.CharField(_('团队活动摘要'), max_length=10, choices=FREQUENCY_CHOICES, default='weekly')
    
    # 全局设置
    email_enabled = models.BooleanField(_('启用邮件通知'), default=True)
    email_verified = models.BooleanField(_('邮箱已验证'), default=False)
    
    # 系统字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('用户通知偏好')
        verbose_name_plural = _('用户通知偏好')
        db_table = 'notifications_user_preference'
    
    def __str__(self):
        return f'{self.user.username} 的通知偏好'


class EmailNotification(models.Model):
    """
    邮件通知记录
    """
    STATUS_CHOICES = [
        ('pending', _('待发送')),
        ('sending', _('发送中')),
        ('sent', _('已发送')),
        ('failed', _('发送失败')),
        ('cancelled', _('已取消')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 收件人信息
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_notifications',
        verbose_name=_('收件人')
    )
    recipient_email = models.EmailField(_('收件人邮箱'))
    
    # 邮件内容
    template_type = models.CharField(_('模板类型'), max_length=30, choices=EmailTemplate.TEMPLATE_TYPES)
    subject = models.CharField(_('邮件主题'), max_length=200)
    body = models.TextField(_('邮件正文'))
    is_html = models.BooleanField(_('HTML格式'), default=True)
    
    # 发送状态
    status = models.CharField(_('发送状态'), max_length=10, choices=STATUS_CHOICES, default='pending')
    send_at = models.DateTimeField(_('计划发送时间'), default=timezone.now)
    sent_at = models.DateTimeField(_('实际发送时间'), null=True, blank=True)
    error_message = models.TextField(_('错误信息'), blank=True, null=True)
    
    # 关联对象 (可选)
    related_task_id = models.PositiveIntegerField(_('关联任务ID'), null=True, blank=True)
    related_board_id = models.PositiveIntegerField(_('关联看板ID'), null=True, blank=True)
    related_team_id = models.PositiveIntegerField(_('关联团队ID'), null=True, blank=True)
    
    # 追踪信息
    read_at = models.DateTimeField(_('阅读时间'), null=True, blank=True)
    clicked_at = models.DateTimeField(_('点击时间'), null=True, blank=True)
    unsubscribed_at = models.DateTimeField(_('退订时间'), null=True, blank=True)
    
    # 系统字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('邮件通知')
        verbose_name_plural = _('邮件通知')
        db_table = 'notifications_email_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['template_type', 'status']),
            models.Index(fields=['send_at']),
        ]
    
    def __str__(self):
        return f'{self.get_template_type_display()} - {self.recipient.username}'
    
    def mark_as_read(self):
        """标记为已读"""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])
    
    def mark_as_clicked(self):
        """标记为已点击"""
        if not self.clicked_at:
            self.clicked_at = timezone.now()
            self.save(update_fields=['clicked_at'])
    
    def mark_as_unsubscribed(self):
        """标记为已退订"""
        if not self.unsubscribed_at:
            self.unsubscribed_at = timezone.now()
            self.save(update_fields=['unsubscribed_at'])


class NotificationQueue(models.Model):
    """
    通知队列模型 - 用于批量发送和定时发送
    """
    QUEUE_STATUS_CHOICES = [
        ('pending', _('待处理')),
        ('processing', _('处理中')),
        ('completed', _('已完成')),
        ('failed', _('处理失败')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('队列名称'), max_length=100)
    description = models.TextField(_('描述'), blank=True)
    
    # 队列类型
    queue_type = models.CharField(_('队列类型'), max_length=30, default='email')
    template_type = models.CharField(_('模板类型'), max_length=30, choices=EmailTemplate.TEMPLATE_TYPES)
    
    # 处理状态
    status = models.CharField(_('状态'), max_length=12, choices=QUEUE_STATUS_CHOICES, default='pending')
    scheduled_at = models.DateTimeField(_('计划执行时间'), default=timezone.now)
    started_at = models.DateTimeField(_('开始时间'), null=True, blank=True)
    completed_at = models.DateTimeField(_('完成时间'), null=True, blank=True)
    
    # 统计信息
    total_count = models.PositiveIntegerField(_('总数'), default=0)
    success_count = models.PositiveIntegerField(_('成功数'), default=0)
    failed_count = models.PositiveIntegerField(_('失败数'), default=0)
    
    # 错误信息
    error_message = models.TextField(_('错误信息'), blank=True, null=True)
    
    # 系统字段
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_notification_queues',
        verbose_name=_('创建人')
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('通知队列')
        verbose_name_plural = _('通知队列')
        db_table = 'notifications_queue'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} ({self.get_status_display()})'
    
    def mark_as_processing(self):
        """标记为处理中"""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def mark_as_completed(self):
        """标记为已完成"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def mark_as_failed(self, error_message: str = ''):
        """标记为处理失败"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])


class UnsubscribeToken(models.Model):
    """
    退订令牌模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(_('令牌'), max_length=64, unique=True, db_index=True)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='unsubscribe_tokens',
        verbose_name=_('用户')
    )
    
    # 退订类型 (空表示全部退订)
    template_type = models.CharField(
        _('模板类型'), 
        max_length=30, 
        choices=EmailTemplate.TEMPLATE_TYPES, 
        blank=True,
        help_text=_('留空表示全部退订')
    )
    
    # 令牌状态
    is_used = models.BooleanField(_('已使用'), default=False)
    used_at = models.DateTimeField(_('使用时间'), null=True, blank=True)
    expires_at = models.DateTimeField(_('过期时间'))
    
    # 系统字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('退订令牌')
        verbose_name_plural = _('退订令牌')
        db_table = 'notifications_unsubscribe_token'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} 的退订令牌'
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_token():
        """生成随机令牌"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def is_valid(self):
        """检查令牌是否有效"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def use_token(self):
        """使用令牌"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
