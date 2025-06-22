"""
Teams应用URL配置
团队管理相关路由
"""
from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    # 团队列表
    path('', views.TeamListView.as_view(), name='list'),
    # 创建团队
    path('create/', views.TeamCreateView.as_view(), name='create'),
    # 团队详情
    path('<int:pk>/', views.TeamDetailView.as_view(), name='detail'),
    # 编辑团队
    path('<int:pk>/edit/', views.TeamUpdateView.as_view(), name='edit'),
    # 团队成员管理
    path('<int:pk>/members/', views.TeamMemberView.as_view(), name='members'),
]
