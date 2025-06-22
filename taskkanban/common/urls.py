"""
Common应用URL配置
通用功能路由
"""
from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    # 首页
    path('', views.IndexView.as_view(), name='index'),
    # 仪表板
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
