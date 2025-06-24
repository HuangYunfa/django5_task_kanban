#!/usr/bin/env python
"""
项目脚本运行器 - 从项目根目录运行脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def run_script_from_root(script_path, *args):
    """从项目根目录运行脚本"""
    
    # 获取项目根目录
    current_dir = Path(__file__).parent.parent.parent
    script_full_path = current_dir / script_path
    
    if not script_full_path.exists():
        print(f"❌ 脚本不存在: {script_full_path}")
        return False
    
    # 切换到项目根目录
    original_dir = os.getcwd()
    try:
        os.chdir(current_dir)
        print(f"📁 工作目录: {current_dir}")
        print(f"🚀 运行脚本: {script_path}")
        
        # 运行脚本
        cmd = [sys.executable, str(script_path)] + list(args)
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
        
    finally:
        os.chdir(original_dir)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python tools/utilities/run_script.py <script_path> [args...]")
        print("")
        print("示例:")
        print("  python tools/utilities/run_script.py tools/utilities/reset_superuser_password.py")
        print("  python tools/utilities/run_script.py tests/integration/email/test_smtp_simple.py")
        return False
    
    script_path = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    return run_script_from_root(script_path, *args)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
