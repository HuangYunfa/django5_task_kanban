"""
Reports应用视图
报表分析相关视图
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class ReportIndexView(LoginRequiredMixin, TemplateView):
    """报表首页视图"""
    template_name = 'reports/index.html'


class TaskReportView(LoginRequiredMixin, TemplateView):
    """任务统计报表视图"""
    template_name = 'reports/tasks.html'


class TeamPerformanceView(LoginRequiredMixin, TemplateView):
    """团队绩效报表视图"""
    template_name = 'reports/team_performance.html'


class ProjectProgressView(LoginRequiredMixin, TemplateView):
    """项目进度报表视图"""
    template_name = 'reports/project_progress.html'


class CustomReportView(LoginRequiredMixin, TemplateView):
    """自定义报表视图"""
    template_name = 'reports/custom.html'
