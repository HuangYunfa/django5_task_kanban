"""
任务状态流转系统URL配置
"""
from django.urls import path
from . import workflow_views

app_name = 'workflow'

urlpatterns = [
    # 工作流状态管理
    path('boards/<slug:board_slug>/workflow/statuses/', 
         workflow_views.WorkflowStatusListView.as_view(), 
         name='status_list'),
    path('boards/<slug:board_slug>/workflow/statuses/create/', 
         workflow_views.WorkflowStatusCreateView.as_view(), 
         name='status_create'),
    
    # 状态转换管理
    path('boards/<slug:board_slug>/workflow/transitions/', 
         workflow_views.WorkflowTransitionListView.as_view(), 
         name='transition_list'),
    
    # 自动化规则管理
    path('boards/<slug:board_slug>/workflow/rules/', 
         workflow_views.WorkflowRuleListView.as_view(), 
         name='rule_list'),
    
    # 工作流统计
    path('boards/<slug:board_slug>/workflow/stats/', 
         workflow_views.WorkflowStatsView.as_view(), 
         name='stats'),
    
    # API接口
    path('tasks/<int:pk>/status/change/', 
         workflow_views.TaskStatusChangeView.as_view(), 
         name='task_status_change'),
    path('tasks/<int:pk>/status/history/', 
         workflow_views.TaskStatusHistoryView.as_view(), 
         name='task_status_history'),
]
