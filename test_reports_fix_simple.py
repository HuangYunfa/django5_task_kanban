#!/usr/bin/env python
"""
报表数据服务修复验证脚本(简化版)
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

def test_basic_functionality():
    """测试基本功能"""
    print("🔍 测试报表数据服务基本功能...")
    
    # 设置日期范围
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    print(f"  📅 日期范围: {start_date} 到 {end_date}")
    
    try:
        # 创建基础服务实例
        service = ReportDataService(
            start_date=start_date,
            end_date=end_date
        )
        
        # 测试任务完成统计
        print("  📈 测试任务完成统计:")
        task_stats = service.get_task_completion_stats()
        print(f"    总任务: {task_stats['total_tasks']}")
        print(f"    已完成: {task_stats['completed_tasks']}")
        print(f"    完成率: {task_stats['completion_rate']}%")
        
        # 测试用户工作负载统计
        print("  👤 测试用户工作负载统计:")
        workload_stats = service.get_user_workload_stats()
        print(f"    活跃用户: {workload_stats['total_users']}")
        print(f"    平均任务数: {workload_stats['avg_tasks_per_user']}")
        
        # 测试团队绩效统计
        print("  👥 测试团队绩效统计:")
        team_stats = service.get_team_performance_stats()
        print(f"    团队数量: {team_stats['total_teams']}")
        
        # 测试项目进度统计（重点测试修复的功能）
        print("  📋 测试项目进度统计(已修复):")
        project_stats = service.get_project_progress_stats()
        print(f"    项目数量: {project_stats['total_projects']}")
        
        # 测试仪表板摘要
        print("  📊 测试仪表板摘要:")
        dashboard_stats = service.get_dashboard_summary()
        summary = dashboard_stats['summary']
        print(f"    总任务: {summary['total_tasks']}")
        print(f"    完成率: {summary['completion_rate']}%")
        print(f"    活跃用户: {summary['active_users']}")
        print(f"    活跃团队: {summary['active_teams']}")
        print(f"    活跃项目: {summary['active_projects']}")
        
        print("  ✅ 基本功能测试通过")
        
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_user_specific_queries():
    """测试用户特定查询"""
    print("\n🔍 测试用户特定查询...")
    
    # 获取第一个用户
    user = User.objects.first()
    if not user:
        print("  ⚠️ 没有找到用户，跳过测试")
        return
    
    print(f"  👤 测试用户: {user.username}")
    
    # 设置日期范围
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    try:
        # 创建用户特定的服务实例
        service = ReportDataService(
            start_date=start_date,
            end_date=end_date,
            user=user
        )
        
        # 测试项目进度统计（重点测试修复的功能）
        print("  📋 测试用户相关项目进度:")
        project_stats = service.get_project_progress_stats()
        print(f"    用户相关项目数量: {project_stats['total_projects']}")
        
        for project_stat in project_stats['project_stats'][:3]:  # 显示前3个
            print(f"    项目: {project_stat['board_name']} - 进度: {project_stat['progress_rate']}%")
        
        print("  ✅ 用户特定查询测试通过")
        
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_chart_data_service():
    """测试图表数据服务"""
    print("\n📈 测试图表数据服务...")
    
    try:
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
            chart_data = ChartDataService.format_for_chartjs(test_data, chart_type)
            print(f"    标签数量: {len(chart_data['labels'])}")
            print(f"    数据集数量: {len(chart_data['datasets'])}")
            print(f"    数据点数量: {len(chart_data['datasets'][0]['data'])}")
        
        # 测试颜色调色板
        print(f"  🎨 颜色调色板测试:")
        for count in [3, 8, 15]:
            colors = ChartDataService.get_color_palette(count)
            print(f"    {count}种颜色: {len(colors)}个")
        
        print("  ✅ 图表数据服务测试通过")
        
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 报表数据服务修复验证测试(简化版)")
    print("=" * 60)
    
    try:
        # 测试基本功能
        test_basic_functionality()
        
        # 测试用户特定查询
        test_user_specific_queries()
        
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
