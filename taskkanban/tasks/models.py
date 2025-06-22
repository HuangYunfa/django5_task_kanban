from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator
from django.utils import timezone
import uuid

# 导入工作流相关模型
from .workflow_models import (
    WorkflowStatus, WorkflowTransition, TaskStatusHistory, 
    WorkflowRule, WorkflowRuleExecution
)

User = get_user_model()


class Task(models.Model):
    """
    任务模型
    """
    PRIORITY_CHOICES = [
        ('low', _('低优先级')),
        ('normal', _('普通')),
        ('high', _('高优先级')),
        ('urgent', _('紧急')),
    ]
    
    STATUS_CHOICES = [
        ('todo', _('待办')),
        ('in_progress', _('进行中')),
        ('review', _('审核中')),
        ('done', _('已完成')),
        ('blocked', _('已阻塞')),
    ]
    
    # 基本信息
    title = models.CharField(
        _('任务标题'), 
        max_length=200, 
        validators=[MinLengthValidator(2)]
    )
    description = models.TextField(_('任务描述'), blank=True, null=True)
    
    # 关联关系
    board = models.ForeignKey(
        'boards.Board',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('所属看板')
    )
    board_list = models.ForeignKey(
        'boards.BoardList',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('所属列表')
    )
      # 任务分配
    assignees = models.ManyToManyField(
        User,
        through='TaskAssignment',
        through_fields=('task', 'user'),
        related_name='assigned_tasks',
        verbose_name=_('分配给'),
        blank=True
    )
    
    # 创建者和报告人
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name=_('创建者')
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='reported_tasks',
        null=True,
        blank=True,
        verbose_name=_('报告人')
    )
    
    # 任务属性
    priority = models.CharField(_('优先级'), max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(_('状态'), max_length=15, choices=STATUS_CHOICES, default='todo')
    position = models.PositiveIntegerField(_('排序位置'), default=0)
    
    # 标签
    labels = models.ManyToManyField(
        'boards.BoardLabel',
        related_name='tasks',
        verbose_name=_('标签'),
        blank=True
    )
    
    # 时间管理
    due_date = models.DateTimeField(_('截止日期'), null=True, blank=True)
    start_date = models.DateTimeField(_('开始日期'), null=True, blank=True)
    estimated_hours = models.DecimalField(
        _('预估工时'), 
        max_digits=5, 
        decimal_places=1, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.1), MaxValueValidator(999.9)]
    )
    actual_hours = models.DecimalField(
        _('实际工时'), 
        max_digits=5, 
        decimal_places=1, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.1), MaxValueValidator(999.9)]
    )
    
    # 进度管理
    progress = models.PositiveIntegerField(
        _('完成进度'), 
        default=0,
        validators=[MaxValueValidator(100)]
    )
    
    # 状态标记
    is_archived = models.BooleanField(_('已归档'), default=False)
    is_template = models.BooleanField(_('模板任务'), default=False)
    
    # 完成信息
    completed_at = models.DateTimeField(_('完成时间'), null=True, blank=True)
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='completed_tasks',
        null=True,
        blank=True,
        verbose_name=_('完成人')
    )
    
    # 系统字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('任务')
        verbose_name_plural = _('任务')
        db_table = 'tasks_task'
        ordering = ['position', '-created_at']
        indexes = [
            models.Index(fields=['board', 'board_list', 'position']),
            models.Index(fields=['creator', '-created_at']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status', '-updated_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # 自动设置完成时间和完成人
        if self.status == 'done' and not self.completed_at:
            self.completed_at = timezone.now()
            self.progress = 100
        elif self.status != 'done':
            self.completed_at = None
            self.completed_by = None
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """是否已过期"""
        if self.due_date and self.status != 'done':
            return timezone.now() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        """距离截止日期天数"""
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
    
    @property
    def assignee_count(self):
        """分配人数"""
        return self.assignees.count()
    
    @property
    def comment_count(self):
        """评论数量"""
        return self.comments.count()
    
    @property
    def attachment_count(self):
        """附件数量"""
        return self.attachments.count()
    
    @property
    def subtask_count(self):
        """子任务数量"""
        return self.subtasks.count()
    
    @property
    def completed_subtask_count(self):
        """已完成子任务数量"""
        return self.subtasks.filter(status='done').count()


class TaskAssignment(models.Model):
    """
    任务分配模型
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_('任务')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_assignments',
        verbose_name=_('用户')
    )
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_task_assignments',
        null=True,
        blank=True,
        verbose_name=_('分配人')
    )
    
    assigned_at = models.DateTimeField(_('分配时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('任务分配')
        verbose_name_plural = _('任务分配')
        db_table = 'tasks_assignment'
        unique_together = ('task', 'user')
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.task.title} -> {self.user.get_display_name()}"


class SubTask(models.Model):
    """
    子任务模型
    """
    parent_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='subtasks',
        verbose_name=_('父任务')
    )
    
    title = models.CharField(_('子任务标题'), max_length=200)
    description = models.TextField(_('描述'), blank=True, null=True)
    
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_subtasks',
        null=True,
        blank=True,
        verbose_name=_('分配给')
    )
    
    status = models.CharField(_('状态'), max_length=15, choices=Task.STATUS_CHOICES, default='todo')
    position = models.PositiveIntegerField(_('排序位置'), default=0)
    
    due_date = models.DateTimeField(_('截止日期'), null=True, blank=True)
    completed_at = models.DateTimeField(_('完成时间'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('子任务')
        verbose_name_plural = _('子任务')
        db_table = 'tasks_subtask'
        ordering = ['position', '-created_at']
    
    def __str__(self):
        return f"{self.parent_task.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if self.status == 'done' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'done':
            self.completed_at = None
        
        super().save(*args, **kwargs)


class TaskDependency(models.Model):
    """
    任务依赖关系模型
    """
    DEPENDENCY_TYPES = [
        ('blocks', _('阻塞')),
        ('depends_on', _('依赖于')),
        ('relates_to', _('关联')),
    ]
    
    from_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='dependencies_from',
        verbose_name=_('源任务')
    )
    to_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='dependencies_to',
        verbose_name=_('目标任务')
    )
    
    dependency_type = models.CharField(_('依赖类型'), max_length=15, choices=DEPENDENCY_TYPES, default='depends_on')
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_dependencies',
        verbose_name=_('创建人')
    )
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('任务依赖')
        verbose_name_plural = _('任务依赖')
        db_table = 'tasks_dependency'
        unique_together = ('from_task', 'to_task', 'dependency_type')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_task.title} {self.get_dependency_type_display()} {self.to_task.title}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # 防止自我依赖
        if self.from_task == self.to_task:
            raise ValidationError(_('任务不能依赖自己'))
        
        # 防止循环依赖（简单检查）
        if TaskDependency.objects.filter(
            from_task=self.to_task,
            to_task=self.from_task,
            dependency_type=self.dependency_type
        ).exists():
            raise ValidationError(_('不能创建循环依赖'))


class TaskComment(models.Model):
    """
    任务评论模型
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('任务')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_comments',
        verbose_name=_('评论用户')
    )
    
    content = models.TextField(_('评论内容'))
    
    # 回复功能
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        verbose_name=_('父评论')
    )
    
    # 提及用户
    mentioned_users = models.ManyToManyField(
        User,
        related_name='mentioned_in_comments',
        verbose_name=_('提及用户'),
        blank=True
    )
    
    # 编辑历史
    is_edited = models.BooleanField(_('已编辑'), default=False)
    edited_at = models.DateTimeField(_('编辑时间'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('任务评论')
        verbose_name_plural = _('任务评论')
        db_table = 'tasks_comment'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} 评论 {self.task.title}"
    
    def save(self, *args, **kwargs):
        if self.pk and self.is_edited:  # 更新现有评论
            self.edited_at = timezone.now()
        super().save(*args, **kwargs)


class TaskAttachment(models.Model):
    """
    任务附件模型
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('任务')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_attachments',
        verbose_name=_('上传用户')
    )
    
    file = models.FileField(_('文件'), upload_to='tasks/attachments/')
    original_name = models.CharField(_('原始文件名'), max_length=255)
    file_size = models.PositiveIntegerField(_('文件大小'))
    content_type = models.CharField(_('文件类型'), max_length=100)
    
    description = models.TextField(_('文件描述'), max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(_('上传时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('任务附件')
        verbose_name_plural = _('任务附件')
        db_table = 'tasks_attachment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.task.title} - {self.original_name}"
    
    def get_file_size_display(self):
        """格式化文件大小显示"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
