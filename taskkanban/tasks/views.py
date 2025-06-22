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
from django.db.models import Q, Count, Prefetch, F
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.db import transaction
import json

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
        
        # 任务分配给用户
        if task.assignees.filter(id=user.id).exists():
            return True
          # 看板成员
        board = task.board
        if board.owner == user:
            return True
              # 团队成员权限
        if board.team:
            team_membership = board.team.memberships.filter(user=user, status='active').first()
            if team_membership:
                return True
        
        # 看板成员权限
        board_membership = board.members.filter(user=user, is_active=True).first()
        if board_membership:
            return True
              # 公开看板的读取权限
        if board.visibility == 'public':
            return True
            
        return False

    def has_task_edit_access(self, task, user):
        """检查用户是否有任务编辑权限"""
        # 任务创建者
        if task.creator == user:
            return True
        
        # 看板创建者
        board = task.board
        if board.owner == user:
            return True
            
        # 团队管理员
        if board.team:
            team_membership = board.team.memberships.filter(user=user, role__in=['admin', 'owner'], status='active').first()
            if team_membership:
                return True
        
        # 看板管理员
        board_membership = board.members.filter(user=user, role='admin', is_active=True).first()
        if board_membership:
            return True
            
        return False


class TaskListView(LoginRequiredMixin, ListView):
    """任务列表视图"""
    model = Task
    template_name = 'tasks/list.html'
    context_object_name = 'tasks'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Task.objects.filter(
            board__in=self.get_accessible_boards()
        ).select_related(
            'board', 'board_list', 'creator'
        ).prefetch_related(
            'labels', 'assignees'
        ).order_by('-created_at')
        
        # 搜索过滤
        search_form = TaskSearchForm(self.request.GET)
        if search_form.is_valid():
            q = search_form.cleaned_data.get('q')
            if q:
                queryset = queryset.filter(
                    Q(title__icontains=q) | 
                    Q(description__icontains=q)
                )
            
            status = search_form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status=status)
                
            priority = search_form.cleaned_data.get('priority')
            if priority:
                queryset = queryset.filter(priority=priority)
                
            assignee = search_form.cleaned_data.get('assignee')
            if assignee:
                queryset = queryset.filter(assignees=assignee)
                
            board = search_form.cleaned_data.get('board')
            if board:
                queryset = queryset.filter(board=board)        
        return queryset
    
    def get_accessible_boards(self):
        """获取用户可访问的看板"""
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) |  # 自己创建的看板
            Q(team__memberships__user=user, team__memberships__status='active') |  # 团队成员
            Q(members__user=user, members__is_active=True) |  # 看板成员
            Q(visibility='public')  # 公开看板
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 统计信息
        accessible_boards = self.get_accessible_boards()
        all_tasks = Task.objects.filter(board__in=accessible_boards)
        
        context.update({
            'search_form': TaskSearchForm(self.request.GET, user=self.request.user),
            'total_tasks': all_tasks.count(),
            'my_tasks': all_tasks.filter(assignees=self.request.user).count(),
            'overdue_tasks': all_tasks.filter(
                due_date__lt=timezone.now(),
                status__in=['todo', 'in_progress']
            ).count(),
        })
        
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


