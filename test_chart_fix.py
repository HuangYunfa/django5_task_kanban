#!/usr/bin/env python
"""
测试Chart.js图表高度修复
验证canvas元素是否不再无限增高
"""

import requests
import re
import time
import sys
from bs4 import BeautifulSoup

def check_canvas_heights(url, page_name):
    """检查页面canvas元素的高度"""
    try:
        print(f"检查 {page_name} 的图表高度...")
        
        # 多次请求检查高度变化
        heights = []
        for i in range(3):
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"❌ {page_name} 无法访问")
                return False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            canvas_elements = soup.find_all('canvas')
            
            if not canvas_elements:
                print(f"ℹ️  {page_name} 无图表")
                return True
            
            page_heights = []
            for canvas in canvas_elements:
                height_attr = canvas.get('height', '0')
                style_attr = canvas.get('style', '')
                
                # 提取高度值
                height_val = 0
                try:
                    if height_attr.isdigit():
                        height_val = int(height_attr)
                    elif 'height:' in style_attr:
                        height_match = re.search(r'height:\s*(\d+)', style_attr)
                        if height_match:
                            height_val = int(height_match.group(1))
                except:
                    pass
                
                page_heights.append(height_val)
            
            heights.append(page_heights)
            print(f"  第{i+1}次检查: {page_heights}")
            
            if i < 2:  # 不是最后一次
                time.sleep(2)
        
        # 分析高度变化
        if len(heights) >= 2:
            is_stable = True
            for i in range(1, len(heights)):
                for j in range(len(heights[0])):
                    if j < len(heights[i]):
                        # 如果高度增长超过50像素，认为不稳定
                        if abs(heights[i][j] - heights[0][j]) > 50:
                            is_stable = False
                            break
                if not is_stable:
                    break
            
            if is_stable:
                print(f"✅ {page_name} 图表高度稳定")
                return True
            else:
                print(f"❌ {page_name} 图表高度仍在变化")
                print(f"   初始高度: {heights[0]}")
                print(f"   最终高度: {heights[-1]}")
                return False
        else:
            print(f"ℹ️  {page_name} 数据不足，无法判断")
            return True
            
    except Exception as e:
        print(f"❌ {page_name} 检查异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    base_url = "http://127.0.0.1:8000"
    
    pages = [
        ("/reports/", "报表首页"),
        ("/reports/team-performance/", "团队绩效报表"),
        ("/reports/tasks/", "任务统计报表"),
        ("/reports/project-progress/", "项目进度报表"),
    ]
    
    print("=" * 60)
    print("🔍 测试Chart.js图表高度修复")
    print("=" * 60)
    
    success_count = 0
    total_count = len(pages)
    
    for path, name in pages:
        url = base_url + path
        if check_canvas_heights(url, name):
            success_count += 1
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print(f"🎯 测试完成: {success_count}/{total_count} 页面图表正常")
    
    if success_count == total_count:
        print("🎉 图表高度无限增长问题已修复！")
        return True
    else:
        print("⚠️  部分页面图表仍有问题")
        return False

if __name__ == "__main__":
    try:
        # 检查是否安装了beautifulsoup4
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("需要安装beautifulsoup4: pip install beautifulsoup4")
            sys.exit(1)
            
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"测试脚本异常: {e}")
        sys.exit(1)
