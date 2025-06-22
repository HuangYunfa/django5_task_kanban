"""
Reports应用URL配置
报表分析相关路由
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # 报表首页/仪表板
    path('', views.ReportIndexView.as_view(), name='index'),
    
    # 预定义报表
    path('tasks/', views.TaskReportView.as_view(), name='tasks'),
    path('team-performance/', views.TeamPerformanceView.as_view(), name='team_performance'),
    path('project-progress/', views.ProjectProgressView.as_view(), name='project_progress'),
    path('custom/', views.CustomReportView.as_view(), name='custom'),
    
    # 报表管理
    path('list/', views.ReportListView.as_view(), name='list'),
    path('create/', views.ReportCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ReportDetailView.as_view(), name='detail'),
      # API接口
    path('api/data/', views.ReportDataAPIView.as_view(), name='api_data'),
    
    # 导出功能
    path('export/', views.ExportReportView.as_view(), name='export'),
    path('export/chart-data/', views.ExportChartDataView.as_view(), name='export_chart_data'),
]
