"""
Users应用URL配置
用户管理相关路由
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 用户列表
    path('', views.UserListView.as_view(), name='list'),
    # 用户详情
    path('<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    # 用户资料
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    # 用户设置
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
]
