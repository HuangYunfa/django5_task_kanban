"""
Teams应用表单
团队管理相关表单
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Team, TeamMembership, TeamInvitation

User = get_user_model()


class TeamForm(forms.ModelForm):
    """团队创建和编辑表单"""
    
    class Meta:
        model = Team
        fields = ['name', 'description', 'avatar', 'is_public', 'allow_join_request']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('请输入团队名称'),
                'maxlength': 100
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('请输入团队描述（可选）'),
                'rows': 4,
                'maxlength': 500
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_join_request': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        team = super().save(commit=False)
        if self.user and not team.created_by_id:
            team.created_by = self.user
        if commit:
            team.save()
            # 创建团队时，创建者自动成为所有者
            if self.user and not team.memberships.filter(user=self.user).exists():
                TeamMembership.objects.create(
                    team=team,
                    user=self.user,
                    role='owner',
                    status='active',
                    joined_at=team.created_at
                )
        return team


class TeamMembershipForm(forms.ModelForm):
    """团队成员关系表单"""
    
    class Meta:
        model = TeamMembership
        fields = ['role', 'status']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class TeamInvitationForm(forms.ModelForm):
    """团队邀请表单"""
    
    # 添加用户名或邮箱输入字段
    user_identifier = forms.CharField(
        label=_('用户名或邮箱'),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('请输入用户名或邮箱地址')
        })
    )
    
    class Meta:
        model = TeamInvitation
        fields = ['role', 'message']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('可选的邀请消息'),
                'rows': 3,
                'maxlength': 200
            }),
        }

    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team', None)
        self.inviter = kwargs.pop('inviter', None)
        super().__init__(*args, **kwargs)

    def clean_user_identifier(self):
        """验证用户标识符"""
        identifier = self.cleaned_data['user_identifier']
        
        # 尝试通过用户名或邮箱查找用户
        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            raise forms.ValidationError(_('用户不存在'))
        
        # 检查用户是否已是团队成员
        if self.team and self.team.memberships.filter(user=user, status='active').exists():
            raise forms.ValidationError(_('该用户已是团队成员'))
        
        # 检查是否有待处理的邀请
        if self.team and TeamInvitation.objects.filter(
            team=self.team, 
            invitee=user, 
            status='pending'
        ).exists():
            raise forms.ValidationError(_('该用户已有待处理的邀请'))
        
        return user

    def save(self, commit=True):
        invitation = super().save(commit=False)
        if self.team:
            invitation.team = self.team
        if self.inviter:
            invitation.inviter = self.inviter
        
        # 设置被邀请人
        user = self.cleaned_data['user_identifier']
        invitation.invitee = user
        
        # 设置过期时间（7天后）
        from django.utils import timezone
        from datetime import timedelta
        invitation.expires_at = timezone.now() + timedelta(days=7)
        
        if commit:
            invitation.save()
        return invitation


class TeamSearchForm(forms.Form):
    """团队搜索表单"""
    
    search = forms.CharField(
        label=_('搜索'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('搜索团队名称或描述...'),
        })
    )
    
    is_public = forms.ChoiceField(
        label=_('可见性'),
        choices=[
            ('', _('全部')),
            ('true', _('公开团队')),
            ('false', _('私有团队')),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    role = forms.ChoiceField(
        label=_('我的角色'),
        choices=[
            ('', _('全部')),
            ('owner', _('所有者')),
            ('admin', _('管理员')),
            ('member', _('成员')),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
