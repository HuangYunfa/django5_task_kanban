from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import EmailConfiguration

@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'port', 'username', 'is_active', 'is_default', 'updated_at', 'test_status']
    list_filter = ['is_active', 'is_default', 'backend', 'use_tls', 'use_ssl']
    search_fields = ['name', 'host', 'username', 'description']
    readonly_fields = ['created_at', 'updated_at', 'test_status']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'is_active', 'is_default')
        }),
        ('SMTP配置', {
            'fields': ('backend', 'host', 'port', 'use_tls', 'use_ssl', 'timeout')
        }),
        ('认证信息', {
            'fields': ('username', 'password', 'default_from_email'),
            'description': '敏感信息，请妥善保管'
        }),
        ('SSL证书', {
            'fields': ('ssl_certfile', 'ssl_keyfile'),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['test_email_config', 'set_as_default']
    
    def test_status(self, obj):
        """显示连接测试状态"""
        try:
            success, message = obj.test_connection()
            if success:
                return format_html(
                    '<span style="color: green;">✅ {}</span>', 
                    message
                )
            else:
                return format_html(
                    '<span style="color: red;">❌ {}</span>', 
                    message
                )
        except Exception as e:
            return format_html(
                '<span style="color: orange;">⚠️ 测试失败: {}</span>', 
                str(e)
            )
    test_status.short_description = '连接状态'
    
    def test_email_config(self, request, queryset):
        """测试邮件配置连接"""
        for config in queryset:
            try:
                success, message = config.test_connection()
                if success:
                    messages.success(request, f"{config.name}: {message}")
                else:
                    messages.error(request, f"{config.name}: {message}")
            except Exception as e:
                messages.error(request, f"{config.name}: 测试失败 - {str(e)}")
    test_email_config.short_description = "测试邮件配置连接"
    
    def set_as_default(self, request, queryset):
        """设置为默认配置"""
        if queryset.count() != 1:
            messages.error(request, "请选择一个配置作为默认配置")
            return
        
        config = queryset.first()
        EmailConfiguration.objects.update(is_default=False)
        config.is_default = True
        config.save()
        messages.success(request, f"已将 {config.name} 设置为默认邮件配置")
    set_as_default.short_description = "设置为默认配置"
    
    def save_model(self, request, obj, form, change):
        """保存模型时的处理"""
        super().save_model(request, obj, form, change)
        
        if change:
            messages.info(request, "邮件配置已更新，新配置将在下次邮件发送时生效")
        else:
            messages.success(request, f"邮件配置 {obj.name} 已创建")
