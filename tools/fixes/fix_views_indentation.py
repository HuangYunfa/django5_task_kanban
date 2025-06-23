#!/usr/bin/env python3
"""
修复 tasks/views.py 文件的缩进问题
"""
import os
import re

def fix_views_indentation():
    """修复views.py文件的缩进问题"""
    views_path = "taskkanban/tasks/views.py"
    
    if not os.path.exists(views_path):
        print(f"文件不存在: {views_path}")
        return
    
    # 备份原文件
    backup_path = f"{views_path}.backup"
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已备份原文件到: {backup_path}")
    
    # 修复已知的缩进问题
    fixed_content = fix_specific_indentation_issues(content)
    
    # 写入修复后的内容
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"已修复缩进问题: {views_path}")

def fix_specific_indentation_issues(content):
    """修复特定的缩进问题"""
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 修复第410行附近的缩进问题
        if "# 执行批量操作" in line and line.startswith("          "):
            # 这一行缩进太多，应该是8个空格
            fixed_lines.append("        # 执行批量操作")
        elif "if new_status not in dict(Task.STATUS_CHOICES):" in line and line.startswith("                      "):
            # 这一行缩进错误，应该是20个空格
            fixed_lines.append("                    if new_status not in dict(Task.STATUS_CHOICES):")
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return '\n'.join(fixed_lines)

if __name__ == "__main__":
    fix_views_indentation()
