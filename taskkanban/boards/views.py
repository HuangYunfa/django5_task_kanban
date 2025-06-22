"""
Boards应用视图
看板管理相关视图
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Prefetch, Max
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .models import Board, BoardList, BoardMember
from .forms import (
    BoardCreateForm, BoardUpdateForm, BoardListCreateForm, 
    BoardMemberInviteForm, BoardSearchForm
)
from tasks.models import Task

User = get_user_model()


class BoardAccessMixin(UserPassesTestMixin):
    """
    看板访问权限检查混入类
    """
    def test_func(self):
        board = self.get_board()
        return self.has_board_access(board, self.request.user)
    
    def get_board(self):
        """获取看板对象"""
        if hasattr(self, 'object') and self.object:
            return self.object
        
        # 从URL参数获取
        slug = self.kwargs.get('slug') or self.kwargs.get('board_slug')
        if slug:
            return get_object_or_404(Board, slug=slug)
        
        pk = self.kwargs.get('pk') or self.kwargs.get('board_pk')
        if pk:
            return get_object_or_404(Board, pk=pk)
        
        return None
    
    def has_board_access(self, board, user):
        """检查用户是否有看板访问权限"""
        if not board or not user.is_authenticated:
            return False
        
        # 看板所有者总是有权限
        if board.owner == user:
            return True
        
        # 检查看板成员权限
        if BoardMember.objects.filter(board=board, user=user).exists():
            return True
          # 检查团队成员权限
        if board.team and board.team.memberships.filter(user=user).exists():
            return True
        
        # 公开看板任何人都可以访问
        if board.visibility == 'public':
            return True
        
        return False


class BoardListView(LoginRequiredMixin, ListView):
    """看板列表视图"""
    model = Board
    template_name = 'boards/list.html'
    context_object_name = 'boards'
    paginate_by = 12
    
    def get_queryset(self):
        user = self.request.user        # 基础查询：用户可以访问的看板
        queryset = Board.objects.filter(
            Q(owner=user) |  # 自己创建的
            Q(members__user=user) |  # 被邀请的
            Q(team__memberships__user=user) |  # 团队看板
            Q(visibility='public')  # 公开看板
        ).distinct().select_related('owner', 'team').prefetch_related(
            'members__user'
        ).annotate(
            total_tasks=Count('lists__tasks', distinct=True),
            total_members=Count('members', distinct=True)
        )
        
        # 处理搜索和过滤
        form = BoardSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            if q:
                queryset = queryset.filter(
                    Q(name__icontains=q) | Q(description__icontains=q)
                )
            
            template = form.cleaned_data.get('template')
            if template:
                queryset = queryset.filter(template=template)
            
            visibility = form.cleaned_data.get('visibility')
            if visibility:
                queryset = queryset.filter(visibility=visibility)
            
            is_closed = form.cleaned_data.get('is_closed')
            if not is_closed:
                queryset = queryset.filter(is_closed=False)
        else:
            # 默认不显示已关闭的看板
            queryset = queryset.filter(is_closed=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = BoardSearchForm(self.request.GET)
        context['total_boards'] = self.get_queryset().count()
          # 分类统计
        user = self.request.user
        context['my_boards_count'] = Board.objects.filter(owner=user).count()
        context['team_boards_count'] = Board.objects.filter(
            team__memberships__user=user
        ).distinct().count()
        context['public_boards_count'] = Board.objects.filter(
            visibility='public'
        ).count()
        
        return context


class BoardCreateView(LoginRequiredMixin, CreateView):
    """创建看板视图"""
    model = Board
    form_class = BoardCreateForm
    template_name = 'boards/create.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        
        # 创建默认列表
        self.create_default_lists(form.instance)
        
        messages.success(
            self.request, 
            _('看板 "{}" 创建成功！').format(form.instance.name)
        )
        return response
    
    def create_default_lists(self, board):
        """根据模板创建默认列表"""
        template = board.template
        
        if template == 'kanban':
            default_lists = [
                {'name': _('待办'), 'position': 1},
                {'name': _('进行中'), 'position': 2},
                {'name': _('已完成'), 'position': 3},
            ]
        elif template == 'scrum':
            default_lists = [
                {'name': _('产品待办'), 'position': 1},
                {'name': _('冲刺待办'), 'position': 2},
                {'name': _('进行中'), 'position': 3},
                {'name': _('测试中'), 'position': 4},
                {'name': _('已完成'), 'position': 5},
            ]
        elif template == 'personal':
            default_lists = [
                {'name': _('今日任务'), 'position': 1},
                {'name': _('本周任务'), 'position': 2},
                {'name': _('以后再做'), 'position': 3},
                {'name': _('已完成'), 'position': 4},
            ]
        elif template == 'project':
            default_lists = [
                {'name': _('需求分析'), 'position': 1},
                {'name': _('设计开发'), 'position': 2},
                {'name': _('测试验收'), 'position': 3},
                {'name': _('上线部署'), 'position': 4},
            ]
        else:  # custom
            default_lists = [
                {'name': _('待办'), 'position': 1},
                {'name': _('进行中'), 'position': 2},
                {'name': _('已完成'), 'position': 3},
            ]
        
        for list_data in default_lists:
            BoardList.objects.create(
                board=board,
                name=list_data['name'],
                position=list_data['position']
            )
    
    def get_success_url(self):
        return reverse('boards:detail', kwargs={'slug': self.object.slug})


class BoardDetailView(LoginRequiredMixin, BoardAccessMixin, DetailView):
    """看板详情视图"""
    model = Board
    template_name = 'boards/detail.html'
    context_object_name = 'board'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        obj = super().get_object()
        # 检查看板是否已关闭且用户不是所有者
        if obj.is_closed and obj.owner != self.request.user:
            if not BoardMember.objects.filter(
                board=obj, 
                user=self.request.user, 
                role__in=['admin', 'owner']
            ).exists():
                messages.warning(
                    self.request, 
                    _('该看板已关闭，您只能查看不能编辑')
                )
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.object
        
        # 获取看板列表和任务
        lists = BoardList.objects.filter(board=board).order_by('position')
          # 预加载任务数据
        lists = lists.prefetch_related(
            Prefetch(
                'tasks',
                queryset=Task.objects.select_related(
                    'creator'
                ).prefetch_related(
                    'assignees', 'labels'
                ).order_by('position')
            )
        )
        
        context['board_lists'] = lists
        
        # 看板成员
        members = BoardMember.objects.filter(board=board).select_related('user')
        context['board_members'] = members
        context['is_board_owner'] = board.owner == self.request.user
        context['is_board_admin'] = BoardMember.objects.filter(
            board=board,
            user=self.request.user,
            role__in=['admin', 'owner']
        ).exists()
        
        # 统计信息
        context['total_tasks'] = Task.objects.filter(board_list__board=board).count()
        context['completed_tasks'] = Task.objects.filter(
            board_list__board=board,
            status='completed'
        ).count()
        
        # 表单
        context['list_form'] = BoardListCreateForm()
        context['invite_form'] = BoardMemberInviteForm(board=board)
        
        return context


class BoardUpdateView(LoginRequiredMixin, BoardAccessMixin, UpdateView):
    """编辑看板视图"""
    model = Board
    form_class = BoardUpdateForm
    template_name = 'boards/edit.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        board = self.get_object()
        user = self.request.user
        
        # 只有看板所有者或管理员可以编辑
        if board.owner == user:
            return True
        
        return BoardMember.objects.filter(
            board=board,
            user=user,
            role__in=['admin', 'owner']
        ).exists()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            _('看板 "{}" 更新成功！').format(form.instance.name)
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('boards:detail', kwargs={'slug': self.object.slug})


class BoardDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """删除看板视图"""
    model = Board
    template_name = 'boards/delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('boards:list')
    
    def test_func(self):
        board = self.get_object()
        return board.owner == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.object
        
        # 统计信息
        context['total_tasks'] = Task.objects.filter(board_list__board=board).count()
        context['total_comments'] = 0  # TODO: 实现评论统计
        
        return context


class BoardCopyView(LoginRequiredMixin, BoardAccessMixin, DetailView):
    """复制看板视图"""
    model = Board
    template_name = 'boards/copy.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.object
        
        # 统计信息
        context['total_tasks'] = Task.objects.filter(board_list__board=board).count()
          # 用户团队（用于团队选择）
        from teams.models import TeamMembership
        user_teams = TeamMembership.objects.filter(
            user=self.request.user,
            role__in=['admin', 'owner']
        ).select_related('team')
        context['user_teams'] = [member.team for member in user_teams]
        
        return context
    
    def post(self, request, *args, **kwargs):
        original_board = self.get_object()
        
        # 获取表单数据
        name = request.POST.get('name', f"{original_board.name} - 副本")
        description = request.POST.get('description', original_board.description)
        visibility = request.POST.get('visibility', 'private')
        team_id = request.POST.get('team')
        
        copy_lists = request.POST.get('copy_lists') == 'on'
        copy_tasks = request.POST.get('copy_tasks') == 'on'
        copy_labels = request.POST.get('copy_labels') == 'on'
        copy_members = request.POST.get('copy_members') == 'on'
        
        # 创建看板副本
        new_board = Board.objects.create(
            name=name,
            description=description,
            template=original_board.template,
            visibility=visibility,
            background_color=original_board.background_color,
            owner=request.user,
            enable_calendar=original_board.enable_calendar,
            enable_timeline=original_board.enable_timeline,
            enable_comments=original_board.enable_comments,
            enable_attachments=original_board.enable_attachments,
        )
        
        # 设置团队
        if team_id:
            from teams.models import Team
            try:
                team = Team.objects.get(id=team_id)
                new_board.team = team
                new_board.save()
            except Team.DoesNotExist:
                pass
        
        # 复制标签
        label_mapping = {}
        if copy_labels:
            from .models import BoardLabel
            for label in BoardLabel.objects.filter(board=original_board):
                new_label = BoardLabel.objects.create(
                    board=new_board,
                    name=label.name,
                    color=label.color
                )
                label_mapping[label.id] = new_label
        
        # 复制列表
        if copy_lists:
            for original_list in original_board.lists.all():
                new_list = BoardList.objects.create(
                    board=new_board,
                    name=original_list.name,
                    position=original_list.position
                )
                
                # 复制任务
                if copy_tasks:
                    for task in original_list.tasks.all():
                        new_task = Task.objects.create(
                            title=task.title,
                            description=task.description,
                            board=new_board,
                            board_list=new_list,
                            creator=request.user,
                            priority=task.priority,
                            position=task.position,
                            due_date=task.due_date,
                            estimated_hours=task.estimated_hours
                        )
                        
                        # 复制任务标签
                        if copy_labels:
                            for label in task.labels.all():
                                if label.id in label_mapping:
                                    new_task.labels.add(label_mapping[label.id])
        
        # 复制成员
        if copy_members:
            for member in original_board.members.all():
                BoardMember.objects.create(
                    board=new_board,
                    user=member.user,
                    role='member'  # 默认成员角色
                )
        
        messages.success(
            request, 
            _('看板 "{}" 复制成功！').format(new_board.name)
        )
        
        return redirect('boards:detail', slug=new_board.slug)


# API视图 (用于AJAX请求)
class BoardListCreateAPIView(LoginRequiredMixin, BoardAccessMixin, View):
    """创建看板列表 API"""
    
    def post(self, request, slug):
        board = get_object_or_404(Board, slug=slug)
        
        if not self.has_board_access(board, request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        form = BoardListCreateForm(request.POST)
        if form.is_valid():
            board_list = form.save(commit=False)
            board_list.board = board
              # 如果没有指定位置，放在最后
            if not board_list.position:
                max_position = BoardList.objects.filter(
                    board=board
                ).aggregate(Max('position'))['position__max'] or 0
                board_list.position = max_position + 1
            
            board_list.save()
            
            return JsonResponse({
                'success': True,
                'list': {
                    'id': board_list.id,
                    'name': board_list.name,
                    'position': board_list.position
                }
            })
        
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


class BoardMemberInviteAPIView(LoginRequiredMixin, BoardAccessMixin, View):
    """邀请看板成员 API"""
    
    def post(self, request, slug):
        board = get_object_or_404(Board, slug=slug)
        
        # 只有看板所有者或管理员可以邀请成员
        if not (board.owner == request.user or BoardMember.objects.filter(
            board=board, user=request.user, role__in=['admin', 'owner']
        ).exists()):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        form = BoardMemberInviteForm(request.POST, board=board)
        if form.is_valid():
            member = form.save()
            
            return JsonResponse({
                'success': True,
                'member': {
                    'id': member.id,
                    'user': {
                        'id': member.user.id,
                        'username': member.user.username,
                        'email': member.user.email,
                        'display_name': member.user.get_display_name()
                    },
                    'role': member.role,
                    'joined_at': member.joined_at.isoformat()
                }
            })
        
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
