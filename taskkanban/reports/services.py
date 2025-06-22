"""
Reports应用数据服务
报表数据分析和统计服务
"""
from django.db.models import Count, Q, Avg, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict
from django.contrib.auth import get_user_model

User = get_user_model()


class ReportDataService:
    """报表数据服务类"""
    
    def __init__(self, start_date=None, end_date=None, user=None, team=None, board=None):
        self.start_date = start_date or (timezone.now().date() - timedelta(days=30))
        self.end_date = end_date or timezone.now().date()
        self.user = user
        self.team = team
        self.board = board
    
    def get_task_completion_stats(self):
        """获取任务完成统计"""
        from tasks.models import Task
        
        # 构建查询条件
        filters = {
            'created_at__date__gte': self.start_date,
            'created_at__date__lte': self.end_date,        }
        
        if self.user:
            filters['assignees'] = self.user
        if self.team:
            filters['board__team'] = self.team
        if self.board:
            filters['board'] = self.board
        
        # 基础统计
        total_tasks = Task.objects.filter(**filters).count()
        completed_tasks = Task.objects.filter(**filters, status='done').count()
        in_progress_tasks = Task.objects.filter(**filters, status='in_progress').count()
        todo_tasks = Task.objects.filter(**filters, status='todo').count()
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 按日期分组的完成趋势
        completion_trend = []
        current_date = self.start_date
        while current_date <= self.end_date:
            day_completed = Task.objects.filter(
                **filters,
                status='done',
                updated_at__date=current_date
            ).count()
            
            completion_trend.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'completed': day_completed
            })
            current_date += timedelta(days=1)
        
        # 按优先级分组
        priority_stats = Task.objects.filter(**filters).values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        
        # 按状态分组
        status_stats = Task.objects.filter(**filters).values('status').annotate(
            count=Count('id')
        )
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'todo_tasks': todo_tasks,
            'completion_rate': round(completion_rate, 2),
            'completion_trend': completion_trend,
            'priority_stats': list(priority_stats),
            'status_stats': list(status_stats),
        }
    
    def get_user_workload_stats(self):
        """获取用户工作负载统计"""
        from tasks.models import Task
        
        # 构建基础查询
        filters = {
            'created_at__date__gte': self.start_date,
            'created_at__date__lte': self.end_date,
        }
        
        if self.team:
            filters['board__team'] = self.team
        if self.board:
            filters['board'] = self.board
          # 获取用户工作负载
        user_workloads = Task.objects.filter(**filters).values(
            'assignees__username',
            'assignees__nickname'
        ).annotate(
            total_tasks=Count('id'),
            completed_tasks=Count('id', filter=Q(status='done')),
            in_progress_tasks=Count('id', filter=Q(status='in_progress')),
            todo_tasks=Count('id', filter=Q(status='todo')),
            high_priority_tasks=Count('id', filter=Q(priority='high')),
        ).order_by('-total_tasks')
        
        # 计算完成率
        for workload in user_workloads:
            total = workload['total_tasks']
            completed = workload['completed_tasks']
            workload['completion_rate'] = (completed / total * 100) if total > 0 else 0
            workload['display_name'] = workload['assignees__nickname'] or workload['assignees__username']
        
        # 团队平均工作负载
        total_users = len(user_workloads)
        if total_users > 0:
            total_team_tasks = sum(w['total_tasks'] for w in user_workloads)
            avg_tasks_per_user = total_team_tasks / total_users
        else:
            avg_tasks_per_user = 0
        
        return {
            'user_workloads': list(user_workloads),
            'total_users': total_users,
            'avg_tasks_per_user': round(avg_tasks_per_user, 2),
        }
    
    def get_team_performance_stats(self):
        """获取团队绩效统计"""
        from tasks.models import Task
        from teams.models import Team
        
        # 如果指定了团队，只分析该团队
        if self.team:
            teams = [self.team]
        else:
            # 获取用户相关的所有团队
            if self.user:
                teams = Team.objects.filter(
                    memberships__user=self.user,
                    memberships__status='active'
                ).distinct()
            else:
                teams = Team.objects.all()[:10]  # 限制数量避免性能问题
        
        team_stats = []
        for team in teams:
            # 团队任务统计
            team_filters = {
                'board__team': team,
                'created_at__date__gte': self.start_date,
                'created_at__date__lte': self.end_date,
            }
            
            total_tasks = Task.objects.filter(**team_filters).count()
            completed_tasks = Task.objects.filter(**team_filters, status='done').count()
            
            # 团队成员数量
            member_count = team.memberships.filter(status='active').count()
            
            # 团队效率指标
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            tasks_per_member = total_tasks / member_count if member_count > 0 else 0
            
            team_stats.append({
                'team_name': team.name,
                'member_count': member_count,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': round(completion_rate, 2),
                'tasks_per_member': round(tasks_per_member, 2),
            })
        
        # 按完成率排序
        team_stats.sort(key=lambda x: x['completion_rate'], reverse=True)        
        return {
            'team_stats': team_stats,
            'total_teams': len(team_stats),
        }
    
    def get_project_progress_stats(self):
        """获取项目进度统计"""
        from boards.models import Board
        from tasks.models import Task
        
        # 构建看板查询条件
        board_filters = {}
        if self.team:
            board_filters['team'] = self.team
        if self.user:
            board_filters['members__user'] = self.user
            board_filters['members__is_active'] = True
        
        boards = Board.objects.filter(**board_filters).distinct()
        
        project_stats = []
        for board in boards:
            # 看板任务统计
            task_filters = {
                'board': board,
                'created_at__date__gte': self.start_date,
                'created_at__date__lte': self.end_date,
            }
            
            total_tasks = Task.objects.filter(**task_filters).count()
            completed_tasks = Task.objects.filter(**task_filters, status='done').count()
            in_progress_tasks = Task.objects.filter(**task_filters, status='in_progress').count()
            
            # 进度计算
            progress_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # 预估完成时间（简单算法）
            if in_progress_tasks > 0 and completed_tasks > 0:
                days_elapsed = (self.end_date - self.start_date).days
                completion_velocity = completed_tasks / days_elapsed if days_elapsed > 0 else 0
                estimated_days = (total_tasks - completed_tasks) / completion_velocity if completion_velocity > 0 else 0
                estimated_completion = self.end_date + timedelta(days=estimated_days)
            else:
                estimated_completion = None
            
            project_stats.append({
                'board_name': board.name,
                'board_description': board.description,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'progress_rate': round(progress_rate, 2),
                'estimated_completion': estimated_completion.strftime('%Y-%m-%d') if estimated_completion else None,
            })
        
        return {
            'project_stats': project_stats,
            'total_projects': len(project_stats),
        }
    
    def get_dashboard_summary(self):
        """获取仪表板摘要数据"""
        task_stats = self.get_task_completion_stats()
        workload_stats = self.get_user_workload_stats()
        team_stats = self.get_team_performance_stats()
        project_stats = self.get_project_progress_stats()
        
        return {
            'summary': {
                'total_tasks': task_stats['total_tasks'],
                'completion_rate': task_stats['completion_rate'],
                'active_users': workload_stats['total_users'],
                'active_teams': team_stats['total_teams'],
                'active_projects': project_stats['total_projects'],
            },
            'task_stats': task_stats,
            'workload_stats': workload_stats,
            'team_stats': team_stats,
            'project_stats': project_stats,
        }


class ChartDataService:
    """图表数据服务类"""
    
    @staticmethod
    def format_for_chartjs(data, chart_type='bar'):
        """将数据格式化为Chart.js格式"""
        if chart_type in ['pie', 'doughnut']:
            return {
                'labels': [item.get('label', item.get('name', '')) for item in data],
                'datasets': [{
                    'data': [item.get('value', item.get('count', 0)) for item in data],
                    'backgroundColor': [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ][:len(data)]
                }]
            }
        else:
            return {
                'labels': [item.get('label', item.get('date', '')) for item in data],
                'datasets': [{
                    'label': '数据',
                    'data': [item.get('value', item.get('count', 0)) for item in data],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                }]            }
    
    @staticmethod
    def get_color_palette(count):
        """获取颜色调色板"""
        colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
            '#4BC0C0', '#FF9F40', '#36A2EB', '#FFCE56'
        ]
        if count <= len(colors):
            return colors[:count]
        else:
            # 扩展颜色列表以满足需要的数量
            extended_colors = colors * (count // len(colors) + 1)
            return extended_colors[:count]
