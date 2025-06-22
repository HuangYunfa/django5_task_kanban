from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Board, BoardList, BoardMember, BoardLabel, BoardActivity


class BoardListInline(admin.TabularInline):
    """
    看板列表内联编辑
    """
    model = BoardList
    extra = 0
    fields = ('name', 'position', 'color', 'is_archived', 'wip_limit')
    ordering = ('position',)


class BoardMemberInline(admin.TabularInline):
    """
    看板成员内联编辑
    """
    model = BoardMember
    extra = 0
    fields = ('user', 'role', 'is_active', 'invited_by')
    readonly_fields = ('joined_at',)


class BoardLabelInline(admin.TabularInline):
    """
    看板标签内联编辑
    """
    model = BoardLabel
    extra = 0
    fields = ('name', 'color')


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    看板管理界面
    """
    list_display = ('name', 'owner', 'team', 'template', 'visibility', 'is_closed', 'member_count', 'list_count', 'created_at')
    list_filter = ('template', 'visibility', 'is_closed', 'enable_calendar', 'enable_timeline', 'created_at')
    search_fields = ('name', 'description', 'owner__email', 'owner__username', 'team__name')
    readonly_fields = ('slug', 'created_at', 'updated_at', 'member_count', 'list_count', 'task_count')
    inlines = [BoardListInline, BoardMemberInline, BoardLabelInline]
    fieldsets = (
        (_('基本信息'), {'fields': ('name', 'slug', 'description')}),
        (_('关联'), {'fields': ('owner', 'team')}),
        (_('样式'), {'fields': ('background_color', 'background_image')}),
        (_('配置'), {'fields': ('template', 'visibility')}),
        (_('功能设置'), {'fields': ('enable_calendar', 'enable_timeline', 'enable_comments', 'enable_attachments')}),
        (_('状态'), {'fields': ('is_closed',)}),
        (_('统计'), {'fields': ('member_count', 'list_count', 'task_count')}),
        (_('时间'), {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'team')


@admin.register(BoardList)
class BoardListAdmin(admin.ModelAdmin):
    """
    看板列表管理界面
    """
    list_display = ('name', 'board', 'position', 'color', 'is_archived', 'is_done_list', 'wip_limit', 'task_count')
    list_filter = ('is_archived', 'is_done_list', 'created_at')
    search_fields = ('name', 'board__name')
    readonly_fields = ('created_at', 'updated_at', 'task_count', 'is_wip_exceeded')
    fieldsets = (
        (_('基本信息'), {'fields': ('board', 'name', 'position')}),
        (_('样式'), {'fields': ('color',)}),
        (_('设置'), {'fields': ('is_done_list', 'wip_limit')}),
        (_('状态'), {'fields': ('is_archived',)}),
        (_('统计'), {'fields': ('task_count', 'is_wip_exceeded')}),
        (_('时间'), {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('board')


@admin.register(BoardMember)
class BoardMemberAdmin(admin.ModelAdmin):
    """
    看板成员管理界面
    """
    list_display = ('board', 'user', 'role', 'is_active', 'invited_by', 'joined_at')
    list_filter = ('role', 'is_active', 'joined_at')
    search_fields = ('board__name', 'user__email', 'user__username')
    readonly_fields = ('joined_at', 'updated_at', 'is_admin')
    fieldsets = (
        (_('基本信息'), {'fields': ('board', 'user', 'role')}),
        (_('状态'), {'fields': ('is_active',)}),
        (_('邀请信息'), {'fields': ('invited_by',)}),
        (_('权限'), {'fields': ('is_admin',)}),
        (_('时间'), {'fields': ('joined_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('board', 'user', 'invited_by')


@admin.register(BoardLabel)
class BoardLabelAdmin(admin.ModelAdmin):
    """
    看板标签管理界面
    """
    list_display = ('name', 'board', 'color', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'board__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        (_('基本信息'), {'fields': ('board', 'name', 'color')}),
        (_('时间'), {'fields': ('created_at',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('board')


@admin.register(BoardActivity)
class BoardActivityAdmin(admin.ModelAdmin):
    """
    看板活动管理界面
    """
    list_display = ('board', 'user', 'action', 'description', 'target_type', 'target_id', 'created_at')
    list_filter = ('action', 'target_type', 'created_at')
    search_fields = ('board__name', 'user__email', 'description')
    readonly_fields = ('created_at',)
    fieldsets = (
        (_('基本信息'), {'fields': ('board', 'user', 'action', 'description')}),
        (_('目标对象'), {'fields': ('target_type', 'target_id')}),
        (_('元数据'), {'fields': ('metadata',)}),
        (_('时间'), {'fields': ('created_at',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('board', 'user')
