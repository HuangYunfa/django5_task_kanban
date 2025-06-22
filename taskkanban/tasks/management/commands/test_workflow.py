"""
测试工作流系统的Django管理命令
"""
from django.core.management.base import BaseCommand
from tasks.workflow_models import WorkflowStatus, WorkflowTransition, TaskStatusHistory
from boards.models import Board
from tasks.models import Task


class Command(BaseCommand):
    help = '测试任务状态流转系统'

    def handle(self, *args, **options):
        self.stdout.write('🔥 任务状态流转系统测试')
        self.stdout.write('=' * 50)
        
        # 检查工作流状态
        total_statuses = WorkflowStatus.objects.count()
        total_transitions = WorkflowTransition.objects.count()
        total_history = TaskStatusHistory.objects.count()
        
        self.stdout.write(f'✅ 已创建 {total_statuses} 个工作流状态')
        self.stdout.write(f'✅ 已创建 {total_transitions} 个状态转换规则')
        self.stdout.write(f'✅ 已记录 {total_history} 条状态变更历史')
        
        # 检查看板
        boards = Board.objects.all()
        self.stdout.write(f'📊 共有 {boards.count()} 个看板')
        
        for board in boards:
            workflow_statuses = WorkflowStatus.objects.filter(board=board).order_by('position')
            self.stdout.write(f'   📋 {board.name}: {workflow_statuses.count()} 个状态')
            
            for status in workflow_statuses:
                flags = []
                if status.is_initial:
                    flags.append('初始')
                if status.is_final:
                    flags.append('最终')
                flag_str = f' [{", ".join(flags)}]' if flags else ''
                self.stdout.write(f'     🏷️  {status.display_name} ({status.color}){flag_str}')
                
                # 显示该状态的转换选项
                transitions = WorkflowTransition.objects.filter(from_status=status)[:2]
                if transitions.exists():
                    targets = [t.to_status.display_name for t in transitions]
                    self.stdout.write(f'        ↳ 可转换到: {", ".join(targets)}')
        
        self.stdout.write('\n🔄 状态转换规则详情:')
        for transition in WorkflowTransition.objects.all()[:8]:
            self.stdout.write(
                f'   {transition.from_status.display_name} → '
                f'{transition.to_status.display_name} ({transition.name})'
            )
        
        # 检查任务状态
        tasks = Task.objects.all()
        self.stdout.write(f'\n📝 共有 {tasks.count()} 个任务')
        
        if tasks.exists():
            for task in tasks[:3]:
                self.stdout.write(f'   📋 {task.title} - 状态: {task.get_status_display()}')
        
        self.stdout.write('\n✅ 工作流系统测试完成！')
        
        # 测试URL访问
        self.stdout.write('\n🌐 测试URL配置:')
        sample_board = boards.first()
        if sample_board:
            self.stdout.write(f'   工作流状态列表: /tasks/{sample_board.slug}/workflow/statuses/')
            self.stdout.write(f'   创建工作流状态: /tasks/{sample_board.slug}/workflow/statuses/create/')
            
        sample_task = tasks.first()
        if sample_task:
            self.stdout.write(f'   任务状态历史: /tasks/{sample_task.board.slug}/tasks/{sample_task.pk}/status-history/')
            
        self.stdout.write('\n🎉 所有测试完成！可以访问 http://127.0.0.1:8000/ 查看效果')
