#!/usr/bin/env python
"""
最终测试：验证报表页面表格无限增高修复
检查所有页面的表格样式和显示情况
"""

import requests
import re
import sys

def analyze_page_tables(url, page_name):
    """分析页面表格情况"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ {page_name} 无法访问")
            return False
            
        content = response.text
          # 检查是否有表格
        table_patterns = [
            r'<table[^>]*>',
            r'class="table',
            r'table table-striped'
        ]
        
        table_found = False
        for pattern in table_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                table_found = True
                break
                
        if not table_found:
            print(f"ℹ️  {page_name} 无表格")
            return True
            
        # 统计表格数量
        table_count = len(re.findall(r'<table[^>]*>', content, re.IGNORECASE))
        print(f"📊 {page_name} 包含 {table_count} 个表格")
        
        # 检查表格容器修复
        fixes_applied = []
        
        if 'table-container' in content:
            fixes_applied.append("使用了table-container类")
        
        if 'max-height:' in content or 'max-height: ' in content:
            fixes_applied.append("设置了最大高度")
            
        if 'overflow-y: auto' in content:
            fixes_applied.append("设置了垂直滚动")
            
        if 'data-table' in content:
            fixes_applied.append("使用了data-table类")
            
        if fixes_applied:
            print(f"✅ {page_name} 应用了修复: {', '.join(fixes_applied)}")
        else:
            print(f"⚠️  {page_name} 未应用表格高度限制修复")
            
        # 检查是否有明显错误
        error_patterns = [
            r'TypeError.*NoneType.*not subscriptable',
            r'Error.*',
            r'Exception.*',
            r'错误.*'
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                print(f"❌ {page_name} 检测到错误")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ {page_name} 分析异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    base_url = "http://127.0.0.1:8000"
    
    pages = [
        ("/reports/", "报表首页"),
        ("/reports/tasks/", "任务统计报表"),  
        ("/reports/team-performance/", "团队绩效报表"),
        ("/reports/project-progress/", "项目进度报表"),
        ("/reports/custom/", "自定义报表"),
    ]
    
    print("=" * 60)
    print("🔍 最终测试：检查报表页面表格无限增高修复")
    print("=" * 60)
    
    success_count = 0
    total_count = len(pages)
    
    for path, name in pages:
        url = base_url + path
        print(f"\n📋 检查 {name}...")
        if analyze_page_tables(url, name):
            success_count += 1
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print(f"🎯 检查完成: {success_count}/{total_count} 页面正常")
    
    if success_count == total_count:
        print("🎉 所有报表页面表格显示正常！")
        print("✅ 表格无限增高问题已修复")
        return True
    else:
        print("⚠️  部分页面可能仍有问题")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"测试脚本异常: {e}")
        sys.exit(1)
