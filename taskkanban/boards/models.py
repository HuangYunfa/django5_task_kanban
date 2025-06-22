from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.utils.text import slugify
import uuid

User = get_user_model()


class Board(models.Model):
    """
    看板模型
    """
    VISIBILITY_CHOICES = [
        ('private', _('私有')),
        ('team', _('团队可见')),
        ('public', _('公开')),
    ]
    
    TEMPLATE_CHOICES = [
        ('kanban', _('看板模板')),
        ('scrum', _('敏捷开发')),
        ('personal', _('个人任务')),
        ('project', _('项目管理')),
        ('custom', _('自定义')),
    ]
    
    # 基本信息
    name = models.CharField(
        _('看板名称'), 
        max_length=100, 
        validators=[MinLengthValidator(2)]
    )
    slug = models.SlugField(_('URL标识'), max_length=120, unique=True, blank=True)
    description = models.TextField(_('看板描述'), max_length=500, blank=True, null=True)
    
    # 背景和样式
    background_color = models.CharField(_('背景颜色'), max_length=7, default='#0079bf')
    background_image = models.ImageField(_('背景图片'), upload_to='boards/backgrounds/', blank=True, null=True)
    
    # 模板和配置
    template = models.CharField(_('模板类型'), max_length=20, choices=TEMPLATE_CHOICES, default='kanban')
    visibility = models.CharField(_('可见性'), max_length=10, choices=VISIBILITY_CHOICES, default='private')
    
    # 设置选项
    is_closed = models.BooleanField(_('已关闭'), default=False)
    enable_calendar = models.BooleanField(_('启用日历视图'), default=True)
    enable_timeline = models.BooleanField(_('启用时间线'), default=True)
    enable_comments = models.BooleanField(_('启用评论'), default=True)
    enable_attachments = models.BooleanField(_('启用附件'), default=True)
    
    # 关联关系
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards',
        verbose_name=_('所有者')
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='boards',
        null=True,
        blank=True,
        verbose_name=_('所属团队')
    )
    
    # 系统字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('看板')
        verbose_name_plural = _('看板')
        db_table = 'boards_board'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['owner', '-updated_at']),
            models.Index(fields=['team', '-updated_at']),
            models.Index(fields=['visibility', '-updated_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Board.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f'/boards/{self.slug}/'
    
    def get_background_url(self):
        """获取背景图片URL"""
        if self.background_image and hasattr(self.background_image, 'url'):
            return self.background_image.url
        return None
    
    @property
    def member_count(self):
        """看板成员数量"""
        return self.members.filter(is_active=True).count()
    
    @property
    def list_count(self):
        """列表数量"""
        return self.lists.filter(is_archived=False).count()
    
    @property
    def task_count(self):
        """任务数量"""
        return sum(list_obj.tasks.filter(is_archived=False).count() for list_obj in self.lists.all())


class BoardList(models.Model):
    """
    看板列表模型
    """
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='lists',
        verbose_name=_('所属看板')
    )
    
    name = models.CharField(_('列表名称'), max_length=100)
    position = models.PositiveIntegerField(_('排序位置'), default=0)
    
    # 样式设置
    color = models.CharField(_('颜色标识'), max_length=7, blank=True, null=True)
    
    # 状态设置
    is_archived = models.BooleanField(_('已归档'), default=False)
    is_done_list = models.BooleanField(_('完成列表'), default=False)
    
    # 限制设置
    wip_limit = models.PositiveIntegerField(_('在制品限制'), null=True, blank=True)
    
    # 系统字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('看板列表')
        verbose_name_plural = _('看板列表')
        db_table = 'boards_list'
        ordering = ['position']
        unique_together = ('board', 'name')
    
    def __str__(self):
        return f"{self.board.name} - {self.name}"
    
    @property
    def task_count(self):
        """任务数量"""
        return self.tasks.filter(is_archived=False).count()
    
    @property
    def is_wip_exceeded(self):
        """是否超过在制品限制"""
        if self.wip_limit:
            return self.task_count > self.wip_limit
        return False


class BoardMember(models.Model):
    """
    看板成员模型
    """
    ROLE_CHOICES = [
        ('admin', _('管理员')),
        ('member', _('成员')),
        ('observer', _('观察者')),
    ]
    
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_('看板')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='board_memberships',
        verbose_name=_('用户')
    )
    
    role = models.CharField(_('角色'), max_length=10, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(_('活跃状态'), default=True)
    
    # 邀请信息
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='board_invitations_sent',
        null=True,
        blank=True,
        verbose_name=_('邀请人')
    )
    
    # 时间字段
    joined_at = models.DateTimeField(_('加入时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('看板成员')
        verbose_name_plural = _('看板成员')
        db_table = 'boards_member'
        unique_together = ('board', 'user')
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.board.name} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """是否为管理员"""
        return self.role == 'admin'


class BoardLabel(models.Model):
    """
    看板标签模型
    """
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='labels',
        verbose_name=_('所属看板')
    )
    
    name = models.CharField(_('标签名称'), max_length=50)
    color = models.CharField(_('标签颜色'), max_length=7, default='#61bd4f')
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('看板标签')
        verbose_name_plural = _('看板标签')
        db_table = 'boards_label'
        unique_together = ('board', 'name')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.board.name} - {self.name}"


class BoardActivity(models.Model):
    """
    看板活动记录模型
    """
    ACTION_CHOICES = [
        ('create_board', _('创建看板')),
        ('update_board', _('更新看板')),
        ('add_member', _('添加成员')),
        ('remove_member', _('移除成员')),
        ('create_list', _('创建列表')),
        ('update_list', _('更新列表')),
        ('archive_list', _('归档列表')),
        ('create_task', _('创建任务')),
        ('update_task', _('更新任务')),
        ('move_task', _('移动任务')),
        ('archive_task', _('归档任务')),
        ('add_comment', _('添加评论')),
        ('add_attachment', _('添加附件')),
    ]
    
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('看板')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='board_activities',
        verbose_name=_('操作用户')
    )
    
    action = models.CharField(_('操作类型'), max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(_('操作描述'), max_length=500)
    
    # 关联对象信息
    target_type = models.CharField(_('目标类型'), max_length=20, blank=True, null=True)
    target_id = models.PositiveIntegerField(_('目标ID'), blank=True, null=True)
    
    # 元数据
    metadata = models.JSONField(_('附加数据'), default=dict, blank=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('看板活动')
        verbose_name_plural = _('看板活动')
        db_table = 'boards_activity'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['board', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} {self.get_action_display()} - {self.board.name}"
