"""
Reports应用视图
报表分析相关视图
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
import json

from .models import Report
from .forms import ReportFilterForm, ReportCreateForm, ChartConfigForm, ExportForm
from .services import ReportDataService
from .chart_services import ChartDataService
from .export_services import ReportExportService, ChartExportService


class ReportIndexView(LoginRequiredMixin, TemplateView):
    """报表首页/仪表板视图"""
    template_name = 'reports/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取筛选表单
        filter_form = ReportFilterForm(self.request.GET, user=self.request.user)
        context['filter_form'] = filter_form
        
        # 获取日期范围
        if filter_form.is_valid():
            start_date, end_date = filter_form.get_date_range()
            team = filter_form.cleaned_data.get('team')
            board = filter_form.cleaned_data.get('board')
            user = filter_form.cleaned_data.get('user')
        else:
            start_date = datetime.now().date() - timedelta(days=30)
            end_date = datetime.now().date()
            team = None
            board = None
            user = None
        
        # 获取报表数据
        data_service = ReportDataService(
            start_date=start_date,
            end_date=end_date,
            user=user,
            team=team,
            board=board
        )
        
        dashboard_data = data_service.get_dashboard_summary()
        context.update(dashboard_data)
        
        # 为图表准备数据
        context['chart_data'] = {
            'task_completion_trend': json.dumps(
                ChartDataService.format_for_chartjs(
                    dashboard_data['task_stats']['completion_trend'], 'line'
                )
            ),
            'status_distribution': json.dumps(
                ChartDataService.format_for_chartjs(
                    [
                        {'label': '待办', 'value': dashboard_data['task_stats']['todo_tasks']},
                        {'label': '进行中', 'value': dashboard_data['task_stats']['in_progress_tasks']},
                        {'label': '已完成', 'value': dashboard_data['task_stats']['completed_tasks']},
                    ], 'doughnut'
                )
            ),
            'user_workload': json.dumps(
                ChartDataService.format_for_chartjs(
                    [
                        {'label': item['display_name'], 'value': item['total_tasks']}
                        for item in dashboard_data['workload_stats']['user_workloads'][:10]
                    ], 'bar'
                )
            ),
        }
        
        # 获取用户的报表列表
        context['user_reports'] = Report.objects.filter(
            created_by=self.request.user
        ).order_by('-created_at')[:5]
        
        return context


class TaskReportView(LoginRequiredMixin, TemplateView):
    """任务统计报表视图"""
    template_name = 'reports/tasks.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取筛选表单
        filter_form = ReportFilterForm(self.request.GET, user=self.request.user)
        context['filter_form'] = filter_form
        
        # 获取筛选条件
        if filter_form.is_valid():
            start_date, end_date = filter_form.get_date_range()
            team = filter_form.cleaned_data.get('team')
            board = filter_form.cleaned_data.get('board')
            user = filter_form.cleaned_data.get('user')
        else:
            start_date = datetime.now().date() - timedelta(days=30)
            end_date = datetime.now().date()
            team = None
            board = None
            user = None
        
        # 获取任务统计数据
        data_service = ReportDataService(
            start_date=start_date,
            end_date=end_date,
            user=user,
            team=team,
            board=board
        )
        
        task_stats = data_service.get_task_completion_stats()
        context['task_stats'] = task_stats
        
        # 图表配置表单
        context['chart_config_form'] = ChartConfigForm()
        
        # 准备图表数据
        context['chart_data'] = {
            'completion_trend': json.dumps(
                ChartDataService.format_for_chartjs(task_stats['completion_trend'], 'line')
            ),
            'priority_distribution': json.dumps(
                ChartDataService.format_for_chartjs(
                    [{'label': item['priority'], 'value': item['count']} for item in task_stats['priority_stats']], 
                    'pie'
                )
            ),
            'status_distribution': json.dumps(
                ChartDataService.format_for_chartjs(
                    [{'label': item['status'], 'value': item['count']} for item in task_stats['status_stats']], 
                    'doughnut'
                )
            ),
        }
        
        return context


class TeamPerformanceView(LoginRequiredMixin, TemplateView):
    """团队绩效报表视图"""
    template_name = 'reports/team_performance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取筛选表单
        filter_form = ReportFilterForm(self.request.GET, user=self.request.user)
        context['filter_form'] = filter_form
        
        # 获取筛选条件
        if filter_form.is_valid():
            start_date, end_date = filter_form.get_date_range()
            team = filter_form.cleaned_data.get('team')
        else:
            start_date = datetime.now().date() - timedelta(days=30)
            end_date = datetime.now().date()
            team = None
        
        # 获取团队绩效数据
        data_service = ReportDataService(
            start_date=start_date,
            end_date=end_date,
            user=self.request.user,
            team=team
        )
        
        team_stats = data_service.get_team_performance_stats()
        workload_stats = data_service.get_user_workload_stats()
        
        context['team_stats'] = team_stats
        context['workload_stats'] = workload_stats
        
        # 准备图表数据
        context['chart_data'] = {
            'team_comparison': json.dumps(
                ChartDataService.format_for_chartjs(
                    [{'label': item['team_name'], 'value': item['completion_rate']} 
                     for item in team_stats['team_stats']], 'bar'
                )
            ),
            'workload_distribution': json.dumps(
                ChartDataService.format_for_chartjs(
                    [{'label': item['display_name'], 'value': item['total_tasks']} 
                     for item in workload_stats['user_workloads'][:10]], 'bar'
                )
            ),
        }
        
        return context


class ProjectProgressView(LoginRequiredMixin, TemplateView):
    """项目进度报表视图"""
    template_name = 'reports/project_progress.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取筛选表单
        filter_form = ReportFilterForm(self.request.GET, user=self.request.user)
        context['filter_form'] = filter_form
        
        # 获取筛选条件
        if filter_form.is_valid():
            start_date, end_date = filter_form.get_date_range()
            team = filter_form.cleaned_data.get('team')
            board = filter_form.cleaned_data.get('board')
        else:
            start_date = datetime.now().date() - timedelta(days=30)
            end_date = datetime.now().date()
            team = None
            board = None
        
        # 获取项目进度数据
        data_service = ReportDataService(
            start_date=start_date,
            end_date=end_date,
            user=self.request.user,
            team=team,
            board=board
        )
        
        project_stats = data_service.get_project_progress_stats()
        context['project_stats'] = project_stats
        
        # 准备图表数据
        context['chart_data'] = {
            'project_progress': json.dumps(
                ChartDataService.format_for_chartjs(
                    [{'label': item['board_name'], 'value': item['progress_rate']} 
                     for item in project_stats['project_stats']], 'bar'
                )
            ),
        }
        
        return context


class ReportListView(LoginRequiredMixin, ListView):
    """报表列表视图"""
    model = Report
    template_name = 'reports/list.html'
    context_object_name = 'reports'
    paginate_by = 10
    
    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user).order_by('-created_at')


class ReportCreateView(LoginRequiredMixin, CreateView):
    """创建报表视图"""
    model = Report
    form_class = ReportCreateForm
    template_name = 'reports/create.html'
    success_url = reverse_lazy('reports:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, _('报表创建成功！'))
        return super().form_valid(form)


class ReportDetailView(LoginRequiredMixin, DetailView):
    """报表详情视图"""
    model = Report
    template_name = 'reports/detail.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user)


class ReportDataAPIView(LoginRequiredMixin, TemplateView):
    """报表数据API视图"""
    
    def get(self, request, *args, **kwargs):
        report_type = request.GET.get('type', 'dashboard')
        
        # 获取筛选参数
        filter_form = ReportFilterForm(request.GET, user=request.user)
        if filter_form.is_valid():
            start_date, end_date = filter_form.get_date_range()
            team = filter_form.cleaned_data.get('team')
            board = filter_form.cleaned_data.get('board')
            user = filter_form.cleaned_data.get('user')
        else:
            start_date = datetime.now().date() - timedelta(days=30)
            end_date = datetime.now().date()
            team = None
            board = None
            user = None
        
        # 获取数据服务
        data_service = ReportDataService(
            start_date=start_date,
            end_date=end_date,
            user=user,
            team=team,
            board=board
        )
        
        # 根据类型返回数据
        if report_type == 'tasks':
            data = data_service.get_task_completion_stats()
        elif report_type == 'workload':
            data = data_service.get_user_workload_stats()
        elif report_type == 'team':
            data = data_service.get_team_performance_stats()
        elif report_type == 'project':
            data = data_service.get_project_progress_stats()
        else:
            data = data_service.get_dashboard_summary()
        
        return JsonResponse(data)


class ExportReportView(LoginRequiredMixin, TemplateView):
    """导出报表视图"""
    
    def post(self, request, *args, **kwargs):
        export_form = ExportForm(request.POST)
        
        if not export_form.is_valid():
            return JsonResponse({'success': False, 'message': '表单数据无效'})
        
        format_type = export_form.cleaned_data['format']
        
        try:
            # 获取筛选参数
            filter_form = ReportFilterForm(request.POST, user=request.user)
            if filter_form.is_valid():
                start_date, end_date = filter_form.get_date_range()
                team = filter_form.cleaned_data.get('team')
                board = filter_form.cleaned_data.get('board')
                user = filter_form.cleaned_data.get('user')
            else:
                start_date = datetime.now().date() - timedelta(days=30)
                end_date = datetime.now().date()
                team = None
                board = None
                user = None
            
            # 获取报表数据
            data_service = ReportDataService(
                start_date=start_date,
                end_date=end_date,
                user=user,
                team=team,
                board=board
            )
            
            # 获取完整的仪表板数据
            data = data_service.get_dashboard_summary()
            
            # 创建导出服务
            export_service = ReportExportService(data, "任务看板报表")
            
            # 根据格式类型导出
            if format_type == 'csv':
                return export_service.export_to_csv()
            elif format_type == 'excel':
                return export_service.export_to_excel()
            elif format_type == 'pdf':
                return export_service.export_to_pdf()
            elif format_type == 'json':
                return export_service.export_to_json()
            else:
                return JsonResponse({'success': False, 'message': '不支持的导出格式'})
                
        except ImportError as e:
            return JsonResponse({
                'success': False, 
                'message': f'缺少必要的库: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'导出失败: {str(e)}'
            })


class ExportReportView(LoginRequiredMixin, View):
    """报表导出视图"""
    
    def get(self, request, *args, **kwargs):
        """处理GET请求，导出报表"""
        try:
            # 获取导出格式
            export_format = request.GET.get('export_format', 'excel')
            
            # 获取筛选参数
            filter_form = ReportFilterForm(request.GET, user=request.user)
            if filter_form.is_valid():
                start_date, end_date = filter_form.get_date_range()
                team = filter_form.cleaned_data.get('team')
                board = filter_form.cleaned_data.get('board')
                user_filter = filter_form.cleaned_data.get('user')
            else:
                start_date = datetime.now().date() - timedelta(days=30)
                end_date = datetime.now().date()
                team = None
                board = None
                user_filter = None
            
            # 获取报表数据
            data_service = ReportDataService(
                start_date=start_date,
                end_date=end_date,
                user=user_filter,
                team=team,
                board=board
            )
            
            # 获取全部数据
            dashboard_data = data_service.get_dashboard_summary()
            task_stats = data_service.get_task_completion_stats()
            workload_stats = data_service.get_user_workload_stats()
            team_stats = data_service.get_team_performance_stats()
            
            # 合并数据
            report_data = {
                'task_stats': task_stats,
                'workload_stats': workload_stats,
                'team_stats': team_stats,
                'summary': dashboard_data
            }
            
            # 构建报表标题
            title_parts = ["任务看板数据报表"]
            if team:
                title_parts.append(f"团队: {team.name}")
            if board:
                title_parts.append(f"看板: {board.name}")
            if user_filter:
                title_parts.append(f"用户: {user_filter.get_display_name()}")
            title_parts.append(f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
            
            report_title = " - ".join(title_parts)
            
            # 创建导出服务
            export_service = ReportExportService(report_data, report_title)
            
            # 根据格式导出
            if export_format == 'excel':
                return export_service.export_to_excel()
            elif export_format == 'csv':
                return export_service.export_to_csv()
            elif export_format == 'pdf':
                return export_service.export_to_pdf()
            elif export_format == 'json':
                return export_service.export_to_json()
            else:
                messages.error(request, f"不支持的导出格式: {export_format}")
                return HttpResponse(status=400)
                
        except Exception as e:
            messages.error(request, f"导出报表失败: {str(e)}")
            return HttpResponse(status=500)


class ExportChartDataView(LoginRequiredMixin, View):
    """导出图表数据视图"""
    
    def get(self, request, *args, **kwargs):
        """导出图表数据"""
        try:
            # 获取图表类型和数据类型
            chart_type = request.GET.get('chart_type', 'bar')
            data_type = request.GET.get('data_type', 'tasks')
            
            # 获取筛选参数
            filter_form = ReportFilterForm(request.GET, user=request.user)
            if filter_form.is_valid():
                start_date, end_date = filter_form.get_date_range()
                team = filter_form.cleaned_data.get('team')
                board = filter_form.cleaned_data.get('board')
                user_filter = filter_form.cleaned_data.get('user')
            else:
                start_date = datetime.now().date() - timedelta(days=30)
                end_date = datetime.now().date()
                team = None
                board = None
                user_filter = None
            
            # 获取报表数据
            data_service = ReportDataService(
                start_date=start_date,
                end_date=end_date,
                user=user_filter,
                team=team,
                board=board
            )
            
            # 根据数据类型获取对应数据
            if data_type == 'tasks':
                raw_data = data_service.get_task_completion_stats()
                chart_data = raw_data.get('status_stats', [])
            elif data_type == 'completion_trend':
                raw_data = data_service.get_task_completion_stats()
                chart_data = raw_data.get('completion_trend', [])
            elif data_type == 'workload':
                raw_data = data_service.get_user_workload_stats()
                chart_data = [
                    {'label': item['display_name'], 'value': item['total_tasks']}
                    for item in raw_data.get('user_workloads', [])[:10]
                ]
            elif data_type == 'teams':
                raw_data = data_service.get_team_performance_stats()
                chart_data = [
                    {'label': item['team_name'], 'value': item['completion_rate']}
                    for item in raw_data.get('team_stats', [])
                ]
            else:
                return JsonResponse({'success': False, 'message': '不支持的数据类型'})
            
            # 格式化为Chart.js数据
            formatted_data = ChartDataService.format_for_chartjs(chart_data, chart_type)
            
            # 返回JSON响应
            return JsonResponse({
                'success': True,
                'data': formatted_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'获取图表数据失败: {str(e)}'
            })


class CustomReportView(LoginRequiredMixin, TemplateView):
    """自定义报表视图"""
    template_name = 'reports/custom.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ReportFilterForm(user=self.request.user)
        context['chart_config_form'] = ChartConfigForm()
        return context
