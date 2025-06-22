from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Task, TaskAssignment, SubTask, TaskDependency,
    TaskComment, TaskAttachment
)


class TaskAssignmentInline(admin.TabularInline):
    """
    任务分配内联编辑
    """
    model = TaskAssignment
    extra = 0
    fields = ('user', 'assigned_by', 'assigned_at')
    readonly_fields = ('assigned_at',)


class SubTaskInline(admin.TabularInline):
    """
    子任务内联编辑
    """
    model = SubTask
    extra = 0
    fields = ('title', 'assignee', 'status', 'position', 'due_date')
    ordering = ('position',)


class TaskCommentInline(admin.TabularInline):
    """
    任务评论内联编辑
    """
    model = TaskComment
    extra = 0
    fields = ('user', 'content', 'is_edited')
    readonly_fields = ('created_at', 'is_edited')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    任务管理界面
    """
    list_display = ('title', 'board', 'board_list', 'creator', 'priority', 'status', 'progress', 'due_date', 'is_overdue', 'created_at')
    list_filter = ('priority', 'status', 'is_archived', 'is_template', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'creator__email', 'board__name')
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'completed_by', 'is_overdue', 'days_until_due', 'assignee_count', 'comment_count', 'attachment_count', 'subtask_count', 'completed_subtask_count')
    filter_horizontal = ('labels',)
    inlines = [TaskAssignmentInline, SubTaskInline, TaskCommentInline]
    fieldsets = (
        (_('基本信息'), {'fields': ('title', 'description')}),
        (_('关联'), {'fields': ('board', 'board_list', 'creator', 'reporter')}),
        (_('属性'), {'fields': ('priority', 'status', 'progress', 'position')}),
        (_('标签'), {'fields': ('labels',)}),
        (_('时间管理'), {'fields': ('start_date', 'due_date', 'estimated_hours', 'actual_hours')}),
        (_('完成信息'), {'fields': ('completed_at', 'completed_by')}),
        (_('状态标记'), {'fields': ('is_archived', 'is_template')}),
        (_('统计信息'), {'fields': ('assignee_count', 'comment_count', 'attachment_count', 'subtask_count', 'completed_subtask_count')}),
        (_('时间字段'), {'fields': ('created_at', 'updated_at')}),
        (_('状态检查'), {'fields': ('is_overdue', 'days_until_due')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('board', 'board_list', 'creator', 'reporter', 'completed_by')


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    """
    任务分配管理界面
    """
    list_display = ('task', 'user', 'assigned_by', 'assigned_at')
    list_filter = ('assigned_at',)
    search_fields = ('task__title', 'user__email', 'assigned_by__email')
    readonly_fields = ('assigned_at',)
    fieldsets = (
        (_('分配信息'), {'fields': ('task', 'user', 'assigned_by')}),
        (_('时间'), {'fields': ('assigned_at',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'user', 'assigned_by')


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    """
    子任务管理界面
    """
    list_display = ('title', 'parent_task', 'assignee', 'status', 'position', 'due_date', 'completed_at')
    list_filter = ('status', 'created_at', 'due_date')
    search_fields = ('title', 'parent_task__title', 'assignee__email')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fieldsets = (
        (_('基本信息'), {'fields': ('parent_task', 'title', 'description')}),
        (_('分配'), {'fields': ('assignee',)}),
        (_('状态'), {'fields': ('status', 'position')}),
        (_('时间'), {'fields': ('due_date', 'completed_at', 'created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent_task', 'assignee')


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    """
    任务依赖管理界面
    """
    list_display = ('from_task', 'to_task', 'dependency_type', 'created_by', 'created_at')
    list_filter = ('dependency_type', 'created_at')
    search_fields = ('from_task__title', 'to_task__title', 'created_by__email')
    readonly_fields = ('created_at',)
    fieldsets = (
        (_('依赖关系'), {'fields': ('from_task', 'to_task', 'dependency_type')}),
        (_('创建信息'), {'fields': ('created_by', 'created_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('from_task', 'to_task', 'created_by')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """
    任务评论管理界面
    """
    list_display = ('task', 'user', 'content_preview', 'parent', 'is_edited', 'created_at')
    list_filter = ('is_edited', 'created_at')
    search_fields = ('task__title', 'user__email', 'content')
    readonly_fields = ('created_at', 'updated_at', 'edited_at')
    filter_horizontal = ('mentioned_users',)
    fieldsets = (
        (_('基本信息'), {'fields': ('task', 'user', 'content')}),
        (_('回复'), {'fields': ('parent',)}),
        (_('提及'), {'fields': ('mentioned_users',)}),
        (_('编辑历史'), {'fields': ('is_edited', 'edited_at')}),
        (_('时间'), {'fields': ('created_at', 'updated_at')}),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = _('评论预览')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'user', 'parent')


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    """
    任务附件管理界面
    """
    list_display = ('task', 'user', 'original_name', 'file_size_display', 'content_type', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('task__title', 'user__email', 'original_name', 'description')
    readonly_fields = ('created_at', 'file_size_display')
    fieldsets = (
        (_('基本信息'), {'fields': ('task', 'user', 'file')}),
        (_('文件信息'), {'fields': ('original_name', 'file_size', 'content_type')}),
        (_('描述'), {'fields': ('description',)}),
        (_('统计'), {'fields': ('file_size_display',)}),
        (_('时间'), {'fields': ('created_at',)}),
    )
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = _('文件大小')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'user')
