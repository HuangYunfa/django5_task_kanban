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
    # 邀请成员
    path('<int:pk>/invite/', views.TeamInviteView.as_view(), name='invite'),
    # 处理邀请（加入/拒绝）
    path('invitation/<int:pk>/join/', views.TeamJoinView.as_view(), name='join'),
    # 离开团队
    path('<int:pk>/leave/', views.TeamLeaveView.as_view(), name='leave'),
    # 我的邀请
    path('my-invitations/', views.MyInvitationsView.as_view(), name='my_invitations'),
]
