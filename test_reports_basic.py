#!/usr/bin/env python3
"""
报表分析模块基本功能测试脚本
"""
import os
import sys
import django

# 设置Django环境
project_root = os.path.dirname(os.path.abspath(__file__))
taskkanban_dir = os.path.join(project_root, 'taskkanban')
sys.path.insert(0, taskkanban_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')

# 初始化Django
django.setup()

from django.contrib.auth import get_user_model
from reports.models import Report
from reports.services import ReportDataService, ChartDataService
from reports.forms import ReportFilterForm, ReportCreateForm
from datetime import datetime, timedelta

User = get_user_model()

def test_reports_module():
    """测试报表模块基础功能"""
    print("🚀 开始测试报表分析模块...")
    print("=" * 50)
    
    try:
        # 1. 测试模型
        print("📋 1. 测试报表模型...")
        
        # 获取或创建测试用户
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': '测试',
                'last_name': '用户'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
        print(f"   ✅ 测试用户: {user.username}")
        
        # 创建测试报表
        report, created = Report.objects.get_or_create(
            name='测试仪表板',
            defaults={
                'description': '这是一个测试用的仪表板报表',
                'report_type': 'dashboard',
                'created_by': user,
                'config': {
                    'chart_type': 'bar',
                    'time_range': '30days',
                    'metrics': ['tasks', 'teams']
                }
            }
        )
        print(f"   ✅ 测试报表: {report.name}")
        
        # 2. 测试数据服务
        print("\n📊 2. 测试数据服务...")
        
        # 初始化数据服务
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()
        
        data_service = ReportDataService(
            start_date=start_date,
            end_date=end_date,
            user=user
        )
        
        # 测试仪表板数据
        dashboard_data = data_service.get_dashboard_summary()
        print(f"   ✅ 仪表板数据获取成功，任务统计: {dashboard_data.get('task_stats', {})}")
        
        # 测试任务统计
        task_stats = data_service.get_task_completion_stats()
        print(f"   ✅ 任务统计数据: 总任务 {task_stats.get('total_tasks', 0)}")
        
        # 测试用户工作负载
        workload_stats = data_service.get_user_workload_stats()
        print(f"   ✅ 工作负载统计: {len(workload_stats.get('user_workloads', []))} 个用户")
        
        # 3. 测试图表数据服务
        print("\n📈 3. 测试图表数据服务...")
        
        # 测试数据格式化
        sample_data = [
            {'label': '任务A', 'value': 10},
            {'label': '任务B', 'value': 20},
            {'label': '任务C', 'value': 15}
        ]
        
        chart_data = ChartDataService.format_for_chartjs(sample_data, 'bar')
        print(f"   ✅ Chart.js数据格式化成功: {len(chart_data.get('labels', []))} 个标签")
        
        # 4. 测试表单
        print("\n📝 4. 测试表单...")
        
        # 测试筛选表单
        filter_form = ReportFilterForm(user=user)
        print("   ✅ 报表筛选表单初始化成功")
        
        # 测试创建表单
        create_form = ReportCreateForm(user=user)
        print("   ✅ 报表创建表单初始化成功")
        
        # 5. 测试报表查询
        print("\n🔍 5. 测试报表查询...")
        
        # 查询用户的报表
        user_reports = Report.objects.filter(created_by=user)
        print(f"   ✅ 用户报表数量: {user_reports.count()}")
        
        # 按类型查询
        dashboard_reports = Report.objects.filter(report_type='dashboard')
        print(f"   ✅ 仪表板报表数量: {dashboard_reports.count()}")
        
        print("\n" + "=" * 50)
        print("🎉 报表分析模块基础功能测试完成！")
        print("\n📋 测试结果总结:")
        print(f"   • 报表模型: ✅ 正常")
        print(f"   • 数据服务: ✅ 正常")
        print(f"   • 图表服务: ✅ 正常") 
        print(f"   • 表单系统: ✅ 正常")
        print(f"   • 数据查询: ✅ 正常")
        
        print(f"\n🔗 可以访问以下URL来查看报表功能:")
        print(f"   • 仪表板: http://localhost:8000/reports/")
        print(f"   • 任务报表: http://localhost:8000/reports/tasks/")
        print(f"   • 团队绩效: http://localhost:8000/reports/team-performance/")
        print(f"   • 项目进度: http://localhost:8000/reports/project-progress/")
        print(f"   • 自定义报表: http://localhost:8000/reports/custom/")
        print(f"   • 报表列表: http://localhost:8000/reports/list/")
        print(f"   • 创建报表: http://localhost:8000/reports/create/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_reports_module()
    if success:
        print(f"\n✅ 报表分析模块测试通过！")
        sys.exit(0)
    else:
        print(f"\n❌ 报表分析模块测试失败！")
        sys.exit(1)
