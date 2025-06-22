"""
Reports应用表单
报表分析相关表单
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .models import Report

User = get_user_model()


class ReportFilterForm(forms.Form):
    """报表筛选表单"""
    
    # 时间范围选择
    TIME_RANGE_CHOICES = [
        ('7days', _('最近7天')),
        ('30days', _('最近30天')),
        ('3months', _('最近3个月')),
        ('6months', _('最近6个月')),
        ('1year', _('最近1年')),
        ('custom', _('自定义范围')),
    ]
    
    time_range = forms.ChoiceField(
        label=_('时间范围'),
        choices=TIME_RANGE_CHOICES,
        initial='30days',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'timeRangeSelect'
        })
    )
    
    start_date = forms.DateField(
        label=_('开始日期'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'startDate'
        })
    )
    
    end_date = forms.DateField(
        label=_('结束日期'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'endDate'
        })
    )
    
    # 团队筛选
    team = forms.ModelChoiceField(
        label=_('团队'),
        queryset=None,  # 将在__init__中设置
        required=False,
        empty_label=_('所有团队'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # 看板筛选
    board = forms.ModelChoiceField(
        label=_('看板'),
        queryset=None,  # 将在__init__中设置
        required=False,
        empty_label=_('所有看板'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # 用户筛选
    user = forms.ModelChoiceField(
        label=_('用户'),
        queryset=None,  # 将在__init__中设置
        required=False,
        empty_label=_('所有用户'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # 获取用户相关的团队
            from teams.models import Team
            user_teams = Team.objects.filter(
                memberships__user=user,
                memberships__status='active'
            ).distinct()
            self.fields['team'].queryset = user_teams
            
            # 获取用户相关的看板
            from boards.models import Board
            user_boards = Board.objects.filter(
                models.Q(created_by=user) |
                models.Q(members=user)
            ).distinct()
            self.fields['board'].queryset = user_boards
            
            # 获取团队相关的用户
            from django.db import models
            team_users = User.objects.filter(
                team_memberships__team__in=user_teams,
                team_memberships__status='active'
            ).distinct()
            self.fields['user'].queryset = team_users

    def get_date_range(self):
        """获取日期范围"""
        time_range = self.cleaned_data.get('time_range')
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        
        today = datetime.now().date()
        
        if time_range == 'custom' and start_date and end_date:
            return start_date, end_date
        elif time_range == '7days':
            return today - timedelta(days=7), today
        elif time_range == '30days':
            return today - timedelta(days=30), today
        elif time_range == '3months':
            return today - timedelta(days=90), today
        elif time_range == '6months':
            return today - timedelta(days=180), today
        elif time_range == '1year':
            return today - timedelta(days=365), today
        else:
            return today - timedelta(days=30), today


class ReportCreateForm(forms.ModelForm):
    """报表创建表单"""
    
    class Meta:
        model = Report
        fields = ['name', 'description', 'report_type', 'frequency', 'board', 'team']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('输入报表名称')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('报表描述（可选）'),
                'rows': 3
            }),
            'report_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'board': forms.Select(attrs={
                'class': 'form-select'
            }),
            'team': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # 设置用户相关的团队和看板选项
            from teams.models import Team
            from boards.models import Board
            from django.db import models
            
            user_teams = Team.objects.filter(
                memberships__user=user,
                memberships__status='active'
            ).distinct()
            self.fields['team'].queryset = user_teams
            self.fields['team'].empty_label = _('选择团队（可选）')
            
            user_boards = Board.objects.filter(
                models.Q(created_by=user) |
                models.Q(members=user)
            ).distinct()
            self.fields['board'].queryset = user_boards
            self.fields['board'].empty_label = _('选择看板（可选）')

    def save(self, commit=True):
        report = super().save(commit=False)
        if hasattr(self, 'user'):
            report.created_by = self.user
        if commit:
            report.save()
        return report


class ChartConfigForm(forms.Form):
    """图表配置表单"""
    
    CHART_TYPES = [
        ('line', _('折线图')),
        ('bar', _('柱状图')),
        ('pie', _('饼图')),
        ('doughnut', _('环形图')),
        ('area', _('面积图')),
        ('scatter', _('散点图')),
    ]
    
    chart_type = forms.ChoiceField(
        label=_('图表类型'),
        choices=CHART_TYPES,
        initial='bar',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    show_legend = forms.BooleanField(
        label=_('显示图例'),
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    show_labels = forms.BooleanField(
        label=_('显示标签'),
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    animate = forms.BooleanField(
        label=_('动画效果'),
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class ExportForm(forms.Form):
    """报表导出表单"""
    
    EXPORT_FORMATS = [
        ('pdf', _('PDF文件')),
        ('excel', _('Excel文件')),
        ('csv', _('CSV文件')),
        ('png', _('PNG图片')),
        ('jpg', _('JPG图片')),
    ]
    
    format = forms.ChoiceField(
        label=_('导出格式'),
        choices=EXPORT_FORMATS,
        initial='pdf',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    include_charts = forms.BooleanField(
        label=_('包含图表'),
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    include_data = forms.BooleanField(
        label=_('包含原始数据'),
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
