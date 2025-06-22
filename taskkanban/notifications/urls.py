from django.urls import path, include
from . import views

app_name = 'notifications'

urlpatterns = [
    # 通知偏好设置
    path('preferences/', views.NotificationPreferencesView.as_view(), name='preferences'),
    path('preferences/update/', views.UpdateNotificationPreferencesView.as_view(), name='update_preferences'),
    
    # 退订功能
    path('unsubscribe/<str:token>/', views.UnsubscribeView.as_view(), name='unsubscribe'),
    path('unsubscribe/success/', views.UnsubscribeSuccessView.as_view(), name='unsubscribe_success'),
    
    # 邮件追踪
    path('track/read/<uuid:notification_id>/', views.TrackEmailReadView.as_view(), name='track_read'),
    path('track/click/<uuid:notification_id>/', views.TrackEmailClickView.as_view(), name='track_click'),
    
    # 通知历史
    path('history/', views.NotificationHistoryView.as_view(), name='history'),
    path('history/<uuid:notification_id>/', views.NotificationDetailView.as_view(), name='detail'),
    
    # 管理功能 (管理员使用)
    path('admin/templates/', views.EmailTemplateListView.as_view(), name='admin_templates'),
    path('admin/templates/create/', views.EmailTemplateCreateView.as_view(), name='admin_template_create'),
    path('admin/templates/<int:pk>/edit/', views.EmailTemplateUpdateView.as_view(), name='admin_template_edit'),
    path('admin/templates/<int:pk>/delete/', views.EmailTemplateDeleteView.as_view(), name='admin_template_delete'),
    
    # 测试发送
    path('admin/test-send/', views.TestEmailSendView.as_view(), name='admin_test_send'),
]
