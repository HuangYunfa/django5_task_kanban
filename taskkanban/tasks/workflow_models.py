"""
任务状态流转系统模型
包含工作流状态、转换规则、状态历史、自动化规则等
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class WorkflowStatus(models.Model):
    """
    工作流状态模型 - 定义看板的自定义状态流程
    """
    name = models.CharField(_('状态名称'), max_length=50)
    display_name = models.CharField(_('显示名称'), max_length=100)
    color = models.CharField(_('状态颜色'), max_length=7, default='#6c757d')
    board = models.ForeignKey(
        'boards.Board',
        on_delete=models.CASCADE,
        related_name='workflow_statuses',
        verbose_name=_('所属看板')
    )
    position = models.PositiveIntegerField(_('排序位置'), default=0)
    is_initial = models.BooleanField(_('是否为初始状态'), default=False)
    is_final = models.BooleanField(_('是否为最终状态'), default=False)
    is_active = models.BooleanField(_('是否激活'), default=True)
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('工作流状态')
        verbose_name_plural = _('工作流状态')
        ordering = ['board', 'position']
        unique_together = [['board', 'name'], ['board', 'position']]
    
    def __str__(self):
        return f"{self.board.name} - {self.display_name}"


class WorkflowTransition(models.Model):
    """
    工作流状态转换模型 - 定义状态之间的转换规则
    """
    from_status = models.ForeignKey(
        WorkflowStatus,
        on_delete=models.CASCADE,
        related_name='outgoing_transitions',
        verbose_name=_('源状态')
    )
    to_status = models.ForeignKey(
        WorkflowStatus,
        on_delete=models.CASCADE,
        related_name='incoming_transitions',
        verbose_name=_('目标状态')
    )
    name = models.CharField(_('转换名称'), max_length=100)
    description = models.TextField(_('转换描述'), blank=True)
    
    # 转换条件
    require_assignee = models.BooleanField(_('需要指定受理人'), default=False)
    require_comment = models.BooleanField(_('需要填写备注'), default=False)
    allowed_roles = models.JSONField(_('允许的角色'), default=list, blank=True)
    
    # 自动化规则
    auto_assign_creator = models.BooleanField(_('自动分配给创建者'), default=False)
    auto_notify_assignees = models.BooleanField(_('自动通知受理人'), default=True)
    auto_move_to_list = models.ForeignKey(
        'boards.BoardList',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('自动移动到列表')
    )
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('工作流转换')
        verbose_name_plural = _('工作流转换')
        unique_together = ['from_status', 'to_status']
    
    def __str__(self):
        return f"{self.from_status.display_name} → {self.to_status.display_name}"


class TaskStatusHistory(models.Model):
    """
    任务状态变更历史记录
    """
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('关联任务')
    )
    from_status = models.CharField(_('原状态'), max_length=15, blank=True)
    to_status = models.CharField(_('新状态'), max_length=15)
    from_workflow_status = models.ForeignKey(
        WorkflowStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='from_history',
        verbose_name=_('原工作流状态')
    )
    to_workflow_status = models.ForeignKey(
        WorkflowStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='to_history',
        verbose_name=_('新工作流状态')
    )
    
    # 变更信息
    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='status_changes',
        verbose_name=_('变更人')
    )
    comment = models.TextField(_('变更备注'), blank=True)
    transition_used = models.ForeignKey(
        WorkflowTransition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('使用的转换')
    )
    
    # 自动化信息
    is_auto_change = models.BooleanField(_('是否自动变更'), default=False)
    auto_rule_name = models.CharField(_('自动化规则名称'), max_length=100, blank=True)
    
    # 额外信息
    metadata = models.JSONField(_('元数据'), default=dict, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField(_('变更时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('任务状态历史')
        verbose_name_plural = _('任务状态历史')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task.title}: {self.from_status} → {self.to_status}"
    
    def get_status_display(self, status):
        """获取状态的显示名称"""
        from .models import Task
        status_choices = dict(Task.STATUS_CHOICES)
        return status_choices.get(status, status)


class WorkflowRule(models.Model):
    """
    工作流自动化规则
    """
    TRIGGER_CHOICES = [
        ('status_change', _('状态变更时')),
        ('task_created', _('任务创建时')),
        ('task_assigned', _('任务分配时')),
        ('due_date_near', _('临近截止日期')),
        ('overdue', _('任务逾期时')),
        ('time_scheduled', _('定时触发')),
    ]
    
    ACTION_CHOICES = [
        ('change_status', _('变更状态')),
        ('assign_user', _('分配用户')),
        ('move_to_list', _('移动到列表')),
        ('set_priority', _('设置优先级')),
        ('add_label', _('添加标签')),
        ('send_notification', _('发送通知')),
        ('create_subtask', _('创建子任务')),
    ]
    
    name = models.CharField(_('规则名称'), max_length=100)
    description = models.TextField(_('规则描述'), blank=True)
    board = models.ForeignKey(
        'boards.Board',
        on_delete=models.CASCADE,
        related_name='workflow_rules',
        verbose_name=_('所属看板')
    )
    
    # 触发条件
    trigger_type = models.CharField(_('触发类型'), max_length=20, choices=TRIGGER_CHOICES)
    trigger_conditions = models.JSONField(_('触发条件'), default=dict)
    
    # 执行动作
    action_type = models.CharField(_('动作类型'), max_length=20, choices=ACTION_CHOICES)
    action_parameters = models.JSONField(_('动作参数'), default=dict)
    
    # 规则设置
    is_active = models.BooleanField(_('是否激活'), default=True)
    priority = models.PositiveIntegerField(_('规则优先级'), default=0)
    max_executions = models.PositiveIntegerField(_('最大执行次数'), null=True, blank=True)
    execution_count = models.PositiveIntegerField(_('已执行次数'), default=0)
    
    # 时间设置
    schedule_cron = models.CharField(_('定时规则(Cron)'), max_length=100, blank=True)
    last_executed = models.DateTimeField(_('上次执行时间'), null=True, blank=True)
    
    # 创建信息
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_workflow_rules',
        verbose_name=_('创建人')
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('工作流规则')
        verbose_name_plural = _('工作流规则')
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.board.name} - {self.name}"
    
    def can_execute(self):
        """检查规则是否可以执行"""
        if not self.is_active:
            return False
        
        if self.max_executions and self.execution_count >= self.max_executions:
            return False
        
        return True
    
    def execute(self, context=None):
        """执行规则"""
        if not self.can_execute():
            return False
        
        # 这里将实现具体的规则执行逻辑
        # 根据action_type和action_parameters执行相应的动作
        
        self.execution_count += 1
        self.last_executed = timezone.now()
        self.save(update_fields=['execution_count', 'last_executed'])
        
        return True


class WorkflowRuleExecution(models.Model):
    """
    工作流规则执行记录
    """
    rule = models.ForeignKey(
        WorkflowRule,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name=_('执行的规则')
    )
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='rule_executions',
        verbose_name=_('关联任务')
    )
    
    # 执行结果
    success = models.BooleanField(_('执行成功'), default=True)
    error_message = models.TextField(_('错误信息'), blank=True)
    execution_details = models.JSONField(_('执行详情'), default=dict)
    
    # 时间戳
    executed_at = models.DateTimeField(_('执行时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('规则执行记录')
        verbose_name_plural = _('规则执行记录')
        ordering = ['-executed_at']
    
    def __str__(self):
        status = '✓' if self.success else '✗'
        return f"{status} {self.rule.name} - {self.task.title}"
