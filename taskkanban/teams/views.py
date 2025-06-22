"""
Teams应用视图
团队管理相关视图
"""
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class TeamListView(LoginRequiredMixin, TemplateView):
    """团队列表视图"""
    template_name = 'teams/list.html'


class TeamCreateView(LoginRequiredMixin, TemplateView):
    """创建团队视图"""
    template_name = 'teams/create.html'


class TeamDetailView(LoginRequiredMixin, TemplateView):
    """团队详情视图"""
    template_name = 'teams/detail.html'


class TeamUpdateView(LoginRequiredMixin, TemplateView):
    """编辑团队视图"""
    template_name = 'teams/edit.html'


class TeamMemberView(LoginRequiredMixin, TemplateView):
    """团队成员管理视图"""
    template_name = 'teams/members.html'
