from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class Report(models.Model):
    """
    报表模型
    """
    REPORT_TYPES = [
        ('task_completion', _('任务完成统计')),
        ('user_workload', _('用户工作负载')),
        ('team_performance', _('团队绩效')),
        ('project_progress', _('项目进度')),
        ('time_tracking', _('时间追踪')),
        ('custom', _('自定义报表')),
    ]
    
    FREQUENCY_CHOICES = [
        ('once', _('一次性')),
        ('daily', _('每日')),
        ('weekly', _('每周')),
        ('monthly', _('每月')),
        ('quarterly', _('每季度')),
        ('yearly', _('每年')),
    ]
    
    # 基本信息
    name = models.CharField(_('报表名称'), max_length=200)
    description = models.TextField(_('报表描述'), blank=True, null=True)
    report_type = models.CharField(_('报表类型'), max_length=20, choices=REPORT_TYPES)
    
    # 创建者
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_reports',
        verbose_name=_('创建者')
    )
    
    # 关联对象
    board = models.ForeignKey(
        'boards.Board',
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True,
        verbose_name=_('关联看板')
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True,
        verbose_name=_('关联团队')
    )
    
    # 报表配置
    config = models.JSONField(_('报表配置'), default=dict, blank=True)
    filters = models.JSONField(_('筛选条件'), default=dict, blank=True)
    
    # 调度设置
    is_scheduled = models.BooleanField(_('定时生成'), default=False)
    frequency = models.CharField(_('生成频率'), max_length=15, choices=FREQUENCY_CHOICES, default='once')
    next_run_at = models.DateTimeField(_('下次生成时间'), null=True, blank=True)
    
    # 共享设置
    is_public = models.BooleanField(_('公开报表'), default=False)
    shared_users = models.ManyToManyField(
        User,
        related_name='shared_reports',
        verbose_name=_('共享用户'),
        blank=True
    )
    
    # 状态
    is_active = models.BooleanField(_('激活状态'), default=True)
    
    # 系统字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('报表')
        verbose_name_plural = _('报表')
        db_table = 'reports_report'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class ReportExecution(models.Model):
    """
    报表执行记录模型
    """
    STATUS_CHOICES = [
        ('pending', _('等待中')),
        ('running', _('执行中')),
        ('completed', _('已完成')),
        ('failed', _('执行失败')),
        ('cancelled', _('已取消')),
    ]
    
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name=_('报表')
    )
    
    # 执行信息
    status = models.CharField(_('执行状态'), max_length=15, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(_('开始时间'), null=True, blank=True)
    completed_at = models.DateTimeField(_('完成时间'), null=True, blank=True)
    
    # 执行结果
    result_data = models.JSONField(_('结果数据'), null=True, blank=True)
    file_path = models.CharField(_('文件路径'), max_length=500, blank=True, null=True)
    error_message = models.TextField(_('错误信息'), blank=True, null=True)
    
    # 统计信息
    record_count = models.PositiveIntegerField(_('记录数量'), default=0)
    execution_time = models.DecimalField(_('执行时间(秒)'), max_digits=10, decimal_places=3, null=True, blank=True)
    
    # 触发信息
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='triggered_executions',
        null=True,
        blank=True,
        verbose_name=_('触发人')
    )
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('报表执行记录')
        verbose_name_plural = _('报表执行记录')
        db_table = 'reports_execution'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report.name} - {self.get_status_display()}"


class Dashboard(models.Model):
    """
    仪表板模型
    """
    name = models.CharField(_('仪表板名称'), max_length=200)
    description = models.TextField(_('描述'), blank=True, null=True)
    
    # 创建者
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_dashboards',
        verbose_name=_('所有者')
    )
    
    # 关联对象
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='dashboards',
        null=True,
        blank=True,
        verbose_name=_('关联团队')
    )
    
    # 布局配置
    layout = models.JSONField(_('布局配置'), default=dict, blank=True)
    
    # 共享设置
    is_public = models.BooleanField(_('公开仪表板'), default=False)
    shared_users = models.ManyToManyField(
        User,
        related_name='shared_dashboards',
        verbose_name=_('共享用户'),
        blank=True
    )
    
    # 设置
    is_default = models.BooleanField(_('默认仪表板'), default=False)
    refresh_interval = models.PositiveIntegerField(_('刷新间隔(秒)'), default=300)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('仪表板')
        verbose_name_plural = _('仪表板')
        db_table = 'reports_dashboard'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """
    仪表板小部件模型
    """
    WIDGET_TYPES = [
        ('chart_line', _('折线图')),
        ('chart_bar', _('柱状图')),
        ('chart_pie', _('饼图')),
        ('chart_doughnut', _('环形图')),
        ('stats_card', _('统计卡片')),
        ('progress_bar', _('进度条')),
        ('task_list', _('任务列表')),
        ('calendar', _('日历')),
        ('timeline', _('时间线')),
        ('custom', _('自定义')),
    ]
    
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets',
        verbose_name=_('仪表板')
    )
    
    # 基本信息
    title = models.CharField(_('标题'), max_length=200)
    widget_type = models.CharField(_('部件类型'), max_length=20, choices=WIDGET_TYPES)
    
    # 位置和大小
    position_x = models.PositiveIntegerField(_('X坐标'), default=0)
    position_y = models.PositiveIntegerField(_('Y坐标'), default=0)
    width = models.PositiveIntegerField(_('宽度'), default=4)
    height = models.PositiveIntegerField(_('高度'), default=3)
    
    # 配置
    config = models.JSONField(_('配置'), default=dict, blank=True)
    data_source = models.JSONField(_('数据源配置'), default=dict, blank=True)
    
    # 关联报表
    report = models.ForeignKey(
        Report,
        on_delete=models.SET_NULL,
        related_name='widgets',
        null=True,
        blank=True,
        verbose_name=_('关联报表')
    )
    
    # 状态
    is_visible = models.BooleanField(_('可见'), default=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('仪表板部件')
        verbose_name_plural = _('仪表板部件')
        db_table = 'reports_dashboard_widget'
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"


class ReportTemplate(models.Model):
    """
    报表模板模型
    """
    name = models.CharField(_('模板名称'), max_length=200)
    description = models.TextField(_('模板描述'), blank=True, null=True)
    
    # 模板内容
    report_type = models.CharField(_('报表类型'), max_length=20, choices=Report.REPORT_TYPES)
    config_template = models.JSONField(_('配置模板'), default=dict)
    filters_template = models.JSONField(_('筛选模板'), default=dict)
    
    # 创建者
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_report_templates',
        verbose_name=_('创建者')
    )
    
    # 分类和标签
    category = models.CharField(_('分类'), max_length=50, blank=True, null=True)
    tags = models.JSONField(_('标签'), default=list, blank=True)
    
    # 使用统计
    usage_count = models.PositiveIntegerField(_('使用次数'), default=0)
    
    # 共享设置
    is_public = models.BooleanField(_('公开模板'), default=False)
    is_system = models.BooleanField(_('系统模板'), default=False)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('报表模板')
        verbose_name_plural = _('报表模板')
        db_table = 'reports_template'
        ordering = ['-usage_count', '-updated_at']
    
    def __str__(self):
        return self.name
