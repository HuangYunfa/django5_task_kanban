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


class IndexView(TemplateView):
    """首页视图"""
    template_name = 'common/index.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # 如果用户已登录，重定向到仪表板
            return redirect('common:dashboard')
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """仪表板视图"""
    template_name = 'common/dashboard.html'
    login_url = '/accounts/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 添加仪表板统计数据
        context.update({
            'total_users': User.objects.count(),
            'total_boards': 0,  # 稍后从boards应用获取
            'total_tasks': 0,   # 稍后从tasks应用获取
            'total_teams': 0,   # 稍后从teams应用获取
        })
        
        return context
