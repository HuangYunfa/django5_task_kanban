"""
任务状态流转系统测试脚本 - Django Shell版本
"""
from tasks.workflow_models import WorkflowStatus, WorkflowTransition, TaskStatusHistory
from boards.models import Board
from tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

print('🔥 任务状态流转系统测试')
print('=' * 50)

# 检查工作流状态
total_statuses = WorkflowStatus.objects.count()
total_transitions = WorkflowTransition.objects.count()
total_history = TaskStatusHistory.objects.count()

print(f'✅ 已创建 {total_statuses} 个工作流状态')
print(f'✅ 已创建 {total_transitions} 个状态转换规则')
print(f'✅ 已记录 {total_history} 条状态变更历史')

# 检查看板
boards = Board.objects.all()
print(f'📊 共有 {boards.count()} 个看板')

for board in boards:
    workflow_statuses = WorkflowStatus.objects.filter(board=board).order_by('position')
    print(f'   📋 {board.name}: {workflow_statuses.count()} 个状态')
    
    for status in workflow_statuses:
        flags = []
        if status.is_initial:
            flags.append('初始')
        if status.is_final:
            flags.append('最终')
        flag_str = f' [{", ".join(flags)}]' if flags else ''
        print(f'     🏷️  {status.display_name} ({status.color}){flag_str}')
        
        # 显示该状态的转换选项
        transitions = WorkflowTransition.objects.filter(from_status=status)[:3]  # 限制显示数量
        if transitions.exists():
            print(f'        ↳ 可转换到: {", ".join([t.to_status.display_name for t in transitions])}')

print('\n🔄 状态转换规则详情:')
for transition in WorkflowTransition.objects.all()[:10]:  # 只显示前10个
    print(f'   {transition.from_status.display_name} → {transition.to_status.display_name} ({transition.name})')

# 检查任务状态
tasks = Task.objects.all()
print(f'\n📝 共有 {tasks.count()} 个任务')

if tasks.exists():
    for task in tasks[:3]:  # 只显示前3个任务
        print(f'   📋 {task.title} - 状态: {task.get_status_display()}')

print('\n✅ 工作流系统测试完成！')
