"""
Tasks应用表单
任务管理相关表单
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Q, Max
from django.db import models

from .models import Task, TaskComment, TaskAttachment
from boards.models import Board, BoardList, BoardLabel
from .workflow_models import WorkflowStatus, WorkflowTransition, TaskStatusHistory

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


class WorkflowStatusForm(forms.ModelForm):
    """
    工作流状态表单
    """
    class Meta:
        model = WorkflowStatus
        fields = [
            'name', 'display_name', 'color', 'position',
            'is_initial', 'is_final', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('status_name'),
                'pattern': '[a-zA-Z_][a-zA-Z0-9_]*',
                'title': _('只能包含字母、数字和下划线，且必须以字母或下划线开头')
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('状态显示名称')
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#6c757d'
            }),
            'position': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1'
            }),
            'is_initial': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_final': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        
        # 设置默认值
        if not self.instance.pk:
            self.fields['is_active'].initial = True
            if board:
                # 设置默认位置为最后
                last_position = WorkflowStatus.objects.filter(
                    board=board
                ).aggregate(Max('position'))['position__max'] or 0
                self.fields['position'].initial = last_position + 1
        
        # 添加help_text
        self.fields['name'].help_text = _('状态的内部标识符，用于API和系统识别')
        self.fields['display_name'].help_text = _('用户界面中显示的状态名称')
        self.fields['color'].help_text = _('状态的显示颜色')
        self.fields['position'].help_text = _('状态的排序位置，数字越小越靠前')
        self.fields['is_initial'].help_text = _('新创建的任务将自动设置为此状态')
        self.fields['is_final'].help_text = _('任务完成后的最终状态')
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # 检查同一看板内是否已存在相同名称的状态
            board = getattr(self.instance, 'board', None)
            if board:
                existing = WorkflowStatus.objects.filter(
                    board=board,
                    name=name
                ).exclude(pk=self.instance.pk if self.instance.pk else None)
                
                if existing.exists():
                    raise forms.ValidationError(
                        _('此看板已存在名为 "{}" 的状态').format(name)
                    )
        return name
    
    def clean_position(self):
        position = self.cleaned_data.get('position')
        if position is not None and position < 0:
            raise forms.ValidationError(_('位置不能为负数'))
        return position


class TaskStatusChangeForm(forms.Form):
    """
    任务状态变更表单
    """
    new_status = forms.ModelChoiceField(
        queryset=WorkflowStatus.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('新状态'),
        help_text=_('选择任务的新状态')
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('添加变更备注（可选）')
        }),
        label=_('变更备注'),
        required=False,
        help_text=_('记录此次状态变更的原因或说明')
    )
    
    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if task:
            # 获取当前任务可转换到的状态
            current_status = task.get_workflow_status()
            if current_status:
                # 获取可转换的状态
                available_transitions = WorkflowTransition.objects.filter(
                    from_status=current_status
                ).select_related('to_status')
                
                self.fields['new_status'].queryset = WorkflowStatus.objects.filter(
                    id__in=[t.to_status.id for t in available_transitions]
                )
            else:
                # 如果没有工作流状态，显示所有该看板的状态
                self.fields['new_status'].queryset = WorkflowStatus.objects.filter(
                    board=task.board,
                    is_active=True
                )
    
    def clean_new_status(self):
        new_status = self.cleaned_data.get('new_status')
        if not new_status:
            raise forms.ValidationError(_('请选择新的状态'))
        return new_status


class WorkflowTransitionForm(forms.ModelForm):
    """
    工作流转换规则表单
    """
    class Meta:
        model = WorkflowTransition
        fields = [
            'from_status', 'to_status', 'name', 'description',
            'require_assignee', 'require_comment', 
            'auto_assign_creator', 'auto_notify_assignees'
        ]
        widgets = {
            'from_status': forms.Select(attrs={'class': 'form-select'}),
            'to_status': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('转换规则名称')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('描述此转换规则的用途和条件')
            }),
            'require_assignee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'require_comment': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_assign_creator': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_notify_assignees': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        
        if board:
            # 限制状态选择范围为当前看板
            board_statuses = WorkflowStatus.objects.filter(board=board, is_active=True)
            self.fields['from_status'].queryset = board_statuses
            self.fields['to_status'].queryset = board_statuses
    
    def clean(self):
        cleaned_data = super().clean()
        from_status = cleaned_data.get('from_status')
        to_status = cleaned_data.get('to_status')
        
        if from_status and to_status:
            if from_status == to_status:
                raise forms.ValidationError(_('源状态和目标状态不能相同'))
            
            # 检查是否已存在相同的转换
            existing = WorkflowTransition.objects.filter(
                from_status=from_status,
                to_status=to_status
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if existing.exists():
                raise forms.ValidationError(
                    _('从 "{}" 到 "{}" 的转换已存在').format(
                        from_status.display_name, 
                        to_status.display_name
                    )
                )
        
        return cleaned_data
