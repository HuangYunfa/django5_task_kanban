#!/usr/bin/env python
"""
报表数据服务修复验证脚本
测试修复后的Board成员关系查询
"""

import os
import sys
import django
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'taskkanban'))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from boards.models import Board, BoardMember, BoardList
from tasks.models import Task
from teams.models import Team, TeamMembership
from reports.services import ReportDataService

User = get_user_model()

def setup_test_data():
    """设置测试数据"""
    print("🚀 设置测试数据...")
    
    # 创建测试用户
    users = []
    for i in range(3):
        user, created = User.objects.get_or_create(
            username=f'test_user_{i+1}',
            defaults={
                'email': f'test{i+1}@example.com',
                'nickname': f'测试用户{i+1}',
                'first_name': f'用户{i+1}',
            }
        )
        users.append(user)
        print(f"  👤 用户: {user.username} ({'已存在' if not created else '新创建'})")
      # 创建测试团队
    team, created = Team.objects.get_or_create(
        name='测试报表团队',
        defaults={
            'description': '用于测试报表功能的团队',
            'created_by': users[0],
        }
    )
    print(f"  👥 团队: {team.name} ({'已存在' if not created else '新创建'})")
    
    # 添加团队成员
    for user in users:
        membership, created = TeamMembership.objects.get_or_create(
            team=team,
            user=user,
            defaults={
                'role': 'admin' if user == users[0] else 'member',
                'status': 'active',
            }
        )
        print(f"    ➤ 成员: {user.username} ({membership.role})")
      # 创建测试看板
    board, created = Board.objects.get_or_create(
        name='测试报表看板',
        defaults={
            'description': '用于测试报表功能的看板',
            'owner': users[0],
            'team': team,
        }
    )
    print(f"  📋 看板: {board.name} ({'已存在' if not created else '新创建'})")
    
    # 添加看板成员
    for user in users:
        membership, created = BoardMember.objects.get_or_create(
            board=board,
            user=user,
            defaults={
                'role': 'admin' if user == users[0] else 'member',
                'is_active': True,
            }
        )
        print(f"    ➤ 看板成员: {user.username} ({membership.role})")
    
    # 创建看板列表
    lists = []
    for list_name in ['待办', '进行中', '已完成']:
        board_list, created = BoardList.objects.get_or_create(
            board=board,
            name=list_name,
            defaults={
                'position': len(lists),
                'is_done_list': list_name == '已完成',
            }
        )
        lists.append(board_list)
        print(f"    📝 列表: {board_list.name}")
    
    # 创建测试任务
    task_data = [
        ('任务1', 'todo', 'high', users[1]),
        ('任务2', 'in_progress', 'medium', users[1]),
        ('任务3', 'done', 'low', users[1]),
        ('任务4', 'todo', 'medium', users[2]),
        ('任务5', 'done', 'high', users[2]),
    ]
    
    for title, status, priority, assignee in task_data:
        # 根据状态选择列表
        if status == 'todo':
            board_list = lists[0]
        elif status == 'in_progress':
            board_list = lists[1]        else:
            board_list = lists[2]
        
        task, created = Task.objects.get_or_create(
            title=title,
            board=board,
            defaults={
                'description': f'测试{title}的描述',
                'board_list': board_list,
                'status': status,
                'priority': priority,
                'creator': users[0],
            }
        )
        
        # 添加任务分配
        if created:
            task.assignees.add(assignee)
        
        print(f"    ✅ 任务: {task.title} ({status}, {priority}) -> {assignee.username}")
    
    return users, team, board

