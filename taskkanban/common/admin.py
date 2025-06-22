from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Notification, ActivityLog, SystemSettings, FileUpload


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    通知管理界面
    """
    list_display = ('recipient', 'sender', 'title', 'notification_type', 'priority', 'is_read', 'is_sent', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'is_sent', 'created_at')
    search_fields = ('recipient__email', 'sender__email', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')
    fieldsets = (
        (_('接收信息'), {'fields': ('recipient', 'sender')}),
        (_('通知内容'), {'fields': ('notification_type', 'title', 'message', 'priority')}),
        (_('关联对象'), {'fields': ('content_type', 'object_id', 'url')}),
        (_('状态'), {'fields': ('is_read', 'is_sent')}),
        (_('时间'), {'fields': ('read_at', 'created_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'sender')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """
    活动日志管理界面
    """
    list_display = ('user', 'action', 'description', 'content_type', 'object_repr', 'ip_address', 'created_at')
    list_filter = ('action', 'content_type', 'created_at')
    search_fields = ('user__email', 'description', 'object_repr', 'ip_address')
    readonly_fields = ('created_at',)
    fieldsets = (
        (_('操作信息'), {'fields': ('user', 'action', 'description')}),
        (_('关联对象'), {'fields': ('content_type', 'object_id', 'object_repr')}),
        (_('环境信息'), {'fields': ('ip_address', 'user_agent')}),
        (_('额外数据'), {'fields': ('extra_data',)}),
        (_('时间'), {'fields': ('created_at',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """
    系统设置管理界面
    """
    list_display = ('name', 'key', 'value_type', 'category', 'is_editable', 'is_public', 'updated_by', 'updated_at')
    list_filter = ('value_type', 'category', 'is_editable', 'is_public', 'updated_at')
    search_fields = ('name', 'key', 'description', 'value')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('基本信息'), {'fields': ('key', 'name', 'description')}),
        (_('值设置'), {'fields': ('value', 'value_type')}),
        (_('分类'), {'fields': ('category',)}),
        (_('约束'), {'fields': ('is_editable', 'is_public')}),
        (_('更新信息'), {'fields': ('updated_by', 'created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('updated_by')


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    """
    文件上传管理界面
    """
    list_display = ('uploaded_by', 'original_name', 'file_size_display', 'content_type', 'is_temporary', 'is_public', 'created_at')
    list_filter = ('content_type', 'is_temporary', 'is_public', 'created_at')
    search_fields = ('uploaded_by__email', 'original_name', 'content_type')
    readonly_fields = ('created_at', 'file_size_display', 'file_hash')
    fieldsets = (
        (_('上传信息'), {'fields': ('uploaded_by', 'file')}),
        (_('文件信息'), {'fields': ('original_name', 'file_size', 'content_type', 'file_hash')}),
        (_('关联对象'), {'fields': ('content_type_related', 'object_id')}),
        (_('状态'), {'fields': ('is_temporary', 'is_public')}),
        (_('元数据'), {'fields': ('metadata',)}),
        (_('统计'), {'fields': ('file_size_display',)}),
        (_('时间'), {'fields': ('created_at',)}),
    )
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = _('文件大小')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('uploaded_by')
