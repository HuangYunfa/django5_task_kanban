from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Team, TeamMembership, TeamInvitation


class TeamMembershipInline(admin.TabularInline):
    """
    团队成员内联编辑
    """
    model = TeamMembership
    extra = 0
    fields = ('user', 'role', 'status', 'joined_at')
    readonly_fields = ('joined_at', 'created_at')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    团队管理界面
    """
    list_display = ('name', 'created_by', 'is_public', 'allow_join_request', 'member_count', 'created_at')
    list_filter = ('is_public', 'allow_join_request', 'created_at')
    search_fields = ('name', 'description', 'created_by__email', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at', 'member_count')
    inlines = [TeamMembershipInline]
    fieldsets = (
        (_('基本信息'), {'fields': ('name', 'description', 'avatar')}),
        (_('设置'), {'fields': ('is_public', 'allow_join_request')}),
        (_('创建信息'), {'fields': ('created_by', 'created_at', 'updated_at')}),
        (_('统计信息'), {'fields': ('member_count',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    """
    团队成员管理界面
    """
    list_display = ('team', 'user', 'role', 'status', 'invited_by', 'joined_at', 'created_at')
    list_filter = ('role', 'status', 'created_at', 'joined_at')
    search_fields = ('team__name', 'user__email', 'user__username', 'invited_by__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('基本信息'), {'fields': ('team', 'user', 'role', 'status')}),
        (_('邀请信息'), {'fields': ('invited_by', 'invitation_message')}),
        (_('时间信息'), {'fields': ('joined_at', 'created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('team', 'user', 'invited_by')


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    """
    团队邀请管理界面
    """
    list_display = ('team', 'inviter', 'invitee', 'role', 'status', 'expires_at', 'created_at')
    list_filter = ('role', 'status', 'created_at', 'expires_at')
    search_fields = ('team__name', 'inviter__email', 'invitee__email')
    readonly_fields = ('created_at', 'updated_at', 'is_expired', 'is_pending')
    fieldsets = (
        (_('邀请信息'), {'fields': ('team', 'inviter', 'invitee', 'role')}),
        (_('状态'), {'fields': ('status', 'message')}),
        (_('时间信息'), {'fields': ('expires_at', 'responded_at', 'created_at', 'updated_at')}),
        (_('状态检查'), {'fields': ('is_expired', 'is_pending')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('team', 'inviter', 'invitee')
