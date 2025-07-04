"""
Tasks应用URL配置
任务管理相关路由
"""
from django.urls import path, include
from . import views

app_name = 'tasks'

urlpatterns = [
    # 任务列表
    path('', views.TaskListView.as_view(), name='list'),
    # 创建任务
    path('create/', views.TaskCreateView.as_view(), name='create'),
    # 任务详情
    path('<int:pk>/', views.TaskDetailView.as_view(), name='detail'),
    # 编辑任务
    path('<int:pk>/edit/', views.TaskUpdateView.as_view(), name='edit'),
    # 删除任务
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),
    # 任务状态更新
    path('<int:pk>/status/', views.TaskStatusUpdateView.as_view(), name='status_update'),
      # API路由
    path('<int:pk>/comments/', views.TaskCommentCreateView.as_view(), name='comment_create'),
    path('<int:pk>/move/', views.TaskMoveView.as_view(), name='move'),
    path('<int:pk>/labels/', views.TaskLabelUpdateView.as_view(), name='label_update'),    # 批量操作和排序API
    path('batch-operation/', views.TaskBatchOperationView.as_view(), name='batch_operation'),
    path('sort/', views.TaskSortView.as_view(), name='sort'),
    
    # 任务状态历史
    path('<slug:board_slug>/<int:task_pk>/status-history/', views.TaskStatusHistoryView.as_view(), name='status_history'),
    
    # 工作流相关URL
    path('workflow/', include('tasks.workflow_urls')),
]
