#!/usr/bin/env python
"""
直接检查项目进度页面源码
"""

import requests

def check_page_source():
    url = "http://127.0.0.1:8000/reports/project-progress/"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text
            
            print("检查项目进度页面源码...")
            print("=" * 50)
            
            # 检查Chart.js
            if 'chart.js' in content.lower():
                print("✅ 包含 Chart.js")
            else:
                print("❌ 不包含 Chart.js")
            
            # 检查maintainAspectRatio
            if 'maintainAspectRatio: false' in content:
                print("⚠️  发现 maintainAspectRatio: false")
            elif 'maintainAspectRatio: true' in content:
                print("✅ 发现 maintainAspectRatio: true")
            else:
                print("ℹ️  未找到 maintainAspectRatio 设置")
            
            # 检查canvas
            import re
            canvas_matches = re.findall(r'<canvas[^>]*>', content, re.IGNORECASE)
            if canvas_matches:
                print(f"📊 发现 {len(canvas_matches)} 个canvas元素:")
                for i, canvas in enumerate(canvas_matches, 1):
                    print(f"  {i}. {canvas}")
            else:
                print("ℹ️  未找到canvas元素")
                
            # 检查new Chart
            if 'new Chart(' in content:
                print("✅ 发现 Chart 初始化代码")
            else:
                print("❌ 未找到 Chart 初始化代码")
                
            # 检查aspectRatio
            if 'aspectRatio:' in content:
                print("✅ 发现 aspectRatio 设置")
            else:
                print("ℹ️  未找到 aspectRatio 设置")
                
        else:
            print(f"页面访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    check_page_source()
