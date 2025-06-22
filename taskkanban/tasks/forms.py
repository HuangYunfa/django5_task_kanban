"""
Tasks应用表单
任务管理相关表单
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Task, TaskComment, TaskAttachment
from boards.models import Board, BoardList, BoardLabel

User = get_user_model()


class TaskCreateForm(forms.ModelForm):
    """
    创建任务表单
    """
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'board_list', 'assignees', 
            'priority', 'due_date', 'labels'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('输入任务标题')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('描述任务详情（可选）'),
                'rows': 4
            }),
            'board_list': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assignees': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'multiple': True
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'labels': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'multiple': True
            })
        }
        labels = {
            'title': _('任务标题'),
            'description': _('任务描述'),
            'board_list': _('所属列表'),
            'assignees': _('分配给'),
            'priority': _('优先级'),
            'due_date': _('截止时间'),
            'labels': _('标签')
        }
    
    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if board:
            # 限制列表选择范围
            self.fields['board_list'].queryset = BoardList.objects.filter(board=board)
            
            # 限制分配用户范围
            board_members = board.members.values_list('user', flat=True)
            self.fields['assignees'].queryset = User.objects.filter(
                id__in=board_members
            )
              # 限制标签选择范围
            self.fields['labels'].queryset = BoardLabel.objects.filter(board=board)
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title.strip()) < 2:
            raise forms.ValidationError(_('任务标题至少需要2个字符'))
        return title.strip()


class TaskUpdateForm(forms.ModelForm):
    """
    编辑任务表单
    """
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'board_list', 'assignees', 
            'priority', 'status', 'due_date', 'labels'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'board_list': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assignees': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'multiple': True
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'labels': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'multiple': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        
        if board:
            self.fields['board_list'].queryset = BoardList.objects.filter(board=board)
            board_members = board.members.values_list('user', flat=True)
            self.fields['assignees'].queryset = User.objects.filter(
                id__in=board_members
            )
            self.fields['labels'].queryset = BoardLabel.objects.filter(board=board)


class TaskCommentForm(forms.ModelForm):
    """
    任务评论表单
    """
    class Meta:
        model = TaskComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('添加评论...'),
                'rows': 3
            })
        }
        labels = {
            'content': _('评论内容')
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 1:
            raise forms.ValidationError(_('评论内容不能为空'))
        return content.strip()


class TaskLabelForm(forms.ModelForm):
    """
    任务标签表单
    """
    class Meta:
        model = BoardLabel
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('标签名称')
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }
        labels = {
            'name': _('标签名称'),
            'color': _('标签颜色')
        }


class TaskAttachmentForm(forms.ModelForm):
    """
    任务附件表单
    """
    class Meta:
        model = TaskAttachment
        fields = ['file', 'description']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('文件描述（可选）')
            })
        }
        labels = {
            'file': _('选择文件'),
            'description': _('文件描述')
        }


class TaskSearchForm(forms.Form):
    """
    任务搜索表单
    """
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('搜索任务...'),
        }),
        label=_('搜索关键词')
    )
    
    status = forms.MultipleChoiceField(
        required=False,
        choices=Task.STATUS_CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select'
        }),
        label=_('任务状态')
    )
    
    priority = forms.MultipleChoiceField(
        required=False,
        choices=Task.PRIORITY_CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select'
        }),
        label=_('优先级')
    )
    
    assignee = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('分配给'),
        empty_label=_('所有人')    )
    
    board = forms.ModelChoiceField(
        required=False,
        queryset=Board.objects.none(),  # 默认为空queryset
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('看板'),
        empty_label=_('所有看板')
    )
    
    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # 设置用户可见的看板
            self.fields['board'].queryset = Board.objects.filter(
                Q(owner=user) |  # 自己创建的看板
                Q(team__memberships__user=user, team__memberships__status='active') |  # 团队成员
                Q(members__user=user, members__is_active=True) |  # 看板成员
                Q(visibility='public')  # 公开看板
            ).distinct()
        
        if board:
            board_members = board.members.values_list('user', flat=True)
            self.fields['assignee'].queryset = User.objects.filter(
                id__in=board_members
            )
