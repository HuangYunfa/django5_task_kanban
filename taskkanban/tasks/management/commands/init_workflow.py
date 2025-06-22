"""
初始化工作流状态的管理命令
为现有看板创建默认的工作流状态和转换规则
"""

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from boards.models import Board
from tasks.workflow_models import WorkflowStatus, WorkflowTransition


class Command(BaseCommand):
    help = '为现有看板初始化默认工作流状态'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--board-id',
            type=int,
            help='指定看板ID，不指定则为所有看板初始化'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建工作流状态'
        )
    
    def handle(self, *args, **options):
        board_id = options.get('board_id')
        force = options.get('force', False)
        
        if board_id:
            try:
                boards = [Board.objects.get(id=board_id)]
                self.stdout.write(f"为看板 ID {board_id} 初始化工作流...")
            except Board.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'看板 ID {board_id} 不存在')
                )
                return
        else:
            boards = Board.objects.all()
            self.stdout.write(f"为 {boards.count()} 个看板初始化工作流...")
        
        total_created = 0
        total_skipped = 0
        
        for board in boards:
            created, skipped = self.init_board_workflow(board, force)
            total_created += created
            total_skipped += skipped
        
        self.stdout.write(
            self.style.SUCCESS(
                f'工作流初始化完成！创建 {total_created} 个状态，跳过 {total_skipped} 个'
            )
        )
    
    def init_board_workflow(self, board, force=False):
        """为指定看板初始化工作流"""
        created_count = 0
        skipped_count = 0
        
        # 检查是否已有工作流状态
        if not force and board.workflow_statuses.exists():
            self.stdout.write(
                f"看板 '{board.name}' 已有工作流状态，跳过"
            )
            return 0, 1
        
        # 如果强制模式，先删除现有状态
        if force:
            board.workflow_statuses.all().delete()
            self.stdout.write(f"清除看板 '{board.name}' 的现有工作流状态")
        
        # 根据看板模板创建默认状态
        statuses_config = self.get_default_statuses_config(board.template)
        
        # 创建状态
        status_objects = {}
        for config in statuses_config:
            status = WorkflowStatus.objects.create(
                name=config['name'],
                display_name=config['display_name'],
                color=config['color'],
                board=board,
                position=config['position'],
                is_initial=config.get('is_initial', False),
                is_final=config.get('is_final', False)
            )
            status_objects[config['name']] = status
            created_count += 1
            
            self.stdout.write(
                f"  创建状态: {status.display_name} ({status.color})"
            )
        
        # 创建状态转换规则
        transitions_config = self.get_default_transitions_config(board.template)
        
        for config in transitions_config:
            from_status = status_objects.get(config['from_status'])
            to_status = status_objects.get(config['to_status'])
            
            if from_status and to_status:
                transition = WorkflowTransition.objects.create(
                    from_status=from_status,
                    to_status=to_status,
                    name=config['name'],
                    description=config.get('description', ''),
                    require_comment=config.get('require_comment', False),
                    auto_notify_assignees=config.get('auto_notify_assignees', True)
                )
                
                self.stdout.write(
                    f"  创建转换: {transition.name}"
                )
        
        return created_count, skipped_count
    
    def get_default_statuses_config(self, template):
        """根据模板获取默认状态配置"""
        if template == 'kanban':
            return [
                {
                    'name': 'todo',
                    'display_name': _('待办'),
                    'color': '#6c757d',
                    'position': 1,
                    'is_initial': True
                },
                {
                    'name': 'in_progress',
                    'display_name': _('进行中'),
                    'color': '#007bff',
                    'position': 2
                },
                {
                    'name': 'review',
                    'display_name': _('审核中'),
                    'color': '#ffc107',
                    'position': 3
                },
                {
                    'name': 'done',
                    'display_name': _('已完成'),
                    'color': '#28a745',
                    'position': 4,
                    'is_final': True
                },
                {
                    'name': 'blocked',
                    'display_name': _('已阻塞'),
                    'color': '#dc3545',
                    'position': 5
                }
            ]
        elif template == 'scrum':
            return [
                {
                    'name': 'backlog',
                    'display_name': _('产品待办'),
                    'color': '#6c757d',
                    'position': 1,
                    'is_initial': True
                },
                {
                    'name': 'sprint_backlog',
                    'display_name': _('冲刺待办'),
                    'color': '#17a2b8',
                    'position': 2
                },
                {
                    'name': 'in_progress',
                    'display_name': _('开发中'),
                    'color': '#007bff',
                    'position': 3
                },
                {
                    'name': 'testing',
                    'display_name': _('测试中'),
                    'color': '#ffc107',
                    'position': 4
                },
                {
                    'name': 'review',
                    'display_name': _('代码审查'),
                    'color': '#fd7e14',
                    'position': 5
                },
                {
                    'name': 'done',
                    'display_name': _('已完成'),
                    'color': '#28a745',
                    'position': 6,
                    'is_final': True
                }
            ]
        else:
            # 默认状态配置
            return [
                {
                    'name': 'todo',
                    'display_name': _('待办'),
                    'color': '#6c757d',
                    'position': 1,
                    'is_initial': True
                },
                {
                    'name': 'in_progress',
                    'display_name': _('进行中'),
                    'color': '#007bff',
                    'position': 2
                },
                {
                    'name': 'done',
                    'display_name': _('已完成'),
                    'color': '#28a745',
                    'position': 3,
                    'is_final': True
                }
            ]
    
    def get_default_transitions_config(self, template):
        """根据模板获取默认转换配置"""
        if template == 'kanban':
            return [
                {
                    'from_status': 'todo',
                    'to_status': 'in_progress',
                    'name': _('开始处理'),
                    'description': _('将任务设为进行中')
                },
                {
                    'from_status': 'in_progress',
                    'to_status': 'review',
                    'name': _('提交审核'),
                    'description': _('提交任务进行审核')
                },
                {
                    'from_status': 'review',
                    'to_status': 'done',
                    'name': _('审核通过'),
                    'description': _('审核通过，任务完成')
                },
                {
                    'from_status': 'review',
                    'to_status': 'in_progress',
                    'name': _('审核退回'),
                    'description': _('审核不通过，退回继续处理')
                },
                {
                    'from_status': 'in_progress',
                    'to_status': 'blocked',
                    'name': _('标记阻塞'),
                    'description': _('任务遇到阻塞'),
                    'require_comment': True
                },
                {
                    'from_status': 'blocked',
                    'to_status': 'in_progress',
                    'name': _('解除阻塞'),
                    'description': _('阻塞问题已解决')
                }
            ]
        elif template == 'scrum':
            return [
                {
                    'from_status': 'backlog',
                    'to_status': 'sprint_backlog',
                    'name': _('加入冲刺'),
                    'description': _('将任务加入当前冲刺')
                },
                {
                    'from_status': 'sprint_backlog',
                    'to_status': 'in_progress',
                    'name': _('开始开发'),
                    'description': _('开始开发任务')
                },
                {
                    'from_status': 'in_progress',
                    'to_status': 'testing',
                    'name': _('提交测试'),
                    'description': _('开发完成，提交测试')
                },
                {
                    'from_status': 'testing',
                    'to_status': 'review',
                    'name': _('代码审查'),
                    'description': _('测试通过，进行代码审查')
                },
                {
                    'from_status': 'review',
                    'to_status': 'done',
                    'name': _('完成'),
                    'description': _('代码审查通过，任务完成')
                },
                {
                    'from_status': 'testing',
                    'to_status': 'in_progress',
                    'name': _('测试不通过'),
                    'description': _('测试不通过，退回开发'),
                    'require_comment': True
                }
            ]
        else:
            return [
                {
                    'from_status': 'todo',
                    'to_status': 'in_progress',
                    'name': _('开始处理'),
                    'description': _('开始处理任务')
                },
                {
                    'from_status': 'in_progress',
                    'to_status': 'done',
                    'name': _('完成'),
                    'description': _('任务已完成')
                },
                {
                    'from_status': 'in_progress',
                    'to_status': 'todo',
                    'name': _('暂停'),
                    'description': _('暂停任务处理')
                }
            ]
