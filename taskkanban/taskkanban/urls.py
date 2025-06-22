"""
URL configuration for taskkanban project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django管理后台
    path('admin/', admin.site.urls),
    
    # 用户认证 (django-allauth)
    path('accounts/', include('allauth.urls')),    # 应用路由
    path('', include('common.urls')),
    path('users/', include('users.urls')),
    path('boards/', include('boards.urls')),
    path('tasks/', include('tasks.urls')),
    path('teams/', include('teams.urls')),
    path('reports/', include('reports.urls')),
    path('notifications/', include('notifications.urls')),
    
    # API路由
    path('api/', include('api.urls')),
]

# 开发环境下的媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
