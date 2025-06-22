"""
API视图
提供RESTful API端点
"""

from rest_framework import generics, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view

from .serializers import (
    UserSerializer, UserCreateSerializer,
    TaskSerializer, TaskCreateSerializer,
    BoardSerializer, BoardCreateSerializer, BoardListSerializer,
    TeamSerializer, TeamCreateSerializer, TeamMembershipSerializer,
    ReportSerializer, CustomTokenObtainPairSerializer
)
from tasks.models import Task
from boards.models import Board, BoardMember, BoardList
from teams.models import Team, TeamMembership
from reports.models import Report

# 导入扩展的ViewSet
from .viewsets_extended import TeamViewSet, ReportViewSet

User = get_user_model()


@extend_schema_view(
    list=extend_schema(summary="获取用户列表"),
    retrieve=extend_schema(summary="获取用户详情"),
    create=extend_schema(summary="创建用户"),
    update=extend_schema(summary="更新用户"),
    partial_update=extend_schema(summary="部分更新用户"),
    destroy=extend_schema(summary="删除用户"),
)
class UserViewSet(viewsets.ModelViewSet):
    """用户管理API"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """更新当前用户资料"""
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(summary="获取任务列表"),
    retrieve=extend_schema(summary="获取任务详情"),
    create=extend_schema(summary="创建任务"),
    update=extend_schema(summary="更新任务"),
    partial_update=extend_schema(summary="部分更新任务"),
    destroy=extend_schema(summary="删除任务"),
)
class TaskViewSet(viewsets.ModelViewSet):
    """任务管理API"""
    queryset = Task.objects.select_related('board_list', 'creator').prefetch_related('assignees')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 只返回用户有权限访问的任务
        user = self.request.user
        queryset = queryset.filter(
            Q(board_list__board__members__user=user) |
            Q(creator=user) |
            Q(assignees=user)
        ).distinct()
        
        # 支持筛选参数
        board_id = self.request.query_params.get('board', None)
        if board_id:
            queryset = queryset.filter(board_list__board_id=board_id)
        
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        assignee_id = self.request.query_params.get('assignee', None)
        if assignee_id:
            queryset = queryset.filter(assignees__id=assignee_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """更改任务状态"""
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Task.STATUS_CHOICES):
            return Response(
                {'error': '无效的状态'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = new_status
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_users(self, request, pk=None):
        """分配用户到任务"""
        task = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        users = User.objects.filter(id__in=user_ids)
        task.assignees.set(users)
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary="获取看板列表"),
    retrieve=extend_schema(summary="获取看板详情"),
    create=extend_schema(summary="创建看板"),
    update=extend_schema(summary="更新看板"),
    partial_update=extend_schema(summary="部分更新看板"),
    destroy=extend_schema(summary="删除看板"),
)
class BoardViewSet(viewsets.ModelViewSet):
    """看板管理API"""
    queryset = Board.objects.select_related('owner').prefetch_related('members', 'boardlist_set')
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BoardCreateSerializer
        elif self.action == 'list':
            return BoardListSerializer
        return BoardSerializer
    
    def get_queryset(self):
        """只返回用户有权限访问的看板"""
        user = self.request.user
        return super().get_queryset().filter(
            Q(members__user=user) | Q(owner=user)
        ).distinct()
    
    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        # 自动将创建者添加为管理员
        BoardMember.objects.create(
            board=board,
            user=self.request.user,
            role='admin'
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """获取看板成员"""
        board = self.get_object()
        members = BoardMember.objects.filter(board=board).select_related('user')
        data = []
        for member in members:
            data.append({
                'user_id': member.user.id,
                'username': member.user.username,
                'email': member.user.email,
                'first_name': member.user.first_name,
                'last_name': member.user.last_name,
                'role': member.role,
                'joined_at': member.joined_at
            })
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """添加看板成员"""
        board = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')
        
        try:
            user = User.objects.get(id=user_id)
            member, created = BoardMember.objects.get_or_create(
                board=board,
                user=user,
                defaults={'role': role}
            )
            
            if not created:
                return Response(
                    {'error': '用户已是看板成员'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                'message': '成员添加成功',
                'member': {
                    'user_id': user.id,
                    'username': user.username,
                    'role': member.role
                }
            })
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )


# JWT认证视图
class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义JWT获取视图"""
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(summary="获取JWT令牌")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    """自定义JWT刷新视图"""
    
    @extend_schema(summary="刷新JWT令牌")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
