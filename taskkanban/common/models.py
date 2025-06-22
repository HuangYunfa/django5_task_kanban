from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Notification(models.Model):
    """
    通知模型
    """
    NOTIFICATION_TYPES = [
        ('task_assigned', _('任务分配')),
        ('task_due', _('任务到期')),
        ('task_completed', _('任务完成')),
        ('comment_added', _('新增评论')),
        ('mention', _('被提及')),
        ('board_invite', _('看板邀请')),
        ('team_invite', _('团队邀请')),
        ('system', _('系统通知')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('低')),
        ('normal', _('普通')),
        ('high', _('高')),
        ('urgent', _('紧急')),
    ]
    
    # 接收用户
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('接收用户')
    )
    
    # 发送用户（可选）
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True,
        verbose_name=_('发送用户')
    )
    
    # 通知内容
    notification_type = models.CharField(_('通知类型'), max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(_('标题'), max_length=200)
    message = models.TextField(_('消息内容'))
    
    # 关联对象
    content_type = models.CharField(_('内容类型'), max_length=50, blank=True, null=True)
    object_id = models.PositiveIntegerField(_('对象ID'), blank=True, null=True)
    url = models.URLField(_('跳转链接'), blank=True, null=True)
    
    # 状态
    is_read = models.BooleanField(_('已读'), default=False)
    is_sent = models.BooleanField(_('已发送'), default=False)
    priority = models.CharField(_('优先级'), max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # 时间字段
    read_at = models.DateTimeField(_('阅读时间'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('通知')
        verbose_name_plural = _('通知')
        db_table = 'common_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.recipient.get_display_name()} - {self.title}"


class ActivityLog(models.Model):
    """
    活动日志模型
    """
    ACTION_TYPES = [
        ('create', _('创建')),
        ('update', _('更新')),
        ('delete', _('删除')),
        ('login', _('登录')),
        ('logout', _('登出')),
        ('view', _('查看')),
        ('download', _('下载')),
        ('upload', _('上传')),
        ('share', _('分享')),
        ('invite', _('邀请')),
        ('join', _('加入')),
        ('leave', _('离开')),
        ('comment', _('评论')),
        ('mention', _('提及')),
    ]
    
    # 操作用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name=_('操作用户')
    )
    
    # 操作信息
    action = models.CharField(_('操作类型'), max_length=20, choices=ACTION_TYPES)
    description = models.TextField(_('操作描述'))
    
    # 关联对象
    content_type = models.CharField(_('内容类型'), max_length=50, blank=True, null=True)
    object_id = models.PositiveIntegerField(_('对象ID'), blank=True, null=True)
    object_repr = models.CharField(_('对象表示'), max_length=200, blank=True, null=True)
    
    # 元数据
    ip_address = models.GenericIPAddressField(_('IP地址'), blank=True, null=True)
    user_agent = models.TextField(_('用户代理'), blank=True, null=True)
    extra_data = models.JSONField(_('额外数据'), default=dict, blank=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('活动日志')
        verbose_name_plural = _('活动日志')
        db_table = 'common_activity_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} {self.get_action_display()} {self.object_repr or ''}"


class SystemSettings(models.Model):
    """
    系统设置模型
    """
    SETTING_TYPES = [
        ('string', _('字符串')),
        ('integer', _('整数')),
        ('boolean', _('布尔值')),
        ('json', _('JSON')),
        ('text', _('文本')),
    ]
    
    key = models.CharField(_('设置键'), max_length=100, unique=True)
    value = models.TextField(_('设置值'))
    value_type = models.CharField(_('值类型'), max_length=10, choices=SETTING_TYPES, default='string')
    
    name = models.CharField(_('设置名称'), max_length=200)
    description = models.TextField(_('设置描述'), blank=True, null=True)
    category = models.CharField(_('分类'), max_length=50, default='general')
    
    # 约束
    is_editable = models.BooleanField(_('可编辑'), default=True)
    is_public = models.BooleanField(_('公开设置'), default=False)
    
    # 更新信息
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='updated_settings',
        null=True,
        blank=True,
        verbose_name=_('更新人')
    )
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('系统设置')
        verbose_name_plural = _('系统设置')
        db_table = 'common_system_settings'
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.name} ({self.key})"
    
    def get_value(self):
        """获取转换后的值"""
        if self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.value_type == 'integer':
            try:
                return int(self.value)
            except ValueError:
                return 0
        elif self.value_type == 'json':
            import json
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return {}
        else:
            return self.value


class FileUpload(models.Model):
    """
    文件上传记录模型
    """
    # 上传用户
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        verbose_name=_('上传用户')
    )
    
    # 文件信息
    file = models.FileField(_('文件'), upload_to='uploads/%Y/%m/%d/')
    original_name = models.CharField(_('原始文件名'), max_length=255)
    file_size = models.PositiveIntegerField(_('文件大小'))
    content_type = models.CharField(_('内容类型'), max_length=100)
    file_hash = models.CharField(_('文件哈希'), max_length=64, blank=True, null=True)
    
    # 关联对象
    content_type_related = models.CharField(_('关联内容类型'), max_length=50, blank=True, null=True)
    object_id = models.PositiveIntegerField(_('关联对象ID'), blank=True, null=True)
    
    # 状态
    is_temporary = models.BooleanField(_('临时文件'), default=True)
    is_public = models.BooleanField(_('公开文件'), default=False)
    
    # 元数据
    metadata = models.JSONField(_('元数据'), default=dict, blank=True)
    
    created_at = models.DateTimeField(_('上传时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('文件上传')
        verbose_name_plural = _('文件上传')
        db_table = 'common_file_upload'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploaded_by', '-created_at']),
            models.Index(fields=['content_type_related', 'object_id']),
        ]
    
    def __str__(self):
        return self.original_name
    
    def get_file_size_display(self):
        """格式化文件大小显示"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
