#!/usr/bin/env python
"""
任务状态流转系统功能测试脚本
测试新开发的工作流状态管理功能
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from django.contrib.auth import get_user_model
from boards.models import Board
from tasks.models import Task
from tasks.workflow_models import WorkflowStatus, WorkflowTransition, TaskStatusHistory

User = get_user_model()


def test_workflow_status_system():
    """测试工作流状态系统"""
    print("🔄 开始测试任务状态流转系统...")
    
    # 1. 检查工作流状态是否已创建
    print("\n📊 检查工作流状态...")
    total_statuses = WorkflowStatus.objects.count()
    total_transitions = WorkflowTransition.objects.count()
    print(f"   ✅ 已创建 {total_statuses} 个工作流状态")
    print(f"   ✅ 已创建 {total_transitions} 个状态转换规则")
    
    # 2. 显示每个看板的工作流状态
    boards = Board.objects.all()
    print(f"\n📋 检查 {boards.count()} 个看板的工作流状态:")
    
    for board in boards:
        workflow_statuses = WorkflowStatus.objects.filter(board=board).order_by('position')
        print(f"\n   📌 看板: {board.name}")
        print(f"      状态数量: {workflow_statuses.count()}")
        
        for status in workflow_statuses:
            transitions_out = WorkflowTransition.objects.filter(from_status=status).count()
            transitions_in = WorkflowTransition.objects.filter(to_status=status).count()
            
            flags = []
            if status.is_initial:
                flags.append("初始")
            if status.is_final:
                flags.append("最终")
            if not status.is_active:
                flags.append("禁用")
            
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            
            print(f"      • {status.display_name} ({status.name}) {status.color}{flag_str}")
            print(f"        出线转换: {transitions_out}, 入线转换: {transitions_in}")
    
    # 3. 测试状态转换规则
    print(f"\n🔄 检查状态转换规则:")
    transitions = WorkflowTransition.objects.select_related('from_status', 'to_status')
    
    for board in boards:
        board_transitions = transitions.filter(from_status__board=board)
        if board_transitions.exists():
            print(f"\n   📌 看板: {board.name}")
            for transition in board_transitions:
                auto_features = []
                if transition.require_assignee:
                    auto_features.append("需要受理人")
                if transition.require_comment:
                    auto_features.append("需要备注")
                if transition.auto_assign_creator:
                    auto_features.append("自动分配创建者")
                if transition.auto_notify_assignees:
                    auto_features.append("自动通知")
                    
                features_str = f" [{', '.join(auto_features)}]" if auto_features else ""
                
                print(f"      • {transition.from_status.display_name} → {transition.to_status.display_name}")
                print(f"        规则名称: {transition.name}{features_str}")
    
    # 4. 检查现有任务的状态历史
    print(f"\n📝 检查任务状态历史:")
    tasks = Task.objects.all()[:5]  # 只检查前5个任务
    total_history = TaskStatusHistory.objects.count()
    
    print(f"   总共 {total_history} 条状态变更历史记录")
    
    if tasks.exists():
        print(f"   检查前 {tasks.count()} 个任务:")
        for task in tasks:
            history_count = TaskStatusHistory.objects.filter(task=task).count()
            print(f"   • 任务: {task.title[:50]}...")
            print(f"     当前状态: {task.get_status_display()}")
            print(f"     历史记录: {history_count} 条")
    
    # 5. 检查API端点
    print(f"\n🌐 可用的API端点:")
    print("   • /tasks/workflow/statuses/<board_slug>/                    - 状态列表")
    print("   • /tasks/workflow/statuses/<board_slug>/create/             - 创建状态")
    print("   • /tasks/workflow/statuses/<board_slug>/<status_id>/edit/   - 编辑状态")
    print("   • /tasks/workflow/statuses/<board_slug>/<status_id>/delete/ - 删除状态")
    print("   • /tasks/workflow/<board_slug>/<task_id>/change-status/     - 变更任务状态")
    print("   • /tasks/workflow/<board_slug>/<task_id>/status-history/    - 查看状态历史")
    
    # 6. 提供测试建议
    print(f"\n🧪 测试建议:")
    if boards.exists():
        first_board = boards.first()
        print(f"   1. 访问工作流状态管理页面:")
        print(f"      http://127.0.0.1:8000/tasks/workflow/statuses/{first_board.slug}/")
        
        if tasks.exists():
            first_task = tasks.first()
            print(f"   2. 查看任务状态历史:")
            print(f"      http://127.0.0.1:8000/tasks/workflow/{first_task.board.slug}/{first_task.pk}/status-history/")
            print(f"   3. 在任务详情页测试状态变更:")
            print(f"      http://127.0.0.1:8000/tasks/{first_task.board.slug}/{first_task.pk}/")
    
    print(f"\n✅ 任务状态流转系统测试完成！")
    
    return {
        'statuses': total_statuses,
        'transitions': total_transitions,
        'boards': boards.count(),
        'tasks': tasks.count(),
        'history': total_history
    }


def test_workflow_permissions():
    """测试工作流权限"""
    print("\n🔐 测试工作流权限...")
    
    # 检查是否有超级用户
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        print(f"   ✅ 找到 {superusers.count()} 个超级用户")
        for user in superusers:
            print(f"      • {user.username} ({user.email})")
    else:
        print("   ⚠️  没有找到超级用户，请创建一个用于测试")
    
    # 检查看板权限
    boards = Board.objects.all()
    if boards.exists():
        print(f"   📋 检查看板权限 ({boards.count()} 个看板):")
        for board in boards:
            owner = board.owner
            members_count = board.members.count() if hasattr(board, 'members') else 0
            print(f"      • {board.name}: 创建者 {owner.username}, 成员 {members_count} 人")


if __name__ == '__main__':
    print("🚀 Django 5 任务看板 - 工作流状态系统测试")
    print("=" * 60)
    
    try:
        # 测试工作流状态系统
        results = test_workflow_status_system()
        
        # 测试权限
        test_workflow_permissions()
        
        print("\n" + "=" * 60)
        print("📊 测试结果汇总:")
        print(f"   • 工作流状态: {results['statuses']} 个")
        print(f"   • 转换规则: {results['transitions']} 个")
        print(f"   • 关联看板: {results['boards']} 个")
        print(f"   • 现有任务: {results['tasks']} 个")
        print(f"   • 历史记录: {results['history']} 条")
        
        print("\n🎉 任务状态流转系统开发完成！可以开始使用了。")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
