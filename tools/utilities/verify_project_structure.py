#!/usr/bin/env python
"""
简单的测试验证脚本
验证项目文件结构整理后测试系统正常工作
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """主函数"""
    print("=" * 60)
    print("项目文件结构整理完成 - 测试验证")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"当前工作目录: {os.getcwd()}")
    print()
    
    # 验证目录结构
    print("1. 验证目录结构:")
    directories = [
        "tests/ui",
        "tests/api", 
        "tests/unit",
        "tests/integration",
        "tests/archived",
        "tools/utilities",
        "tools/debug",
        "tools/fixes",
        "tools/analysis",
        "tools/demo",
        "tools/planning"
    ]
    
    for directory in directories:
        if Path(directory).exists():
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory}")
    print()
    
    # 验证根目录清洁度
    print("2. 验证根目录清洁度:")
    py_files = list(Path(".").glob("*.py"))
    if not py_files:
        print("✅ 根目录没有Python文件")
    else:
        print(f"❌ 根目录仍有Python文件: {[f.name for f in py_files]}")
    print()
    
    # 验证测试工具
    print("3. 验证关键工具脚本:")
    tools = [
        "tools/utilities/email_config_manager.py",
        "tools/utilities/fix_email_config.py", 
        "tools/analysis/check_project_progress.py"
    ]
    
    for tool in tools:
        if Path(tool).exists():
            print(f"✅ {tool}")
        else:
            print(f"❌ {tool}")
    print()
    
    # 尝试运行一个简单的pytest测试
    print("4. 验证pytest配置:")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--version"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ pytest可用: {result.stdout.strip()}")
        else:
            print(f"❌ pytest问题: {result.stderr}")
    except Exception as e:
        print(f"❌ pytest测试失败: {e}")
    print()
    
    print("=" * 60)
    print("验证完成！")
    print("=" * 60)
    print()
    print("使用指南:")
    print("- 运行所有测试: pytest")
    print("- 运行UI测试: pytest tests/ui/")
    print("- 运行单元测试: pytest tests/unit/")
    print("- 运行集成测试: pytest tests/integration/")
    print("- 运行邮件配置工具: python -m tools.utilities.email_config_manager")

if __name__ == "__main__":
    main()
