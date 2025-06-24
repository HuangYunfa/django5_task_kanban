#!/usr/bin/env python
"""
快速启动UI测试脚本
"""
import os
import sys
import subprocess
import asyncio

def check_django_server():
    """检查Django服务器是否运行"""
    import urllib.request
    try:
        response = urllib.request.urlopen('http://127.0.0.1:8000/')
        return response.status == 200
    except:
        return False

def start_django_server():
    """启动Django开发服务器"""
    print("🚀 启动Django开发服务器...")
    try:
        # 切换到项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        
        # 启动Django服务器
        process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver', '--noreload'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ 等待Django服务器启动...")
        import time
        time.sleep(5)  # 等待服务器启动
        
        if check_django_server():
            print("✅ Django服务器已启动")
            return process
        else:
            print("❌ Django服务器启动失败")
            return None
    except Exception as e:
        print(f"❌ 启动Django服务器出错: {e}")
        return None

async def run_ui_test():
    """运行UI测试"""
    # 导入测试函数
    from test_workflow_ui_simple import main
    await main()

def main():
    """主函数"""
    print("🎭 Playwright UI测试启动器")
    print("=" * 50)
    
    # 检查Django服务器
    if not check_django_server():
        print("⚠️  Django服务器未运行")
        choice = input("是否自动启动Django服务器? (y/n): ").lower()
        
        if choice == 'y':
            server_process = start_django_server()
            if not server_process:
                print("❌ 无法启动Django服务器，请手动启动")
                return
        else:
            print("请手动启动Django服务器: python manage.py runserver")
            return
    else:
        print("✅ Django服务器正在运行")
    
    # 运行UI测试
    print("\n🎭 开始运行UI测试...")
    asyncio.run(run_ui_test())

if __name__ == '__main__':
    main()
