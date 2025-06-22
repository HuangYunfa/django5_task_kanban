"""
Users应用视图
用户管理相关视图
"""
from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserListView(LoginRequiredMixin, ListView):
    """用户列表视图"""
    model = User
    template_name = 'users/list.html'
    context_object_name = 'users'
    paginate_by = 20


class UserDetailView(LoginRequiredMixin, DetailView):
    """用户详情视图"""
    model = User
    template_name = 'users/detail.html'
    context_object_name = 'user_detail'


class UserProfileView(LoginRequiredMixin, TemplateView):
    """用户资料视图"""
    template_name = 'users/profile.html'


class UserSettingsView(LoginRequiredMixin, TemplateView):
    """用户设置视图"""
    template_name = 'users/settings.html'
