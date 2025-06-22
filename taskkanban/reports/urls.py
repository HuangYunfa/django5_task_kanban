"""
Reports应用URL配置
报表分析相关路由
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # 报表首页
    path('', views.ReportIndexView.as_view(), name='index'),
    # 任务统计报表
    path('tasks/', views.TaskReportView.as_view(), name='tasks'),
    # 团队绩效报表
    path('team-performance/', views.TeamPerformanceView.as_view(), name='team_performance'),
    # 项目进度报表
    path('project-progress/', views.ProjectProgressView.as_view(), name='project_progress'),
    # 自定义报表
    path('custom/', views.CustomReportView.as_view(), name='custom'),
]
