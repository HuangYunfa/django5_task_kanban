#!/usr/bin/env python
"""
简单检查页面中的canvas元素
"""

import requests

def check_page(url):
    try:
        response = requests.get(url)
        content = response.text
        
        canvas_count = content.count('<canvas')
        maintainAspectRatio_false_count = content.count('maintainAspectRatio: false')
        
        print(f"URL: {url}")
        print(f"Canvas元素数量: {canvas_count}")
        print(f"maintainAspectRatio:false 数量: {maintainAspectRatio_false_count}")
        
        if canvas_count > 0:
            print("包含的canvas元素:")
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '<canvas' in line:
                    print(f"  第{i+1}行: {line.strip()}")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"检查 {url} 时出错: {e}")

if __name__ == "__main__":
    urls = [
        "http://127.0.0.1:8000/reports/",
        "http://127.0.0.1:8000/reports/team-performance/",
        "http://127.0.0.1:8000/reports/tasks/"
    ]
    
    for url in urls:
        check_page(url)
