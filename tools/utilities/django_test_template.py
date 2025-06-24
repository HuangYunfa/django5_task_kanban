#!/usr/bin/env python
"""
测试脚本模板 - 正确的Django配置
"""
import os
import sys
import django
from pathlib import Path

# 添加项目根目录到Python路径 - 根据脚本位置自动计算
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent / 'taskkanban'  # 根据实际层级调整
sys.path.insert(0, str(project_root))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskkanban.settings')
django.setup()

# 在这里添加你的测试代码
if __name__ == '__main__':
    print("Django setup 成功!")
    print(f"项目根目录: {project_root}")
    print(f"脚本位置: {__file__}")
