"""
Users应用URL配置
用户管理相关路由
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 用户认证
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # 密码管理
    path('password/reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password/change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', views.UserPasswordChangeDoneView.as_view(), name='password_change_done'),
      # 邮箱验证
    path('email/verify/<uidb64>/<token>/', views.email_verify, name='email_verify'),
    path('email/resend/', views.resend_verification_email, name='resend_verification'),
    
    # 用户管理
    path('', views.UserListView.as_view(), name='list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('preferences/', views.UserPreferencesView.as_view(), name='preferences'),
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('avatar/upload/', views.AvatarUploadView.as_view(), name='avatar_upload'),
    path('activity/', views.UserActivityView.as_view(), name='activity'),
    path('notifications/', views.UserNotificationsView.as_view(), name='notifications'),
    path('teams/', views.UserTeamsView.as_view(), name='teams'),
    path('boards/', views.UserBoardsView.as_view(), name='boards'),
    
    # Ajax API
    path('ajax/search/', views.ajax_user_search, name='ajax_search'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('account/deactivate/', views.deactivate_account, name='deactivate_account'),
]
