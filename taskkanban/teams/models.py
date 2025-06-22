from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator

User = get_user_model()


class Team(models.Model):
    """
    团队模型
    """
    name = models.CharField(
        _('团队名称'), 
        max_length=100, 
        validators=[MinLengthValidator(2)]
    )
    description = models.TextField(_('团队描述'), max_length=500, blank=True, null=True)
    avatar = models.ImageField(_('团队头像'), upload_to='teams/avatars/', blank=True, null=True)
    
    # 团队设置
    is_public = models.BooleanField(_('公开团队'), default=False, help_text=_('公开团队允许任何人查看'))
    allow_join_request = models.BooleanField(_('允许加入申请'), default=True)
    
    # 创建者和管理员
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_teams',
        verbose_name=_('创建者')
    )
    
    # 系统字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('团队')
        verbose_name_plural = _('团队')
        db_table = 'teams_team'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_avatar_url(self):
        """获取团队头像URL"""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default-team-avatar.png'
    
    @property
    def member_count(self):
        """团队成员数量"""
        return self.memberships.filter(status='active').count()
    
    @property
    def admin_count(self):
        """团队管理员数量"""
        return self.memberships.filter(
            status='active',
            role__in=['admin', 'owner']
        ).count()


class TeamMembership(models.Model):
    """
    团队成员关系模型
    """
    ROLE_CHOICES = [
        ('owner', _('所有者')),
        ('admin', _('管理员')),
        ('member', _('成员')),
        ('guest', _('访客')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('待确认')),
        ('active', _('活跃')),
        ('inactive', _('非活跃')),
        ('blocked', _('已屏蔽')),
    ]
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('团队')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_memberships',
        verbose_name=_('用户')
    )
    
    role = models.CharField(_('角色'), max_length=10, choices=ROLE_CHOICES, default='member')
    status = models.CharField(_('状态'), max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # 邀请信息
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='sent_invitations',
        null=True,
        blank=True,
        verbose_name=_('邀请人')
    )
    invitation_message = models.TextField(_('邀请消息'), max_length=200, blank=True, null=True)
    
    # 时间字段
    joined_at = models.DateTimeField(_('加入时间'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('团队成员')
        verbose_name_plural = _('团队成员')
        db_table = 'teams_membership'
        unique_together = ('team', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.team.name} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """是否为管理员"""
        return self.role in ['owner', 'admin']
    
    @property
    def is_active(self):
        """是否为活跃成员"""
        return self.status == 'active'


class TeamInvitation(models.Model):
    """
    团队邀请模型
    """
    STATUS_CHOICES = [
        ('pending', _('待处理')),
        ('accepted', _('已接受')),
        ('declined', _('已拒绝')),
        ('expired', _('已过期')),
        ('cancelled', _('已取消')),
    ]
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name=_('团队')
    )
    inviter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_team_invitations',
        verbose_name=_('邀请人')
    )
    invitee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_team_invitations',
        verbose_name=_('被邀请人')
    )
    
    role = models.CharField(_('邀请角色'), max_length=10, choices=TeamMembership.ROLE_CHOICES, default='member')
    status = models.CharField(_('状态'), max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(_('邀请消息'), max_length=200, blank=True, null=True)
    
    # 时间字段
    expires_at = models.DateTimeField(_('过期时间'))
    responded_at = models.DateTimeField(_('响应时间'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('团队邀请')
        verbose_name_plural = _('团队邀请')
        db_table = 'teams_invitation'
        unique_together = ('team', 'invitee', 'status')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.inviter.get_display_name()} 邀请 {self.invitee.get_display_name()} 加入 {self.team.name}"
    
    @property
    def is_expired(self):
        """是否已过期"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_pending(self):
        """是否待处理"""
        return self.status == 'pending' and not self.is_expired
