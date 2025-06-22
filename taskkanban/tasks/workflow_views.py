"""
任务状态流转系统视图
处理工作流状态管理、状态转换、自动化规则等功能
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Prefetch, Max
from django.db import models
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import transaction

from .workflow_models import (
    WorkflowStatus, WorkflowTransition, TaskStatusHistory, 
    WorkflowRule, WorkflowRuleExecution
)
from .models import Task
from boards.models import Board, BoardList
from boards.views import BoardAccessMixin


class WorkflowStatusListView(LoginRequiredMixin, BoardAccessMixin, ListView):
    """工作流状态列表视图"""
    model = WorkflowStatus
    template_name = 'tasks/workflow/status_list.html'
    context_object_name = 'statuses'
    
    def get_board(self):
        return get_object_or_404(Board, slug=self.kwargs['board_slug'])
    
    def get_queryset(self):
        board = self.get_board()
        return WorkflowStatus.objects.filter(board=board).order_by('position')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_board()
        context['board'] = board
        
        # 获取转换规则
        transitions = WorkflowTransition.objects.filter(
            from_status__board=board
        ).select_related('from_status', 'to_status')
        context['transitions'] = transitions
        
        return context


class WorkflowStatusCreateView(LoginRequiredMixin, BoardAccessMixin, CreateView):
    """创建工作流状态视图"""
    model = WorkflowStatus
    template_name = 'tasks/workflow/status_form.html'
    fields = ['name', 'display_name', 'color', 'position', 'is_initial', 'is_final']
    
    def get_board(self):
        return get_object_or_404(Board, slug=self.kwargs['board_slug'])
    
    def test_func(self):
        board = self.get_board()
        return self.has_board_edit_access(board, self.request.user)
    
    def form_valid(self, form):
        board = self.get_board()
        form.instance.board = board
          # 如果没有设置位置，设为最后
        if not form.instance.position:
            max_position = WorkflowStatus.objects.filter(
                board=board
            ).aggregate(Max('position'))['position__max'] or 0
            form.instance.position = max_position + 1
        
        messages.success(
            self.request,
            _('工作流状态 "{}" 创建成功！').format(form.instance.display_name)
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tasks:workflow_status_list', kwargs={
            'board_slug': self.kwargs['board_slug']
        })


class TaskStatusChangeView(LoginRequiredMixin, View):
    """任务状态变更视图"""
    
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        
        # 权限检查
        if not self.has_task_edit_access(task, request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        new_status = request.POST.get('new_status')
        comment = request.POST.get('comment', '')
        transition_id = request.POST.get('transition_id')
        
        if not new_status:
            return JsonResponse({'error': 'Missing new_status'}, status=400)
        
        # 验证状态转换
        if transition_id:
            try:
                transition = WorkflowTransition.objects.get(id=transition_id)
                if not self.can_use_transition(transition, task, request.user):
                    return JsonResponse({'error': 'Cannot use this transition'}, status=400)
            except WorkflowTransition.DoesNotExist:
                transition = None
        else:
            transition = None
        
        # 执行状态变更
        old_status = task.status
        
        try:
            with transaction.atomic():
                # 更新任务状态
                task.status = new_status
                task.save(update_fields=['status'])
                
                # 记录状态变更历史
                TaskStatusHistory.objects.create(
                    task=task,
                    from_status=old_status,
                    to_status=new_status,
                    changed_by=request.user,
                    comment=comment,
                    transition_used=transition
                )
                
                # 执行转换后的自动化动作
                if transition:
                    self.execute_transition_actions(transition, task, request.user)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
        return JsonResponse({
            'success': True,
            'message': _('任务状态已更新'),
            'old_status': old_status,
            'new_status': new_status,
            'task_id': task.id
        })
    
    def has_task_edit_access(self, task, user):
        """检查用户是否有任务编辑权限"""
        # 任务创建者
        if task.creator == user:
            return True
        
        # 任务受理人
        if task.assignees.filter(id=user.id).exists():
            return True
        
        # 看板权限检查
        board = task.board
        if board.owner == user:
            return True
        
        # 看板成员权限
        from boards.models import BoardMember
        if BoardMember.objects.filter(
            board=board, 
            user=user, 
            role__in=['admin', 'owner', 'member']
        ).exists():
            return True
        
        return False
    
    def can_use_transition(self, transition, task, user):
        """检查用户是否可以使用指定的转换"""
        # 检查转换的条件
        if transition.require_assignee and not task.assignees.exists():
            return False
        
        # 检查允许的角色
        if transition.allowed_roles:
            user_roles = self.get_user_roles(user, task.board)
            if not any(role in transition.allowed_roles for role in user_roles):
                return False
        
        return True
    
    def get_user_roles(self, user, board):
        """获取用户在看板中的角色"""
        roles = []
        
        if board.owner == user:
            roles.append('owner')
        
        from boards.models import BoardMember
        member = BoardMember.objects.filter(board=board, user=user).first()
        if member:
            roles.append(member.role)
        
        return roles
    
    def execute_transition_actions(self, transition, task, user):
        """执行转换的自动化动作"""
        # 自动分配给创建者
        if transition.auto_assign_creator and task.creator:
            task.assignees.add(task.creator)
        
        # 自动移动到指定列表
        if transition.auto_move_to_list:
            task.board_list = transition.auto_move_to_list
            task.save(update_fields=['board_list'])
        
        # 自动通知受理人
        if transition.auto_notify_assignees and task.assignees.exists():
            # 这里后续可以集成通知系统
            pass


class TaskStatusHistoryView(LoginRequiredMixin, View):
    """任务状态历史查看视图"""
    
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        
        # 权限检查
        if not self.has_task_view_access(task, request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # 获取状态历史
        history = task.status_history.select_related(
            'changed_by', 'transition_used'
        ).order_by('-created_at')
        
        history_data = []
        for record in history:
            history_data.append({
                'id': record.id,
                'from_status': record.from_status,
                'to_status': record.to_status,
                'from_status_display': record.get_status_display(record.from_status),
                'to_status_display': record.get_status_display(record.to_status),
                'changed_by': {
                    'id': record.changed_by.id,
                    'username': record.changed_by.username,
                    'display_name': record.changed_by.get_display_name()
                },
                'comment': record.comment,
                'is_auto_change': record.is_auto_change,
                'auto_rule_name': record.auto_rule_name,
                'transition_name': record.transition_used.name if record.transition_used else '',
                'created_at': record.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'history': history_data
        })
    
    def has_task_view_access(self, task, user):
        """检查用户是否有任务查看权限"""
        # 基本上与编辑权限相同，但更宽松
        board = task.board
        
        # 公开看板
        if board.visibility == 'public':
            return True
        
        # 看板所有者
        if board.owner == user:
            return True
        
        # 看板成员
        from boards.models import BoardMember
        if BoardMember.objects.filter(board=board, user=user).exists():
            return True
        
        # 团队成员
        if board.team and board.team.memberships.filter(user=user).exists():
            return True
        
        return False


class WorkflowTransitionListView(LoginRequiredMixin, BoardAccessMixin, ListView):
    """工作流转换规则列表视图"""
    model = WorkflowTransition
    template_name = 'tasks/workflow/transition_list.html'
    context_object_name = 'transitions'
    
    def get_board(self):
        return get_object_or_404(Board, slug=self.kwargs['board_slug'])
    
    def get_queryset(self):
        board = self.get_board()
        return WorkflowTransition.objects.filter(
            from_status__board=board
        ).select_related('from_status', 'to_status').order_by(
            'from_status__position', 'to_status__position'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_board()
        context['board'] = board
        context['statuses'] = board.workflow_statuses.filter(is_active=True)
        return context


class WorkflowRuleListView(LoginRequiredMixin, BoardAccessMixin, ListView):
    """工作流自动化规则列表视图"""
    model = WorkflowRule
    template_name = 'tasks/workflow/rule_list.html'
    context_object_name = 'rules'
    paginate_by = 20
    
    def get_board(self):
        return get_object_or_404(Board, slug=self.kwargs['board_slug'])
    
    def get_queryset(self):
        board = self.get_board()
        return WorkflowRule.objects.filter(board=board).order_by('-priority', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_board()
        context['board'] = board
        
        # 统计信息
        context['total_rules'] = self.get_queryset().count()
        context['active_rules'] = self.get_queryset().filter(is_active=True).count()
        
        return context


class WorkflowStatsView(LoginRequiredMixin, BoardAccessMixin, TemplateView):
    """工作流统计视图"""
    template_name = 'tasks/workflow/stats.html'
    
    def get_board(self):
        return get_object_or_404(Board, slug=self.kwargs['board_slug'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_board()
        context['board'] = board
        
        # 状态统计
        status_stats = []
        for status in board.workflow_statuses.filter(is_active=True):
            task_count = Task.objects.filter(board=board, status=status.name).count()
            status_stats.append({
                'status': status,
                'task_count': task_count
            })
        context['status_stats'] = status_stats
        
        # 最近的状态变更
        recent_changes = TaskStatusHistory.objects.filter(
            task__board=board
        ).select_related(
            'task', 'changed_by'
        ).order_by('-created_at')[:10]
        context['recent_changes'] = recent_changes
        
        # 规则执行统计
        rule_stats = WorkflowRuleExecution.objects.filter(
            rule__board=board
        ).values('rule__name').annotate(
            total_executions=Count('id'),
            success_executions=Count('id', filter=Q(success=True))
        ).order_by('-total_executions')[:10]
        context['rule_stats'] = rule_stats
        
        return context
