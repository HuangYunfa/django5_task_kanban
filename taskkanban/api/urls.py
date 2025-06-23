"""
API URL配置
"""

from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularRedocView, 
    SpectacularSwaggerView
)

from .views import (
    UserViewSet, TaskViewSet, BoardViewSet,
    CustomTokenObtainPairView, CustomTokenRefreshView
)
from .viewsets_extended import TeamViewSet, ReportViewSet

app_name = 'api'

# DRF路由器
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'boards', BoardViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'reports', ReportViewSet)

urlpatterns = [
    # API根路径重定向到文档
    path('', RedirectView.as_view(url='docs/', permanent=False), name='api-root'),
    
    # API文档
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', RedirectView.as_view(url='../docs/', permanent=False), name='schema-swagger-ui-redirect'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
    
    # JWT认证
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # API端点
    path('v1/', include(router.urls)),
    
    # DRF浏览界面认证
    path('auth/', include('rest_framework.urls')),
]
