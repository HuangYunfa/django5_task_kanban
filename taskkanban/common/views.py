"""
Common应用视图
通用功能视图
"""
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.contrib.auth import get_user_model

User = get_user_model()

# 导入相关模型用于统计
try:
    from boards.models import Board
    from tasks.models import Task
    from teams.models import Team
except ImportError:
    # 如果模型不存在，设置为None
    Board = None
    Task = None
    Team = None


class IndexView(TemplateView):
    """首页视图"""
    template_name = 'common/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 为已登录用户提供额外的上下文信息
        if self.request.user.is_authenticated:
            context['show_dashboard_link'] = True
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """仪表板视图"""
    template_name = 'common/dashboard.html'
    login_url = '/accounts/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 添加仪表板统计数据
        context.update({
            'total_users': User.objects.count(),
            'total_boards': Board.objects.count() if Board else 0,
            'total_tasks': Task.objects.count() if Task else 0,
            'total_teams': Team.objects.count() if Team else 0,
        })
          # 添加当前用户相关的数据
        if self.request.user.is_authenticated:
            user = self.request.user
            context.update({
                'my_boards_count': Board.objects.filter(owner=user).count() if Board else 0,
                'my_tasks_count': Task.objects.filter(assignees=user).count() if Task else 0,
                'my_teams_count': user.team_memberships.count() if hasattr(user, 'team_memberships') else 0,
            })
        
        return context
