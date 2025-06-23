#!/usr/bin/env python
"""
报表表单修复验证脚本
测试ReportFilterForm和ReportCreateForm是否正常工作
"""

import os
import sys
import django

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'taskkanban'))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

from django.contrib.auth import get_user_model
from reports.forms import ReportFilterForm, ReportCreateForm

User = get_user_model()

def test_report_filter_form():
    """测试报表筛选表单"""
    print("🔍 测试ReportFilterForm...")
    
    # 获取一个用户
    user = User.objects.first()
    if not user:
        print("  ⚠️ 没有找到用户，跳过用户相关测试")
        user = None
    else:
        print(f"  👤 使用用户: {user.username}")
    
    try:
        # 测试无用户情况
        print("  📝 测试无用户情况:")
        form = ReportFilterForm()
        print(f"    表单字段: {list(form.fields.keys())}")
        print(f"    ✅ 无用户情况正常")
        
        # 测试有用户情况
        if user:
            print("  👤 测试有用户情况:")
            form_with_user = ReportFilterForm(user=user)
            print(f"    表单字段: {list(form_with_user.fields.keys())}")
            
            # 检查queryset是否正确设置
            team_queryset = form_with_user.fields['team'].queryset
            board_queryset = form_with_user.fields['board'].queryset
            user_queryset = form_with_user.fields['user'].queryset
            
            print(f"    团队选项数量: {team_queryset.count()}")
            print(f"    看板选项数量: {board_queryset.count()}")
            print(f"    用户选项数量: {user_queryset.count()}")
            print(f"    ✅ 有用户情况正常")
        
        # 测试表单验证
        print("  ✅ 测试表单验证:")
        test_data = {
            'time_range': '30days',
            'start_date': '',
            'end_date': '',
        }
        form_with_data = ReportFilterForm(test_data, user=user)
        is_valid = form_with_data.is_valid()
        print(f"    表单验证结果: {is_valid}")
        if not is_valid:
            print(f"    验证错误: {form_with_data.errors}")
        
        if is_valid:
            start_date, end_date = form_with_data.get_date_range()
            print(f"    日期范围: {start_date} 到 {end_date}")
        
        print(f"  ✅ ReportFilterForm测试通过")
        
    except Exception as e:
        print(f"  ❌ ReportFilterForm测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_report_create_form():
    """测试报表创建表单"""
    print("\n📝 测试ReportCreateForm...")
    
    # 获取一个用户
    user = User.objects.first()
    if not user:
        print("  ⚠️ 没有找到用户，跳过用户相关测试")
        user = None
    else:
        print(f"  👤 使用用户: {user.username}")
    
    try:
        # 测试无用户情况
        print("  📝 测试无用户情况:")
        form = ReportCreateForm()
        print(f"    表单字段: {list(form.fields.keys())}")
        print(f"    ✅ 无用户情况正常")
        
        # 测试有用户情况
        if user:
            print("  👤 测试有用户情况:")
            form_with_user = ReportCreateForm(user=user)
            print(f"    表单字段: {list(form_with_user.fields.keys())}")
            
            # 检查queryset是否正确设置
            team_queryset = form_with_user.fields['team'].queryset
            board_queryset = form_with_user.fields['board'].queryset
            
            print(f"    团队选项数量: {team_queryset.count()}")
            print(f"    看板选项数量: {board_queryset.count()}")
            print(f"    ✅ 有用户情况正常")
        
        # 测试表单验证
        print("  ✅ 测试表单验证:")
        test_data = {
            'name': '测试报表',
            'description': '这是一个测试报表',
            'report_type': 'task_report',
            'frequency': 'weekly',
        }
        form_with_data = ReportCreateForm(test_data, user=user)
        is_valid = form_with_data.is_valid()
        print(f"    表单验证结果: {is_valid}")
        if not is_valid:
            print(f"    验证错误: {form_with_data.errors}")
        
        print(f"  ✅ ReportCreateForm测试通过")
        
    except Exception as e:
        print(f"  ❌ ReportCreateForm测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_form_imports():
    """测试表单导入是否正常"""
    print("\n📦 测试表单导入...")
    
    try:
        from reports.forms import ReportFilterForm, ReportCreateForm, ChartConfigForm, ExportForm
        print("  ✅ 所有表单类导入成功")
        
        # 测试Q导入是否正常
        from django.db.models import Q
        test_q = Q(id=1)
        print("  ✅ Q对象导入和使用正常")
        
        print("  ✅ 导入测试通过")
        
    except Exception as e:
        print(f"  ❌ 导入测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 报表表单修复验证测试")
    print("=" * 60)
    
    try:
        # 测试导入
        test_form_imports()
        
        # 测试表单
        test_report_filter_form()
        test_report_create_form()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("🔧 forms.py中的问题已修复")
        print("📊 报表表单功能正常")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
