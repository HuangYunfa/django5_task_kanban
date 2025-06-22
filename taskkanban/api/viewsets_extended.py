"""
扩展的API ViewSet
包含Team和Report的完整实现
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view

from .serializers import (
    TeamSerializer, TeamCreateSerializer, TeamMembershipSerializer,
    ReportSerializer
)
from tasks.models import Task
from boards.models import Board
from teams.models import Team, TeamMembership
from reports.models import Report

User = get_user_model()


@extend_schema_view(
    list=extend_schema(summary="获取团队列表"),
    retrieve=extend_schema(summary="获取团队详情"),
    create=extend_schema(summary="创建团队"),
    update=extend_schema(summary="更新团队"),
    partial_update=extend_schema(summary="部分更新团队"),
    destroy=extend_schema(summary="删除团队"),
)
class TeamViewSet(viewsets.ModelViewSet):
    """团队管理API"""
    queryset = Team.objects.select_related('created_by').prefetch_related('members')
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeamCreateSerializer
        return TeamSerializer
    
    def get_queryset(self):
        """只返回用户所属的团队"""
        user = self.request.user
        return super().get_queryset().filter(
            Q(members__user=user) | Q(created_by=user)
        ).distinct()
    
    def perform_create(self, serializer):
        team = serializer.save(created_by=self.request.user)
        # 自动将创建者添加为管理员
        TeamMembership.objects.create(
            team=team,
            user=self.request.user,
            role='admin'
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """获取团队成员"""
        team = self.get_object()
        memberships = TeamMembership.objects.filter(team=team).select_related('user')
        serializer = TeamMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """添加团队成员"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')
        
        try:
            user = User.objects.get(id=user_id)
            membership, created = TeamMembership.objects.get_or_create(
                team=team,
                user=user,
                defaults={'role': role}
            )
            
            if not created:
                return Response(
                    {'error': '用户已是团队成员'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = TeamMembershipSerializer(membership)
            return Response({
                'message': '成员添加成功',
                'membership': serializer.data
            })
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """移除团队成员"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            membership = TeamMembership.objects.get(team=team, user_id=user_id)
            membership.delete()
            return Response({'message': '成员移除成功'})
        except TeamMembership.DoesNotExist:
            return Response(
                {'error': '成员不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """获取团队绩效数据"""
        team = self.get_object()
        
        # 获取团队成员
        members = User.objects.filter(teammembership__team=team)
          # 统计数据
        performance_data = []
        for member in members:
            tasks_created = Task.objects.filter(creator=member).count()
            tasks_assigned = Task.objects.filter(assignees=member).count()
            tasks_completed = Task.objects.filter(
                assignees=member, 
                status='completed'
            ).count()
            
            performance_data.append({
                'user_id': member.id,
                'username': member.username,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'tasks_created': tasks_created,
                'tasks_assigned': tasks_assigned,
                'tasks_completed': tasks_completed,
                'completion_rate': (tasks_completed / tasks_assigned * 100) if tasks_assigned > 0 else 0
            })
        
        return Response({
            'team_name': team.name,
            'member_count': len(performance_data),
            'performance': performance_data
        })


@extend_schema_view(
    list=extend_schema(summary="获取报表列表"),
    retrieve=extend_schema(summary="获取报表详情"),
    create=extend_schema(summary="创建报表"),
    update=extend_schema(summary="更新报表"),
    partial_update=extend_schema(summary="部分更新报表"),
    destroy=extend_schema(summary="删除报表"),
)
class ReportViewSet(viewsets.ModelViewSet):
    """报表管理API"""
    queryset = Report.objects.select_related('created_by')
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """只返回用户有权限访问的报表"""
        user = self.request.user
        queryset = super().get_queryset().filter(created_by=user)
        
        # 支持按类型筛选
        report_type = self.request.query_params.get('type', None)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """获取报表数据"""
        report = self.get_object()
        
        # 根据报表类型生成数据
        if report.report_type == 'task_summary':
            data = self._get_task_summary_data(report)
        elif report.report_type == 'team_performance':
            data = self._get_team_performance_data(report)
        elif report.report_type == 'project_progress':
            data = self._get_project_progress_data(report)
        else:
            data = {'error': '不支持的报表类型'}
        
        return Response(data)
    
    def _get_task_summary_data(self, report):
        """获取任务汇总数据"""
        # 获取过滤条件
        filters = report.filters or {}
        date_range = filters.get('date_range', 30)  # 默认30天
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=date_range)
        
        # 基础查询
        tasks = Task.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # 应用过滤器
        if 'board_id' in filters:
            tasks = tasks.filter(board_list__board_id=filters['board_id'])
        if 'assignee_id' in filters:
            tasks = tasks.filter(assignees__id=filters['assignee_id'])
        
        # 统计数据
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        in_progress_tasks = tasks.filter(status='in_progress').count()
        todo_tasks = tasks.filter(status='todo').count()
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'todo_tasks': todo_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
    
    def _get_team_performance_data(self, report):
        """获取团队绩效数据"""
        filters = report.filters or {}
        
        if 'team_id' not in filters:
            return {'error': '团队绩效报表需要指定团队ID'}
        
        try:
            team = Team.objects.get(id=filters['team_id'])
            members = User.objects.filter(teammembership__team=team)
            
            performance_data = []
            for member in members:
                tasks_created = Task.objects.filter(creator=member).count()
                tasks_assigned = Task.objects.filter(assignees=member).count()
                tasks_completed = Task.objects.filter(
                    assignees=member, 
                    status='completed'
                ).count()
                
                performance_data.append({
                    'user_id': member.id,
                    'username': member.username,
                    'display_name': f"{member.first_name} {member.last_name}".strip() or member.username,
                    'tasks_created': tasks_created,
                    'tasks_assigned': tasks_assigned,
                    'tasks_completed': tasks_completed,
                    'completion_rate': (tasks_completed / tasks_assigned * 100) if tasks_assigned > 0 else 0
                })
            
            return {
                'team_name': team.name,
                'member_count': len(performance_data),
                'performance': performance_data
            }
        except Team.DoesNotExist:
            return {'error': '团队不存在'}
    
    def _get_project_progress_data(self, report):
        """获取项目进度数据"""
        filters = report.filters or {}
        
        if 'board_id' not in filters:
            return {'error': '项目进度报表需要指定看板ID'}
        
        try:
            board = Board.objects.get(id=filters['board_id'])
            
            # 获取看板下的所有任务
            tasks = Task.objects.filter(board_list__board=board)
            total_tasks = tasks.count()
            
            if total_tasks == 0:
                return {
                    'board_name': board.title,
                    'total_tasks': 0,
                    'progress_data': []
                }
            
            # 按状态统计
            status_stats = {}
            for status_key, status_name in Task.STATUS_CHOICES:
                count = tasks.filter(status=status_key).count()
                status_stats[status_key] = {
                    'name': status_name,
                    'count': count,
                    'percentage': (count / total_tasks * 100) if total_tasks > 0 else 0
                }
            
            # 按列表统计
            list_stats = []
            for board_list in board.boardlist_set.all():
                list_tasks = tasks.filter(board_list=board_list)
                list_count = list_tasks.count()
                completed_count = list_tasks.filter(status='completed').count()
                
                list_stats.append({
                    'list_name': board_list.name,
                    'total_tasks': list_count,
                    'completed_tasks': completed_count,
                    'completion_rate': (completed_count / list_count * 100) if list_count > 0 else 0
                })
            
            return {
                'board_name': board.title,
                'total_tasks': total_tasks,
                'status_distribution': status_stats,
                'list_progress': list_stats,
                'overall_completion': (
                    tasks.filter(status='completed').count() / total_tasks * 100
                ) if total_tasks > 0 else 0
            }
        except Board.DoesNotExist:
            return {'error': '看板不存在'}
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """导出报表"""
        report = self.get_object()
        export_format = request.data.get('format', 'json')
        
        # 获取报表数据
        data_response = self.data(request, pk)
        data = data_response.data
        
        if export_format == 'json':
            return Response({
                'report_name': report.name,
                'generated_at': timezone.now(),
                'data': data
            })
        else:
            return Response(
                {'error': '暂不支持该导出格式'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
