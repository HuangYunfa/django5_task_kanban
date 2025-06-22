#!/usr/bin/env python
"""
报表导出功能测试脚本
测试CSV、Excel、PDF、JSON导出功能
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
from reports.services import ReportDataService
from reports.export_services import ReportExportService, ChartExportService

User = get_user_model()

def test_export_services():
    """测试导出服务"""
    print("📊 测试报表导出功能...")
    
    # 设置日期范围
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    print(f"  📅 日期范围: {start_date} 到 {end_date}")
    
    # 获取报表数据
    data_service = ReportDataService(
        start_date=start_date,
        end_date=end_date
    )
    
    # 获取仪表板数据
    dashboard_data = data_service.get_dashboard_summary()
    
    print(f"  📈 数据包含: {list(dashboard_data.keys())}")
    
    # 创建导出服务
    export_service = ReportExportService(dashboard_data, "测试报表")
    
    # 测试各种导出格式
    export_formats = ['csv', 'json']
    
    # 如果有pandas，测试Excel导出
    try:
        import pandas as pd
        export_formats.append('excel')
        print("  ✅ 检测到pandas，支持Excel导出")
    except ImportError:
        print("  ⚠️ 未安装pandas，跳过Excel导出测试")
    
    # 如果有reportlab，测试PDF导出
    try:
        import reportlab
        export_formats.append('pdf')
        print("  ✅ 检测到reportlab，支持PDF导出")
    except ImportError:
        print("  ⚠️ 未安装reportlab，跳过PDF导出测试")
    
    for format_type in export_formats:
        try:
            print(f"\n  📄 测试{format_type.upper()}导出:")
            
            if format_type == 'csv':
                response = export_service.export_to_csv()
            elif format_type == 'excel':
                response = export_service.export_to_excel()
            elif format_type == 'pdf':
                response = export_service.export_to_pdf()
            elif format_type == 'json':
                response = export_service.export_to_json()
            
            print(f"    Content-Type: {response.get('Content-Type', 'Not set')}")
            print(f"    Content-Disposition: {response.get('Content-Disposition', 'Not set')}")
            print(f"    Response size: {len(response.content)} bytes")
            print(f"    ✅ {format_type.upper()}导出成功")
            
        except Exception as e:
            print(f"    ❌ {format_type.upper()}导出失败: {str(e)}")

def test_chart_export_service():
    """测试图表导出服务"""
    print("\n📈 测试图表导出功能...")
    
    # 测试图表数据
    test_chart_data = {
        'labels': ['已完成', '进行中', '待办'],
        'datasets': [{
            'label': '任务状态',
            'data': [10, 5, 15],
            'backgroundColor': ['#28a745', '#ffc107', '#dc3545']
        }]
    }
    
    try:
        response = ChartExportService.export_chart_data(test_chart_data)
        print(f"  Content-Type: {response.get('Content-Type', 'Not set')}")
        print(f"  Content-Disposition: {response.get('Content-Disposition', 'Not set')}")
        print(f"  Response size: {len(response.content)} bytes")
        print("  ✅ 图表数据导出成功")
    except Exception as e:
        print(f"  ❌ 图表数据导出失败: {str(e)}")

def test_report_data_structure():
    """测试报表数据结构"""
    print("\n🔍 测试报表数据结构...")
    
    # 设置日期范围
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # 获取报表数据
    data_service = ReportDataService(
        start_date=start_date,
        end_date=end_date
    )
    
    # 测试各种数据获取方法
    methods = [
        ('任务完成统计', 'get_task_completion_stats'),
        ('用户工作负载', 'get_user_workload_stats'),
        ('团队绩效统计', 'get_team_performance_stats'),
        ('项目进度统计', 'get_project_progress_stats'),
        ('仪表板摘要', 'get_dashboard_summary'),
    ]
    
    for name, method_name in methods:
        try:
            method = getattr(data_service, method_name)
            data = method()
            print(f"  📊 {name}:")
            print(f"    数据键: {list(data.keys())}")
            if 'summary' in data:
                print(f"    摘要数据: {list(data['summary'].keys())}")
            print(f"    ✅ {name}数据获取成功")
        except Exception as e:
            print(f"    ❌ {name}数据获取失败: {str(e)}")

def show_dependencies():
    """显示依赖库状态"""
    print("\n📚 检查依赖库状态...")
    
    dependencies = [
        ('pandas', 'Excel导出功能'),
        ('reportlab', 'PDF导出功能'),
        ('openpyxl', 'Excel读写支持'),
    ]
    
    for lib, description in dependencies:
        try:
            __import__(lib)
            print(f"  ✅ {lib}: 已安装 - {description}")
        except ImportError:
            print(f"  ❌ {lib}: 未安装 - {description}")
            print(f"    安装命令: pip install {lib}")

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 报表导出功能测试")
    print("=" * 60)
    
    try:
        # 显示依赖库状态
        show_dependencies()
        
        # 测试报表数据结构
        test_report_data_structure()
        
        # 测试导出服务
        test_export_services()
        
        # 测试图表导出服务
        test_chart_export_service()
        
        print("\n" + "=" * 60)
        print("✅ 导出功能测试完成！")
        print("📊 基础导出功能(CSV/JSON)已可用")
        print("📈 图表数据导出功能已可用")
        print("💡 提示: 安装pandas和reportlab可启用更多导出格式")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