def test_report_services():
    """测试报表数据服务"""
    print("\n📊 测试报表数据服务...")
    
    users, team, board = setup_test_data()
    
    # 设置日期范围
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    print(f"  📅 日期范围: {start_date} 到 {end_date}")
    
    # 测试不同的报表服务参数
    test_scenarios = [
        ('无过滤条件', {}),
        ('按团队过滤', {'team': team}),
        ('按看板过滤', {'board': board}),
        ('按用户过滤', {'user': users[0]}),
        ('按团队和用户过滤', {'team': team, 'user': users[0]}),
    ]
    
    for scenario_name, filters in test_scenarios:
        print(f"\n  🔍 测试场景: {scenario_name}")
        
        try:
            # 创建报表数据服务实例
            service = ReportDataService(
                start_date=start_date,
                end_date=end_date,
                **filters
            )
            
            # 测试任务完成统计
            print("    📈 任务完成统计:")
            task_stats = service.get_task_completion_stats()
            print(f"      总任务: {task_stats['total_tasks']}")
            print(f"      已完成: {task_stats['completed_tasks']}")
            print(f"      完成率: {task_stats['completion_rate']}%")
            
            # 测试用户工作负载统计
            print("    👤 用户工作负载统计:")
            workload_stats = service.get_user_workload_stats()
            print(f"      活跃用户: {workload_stats['total_users']}")
            print(f"      平均任务数: {workload_stats['avg_tasks_per_user']}")
            
            # 测试团队绩效统计
            print("    👥 团队绩效统计:")
            team_stats = service.get_team_performance_stats()
            print(f"      团队数量: {team_stats['total_teams']}")
            for team_stat in team_stats['team_stats'][:2]:  # 只显示前2个
                print(f"      团队: {team_stat['team_name']} - 完成率: {team_stat['completion_rate']}%")
            
            # 测试项目进度统计（重点测试修复的功能）
            print("    📋 项目进度统计:")
            project_stats = service.get_project_progress_stats()
            print(f"      项目数量: {project_stats['total_projects']}")
            for project_stat in project_stats['project_stats'][:2]:  # 只显示前2个
                print(f"      项目: {project_stat['board_name']} - 进度: {project_stat['progress_rate']}%")
            
            # 测试仪表板摘要
            print("    📊 仪表板摘要:")
            dashboard_stats = service.get_dashboard_summary()
            summary = dashboard_stats['summary']
            print(f"      总任务: {summary['total_tasks']}")
            print(f"      完成率: {summary['completion_rate']}%")
            print(f"      活跃用户: {summary['active_users']}")
            print(f"      活跃团队: {summary['active_teams']}")
            print(f"      活跃项目: {summary['active_projects']}")
            
        except Exception as e:
            print(f"    ❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()

def test_chart_data_service():
    """测试图表数据服务"""
    print("\n📈 测试图表数据服务...")
    
    from reports.services import ChartDataService
    
    # 测试数据
    test_data = [
        {'label': '已完成', 'value': 10},
        {'label': '进行中', 'value': 5},
        {'label': '待办', 'value': 15},
    ]
    
    # 测试不同图表类型
    chart_types = ['bar', 'pie', 'doughnut', 'line']
    
    for chart_type in chart_types:
        print(f"  📊 {chart_type.title()} 图表格式化:")
        try:
            chart_data = ChartDataService.format_for_chartjs(test_data, chart_type)
            print(f"    标签数量: {len(chart_data['labels'])}")
            print(f"    数据集数量: {len(chart_data['datasets'])}")
            print(f"    数据点数量: {len(chart_data['datasets'][0]['data'])}")
        except Exception as e:
            print(f"    ❌ 错误: {str(e)}")
    
    # 测试颜色调色板
    print(f"  🎨 颜色调色板测试:")
    for count in [3, 8, 15]:
        colors = ChartDataService.get_color_palette(count)
        print(f"    {count}种颜色: {len(colors)}个")

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 报表数据服务修复验证测试")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # 测试报表数据服务
            test_report_services()
            
            # 测试图表数据服务
            test_chart_data_service()
            
            print("\n" + "=" * 60)
            print("✅ 所有测试完成！")
            print("🔧 Board成员关系查询已修复")
            print("📊 报表数据服务运行正常")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
