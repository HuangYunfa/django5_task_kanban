"""
Boards应用URL配置
看板管理相关路由
"""
from django.urls import path
from . import views

app_name = 'boards'

urlpatterns = [
    # 看板列表
    path('', views.BoardListView.as_view(), name='list'),
    
    # 创建看板
    path('create/', views.BoardCreateView.as_view(), name='create'),
    
    # 看板详情 (使用slug)
    path('<slug:slug>/', views.BoardDetailView.as_view(), name='detail'),
    
    # 编辑看板
    path('<slug:slug>/edit/', views.BoardUpdateView.as_view(), name='edit'),
    
    # 删除看板
    path('<slug:slug>/delete/', views.BoardDeleteView.as_view(), name='delete'),
    
    # 复制看板
    path('<slug:slug>/copy/', views.BoardCopyView.as_view(), name='copy'),
    
    # API路由
    path('api/lists/', views.BoardListsAPIView.as_view(), name='board_lists'),
    path('<slug:slug>/lists/create/', views.BoardListCreateAPIView.as_view(), name='list_create_api'),
    path('<slug:slug>/members/invite/', views.BoardMemberInviteAPIView.as_view(), name='member_invite_api'),
    
    # 标签管理API路由
    path('<slug:slug>/labels/', views.BoardLabelListCreateView.as_view(), name='label_list_create_api'),
    path('<slug:slug>/labels/<int:label_pk>/', views.BoardLabelUpdateView.as_view(), name='label_update_api'),
]
