"""
Boards应用视图
看板管理相关视图
"""
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class BoardListView(LoginRequiredMixin, TemplateView):
    """看板列表视图"""
    template_name = 'boards/list.html'


class BoardCreateView(LoginRequiredMixin, TemplateView):
    """创建看板视图"""
    template_name = 'boards/create.html'


class BoardDetailView(LoginRequiredMixin, TemplateView):
    """看板详情视图"""
    template_name = 'boards/detail.html'


class BoardUpdateView(LoginRequiredMixin, TemplateView):
    """编辑看板视图"""
    template_name = 'boards/edit.html'


class BoardDeleteView(LoginRequiredMixin, TemplateView):
    """删除看板视图"""
    template_name = 'boards/delete.html'