class TaskBatchOperationView(LoginRequiredMixin, View):
    """任务批量操作API"""
    
    def post(self, request):
        """批量操作处理"""
        try:
            # 尝试解析JSON数据
            if request.content_type == 'application/json':
                import json
                data = json.loads(request.body)
                task_ids = data.get('task_ids', [])
                operation = data.get('action') or data.get('operation')
            else:
                # 处理表单数据
                task_ids = request.POST.getlist('task_ids')
                operation = request.POST.get('action') or request.POST.get('operation')
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        
        if not task_ids:
            return JsonResponse({
                'success': False,
                'error': 'No tasks selected'
            }, status=400)
        
        if not operation:
            return JsonResponse({
                'success': False,
                'error': 'No operation specified'
            }, status=400)
        
        # 验证任务权限
        tasks = []
        for task_id in task_ids:
            try:
                task = Task.objects.get(id=task_id)
                if not self.has_task_edit_access(task, request.user):
                    return JsonResponse({
                        'success': False,
                        'error': f'No permission to edit task {task_id}'
                    }, status=403)
                tasks.append(task)
            except Task.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Task {task_id} not found'
                }, status=404)
        
        # 执行批量操作
        try:
            with transaction.atomic():
                if operation == 'delete':
                    count = len(tasks)
                    for task in tasks:
                        task.is_archived = True  # 软删除
                        task.save(update_fields=['is_archived', 'updated_at'])
                    return JsonResponse({
                        'success': True,
                        'message': f'Successfully deleted {count} tasks'
                    })
                
                elif operation == 'change_status':
                    if request.content_type == 'application/json':
                        new_status = data.get('new_status')
                    else:
                        new_status = request.POST.get('new_status')
                    
                    if new_status not in dict(Task.STATUS_CHOICES):
                        return JsonResponse({
                            'success': False,
                            'error': 'Invalid status'
                        }, status=400)
                    
                    count = 0
                    for task in tasks:
                        task.status = new_status
                        task.save(update_fields=['status', 'updated_at'])
                        count += 1
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Successfully updated {count} tasks'
                    })
                
                elif operation == 'change_priority':
                    if request.content_type == 'application/json':
                        new_priority = data.get('new_priority')
                    else:
                        new_priority = request.POST.get('new_priority')
                        
                    if new_priority not in dict(Task.PRIORITY_CHOICES):
                        return JsonResponse({
                            'success': False,
                            'error': 'Invalid priority'
                        }, status=400)
                    
                    count = 0
                    for task in tasks:
                        task.priority = new_priority
                        task.save(update_fields=['priority', 'updated_at'])
                        count += 1
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Successfully updated {count} tasks'
                    })
                
                elif operation == 'assign':
                    if request.content_type == 'application/json':
                        assignee_id = data.get('assignee_id')
                    else:
                        assignee_id = request.POST.get('assignee_id')
                    
                    if assignee_id:
                        try:
                            assignee = User.objects.get(id=assignee_id)
                        except User.DoesNotExist:
                            return JsonResponse({
                                'success': False,
                                'error': 'Assignee not found'
                            }, status=404)
                    else:
                        assignee = None
                    
                    count = 0
                    for task in tasks:
                        if assignee:
                            task.assignees.add(assignee)
                        else:
                            task.assignees.clear()
                        count += 1
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Successfully assigned {count} tasks'
                    })
                
                elif operation == 'move_to_list':
                    if request.content_type == 'application/json':
                        new_list_id = data.get('new_list_id')
                    else:
                        new_list_id = request.POST.get('new_list_id')
                    
                    if not new_list_id:
                        return JsonResponse({
                            'success': False,
                            'error': 'No target list specified'
                        }, status=400)
                    
                    try:
                        new_list = BoardList.objects.get(id=new_list_id)
                    except BoardList.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'error': 'Target list not found'
                        }, status=404)
                    
                    # 验证所有任务都属于同一个看板
                    board = tasks[0].board
                    if not all(task.board == board for task in tasks):
                        return JsonResponse({
                            'success': False,
                            'error': 'All tasks must belong to the same board'
                        }, status=400)
                    
                    # 验证目标列表属于同一个看板  
                    if new_list.board != board:
                        return JsonResponse({
                            'success': False,
                            'error': 'Target list must belong to the same board'
                        }, status=400)
                    
                    count = 0
                    for task in tasks:
                        task.board_list = new_list
                        task.save(update_fields=['board_list', 'updated_at'])
                        count += 1
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Successfully moved {count} tasks'
                    })
                
                else:
                    return JsonResponse({
                        'success': False,
                        'error': f'Unknown operation: {operation}'
                    }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def has_task_edit_access(self, task, user):
        """检查用户是否有编辑任务的权限"""
        # 任务创建者
        if task.creator == user:
            return True
        
        # 任务被分配人
        if task.assignees.filter(id=user.id).exists():
            return True
            
        # 看板所有者
        if task.board.owner == user:
            return True
        
        # 看板管理员
        board_membership = task.board.members.filter(user=user, role='admin', is_active=True).first()
        if board_membership:
            return True
            
        return False


class TaskSortView(LoginRequiredMixin, View):
    """任务拖拽排序API"""
    
    def post(self, request):
        """处理任务拖拽排序"""
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            new_list_id = data.get('new_list_id')
            new_position = data.get('new_position', 0)
            old_list_id = data.get('old_list_id')
            
            # 获取任务
            task = get_object_or_404(Task, id=task_id)
            
            # 检查权限
            if not self.has_task_edit_access(task, request.user):
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied'
                }, status=403)
            
            # 验证目标列表
            new_list = get_object_or_404(BoardList, id=new_list_id)
            if new_list.board != task.board:
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot move task to different board'
                }, status=400)
            
            with transaction.atomic():
                old_list = task.board_list
                
                # 如果是跨列表移动
                if new_list_id != old_list_id:
                    # 更新原列表中其他任务的位置
                    old_list.tasks.filter(
                        position__gt=task.position
                    ).update(position=F('position') - 1)
                    
                    # 更新目标列表中任务的位置
                    new_list.tasks.filter(
                        position__gte=new_position
                    ).update(position=F('position') + 1)
                    
                    # 更新任务的列表和位置
                    task.board_list = new_list
                    task.position = new_position
                else:
                    # 同一列表内排序
                    if new_position > task.position:
                        # 向下移动
                        new_list.tasks.filter(
                            position__gt=task.position,
                            position__lte=new_position
                        ).update(position=F('position') - 1)
                    else:
                        # 向上移动
                        new_list.tasks.filter(
                            position__gte=new_position,
                            position__lt=task.position
                        ).update(position=F('position') + 1)
                    
                    task.position = new_position
                
                task.save()
                
                return JsonResponse({
                    'success': True,
                    'task_id': task_id,
                    'new_list_id': new_list_id,
                    'new_position': new_position
                })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def has_task_edit_access(self, task, user):
        """检查用户是否有任务编辑权限"""
        # 任务创建者
        if task.creator == user:
            return True
          # 看板创建者
        board = task.board
        if board.owner == user:
            return True
            
        # 团队管理员
        if board.team:
            team_membership = board.team.memberships.filter(user=user, role__in=['admin', 'owner'], status='active').first()
            if team_membership:
                return True
        
        # 看板管理员
        board_membership = board.members.filter(user=user, role='admin', is_active=True).first()
        if board_membership:
            return True
            
        return False
