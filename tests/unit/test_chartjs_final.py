#!/usr/bin/env python
"""
全面测试Chart.js图表无限增高修复
检查所有报表页面的Chart.js配置
"""

import requests
import re
import sys
import time

def check_chartjs_config(url, page_name):
    """检查页面的Chart.js配置"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ {page_name} 无法访问")
            return False
            
        content = response.text
        
        # 检查是否包含Chart.js
        has_chartjs = 'chart.js' in content.lower() or 'new Chart(' in content
        if not has_chartjs:
            print(f"ℹ️  {page_name} 不使用Chart.js")
            return True
            
        print(f"📊 {page_name} 使用Chart.js")
        
        # 检查问题配置
        problems = []
        fixes = []
        
        # 检查 maintainAspectRatio: false
        if re.search(r'maintainAspectRatio:\s*false', content, re.IGNORECASE):
            problems.append("使用了 maintainAspectRatio: false")
        elif re.search(r'maintainAspectRatio:\s*true', content, re.IGNORECASE):
            fixes.append("设置了 maintainAspectRatio: true")
        
        # 检查 aspectRatio 设置
        if re.search(r'aspectRatio:\s*\d+', content, re.IGNORECASE):
            fixes.append("设置了 aspectRatio")
            
        # 检查防重复创建
        if 'destroy()' in content:
            fixes.append("添加了防重复创建逻辑")
            
        # 检查canvas高度限制
        canvas_matches = re.findall(r'<canvas[^>]*height="(\d+)"[^>]*>', content, re.IGNORECASE)
        if canvas_matches:
            for height in canvas_matches:
                if int(height) > 200:
                    problems.append(f"Canvas高度过高: {height}px")
                else:
                    fixes.append(f"Canvas高度合理: {height}px")
        
        # 报告结果
        if problems:
            print(f"⚠️  {page_name} 发现问题: {', '.join(problems)}")
        
        if fixes:
            print(f"✅ {page_name} 应用了修复: {', '.join(fixes)}")
            
        if not problems and fixes:
            print(f"🎉 {page_name} Chart.js配置良好")
            return True
        elif not problems and not fixes:
            print(f"ℹ️  {page_name} Chart.js配置无特殊处理")
            return True
        else:
            return len(problems) == 0
            
    except Exception as e:
        print(f"❌ {page_name} 检查异常: {str(e)}")
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
    
    print("=" * 70)
    print("🎯 全面测试：Chart.js图表无限增高修复验证")
    print("=" * 70)
    
    success_count = 0
    total_count = len(pages)
    
    for path, name in pages:
        url = base_url + path
        print(f"\n🔍 检查 {name}...")
        if check_chartjs_config(url, name):
            success_count += 1
        print("-" * 50)
        time.sleep(0.5)  # 避免请求过快
    
    print("\n" + "=" * 70)
    print(f"📈 检查完成: {success_count}/{total_count} 页面Chart.js配置正常")
    
    if success_count == total_count:
        print("🎉 所有报表页面Chart.js配置已修复！")
        print("✅ Canvas无限增高问题应该已解决")
        return True
    else:
        print("⚠️  部分页面Chart.js配置可能仍有问题")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        print("\n" + "=" * 70)
        print("💡 修复建议:")
        print("1. 所有Chart.js图表都应设置 maintainAspectRatio: true")
        print("2. 建议设置合理的 aspectRatio 值（如 2）")
        print("3. Canvas元素应设置合理的初始高度（不超过100px）")
        print("4. 添加防重复创建图表的逻辑")
        print("5. 在CSS中为图表容器设置max-height")
        
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"测试脚本异常: {e}")
        sys.exit(1)
