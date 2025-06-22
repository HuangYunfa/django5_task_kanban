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
    # 看板详情
    path('<int:pk>/', views.BoardDetailView.as_view(), name='detail'),
    # 编辑看板
    path('<int:pk>/edit/', views.BoardUpdateView.as_view(), name='edit'),
    # 删除看板
    path('<int:pk>/delete/', views.BoardDeleteView.as_view(), name='delete'),
]
