from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import User, UserProfile


class AdminUserForm(forms.ModelForm):
    """
    Admin用户表单
    """
    class Meta:
        model = User
        fields = '__all__'
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # 检查文件大小（限制为5MB）
            if hasattr(avatar, 'size') and avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('头像文件大小不能超过5MB'))
            
            # 检查文件类型
            if hasattr(avatar, 'content_type'):
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if avatar.content_type not in allowed_types:
                    raise forms.ValidationError(_('请上传JPEG、PNG、GIF或WebP格式的图片'))
        
        return avatar


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    自定义用户管理界面
    """
    form = AdminUserForm
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('个人信息'), {'fields': ('first_name', 'last_name', 'nickname', 'phone', 'avatar', 'bio', 'location', 'website')}),
        (_('偏好设置'), {'fields': ('language', 'timezone')}),
        (_('验证状态'), {'fields': ('email_verified', 'phone_verified')}),
        (_('权限'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('重要日期'), {'fields': ('last_login', 'date_joined', 'last_login_ip')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'username', 'nickname', 'get_display_name', 'is_staff', 'is_active', 'email_verified', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'email_verified', 'phone_verified', 'language', 'created_at')
    search_fields = ('email', 'username', 'nickname', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at', 'last_login_ip')
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = _('显示名称')


class UserProfileInline(admin.StackedInline):
    """
    用户资料内联编辑
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('用户资料')
    fields = (
        ('job_title', 'company', 'department'),
        'skills',
        ('email_notifications', 'browser_notifications', 'mobile_notifications'),
        ('show_email', 'show_phone'),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    用户资料管理界面
    """
    list_display = ('user', 'job_title', 'company', 'department', 'email_notifications', 'created_at')
    list_filter = ('company', 'department', 'email_notifications', 'browser_notifications', 'mobile_notifications', 'created_at')
    search_fields = ('user__email', 'user__username', 'user__nickname', 'job_title', 'company', 'department')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('职业信息'), {'fields': ('user', 'job_title', 'company', 'department')}),
        (_('技能标签'), {'fields': ('skills',)}),
        (_('通知设置'), {'fields': ('email_notifications', 'browser_notifications', 'mobile_notifications')}),
        (_('隐私设置'), {'fields': ('show_email', 'show_phone')}),
        (_('时间信息'), {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
