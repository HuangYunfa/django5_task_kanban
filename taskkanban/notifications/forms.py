from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import EmailTemplate, UserNotificationPreference

User = get_user_model()


class NotificationPreferencesForm(forms.ModelForm):
    """用户通知偏好设置表单"""
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'email_enabled',
            'task_assigned', 'task_status_changed', 'task_due_reminder', 'task_comment_mention',
            'team_invitation', 'board_member_added',
            'daily_summary', 'weekly_summary', 'team_activity_summary'
        ]
        widgets = {
            'email_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'task_assigned': forms.Select(attrs={'class': 'form-select'}),
            'task_status_changed': forms.Select(attrs={'class': 'form-select'}),
            'task_due_reminder': forms.Select(attrs={'class': 'form-select'}),
            'task_comment_mention': forms.Select(attrs={'class': 'form-select'}),
            'team_invitation': forms.Select(attrs={'class': 'form-select'}),
            'board_member_added': forms.Select(attrs={'class': 'form-select'}),
            'daily_summary': forms.Select(attrs={'class': 'form-select'}),
            'weekly_summary': forms.Select(attrs={'class': 'form-select'}),
            'team_activity_summary': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 自定义字段标签
        self.fields['email_enabled'].label = _('启用邮件通知')
        self.fields['task_assigned'].label = _('任务分配通知')
        self.fields['task_status_changed'].label = _('任务状态变更通知')
        self.fields['task_due_reminder'].label = _('任务截止提醒')
        self.fields['task_comment_mention'].label = _('任务评论@提及')
        self.fields['team_invitation'].label = _('团队邀请通知')
        self.fields['board_member_added'].label = _('看板成员添加通知')
        self.fields['daily_summary'].label = _('每日工作摘要')
        self.fields['weekly_summary'].label = _('每周工作摘要')
        self.fields['team_activity_summary'].label = _('团队活动摘要')
        
        # 添加帮助文本
        self.fields['email_enabled'].help_text = _('关闭此选项将停止所有邮件通知')
        self.fields['daily_summary'].help_text = _('每日发送工作摘要邮件')
        self.fields['weekly_summary'].help_text = _('每周发送工作摘要邮件')


class EmailTemplateForm(forms.ModelForm):
    """邮件模板表单"""
    
    class Meta:
        model = EmailTemplate
        fields = [
            'name', 'template_type', 'subject_template', 'body_template', 
            'is_html', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'template_type': forms.Select(attrs={'class': 'form-select'}),
            'subject_template': forms.TextInput(attrs={'class': 'form-control'}),
            'body_template': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': _('支持Django模板语法，如 {{ user.username }}, {{ task.title }} 等')
            }),
            'is_html': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 添加帮助文本
        self.fields['subject_template'].help_text = _('邮件主题模板，支持Django模板语法')
        self.fields['body_template'].help_text = _('邮件正文模板，支持Django模板语法和HTML')
        self.fields['is_html'].help_text = _('勾选表示邮件正文为HTML格式')
        self.fields['is_active'].help_text = _('只有激活的模板才会被使用')
    
    def clean_body_template(self):
        """验证模板语法"""
        body_template = self.cleaned_data.get('body_template')
        
        if body_template:
            try:
                from django.template import Template
                Template(body_template)
            except Exception as e:
                raise forms.ValidationError(_('模板语法错误: {}').format(str(e)))
        
        return body_template
    
    def clean_subject_template(self):
        """验证主题模板语法"""
        subject_template = self.cleaned_data.get('subject_template')
        
        if subject_template:
            try:
                from django.template import Template
                Template(subject_template)
            except Exception as e:
                raise forms.ValidationError(_('模板语法错误: {}').format(str(e)))
        
        return subject_template


class TestEmailForm(forms.Form):
    """测试邮件发送表单"""
    
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label=_('收件人'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text=_('选择接收测试邮件的用户')
    )
    
    template_type = forms.ChoiceField(
        choices=EmailTemplate.TEMPLATE_TYPES,
        label=_('邮件模板'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text=_('选择要测试的邮件模板类型')
    )
    
    test_message = forms.CharField(
        label=_('测试消息'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('可选的测试消息内容')
        }),
        required=False,
        help_text=_('将作为test_message变量传递给模板')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 只显示有邮箱的用户
        self.fields['recipient'].queryset = User.objects.filter(
            email__isnull=False
        ).exclude(email='').order_by('username')
    
    def clean_recipient(self):
        """验证收件人"""
        recipient = self.cleaned_data.get('recipient')
        
        if recipient and not recipient.email:
            raise forms.ValidationError(_('所选用户没有邮箱地址'))
        
        return recipient


class BulkEmailForm(forms.Form):
    """批量发送邮件表单"""
    
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        label=_('收件人'),
        widget=forms.CheckboxSelectMultiple(),
        help_text=_('选择接收邮件的用户')
    )
    
    template_type = forms.ChoiceField(
        choices=EmailTemplate.TEMPLATE_TYPES,
        label=_('邮件模板'),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    scheduled_at = forms.DateTimeField(
        label=_('计划发送时间'),
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        required=False,
        help_text=_('留空表示立即发送')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 只显示有邮箱的用户
        self.fields['recipients'].queryset = User.objects.filter(
            email__isnull=False
        ).exclude(email='').order_by('username')


class EmailSearchForm(forms.Form):
    """邮件搜索表单"""
    
    STATUS_CHOICES = [
        ('', _('全部状态')),
        ('pending', _('待发送')),
        ('sending', _('发送中')),
        ('sent', _('已发送')),
        ('failed', _('发送失败')),
        ('cancelled', _('已取消')),
    ]
    
    TEMPLATE_CHOICES = [('', _('全部类型'))] + list(EmailTemplate.TEMPLATE_TYPES)
    
    q = forms.CharField(
        label=_('搜索关键词'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('搜索邮件主题、收件人...')
        })
    )
    
    status = forms.ChoiceField(
        label=_('发送状态'),
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    template_type = forms.ChoiceField(
        label=_('邮件类型'),
        choices=TEMPLATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        label=_('起始日期'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        label=_('结束日期'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
