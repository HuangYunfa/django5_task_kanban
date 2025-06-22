"""
看板应用表单
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Board, BoardList, BoardMember, BoardLabel

User = get_user_model()


class BoardCreateForm(forms.ModelForm):
    """
    创建看板表单
    """
    class Meta:
        model = Board
        fields = [
            'name', 'description', 'template', 'visibility',
            'background_color', 'background_image',
            'enable_calendar', 'enable_timeline', 'enable_comments',
            'enable_attachments', 'team'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('输入看板名称'),
                'maxlength': 100
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('描述这个看板的用途和目标'),
                'rows': 4,
                'maxlength': 500
            }),
            'template': forms.Select(attrs={
                'class': 'form-select'
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-select'
            }),
            'background_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': _('选择背景颜色')
            }),
            'background_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'team': forms.Select(attrs={
                'class': 'form-select'
            }),
            'enable_calendar': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'enable_timeline': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'enable_comments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'enable_attachments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': _('看板名称'),
            'description': _('看板描述'),
            'template': _('模板类型'),
            'visibility': _('可见性'),
            'background_color': _('背景颜色'),
            'background_image': _('背景图片'),
            'team': _('所属团队'),
            'enable_calendar': _('启用日历视图'),
            'enable_timeline': _('启用时间线'),
            'enable_comments': _('启用评论'),
            'enable_attachments': _('启用附件'),
        }
        help_texts = {
            'name': _('给您的看板起一个容易记忆的名称'),
            'description': _('简要描述看板的用途，帮助团队成员理解'),
            'template': _('选择适合您项目的模板'),
            'visibility': _('设置谁可以看到这个看板'),
            'team': _('选择看板所属的团队（可选）'),
            'background_color': _('自定义看板的背景颜色'),
            'background_image': _('上传自定义背景图片'),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
          # 限制团队选择为用户所属的团队
        if self.user:
            from teams.models import Team
            self.fields['team'].queryset = Team.objects.filter(
                memberships__user=self.user
            ).distinct()
        
        # 设置默认值
        if not self.instance.pk:
            self.fields['template'].initial = 'kanban'
            self.fields['visibility'].initial = 'private'
            self.fields['background_color'].initial = '#0079bf'
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError(_('看板名称至少需要2个字符'))
        return name
    
    def clean_background_image(self):
        image = self.cleaned_data.get('background_image')
        if image:
            # 检查文件大小 (限制为5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('图片大小不能超过5MB'))
            
            # 检查文件类型
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_types:
                raise forms.ValidationError(_('只支持 JPEG、PNG、GIF、WebP 格式的图片'))
        
        return image


class BoardUpdateForm(BoardCreateForm):
    """
    更新看板表单
    """
    class Meta(BoardCreateForm.Meta):
        fields = BoardCreateForm.Meta.fields + ['is_closed']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 添加关闭看板的选项
        self.fields['is_closed'] = forms.BooleanField(
            label=_('关闭看板'),
            help_text=_('关闭后看板将变为只读状态'),
            required=False,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
        )


class BoardListCreateForm(forms.ModelForm):
    """
    创建看板列表表单
    """
    class Meta:
        model = BoardList
        fields = ['name', 'position']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('输入列表名称')
            }),
            'position': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }
        labels = {
            'name': _('列表名称'),
            'position': _('显示位置')
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 1:
                raise forms.ValidationError(_('列表名称不能为空'))
        return name


class BoardMemberInviteForm(forms.ModelForm):
    """
    邀请看板成员表单
    """
    email = forms.EmailField(
        label=_('邮箱地址'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('输入要邀请的用户邮箱')
        }),
        help_text=_('输入要邀请加入看板的用户邮箱地址')
    )
    
    class Meta:
        model = BoardMember
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'role': _('角色权限')
        }
    
    def __init__(self, *args, **kwargs):
        self.board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        
        # 设置默认角色
        self.fields['role'].initial = 'member'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # 检查用户是否存在
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(_('该邮箱地址对应的用户不存在'))
        
        # 检查用户是否已经是看板成员
        if self.board and BoardMember.objects.filter(
            board=self.board, 
            user=user
        ).exists():
            raise forms.ValidationError(_('该用户已经是看板成员'))
        
        return email
    
    def save(self, commit=True):
        email = self.cleaned_data.get('email')
        user = User.objects.get(email=email)
        
        member = super().save(commit=False)
        member.user = user
        member.board = self.board
        
        if commit:
            member.save()
        
        return member


class BoardSearchForm(forms.Form):
    """
    看板搜索表单
    """
    q = forms.CharField(
        label=_('搜索关键词'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('搜索看板名称或描述'),
            'autocomplete': 'off'
        })
    )
    
    template = forms.ChoiceField(
        label=_('模板类型'),
        choices=[('', _('全部模板'))] + Board.TEMPLATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    visibility = forms.ChoiceField(
        label=_('可见性'),
        choices=[('', _('全部'))] + Board.VISIBILITY_CHOICES,        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    is_closed = forms.BooleanField(
        label=_('包含已关闭的看板'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class BoardLabelForm(forms.ModelForm):
    """
    看板标签表单
    """
    class Meta:
        model = BoardLabel
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('标签名称'),
                'maxlength': 50
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': _('选择标签颜色')
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        
        # 为字段设置标签
        self.fields['name'].label = _('标签名称')
        self.fields['color'].label = _('标签颜色')
    
    def save(self, commit=True):
        label = super().save(commit=False)
        if self.board:
            label.board = self.board
        if commit:
            label.save()
        return label
