"""
Tasks应用视图
任务管理相关视图
"""
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class TaskListView(LoginRequiredMixin, TemplateView):
    """任务列表视图"""
    template_name = 'tasks/list.html'


class TaskCreateView(LoginRequiredMixin, TemplateView):
    """创建任务视图"""
    template_name = 'tasks/create.html'


class TaskDetailView(LoginRequiredMixin, TemplateView):
    """任务详情视图"""
    template_name = 'tasks/detail.html'


class TaskUpdateView(LoginRequiredMixin, TemplateView):
    """编辑任务视图"""
    template_name = 'tasks/edit.html'


class TaskDeleteView(LoginRequiredMixin, TemplateView):
    """删除任务视图"""
    template_name = 'tasks/delete.html'


class TaskStatusUpdateView(LoginRequiredMixin, TemplateView):
    """任务状态更新视图"""
    template_name = 'tasks/status_update.html'
