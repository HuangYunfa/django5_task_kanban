"""
Tasks应用视图
任务管理相关视图
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .models import Task, TaskComment, TaskAttachment
from .forms import (
    TaskCreateForm, TaskUpdateForm, TaskCommentForm, 
    TaskLabelForm, TaskAttachmentForm, TaskSearchForm
)
from boards.models import Board, BoardList, BoardLabel

User = get_user_model()


class TaskAccessMixin:
    """任务访问权限混入类"""
    
    def has_task_access(self, task, user):
        """检查用户是否有任务访问权限"""
        # 任务创建者
        if task.creator == user:
            return True
        
        # 任务分配者
        if task.assignees.filter(id=user.id).exists():
            return True
        
        # 看板权限
        board = task.board
        if board.owner == user:
            return True
        
        # 看板成员
        if board.members.filter(user=user).exists():
            return True
        
        # 团队成员
        if board.team and board.team.memberships.filter(user=user).exists():
            return True
        
        # 公开看板
        if board.visibility == 'public':
            return True
        
        return False
    
    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            if not self.has_task_access(obj, request.user):
                messages.error(request, _('您没有权限访问此任务'))
                return redirect('boards:list')
        return super().dispatch(request, *args, **kwargs)


class TaskListView(LoginRequiredMixin, ListView):
    """任务列表视图"""
    model = Task
    template_name = 'tasks/list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        
        # 基础查询：用户可以访问的任务
        queryset = Task.objects.filter(
            Q(creator=user) |  # 自己创建的
            Q(assignees=user) |  # 分配给自己的
            Q(board__owner=user) |  # 自己的看板
            Q(board__members__user=user) |  # 看板成员
            Q(board__team__memberships__user=user) |  # 团队看板
            Q(board__visibility='public')  # 公开看板
        ).distinct().select_related(
            'creator', 'board', 'board_list'
        ).prefetch_related(
            'assignees', 'labels'
        )
        
        # 处理搜索和过滤
        form = TaskSearchForm(self.request.GET, board=None)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            if q:
                queryset = queryset.filter(
                    Q(title__icontains=q) |
                    Q(description__icontains=q)
                )
            
            status = form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status__in=status)
            
            priority = form.cleaned_data.get('priority')
            if priority:
                queryset = queryset.filter(priority__in=priority)
            
            assignee = form.cleaned_data.get('assignee')
            if assignee:
                queryset = queryset.filter(assignees=assignee)
        
        return queryset.order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = TaskSearchForm(self.request.GET)
        
        # 统计信息
        user = self.request.user
        context['total_tasks'] = self.get_queryset().count()
        context['my_tasks'] = self.get_queryset().filter(assignees=user).count()
        context['overdue_tasks'] = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        ).count()
        
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    """创建任务视图"""
    model = Task
    form_class = TaskCreateForm
    template_name = 'tasks/create.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        # 获取看板信息
        board_slug = self.request.GET.get('board')
        if board_slug:
            board = get_object_or_404(Board, slug=board_slug)
            kwargs['board'] = board
        
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        
        # 设置看板
        board_slug = self.request.GET.get('board')
        if board_slug:
            board = get_object_or_404(Board, slug=board_slug)
            form.instance.board = board
        
        messages.success(self.request, _('任务创建成功！'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        board_slug = self.request.GET.get('board')
        if board_slug:
            board = get_object_or_404(Board, slug=board_slug)
            context['board'] = board
        
        return context


class TaskDetailView(LoginRequiredMixin, TaskAccessMixin, DetailView):
    """任务详情视图"""
    model = Task
    template_name = 'tasks/detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return Task.objects.select_related(
            'creator', 'board', 'board_list'
        ).prefetch_related(
            'assignees', 'labels', 'comments__author', 'attachments'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        
        # 评论表单
        context['comment_form'] = TaskCommentForm()
        
        # 附件表单
        context['attachment_form'] = TaskAttachmentForm()
        
        # 权限检查
        context['can_edit'] = (
            task.creator == self.request.user or 
            task.board.owner == self.request.user or
            task.board.members.filter(
                user=self.request.user, 
                role__in=['admin', 'owner']
            ).exists()
        )
        
        # 活动记录（评论和系统活动）
        context['activities'] = task.comments.all().order_by('-created_at')
        
        return context


class TaskUpdateView(LoginRequiredMixin, TaskAccessMixin, UpdateView):
    """编辑任务视图"""
    model = Task
    form_class = TaskUpdateForm
    template_name = 'tasks/edit.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['board'] = self.object.board
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _('任务更新成功！'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(LoginRequiredMixin, TaskAccessMixin, DeleteView):
    """删除任务视图"""
    model = Task
    template_name = 'tasks/delete.html'
    
    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        board_slug = task.board.slug
        messages.success(request, _('任务删除成功！'))
        result = super().delete(request, *args, **kwargs)
        return result
    
    def get_success_url(self):
        return reverse('boards:detail', kwargs={'slug': self.object.board.slug})


class TaskStatusUpdateView(LoginRequiredMixin, TaskAccessMixin, View):
    """任务状态更新视图"""
    
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        
        if not self.has_task_access(task, request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            
            return JsonResponse({
                'success': True,
                'status': new_status,
                'status_display': task.get_status_display()
            })
        
        return JsonResponse({
            'success': False,
            'error': 'Invalid status'
        }, status=400)


# API视图
class TaskCommentCreateView(LoginRequiredMixin, TaskAccessMixin, View):
    """创建任务评论API"""
    
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        
        if not self.has_task_access(task, request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        form = TaskCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.get_display_name(),
                    'created_at': comment.created_at.isoformat()
                }
            })
        
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


class TaskMoveView(LoginRequiredMixin, TaskAccessMixin, View):
    """任务移动API"""
    
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        
        if not self.has_task_access(task, request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        new_list_id = request.POST.get('list_id')
        new_position = request.POST.get('position', 0)
        
        try:
            new_list = BoardList.objects.get(id=new_list_id, board=task.board)
            task.board_list = new_list
            task.position = int(new_position)
            task.save()
            
            return JsonResponse({
                'success': True,
                'list_id': new_list.id,
                'position': task.position
            })
        except (BoardList.DoesNotExist, ValueError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid list or position'
            }, status=400)
