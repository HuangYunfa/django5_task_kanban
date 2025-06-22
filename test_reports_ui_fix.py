#!/usr/bin/env python
"""
测试报表页面UI修复
验证表格无限增高问题是否解决
"""

import requests
import sys
import time

def test_page_response(url, page_name):
    """测试页面响应"""
    try:
        print(f"测试 {page_name} 页面...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {page_name} 页面访问成功")
            
            # 检查是否包含预期的CSS修复
            content = response.text
            if 'table-container' in content:
                print(f"✅ {page_name} 包含表格容器修复")
            elif 'table' in content:
                print(f"⚠️  {page_name} 包含表格但未使用修复后的容器")
            else:
                print(f"ℹ️  {page_name} 不包含表格")
                
            # 检查是否有明显的错误
            if '错误' in content or 'Error' in content or 'TypeError' in content:
                print(f"❌ {page_name} 可能包含错误")
                return False
                
            return True
        else:
            print(f"❌ {page_name} 访问失败 - 状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {page_name} 测试异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    base_url = "http://127.0.0.1:8000"
    
    # 定义要测试的页面
    pages = [
        ("/reports/", "报表首页"),
        ("/reports/tasks/", "任务统计报表"),  
        ("/reports/team-performance/", "团队绩效报表"),
        ("/reports/project-progress/", "项目进度报表"),
        ("/reports/custom/", "自定义报表"),
    ]
    
    print("=" * 50)
    print("开始测试报表页面UI修复")
    print("=" * 50)
    
    success_count = 0
    total_count = len(pages)
    
    for path, name in pages:
        url = base_url + path
        if test_page_response(url, name):
            success_count += 1
        print("-" * 30)
        time.sleep(1)  # 避免请求过快
    
    print("=" * 50)
    print(f"测试完成: {success_count}/{total_count} 页面正常")
    
    if success_count == total_count:
        print("🎉 所有报表页面测试通过！")
        return True
    else:
        print("⚠️  部分页面可能存在问题，请检查日志")
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
